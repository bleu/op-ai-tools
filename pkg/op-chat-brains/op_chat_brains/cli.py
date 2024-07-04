import click
from op_chat_brains.structured_logger import StructuredLogger
from op_chat_brains.model import RAGModel
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
    PROMPT_TEMPLATE,
    PROMPT_BUILDER,
    PROMPT_BUILDER_EXPANDER,
)

logger = StructuredLogger()


@click.command()
@click.argument("question")
# optional
@click.option("--rag-structure", default=DEFAULT_RAG_STRUCTURE)
def main(question, rag_structure):
    match rag_structure:
        case "openai-simple":
            rag = RAGModel.SimpleOpenAI(
                dbs_name=DEFAULT_DBS,
                embeddings_name=EMBEDDING_MODEL,
                chat_pars={
                    "model": CHAT_MODEL_OPENAI,
                    "temperature": CHAT_TEMPERATURE,
                    "max_retries": MAX_RETRIES,
                },
                prompt_template=PROMPT_TEMPLATE,
                retriever_pars={"search_kwargs": {"k": K_RETRIEVER}},
                vectorstore=VECTORSTORE,
            )
        case "claude-simple":
            rag = RAGModel.SimpleClaude(
                dbs_name=DEFAULT_DBS,
                embeddings_name=EMBEDDING_MODEL,
                retriever_pars={"search_kwargs": {"k": K_RETRIEVER}},
                vectorstore=VECTORSTORE,
                prompt_builder=PROMPT_BUILDER,
                chat_pars={
                    "model": CHAT_MODEL_CLAUDE,
                    "temperature": CHAT_TEMPERATURE,
                    "max_retries": MAX_RETRIES,
                },
            )
        case "claude-expander":
            rag = RAGModel.ExpanderClaude(
                dbs_name=DEFAULT_DBS,
                embeddings_name=EMBEDDING_MODEL,
                retriever_pars={"search_kwargs": {"k": K_RETRIEVER}},
                vectorstore=VECTORSTORE,
                prompt_builder=PROMPT_BUILDER,
                prompt_builder_expander=PROMPT_BUILDER_EXPANDER,
                chat_pars={
                    "model": CHAT_MODEL_CLAUDE,
                    "temperature": CHAT_TEMPERATURE,
                    "max_retries": MAX_RETRIES,
                },
            )
        case _:
            raise ValueError(f"Unsupported RAG structure: {rag_structure}")


    output = rag.predict(question)
    print(output["answer"])
    logger.log_query(question, output)

if __name__ == "__main__":
    main()
