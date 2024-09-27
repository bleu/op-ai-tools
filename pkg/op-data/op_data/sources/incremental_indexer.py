import tempfile
import os
import zlib
import json
import io
import faiss
from langchain_community.vectorstores import FAISS
from tortoise.exceptions import DoesNotExist
from op_data.db.models import FaissIndex, ManagedIndex, RawTopic
import asyncio
from op_brains.documents import DataExporter
from op_brains.setup import reorder_index, generate_indexes_from_fragment
from op_brains.chat.apis import access_APIs
import numpy as np
from op_brains.config import CHAT_MODEL, EMBEDDING_MODEL
import datetime as dt
import pickle
from op_core.config import config
import time
import boto3
from botocore.client import Config


class IncrementalIndexerService:
    s3 = boto3.client(
        "s3",
        **config.get_r2_config(),
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )

    def __init__(self):
        self.embeddings = access_APIs.get_embedding(EMBEDDING_MODEL)
        self.llm = access_APIs.get_llm(CHAT_MODEL)
        self.vector_stores = {}
        self.questions_index = {}
        self.keywords_index = {}
        self.should_save_update = False

    @classmethod
    def retrieve_object_from_s3(cls, key):
        return cls.s3.get_object(Bucket=config.R2_BUCKET_NAME, Key=key)["Body"].read()

    def upload_to_s3(self, key, data):
        return self.s3.put_object(Bucket=config.R2_BUCKET_NAME, Key=key, Body=data)

    async def get_updated_documents(self):
        return await DataExporter.get_langchain_documents(only_not_embedded=True)

    async def save_managed_index(self, index, index_type, updated_documents_urls):
        index_questions = list(index.keys())
        index_embed = np.array(self.embeddings.embed_documents(index_questions))
        buffer = io.BytesIO()
        np.savez_compressed(buffer, index_embed=index_embed)
        embed_bytes = buffer.getvalue()

        reordered_index = await reorder_index(index, updated_documents_urls)

        jsonObjectKey = f"managed_index_reranked_{int(time.time())}.json"
        compressedObjectKey = f"compressed_managed_index{int(time.time())}.zlib"

        # Save the compressed data to the R2 bucket
        self.upload_to_s3(key=jsonObjectKey, data=json.dumps(reordered_index))
        self.upload_to_s3(key=compressedObjectKey, data=embed_bytes)

        # Save the object key to the database
        await ManagedIndex.create(
            jsonObjectKey=jsonObjectKey,
            compressedObjectKey=compressedObjectKey,
            indexType=index_type,
        )

    @classmethod
    async def get_latest_compressed_faiss_indexes(cls):
        try:
            last_saved_indexes = await FaissIndex.all().order_by("-createdAt").first()
            if last_saved_indexes is None:
                return None

            # Load the compressed data from the R2 bucket
            return cls.retrieve_object_from_s3(
                last_saved_indexes.objectKey,
            )
        except DoesNotExist:
            return None

    @classmethod
    async def load_faiss_indexes(cls, embeddings):
        compressed_data = await cls.get_latest_compressed_faiss_indexes()

        if compressed_data is None:
            return {}

        decompressed_data = zlib.decompress(compressed_data)
        folder_content = json.loads(decompressed_data.decode("utf-8"))

        indexes = {}
        for db_name, index_data in folder_content.items():
            serialized_index = index_data.encode("latin-1")

            faiss_index = FAISS.deserialize_from_bytes(
                serialized_index, embeddings, allow_dangerous_deserialization=True
            )

            indexes[db_name] = faiss_index

        return indexes

    async def save_faiss_indexes(self):
        folder_content = {}
        for db_name, db in self.vector_stores.items():
            serialized_data = db.serialize_to_bytes()
            folder_content[db_name] = serialized_data.decode("latin-1")

        json_data = json.dumps(folder_content)
        compressed_data = zlib.compress(json_data.encode("utf-8"))

        key = f"compressed_faiss_indexes_{int(time.time())}.zlib"

        # Save the compressed data to the R2 bucket
        self.upload_to_s3(key, compressed_data)
        # Save the object key to the database
        await FaissIndex.create(objectKey=key)

    @classmethod
    async def get_latest_managed_index(cls, index_type):
        try:
            questions_index = (
                await ManagedIndex.filter(indexType=index_type)
                .order_by("-createdAt")
                .first()
            )
            if questions_index is None:
                return {}

            # Load the index from the R2 bucket
            object_key = questions_index.jsonObjectKey
            data = cls.retrieve_object_from_s3(
                object_key,
            )

            return json.loads(data)

        except DoesNotExist:
            return {}

    def get_updated_documents_urls(self, data):
        urls = []
        for db_name, contexts in data.items():
            for context in contexts:
                url = context.dict()["metadata"]["url"]
                urls.append(url)
        return urls

    async def save_raw_topics_as_embedded(self, urls):
        await RawTopic.filter(url__in=urls).update(
            lastEmbeddedAt=dt.datetime.now(dt.UTC)
        )
        return urls

    def update_index(self, db_name, contexts):
        if db_name in self.vector_stores:
            # Skip updating documentation index as it's hardcoded
            if db_name == "documentation":
                return False

            vector_store = self.vector_stores[db_name]

            # Update existing index by adding new documents or updating existing ones
            for document in contexts:
                if not isinstance(
                    vector_store.docstore.search(document.metadata["url"]), str
                ):
                    vector_store.delete(ids=[document.metadata["url"]])
                    vector_store.add_documents(
                        [document], ids=[document.metadata["url"]]
                    )
                else:
                    vector_store.add_documents(
                        [document], ids=[document.metadata["url"]]
                    )

        else:
            # Create new index if it doesn't exist
            self.vector_stores[db_name] = FAISS.from_documents(
                contexts,
                self.embeddings,
                ids=[context.metadata["url"] for context in contexts],
            )

        self.should_save_update = True
        return True

    async def parse_index(self, contexts, llm):
        q_index, kw_index = await generate_indexes_from_fragment(contexts, llm)

        for q, urls in q_index.items():
            if q not in self.questions_index:
                self.questions_index[q] = []
            self.questions_index[q].extend(
                [url for url in urls if url not in self.questions_index[q]]
            )

        for k, urls in kw_index.items():
            if k not in self.keywords_index:
                self.keywords_index[k] = []
            self.keywords_index[k].extend(
                [url for url in urls if url not in self.keywords_index[k]]
            )

    async def acquire_and_save(self):
        """
        Perform the incremental update to the indexes by updating existing indexes or creating than when necessary, and saves the updated data.

        This method performs the following steps:
        - Loads existing question and keyword indexes files from the postgres database.
        - Loads all existing vector stores from the postgres database.
        - Updates the vector stores with new documents.
        - If updates were made, saves all indexes, including vector stores, question index, and keyword index.
        - Marks the raw topics as embedded (updated) so we will update only when new topics exists.

        Args:
            model (str): The name of the language model to use. Defaults to "gpt-4o-mini".

        Returns:
            None

        Note:
            This method sets the `should_save_update` flag to True if any updates are made to the indexes.
        """
        data = await self.get_updated_documents()

        self.questions_index = await self.get_latest_managed_index("questions")
        self.keywords_index = await self.get_latest_managed_index("keywords")
        self.vector_stores = await IncrementalIndexerService.load_faiss_indexes(
            self.embeddings
        )

        for db_name, contexts in data.items():
            if "archived" in db_name:
                continue

            index_updated = self.update_index(db_name, contexts)
            if index_updated:
                await self.parse_index(contexts, self.llm)

        if not self.should_save_update:
            return

        updated_documents_urls = self.get_updated_documents_urls(data)
        # Save updated indexes and set the raw topics as embedded
        await self.save_faiss_indexes()
        await self.save_managed_index(
            self.questions_index, "questions", updated_documents_urls
        )
        await self.save_managed_index(
            self.keywords_index, "keywords", updated_documents_urls
        )
        await self.save_raw_topics_as_embedded(updated_documents_urls)
