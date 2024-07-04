import click
from op_chat_brains.structured_logger import StructuredLogger
from op_chat_brains.config import (
    DEFAULT_DBS,
    DEFAULT_RAG_STRUCTURE,
    VECTORSTORE,
    EMBEDDING_MODEL,
    CHAT_MODEL_OPENAI,
    CHAT_MODEL_CLAUDE,
    CHAT_TEMPERATURE,
    MAX_RETRIES,
    K_RETRIEVER,
)
from op_chat_brains.prompts import PROMPT_BUILDER, PROMPT_BUILDER_EXPANDER
from op_chat_brains.utils import process_question

logger = StructuredLogger()


@click.command()
@click.argument("question")
@click.option("--rag-structure", default=DEFAULT_RAG_STRUCTURE)
def main(question: str, rag_structure: str) -> None:
    config = {
        "DEFAULT_DBS": DEFAULT_DBS,
        "EMBEDDING_MODEL": EMBEDDING_MODEL,
        "K_RETRIEVER": K_RETRIEVER,
        "VECTORSTORE": VECTORSTORE,
        "PROMPT_BUILDER": PROMPT_BUILDER,
        "PROMPT_BUILDER_EXPANDER": PROMPT_BUILDER_EXPANDER,
        "CHAT_MODEL_CLAUDE": CHAT_MODEL_CLAUDE,
        "CHAT_MODEL_OPENAI": CHAT_MODEL_OPENAI,
        "CHAT_TEMPERATURE": CHAT_TEMPERATURE,
        "MAX_RETRIES": MAX_RETRIES,
    }

    result = process_question(question, rag_structure, logger, config)

    if result["error"]:
        print(f"An error occurred: {result['error']}")
    else:
        print(result["answer"])


if __name__ == "__main__":
    main()
