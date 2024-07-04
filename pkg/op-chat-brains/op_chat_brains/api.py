from flask import Flask, request, jsonify
from op_chat_brains.structured_logger import StructuredLogger
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


app = Flask(__name__)

logger = StructuredLogger()

rag = RAGModel(
    dbs_name=DEFAULT_DBS,
    embeddings_name=EMBEDDING_MODEL,
    chat_pars={
        "model": CHAT_MODEL,
        "temperature": CHAT_TEMPERATURE,
        "max_retries": MAX_RETRIES,
    },
    prompt_template=PROMPT_TEMPLATE,
    retriever_pars={"search_kwargs": {"k": K_RETRIEVER}},
    vectorstore=VECTORSTORE,
)


@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    question = data.get("question")
    if not question:
        return jsonify({"error": "No question provided"}), 400

    output = rag.predict(question)
    logger.log_query(question, output)

    return jsonify({"answer": output["answer"]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3123)
