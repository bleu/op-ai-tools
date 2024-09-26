from typing import Tuple
import os

from langchain_community.vectorstores import FAISS

from op_brains.config import DB_STORAGE_PATH, EMBEDDING_MODEL
import asyncio
from op_brains.chat import model_utils

from typing import Optional
import time
from op_data.sources.incremental_indexer import IncrementalIndexerService
from op_core.logger import get_logger

logger = get_logger(__name__)


class CachedDatabaseLoader:
    _db_cache: Optional[FAISS] = None
    _db_cache_time: Optional[float] = None
    _cache_lock = asyncio.Lock()
    CACHE_TTL = 10 # * 60 * 24  # day in seconds

    @classmethod
    async def load_db(cls, vectorstore: str = "faiss") -> FAISS:
        if vectorstore == "faiss":
            async with cls._cache_lock:
                current_time = time.time()
                if (
                    cls._db_cache is None
                    or (current_time - cls._db_cache_time) > cls.CACHE_TTL
                ):
                    
                    embeddings = model_utils.access_APIs.get_embedding(EMBEDDING_MODEL)
                    loaded_dbs = await IncrementalIndexerService.load_faiss_indexes(
                        embeddings
                    )
                    
                    logger.info(f"Embedding model: {EMBEDDING_MODEL}")
                    logger.info(f"Merging databases: {len(loaded_dbs.keys())}")
                    logger.info(f"Loaded databases: {loaded_dbs}")

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
