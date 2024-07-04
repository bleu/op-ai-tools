from functools import lru_cache
from typing import Dict, Any
from op_chat_brains.model import RAGModel
from op_chat_brains.exceptions import UnsupportedVectorstoreError, OpChatBrainsException
from op_chat_brains.structured_logger import StructuredLogger


@lru_cache(maxsize=None)
def get_rag_model(
    rag_structure,
    dbs_name,
    embeddings_name,
    retriever_pars,
    vectorstore,
    prompt_builder,
    prompt_builder_expander,
    chat_pars,
):
    rag_classes = {
        "openai-simple": RAGModel.SimpleOpenAI,
        "claude-simple": RAGModel.SimpleClaude,
        "claude-expander": RAGModel.ExpanderClaude,
    }

    rag_class = rag_classes.get(rag_structure)
    if not rag_class:
        raise UnsupportedVectorstoreError(f"Unsupported RAG structure: {rag_structure}")

    return rag_class(
        dbs_name=dbs_name,
        embeddings_name=embeddings_name,
        retriever_pars=retriever_pars,
        vectorstore=vectorstore,
        prompt_builder=prompt_builder,
        prompt_builder_expander=prompt_builder_expander,
        chat_pars=chat_pars,
    )


def process_question(
    question: str, rag_structure: str, logger: StructuredLogger, config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Process a question using the specified RAG model.

    :param question: The input question
    :param rag_structure: The RAG structure to use
    :param logger: The logger instance
    :param config: A dictionary containing configuration parameters
    :return: A dictionary containing the answer and any error information
    """

    try:
        rag = get_rag_model(
            rag_structure=rag_structure,
            dbs_name=tuple(config["DEFAULT_DBS"]),
            embeddings_name=config["EMBEDDING_MODEL"],
            retriever_pars={"search_kwargs": {"k": config["K_RETRIEVER"]}},
            vectorstore=config["VECTORSTORE"],
            prompt_builder=config["PROMPT_BUILDER"],
            prompt_builder_expander=config["PROMPT_BUILDER_EXPANDER"],
            chat_pars={
                "model": config["CHAT_MODEL_CLAUDE"]
                if "claude" in rag_structure
                else config["CHAT_MODEL_OPENAI"],
                "temperature": config["CHAT_TEMPERATURE"],
                "max_retries": config["MAX_RETRIES"],
            },
        )
        output = rag.predict(question)
        logger.log_query(question, output)
        return {"answer": output["answer"], "error": None}
    except OpChatBrainsException as e:
        logger.logger.error(f"OpChatBrains error during prediction: {str(e)}")
        return {"answer": None, "error": e}
    except Exception as e:
        logger.logger.error(f"Unexpected error during prediction: {str(e)}")
        return {
            "answer": None,
            "error": "An unexpected error occurred during prediction",
        }
