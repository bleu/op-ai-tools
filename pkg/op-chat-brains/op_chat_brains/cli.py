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
    SUMMARIZER_MODEL,
)
from op_chat_brains.chat.prompts import PROMPT_BUILDER, PROMPT_BUILDER_EXPANDER
from op_chat_brains.chat.utils import process_question
from op_chat_brains.summarizer.summarizer import summarize_thread
from op_chat_brains.exceptions import OpChatBrainsException

logger = StructuredLogger()


def get_config():
    return {
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


@click.group()
def cli():
    pass


@cli.command()
@click.argument("question")
@click.option("--rag-structure", default=DEFAULT_RAG_STRUCTURE)
def ask(question: str, rag_structure: str) -> None:
    try:
        result = process_question(question, rag_structure, logger, get_config())
        click.echo(result["answer"])
    except OpChatBrainsException as e:
        click.echo(f"Error: {str(e)}", err=True)


@cli.command()
@click.argument("url")
@click.option(
    "--model", default=SUMMARIZER_MODEL, help="Model to use for summarization"
)
def summarize(url: str, model: str) -> None:
    try:
        summary = summarize_thread(url, model)
        click.echo(summary)
        logger.log_summary(url, summary)
    except OpChatBrainsException as e:
        click.echo(f"Error: {str(e)}", err=True)


if __name__ == "__main__":
    cli()
