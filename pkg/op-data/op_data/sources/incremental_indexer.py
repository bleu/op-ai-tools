import tempfile
import os
import zlib
import json
import io
import faiss
from langchain_community.vectorstores import FAISS
from tortoise.exceptions import DoesNotExist
from op_data.db.models import Embedding, EmbeddingIndex
import asyncio
from op_brains.documents import DataExporter
from langchain.docstore.in_memory import InMemoryDocstore
from op_brains.setup import reorder_index, generate_indexes_from_fragment
from op_brains.chat import model_utils
import numpy as np
from op_brains.config import CHAT_MODEL, EMBEDDING_MODEL
from .mock import QUESTIONS_INDEX, KEYWORDS_INDEX


class IncrementalIndexerService:
    def __init__(self):
        self.embeddings = model_utils.access_APIs.get_embedding(EMBEDDING_MODEL)
        self.llm = model_utils.access_APIs.get_llm(CHAT_MODEL)
        self.vector_stores = {}
        self.questions_index = {}
        self.keywords_index = {}
        self.should_save_update = False

    async def get_updated_documents(self):
        return await DataExporter.get_langchain_documents(only_not_embedded=True)

    async def save_embedding_index(self, index, index_type, updated_documents_urls):
        index_questions = list(index.keys())
        index_embed = np.array(self.embeddings.embed_documents(index_questions))
        buffer = io.BytesIO()
        np.savez_compressed(buffer, index_embed=index_embed)
        embed_bytes = buffer.getvalue()

        reorded_index = await reorder_index(index, updated_documents_urls)

        await EmbeddingIndex.create(
            data=reorded_index,
            embedData=embed_bytes,
            indexType=index_type
        )

    @classmethod
    async def get_compressed_embeddings(cls):
        try:
            last_embedding = await Embedding.all().order_by("-createdAt").first()
            if last_embedding is None:
                return None
            return last_embedding.compressedData
        except DoesNotExist:
            return None

    @classmethod
    async def get_embedding_index(cls, index_type):
        try:
            questions_index = (
                await EmbeddingIndex.filter(indexType=index_type)
                .order_by("-createdAt")
                .first()
            )
            if questions_index is None:
                return {}
            return questions_index.data
        except DoesNotExist:
            return {}
    
    @classmethod
    async def get_compressed_embeddings(cls):
        try:
            last_embedding = await Embedding.all().order_by("-createdAt").first()
            if last_embedding is None:
                return None
            return last_embedding.compressedData
        except DoesNotExist:
            return None
    
    @classmethod
    async def load_all_indexes(cls, embeddings):
        compressed_data = await cls.get_compressed_embeddings()

        if compressed_data is None:
            return {}

        decompressed_data = zlib.decompress(compressed_data)
        folder_content = json.loads(decompressed_data.decode("utf-8"))

        indexes = {}
        for db_name, index_data in folder_content.items():
            serialized_index = index_data.encode("latin-1")
            
            faiss_index = FAISS.deserialize_from_bytes(
                serialized_index, 
                embeddings,
                allow_dangerous_deserialization=True
            )
            
            indexes[db_name] = faiss_index

        return indexes
    
    async def save_all_indexes(self):
        folder_content = {}
        for db_name, db in self.vector_stores.items():
            serialized_data = db.serialize_to_bytes()
            folder_content[db_name] = serialized_data.decode("latin-1")
            
        json_data = json.dumps(folder_content)
        compressed_data = zlib.compress(json_data.encode("utf-8"))
        await Embedding.create(compressedData=compressed_data)

    def get_updated_documents_urls(self, data):
        urls = []
        for db_name, contexts in data.items():
            for context in contexts:
                url = context.dict()["metadata"]["url"]
                urls.append(url)
        return urls
    
    async def save_raw_topics_as_embedded(self, urls):
        # await RawTopic.filter(url__in=urls).update(
        #     lastEmbeddedAt=dt.datetime.now(dt.UTC)
        # )
        await asyncio.sleep(1)
        return urls

    def update_index(self, db_name, contexts):        
        if db_name in self.vector_stores:
            # Skip updating documentation index as it's hardcoded
            if db_name == "documentation":
                return False
            
            vector_store = self.vector_stores[db_name]
            
            # Update existing index by adding new documents or updating existing ones
            for document in contexts:
                if not isinstance(vector_store.docstore.search(document.metadata["url"]), str):
                    vector_store.delete(ids=[document.metadata["url"]])
                    vector_store.add_documents([document], ids = [document.metadata["url"]])
                else:
                    vector_store.add_documents([document], ids = [document.metadata["url"]])

        else:
            # Create new index if it doesn't exist
            self.vector_stores[db_name] = FAISS.from_documents(
                contexts, self.embeddings, ids = [context.metadata["url"] for context in contexts]
            )

        self.should_save_update = True
        return True

    def parse_index(self, contexts, llm):
        q_index, kw_index = generate_indexes_from_fragment(contexts, llm)

        for q, urls in q_index.items():
            if q not in self.questions_index:
                self.questions_index[q] = []
            self.questions_index[q].extend([url for url in urls if url not in self.questions_index[q]])

        for k, urls in kw_index.items():
            if k not in self.keywords_index:
                self.keywords_index[k] = []
            self.keywords_index[k].extend([url for url in urls if url not in self.keywords_index[k]])

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

        self.questions_index = await self.get_embedding_index("questions")
        self.keywords_index = await self.get_embedding_index("keywords")
        self.vector_stores = await IncrementalIndexerService.load_all_indexes(
            self.embeddings
        )

        for db_name, contexts in data.items():
            if "archived" in db_name:
                continue

            index_updated = self.update_index(db_name, contexts)
            if index_updated:
                self.parse_index(contexts, self.llm)
        
        if not self.should_save_update:
            return
        
        updated_documents_urls = self.get_updated_documents_urls(data)

        # Save updated indexes and set the raw topics as embedded
        await asyncio.gather(
            self.save_all_indexes(),
            self.save_embedding_index(self.questions_index, "questions", updated_documents_urls),
            self.save_embedding_index(self.keywords_index, "keywords", updated_documents_urls),
            # self.save_raw_topics_as_embedded(updated_documents_urls)
        )
