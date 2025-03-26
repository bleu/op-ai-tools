import os
from op_brains.chat import model_utils
from op_brains.chat.system_structure import RAGSystem
from typing import Dict, Any, List, Tuple
from op_brains.documents import DataExporter
import numpy as np
import io
from op_data.db.models import ManagedIndex
import pickle
import zlib
from op_brains.config import DB_STORAGE_PATH, CHAT_MODEL
from op_data.sources.incremental_indexer import IncrementalIndexerService
import json
import asyncio
from aiocache import cached
from op_core.logger import get_logger

logger = get_logger(__name__)


def transform_memory_entries(entries: List[Dict[str, str]]) -> List[Tuple[str, str]]:
    """
    Transforms a list of dictionaries containing 'name' and 'message' keys
    into a list of tuples with the same values.

    Args:
        entries (List[Dict[str, str]]): A list of dictionaries, each with 'name' and 'message' keys.

    Returns:
        List[Tuple[str, str]]: A list of tuples, each containing the 'name' and 'message' values.
    """
    return [
        (entry["name"], entry["message"]) for entry in entries if "message" in entry
    ]


async def build_managed_index(k_max=5, treshold=0.95, indexType="questions"):
    index = (
        await ManagedIndex.filter(indexType=indexType).order_by("-createdAt").first()
    )

    managed_index_json = IncrementalIndexerService.retrieve_object_from_s3(
        index.jsonObjectKey
    )
    managed_index_npz = IncrementalIndexerService.retrieve_object_from_s3(
        index.compressedObjectKey
    )
    managed_index_npz_bytes = io.BytesIO(managed_index_npz)
    loaded_data = np.load(managed_index_npz_bytes)

    embed_index = loaded_data["index_embed"]
    index_dict = json.loads(managed_index_json)

    logger.info(f"Building managed index, {indexType}, {len(index_dict.keys())}")
    return model_utils.RetrieverBuilder.build_index(
        index_dict, embed_index, k_max, treshold
    )


# @cached(ttl=60 * 60 * 24)
async def get_indexes():
    questions_task = build_managed_index(k_max=5, treshold=0.93, indexType="questions")
    keywords_task = build_managed_index(k_max=5, treshold=0.95, indexType="keywords")
    default_task = model_utils.RetrieverBuilder.build_faiss_retriever(k=5)

    (
        questions_index_retriever,
        keywords_index_retriever,
        default_retriever,
    ) = await asyncio.gather(questions_task, keywords_task, default_task)

    return questions_index_retriever, keywords_index_retriever, default_retriever


async def process_question(
    question: str,
    memory: List[Dict[str, str]],
    # config: Dict[str, Any],
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Processes a given question using a RAG model,
    leveraging contextual memory and retrievers for enhanced response generation.

    Args:
        question (str): The input question to be processed.
        memory (List[Dict[str, str]], optional): A list of dictionaries containing
            previous interactions, each with 'name' (being 'user' or 'chat') and 'message' keys.
            Defaults to an empty list.

    Returns:
        A dict containing the response to the question.
            The dictionary has the following keys:
            - "answer" (str): The generated answer from the RAG model.
            - "error" (str): An error message if an exception occurred, otherwise None.

    Raises:
        Exception: Any unexpected error that occurs during the prediction process
            is caught and logged, with a user-friendly error message returned in the dictionary.
    """

    contexts_df = await DataExporter.get_dataframe(only_not_embedded=False)

    chat_model = (
        CHAT_MODEL,
        {
            "temperature": 0.0,
            "max_retries": 5,
            "max_tokens": 1024,
            "timeout": 60,
        },
    )

    try:
        (
            questions_index_retriever,
            keywords_index_retriever,
            default_retriever,
        ) = await get_indexes()

        def contains(must_contain):
            return lambda similar: [s for s in similar if must_contain in s]

        async def retriever(query: dict, reasoning_level: int) -> list:
            if reasoning_level < 1 and "keyword" in query:
                if "instance" in query:
                    context = await keywords_index_retriever(
                        query["keyword"],
                        contexts_df,
                        criteria=contains(query["instance"]),
                    )
                else:
                    context = await keywords_index_retriever(
                        query["keyword"], contexts_df
                    )
                return context

            if "question" in query:
                if reasoning_level < 1:
                    context = await questions_index_retriever(
                        query["question"], contexts_df
                    )
                    if len(context) > 0:
                        return context
                return default_retriever(query["question"])

            if "query" in query:
                if reasoning_level > 1:
                    return default_retriever(query["query"])
            return []

        rag_model = RAGSystem(
            reasoning_limit=1,
            models_to_use=[chat_model, chat_model],
            retriever=retriever,
            context_filter=model_utils.ContextHandling.filter,
            system_prompt_preprocessor=model_utils.Prompt.preprocessor,
            system_prompt_responder=model_utils.Prompt.responder,
        )

        formatted_memory = transform_memory_entries(memory)
        result = await rag_model.predict(
            question, contexts_df, memory=formatted_memory, verbose=verbose
        )

        # logger.log_query(question, result)
        return {"data": result["answer"], "error": None}
    except Exception as e:
        logger.error(f"Error. An unexpected error occurred during prediction: {str(e)}")
        return {
            "data": {},
            "error": "An unexpected error occurred during prediction",
        }


# if __name__ == "__main__":
#     print(
#         process_question("Can the length of the challenge period be changed?", [], "")
#     )
