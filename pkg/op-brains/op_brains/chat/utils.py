import os
from op_brains.chat import model_utils
from op_brains.chat.system_structure import RAGSystem
from typing import Dict, Any, List, Tuple
from op_brains.documents import DataExporter
import numpy as np
import io
from op_data.db.models import EmbeddingIndex
import pickle
import zlib
from op_brains.config import DB_STORAGE_PATH, CHAT_MODEL


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


# TODO: cache this function
async def build_questions_index(k_max=2, treshold=0.9, ttl_hash=None):
    del ttl_hash # to emphasize we don't use it and to shut pylint up
    index = (
        await EmbeddingIndex.filter(indexType="questions")
        .order_by("-createdAt")
        .first()
    )

    buffer = io.BytesIO(index.embedData)
    loaded_data = np.load(buffer)
    embed_index = loaded_data["index_embed"]

    compressed_data = index.data
    decompressed_data = zlib.decompress(compressed_data)
    index_dict = pickle.loads(decompressed_data)

    return model_utils.RetrieverBuilder.build_index(
        index_dict, embed_index, k_max, treshold
    )

# TODO: cache this function
async def build_keywords_index(k_max=5, treshold=0.95):
    index = (
        await EmbeddingIndex.filter(indexType="keywords").order_by("-createdAt").first()
    )
    buffer = io.BytesIO(index.embedData)
    loaded_data = np.load(buffer)
    embed_index = loaded_data["index_embed"]
    
    compressed_data = index.data
    decompressed_data = zlib.decompress(compressed_data)
    index_dict = pickle.loads(decompressed_data)

    return model_utils.RetrieverBuilder.build_index(
        index_dict, embed_index, k_max, treshold
    )


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
        questions_index_retriever = await build_questions_index(k_max=5, treshold=0.93)
        keywords_index_retriever = await build_keywords_index(k_max=5, treshold=0.95)
        default_retriever = model_utils.RetrieverBuilder.build_faiss_retriever(
            k=5,
        )

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
    except Exception:
        return {
            "data": None,
            "error": "An unexpected error occurred during prediction",
        }


# if __name__ == "__main__":
#     print(
#         process_question("Can the length of the challenge period be changed?", [], "")
#     )
