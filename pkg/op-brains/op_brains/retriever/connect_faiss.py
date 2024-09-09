from typing import Tuple
import os

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from op_brains.config import DB_STORAGE_PATH, EMBEDDING_MODEL
import asyncio

from typing import Optional
import time


class DatabaseLoader:
    @staticmethod
    def load_db(dbs: Tuple[str, ...], vectorstore: str = "faiss") -> FAISS:
        embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        if vectorstore == "faiss":
            db_paths = [
                os.path.join(DB_STORAGE_PATH, f"{name}_db/faiss/{EMBEDDING_MODEL}")
                for name in dbs
            ]
            loaded_dbs = [
                FAISS.load_local(
                    db_path, embeddings, allow_dangerous_deserialization=True
                )
                for db_path in db_paths
            ]
            merged_db = loaded_dbs[0]
            for db in loaded_dbs[1:]:
                merged_db.merge_from(db)
            return merged_db
        raise ValueError(f"Unsupported vectorstore: {vectorstore}")


class CachedDatabaseLoader:
    _db_cache: Optional[FAISS] = None
    _db_cache_time: Optional[float] = None
    _cache_lock = asyncio.Lock()
    CACHE_TTL = 60 * 60 * 24  # day in seconds

    @classmethod
    async def load_db(cls, dbs: Tuple[str, ...], vectorstore: str = "faiss") -> FAISS:
        if vectorstore == "faiss":
            async with cls._cache_lock:
                current_time = time.time()
                if (
                    cls._db_cache is None
                    or (current_time - cls._db_cache_time) > cls.CACHE_TTL
                ):
                    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
                    loaded_dbs = IncrementalIndexerService.load_all_indexes(embeddings)

                    merged_db = None
                    for key, faiss_index in loaded_dbs.items():
                        if merged_db is None:
                            merged_db = faiss_index
                        else:
                            merged_db.merge_from(faiss_index)

                    cls._db_cache = merged_db
                    cls._db_cache_time = current_time
            return cls._db_cache
        raise ValueError(f"Unsupported vectorstore: {vectorstore}")

    @classmethod
    async def clear_cache(cls):
        async with cls._cache_lock:
            cls._db_cache = None
            cls._db_cache_time = None

    @classmethod
    async def refresh_data(cls):
        await cls.clear_cache()
        await cls.load_db()
