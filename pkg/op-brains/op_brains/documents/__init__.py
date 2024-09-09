import pandas as pd
from op_brains.documents.optimism import (
    FragmentsProcessingStrategy,
    SummaryProcessingStrategy,
)
from typing import Optional, Dict
import asyncio
import aiohttp
import time

chat_sources = [
    # [
    #     FragmentsProcessingStrategy,
    # ],
    [
        SummaryProcessingStrategy,
    ],
]


class DataExporter:
    _dataframe_cache: Optional[pd.DataFrame] = None
    _dataframe_cache_time: Optional[float] = None
    _langchain_documents_cache: Optional[Dict] = None
    _langchain_documents_cache_time: Optional[float] = None
    _cache_lock = asyncio.Lock()
    CACHE_TTL = 60 * 60 * 24  # day in seconds

    @classmethod
    async def get_dataframe(cls, only_not_embedded=False):
        async with cls._cache_lock:
            current_time = time.time()
            if (
                cls._dataframe_cache is None
                or (current_time - cls._dataframe_cache_time) > cls.CACHE_TTL
            ):
                context_df = []
                for priority_class in chat_sources:
                    dfs_class = await asyncio.gather(
                        *[source.dataframe_process(only_not_embedded=only_not_embedded) for source in priority_class]
                    )
                    dfs_class = pd.concat(dfs_class)
                    dfs_class = dfs_class.sort_values(by="last_date", ascending=False)
                    context_df.append(dfs_class)

                cls._dataframe_cache = pd.concat(context_df)
                cls._dataframe_cache_time = current_time

        return cls._dataframe_cache

    @classmethod
    async def get_langchain_documents(cls):
        async with cls._cache_lock:
            current_time = time.time()
            if (
                cls._langchain_documents_cache is None
                or (current_time - cls._langchain_documents_cache_time) > cls.CACHE_TTL
            ):
                out = {}
                async with aiohttp.ClientSession() as session:
                    tasks = []
                    for source in [x for xs in chat_sources for x in xs]:
                        tasks.append(cls._fetch_documents(session, source))
                    results = await asyncio.gather(*tasks)

                    for result in results:
                        out.update(result)

                cls._langchain_documents_cache = out
                cls._langchain_documents_cache_time = current_time

        return cls._langchain_documents_cache

    @staticmethod
    async def _fetch_documents(session, source):
        documents = await source.langchain_process()
        if isinstance(documents, dict):
            return {
                f"{source.name_source}_{key}": value for key, value in documents.items()
            }
        elif isinstance(documents, list):
            return {source.name_source: documents}
        else:
            raise ValueError(f"Unexpected type of documents: {type(documents)}")

    @classmethod
    async def clear_cache(cls):
        async with cls._cache_lock:
            cls._dataframe_cache = None
            cls._dataframe_cache_time = None
            cls._langchain_documents_cache = None
            cls._langchain_documents_cache_time = None

    @classmethod
    async def refresh_data(cls):
        await cls.clear_cache()
        await cls.get_dataframe()
        await cls.get_langchain_documents()
