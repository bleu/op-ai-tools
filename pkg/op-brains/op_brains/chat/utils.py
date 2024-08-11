import os
from op_brains.chat import model_utils
from op_brains.chat.system_structure import RAGSystem
from typing import Dict, Any, List, Tuple

from op_brains.config import DB_STORAGE_PATH


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

        questions_index_retriever = model_utils.RetrieverBuilder.build_questions_index(
            k_max=2, treshold=0.9
        )

        keywords_index_retriever = model_utils.RetrieverBuilder.build_keywords_index(
            k_max=3, treshold=0.95
        )

        def contains(must_contain):
            return lambda similar: [s for s in similar if must_contain in s]

        default_retriever = model_utils.RetrieverBuilder.build_faiss_retriever(
            dbs,
            k=5,
        )

        def retriever(query: dict, reasoning_level: int) -> list:
            if reasoning_level < 2 and "keyword" in query:
                if "instance" in query:
                    context = keywords_index_retriever(
                        query["keyword"], criteria=contains(query["instance"])
                    )
                else:
                    context = keywords_index_retriever(query["keyword"])
                return context

            if "question" in query:
                if reasoning_level < 2:
                    context = questions_index_retriever(query["question"])
                    if len(context) > 0:
                        return context
                return default_retriever(query["question"])
            return []

        rag_model = RAGSystem(
            REASONING_LIMIT=3,
            models_to_use=[chat_model, chat_model],
            retriever=retriever,
            context_filter=model_utils.ContextHandling.filter,
            system_prompt_preprocessor=model_utils.Prompt.preprocessor,
            system_prompt_responder=model_utils.Prompt.responder,
            system_prompt_final_responder=model_utils.Prompt.final_responder,
        )

        formatted_memory = transform_memory_entries(memory)
        result = rag_model.predict(question, memory=formatted_memory, verbose=False)

        # logger.log_query(question, result)
        return {"answer": result["answer"], "error": None}
    except Exception:
        raise
        # logger.logger.error(f"Unexpected error during prediction: {str(e)}")
        return {
            "answer": None,
            "error": "An unexpected error occurred during prediction",
        }


if __name__ == "__main__":
    print(
        process_question("Can the length of the challenge period be changed?", [], "")
    )
