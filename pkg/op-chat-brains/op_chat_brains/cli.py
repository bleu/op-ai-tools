import click
from op_chat_brains.logging import StructuredLogger
from op_chat_brains.model import RAGModel
from op_chat_brains.config import (
    DEFAULT_DBS,
    VECTORSTORE,
    EMBEDDING_MODEL,
    CHAT_MODEL,
    CHAT_TEMPERATURE,
    MAX_RETRIES,
    K_RETRIEVER,
    PROMPT_TEMPLATE,
)

chat_pars = {
    "model": CHAT_MODEL,
    "temperature": CHAT_TEMPERATURE,
    "max_retries": MAX_RETRIES,
}

rag = RAGModel(
    dbs_name=DEFAULT_DBS,
    embeddings_name=EMBEDDING_MODEL,
    chat_pars=chat_pars,
    prompt_template=PROMPT_TEMPLATE,
    retriever_pars={"search_kwargs": {"k": K_RETRIEVER}},
    vectorstore=VECTORSTORE,
)

logger = StructuredLogger()


@click.command()
@click.argument("question")
def main(question):
    output = rag.predict(question)

    print(output["answer"])
    logger.log_query(question, output)
    logger.close()


if __name__ == "__main__":
    main()
