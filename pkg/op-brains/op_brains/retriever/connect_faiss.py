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
from aiocache import cached

logger = get_logger(__name__)

# @cached(ttl=10)
async def load_faiss_indexes(vectorstore: str = "faiss") -> FAISS:
    if vectorstore == "faiss":
        embeddings = model_utils.access_APIs.get_embedding(EMBEDDING_MODEL)
        loaded_dbs = await IncrementalIndexerService.load_faiss_indexes(
            embeddings
        )
        
        logger.info(f"Embedding model: {EMBEDDING_MODEL}")
        logger.info(f"Merging databases: {len(loaded_dbs.keys())}")
        # logger.info(f"Loaded databases: {loaded_dbs}")

        merged_db = None
        for key, faiss_index in loaded_dbs.items():
            
            if merged_db is None:
                merged_db = faiss_index
            else:
                logger.info(f"merging {key}, {faiss_index} into {merged_db}, {type(merged_db)}, {type(faiss_index)}")
                try:
                    merged_db.merge_from(faiss_index)
                except Exception as e:
                    logger.error(f"Failed to merge faiss databases")
                    raise e
        
        logger.info(f"Successfully merged databases: {len(loaded_dbs.keys())}")

        return merged_db
    raise ValueError(f"Unsupported vectorstore: {vectorstore}")