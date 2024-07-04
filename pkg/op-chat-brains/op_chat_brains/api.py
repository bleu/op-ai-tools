from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from op_chat_brains.exceptions import OpChatBrainsException
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
    API_RATE_LIMIT,
    API_SECRET_KEY,
)
from op_chat_brains.prompts import PROMPT_BUILDER, PROMPT_BUILDER_EXPANDER

from op_chat_brains.utils import process_question

app = Flask(__name__)
app.config["SECRET_KEY"] = API_SECRET_KEY

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[f"{API_RATE_LIMIT} per minute"],
    storage_uri="memory://",
)

logger = StructuredLogger()


@app.route("/predict", methods=["POST"])
@limiter.limit(f"{API_RATE_LIMIT} per minute")
def predict():
    data = request.json
    question = data.get("question")
    rag_structure = data.get("rag_structure", DEFAULT_RAG_STRUCTURE)

    if not question:
        return jsonify({"error": "No question provided"}), 400

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
        return jsonify({"error": str(result["error"])}), 400 if isinstance(
            result["error"], OpChatBrainsException
        ) else 500
    else:
        return jsonify({"answer": result["answer"]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3123)
