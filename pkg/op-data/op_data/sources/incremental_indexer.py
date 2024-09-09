import tempfile
import os
import zlib
import json
import io
import faiss
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from tortoise.exceptions import DoesNotExist
from langchain.embeddings import HuggingFaceEmbeddings
from op_data.db.models import Embedding
import asyncio
from op_brains.documents import DataExporter
from langchain.docstore.in_memory import InMemoryDocstore
import datetime as dt


class IncrementalIndexerService:
    def __init__(self):
        # self.embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)    ### todo: make it work for OpenAIEmbeddings
        self.embeddings = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
        self.vector_stores = {}

    async def get_updated_documents(self):
        return await DataExporter.get_langchain_documents()
    
    async def save_compressed_folder(self, compressed_data):
        await Embedding.create(compressedData=compressed_data)

    @classmethod
    async def get_compressed_embeddings(cls):        
        try:
            last_embedding = await Embedding.all().order_by('-createdAt').first()
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
        folder_content = json.loads(decompressed_data.decode('utf-8'))

        indexes = {}
        for db_name, index_data in folder_content.items():
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(index_data.encode('latin-1'))
                temp_file.flush()

                # Read the index from the temporary file
                index = faiss.read_index(temp_file.name)
                # indexes[db_name] = FAISS.load_local(temp_file.name, embeddings, allow_dangerous_deserialization=True)
                
            os.unlink(temp_file.name)

            # Create the FAISS object
            docstore = InMemoryDocstore({})
            indexes[db_name] = FAISS(embeddings.embed_query, index, docstore, {})
            # indexes[db_name] = FAISS(embeddings.embed_query, index, None, {})

        return indexes

    async def save_all_indexes(self):
        folder_content = {}
        for db_name, db in self.vector_stores.items():
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                faiss.write_index(db.index, temp_file.name)
                with open(temp_file.name, 'rb') as f:
                    index_data = f.read()
                
                # store the binary data in the folder_content dictionary
                folder_content[db_name] = index_data.decode('latin-1')
                
            os.unlink(temp_file.name)

        # serialize and compress the folder content
        json_data = json.dumps(folder_content)
        compressed_data = zlib.compress(json_data.encode('utf-8'))
        
        # Save the compressed data
        await self.save_compressed_folder(compressed_data)

    async def update_index(self, db_name, contexts):    ### todo: replace this code with notebook results
        if db_name in self.vector_stores:
            # Add new documents to existing index 
            self.vector_stores[db_name].add_documents(contexts)
        else:
            # Create new index if it doesn't exist
            self.vector_stores[db_name] = FAISS.from_documents(contexts, self.embeddings)

    async def save_raw_topics_as_embedded(self, data):
        urls = []
        for db_name, contexts in data.items():
            for context in contexts:
                url = context.dict()['metadata']['url']
                urls.append(url)

        # await RawTopic.filter(url__in=urls).update(
        #     lastEmbeddedAt=dt.datetime.now(dt.UTC)
        # )
        await asyncio.sleep(1)
        return urls
    
    async def acquire_and_save(self):
        self.vector_stores = await IncrementalIndexerService.load_all_indexes(self.embeddings)

        data = await self.get_updated_documents()
        
        for db_name, contexts in data.items():
            await self.update_index(db_name, contexts)
        
        # Save all indexes after update
        await self.save_all_indexes()

        urls = await self.save_raw_topics_as_embedded(data)
        
