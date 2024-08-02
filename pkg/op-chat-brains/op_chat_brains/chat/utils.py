from op_chat_brains.chat.system_structure import RAGModel
from op_chat_brains.chat.model_utils import (
    ContextHandling,
    access_APIs,
    RetrieverBuilder,
)
from typing import Dict, Any, List, Tuple
from op_chat_brains.chat.prompts import Prompt
from op_chat_brains.config import DB_STORAGE_PATH
import os
from op_chat_brains.structured_logger import StructuredLogger

def transform_memory_entries(entries: List[Dict[str, str]]) -> List[Tuple[str, str]]:
    """
    Transforms a list of dictionaries containing 'name' and 'message' keys
    into a list of tuples with the same values.

    Args:
        entries (List[Dict[str, str]]): A list of dictionaries, each with 'name' and 'message' keys.

    Returns:
        List[Tuple[str, str]]: A list of tuples, each containing the 'name' and 'message' values.
    """
    return [(entry["name"], entry["message"]) for entry in entries]


def process_question(
    question: str,
    memory: List[Dict[str, str]],
    rag_structure,
    # logger: StructuredLogger,
    # config: Dict[str, Any],
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

    embedding_model = "text-embedding-ada-002"
    chat_model = (
        "gpt-4o-mini",
        {
            "temperature": 0.0,
            "max_retries": 5,
            "max_tokens": 1024,
            "timeout": 60,
        },
    )

    try:
        list_dbs = os.listdir(DB_STORAGE_PATH)
        list_dbs = [db[:-3] for db in list_dbs if db[-3:] == "_db"]
        filter_out_dbs = ["summary_archived___old_missions"]
        dbs = [db for db in list_dbs if db not in filter_out_dbs]

        index_retriever = RetrieverBuilder.build_index(
            embedding_model, k_max=2, treshold=0.9
        )

        default_retriever = RetrieverBuilder.build_faiss_retriever(
            dbs,
            embedding_model,
            k=5,
        )

        # Instantiate RAGModel with parameters
        rag_model = RAGModel(
            REASONING_LIMIT=3,
            models_to_use=[chat_model, chat_model],
            index_retriever=index_retriever,
            factual_retriever=default_retriever,
            temporal_retriever=default_retriever,
            context_filter=ContextHandling.filter,
            system_prompt_preprocessor=Prompt.preprocessor,
            system_prompt_responder=Prompt.responder,
            system_prompt_final_responder=Prompt.final_responder,
        )

        formatted_memory = transform_memory_entries(memory)
        result = rag_model.predict(question, memory=formatted_memory, verbose=False)

        # logger.log_query(question, result)
        return {"answer": result["answer"], "error": None}
    except Exception as e:
        # logger.logger.error(f"Unexpected error during prediction: {str(e)}")
        return {
            "answer": None,
            "error": "An unexpected error occurred during prediction",
        }
