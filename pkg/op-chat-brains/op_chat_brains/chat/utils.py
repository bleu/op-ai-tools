from op_chat_brains.chat.system_structure import RAGModel
from op_chat_brains.chat.model_utils import ContextHandling, access_APIs, RetrieverBuilder
from typing import Dict, Any
from op_chat_brains.chat.prompts import Prompt
from op_chat_brains.config import DB_STORAGE_PATH
import os


def process_question(question: str) -> Dict[str, Any]:
    """
    TODO: add docstring
    """

    embedding_model = "text-embedding-ada-002"
    chat_model = ("gpt-4o-mini", {
                "temperature": 0.0,
                "max_retries": 5,
                "max_tokens": 1024,
                "timeout": 60,
            })

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

        sample_memory = []
        result = rag_model.predict(question, memory=sample_memory, verbose=True)

        return {
            "answer": result,
            "error": None,
        }

    except Exception as e:
        # logger.logger.error(f"Unexpected error during prediction: {str(e)}")
        print(f"Unexpected error during prediction: {str(e)}")
        return {
            "answer": None,
            "error": "An unexpected error occurred during prediction",
        }

if __name__ == "__main__":
    print(process_question("Can Optimism currently censor user transactions?"))