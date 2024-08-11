from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from op_brains.exceptions import UnsupportedVectorstoreError
from op_brains.structured_logger import StructuredLogger
from op_brains.config import (
    API_RATE_LIMIT,
    DEFAULT_RAG_STRUCTURE,
    POSTHOG_API_KEY,
    VECTORSTORE,
    EMBEDDING_MODEL,
    CHAT_MODEL_OPENAI,
    CHAT_MODEL_CLAUDE,
    CHAT_TEMPERATURE,
    MAX_RETRIES,
    K_RETRIEVER,
)
from op_brains.chat.utils import process_question
from flask_cors import CORS
from posthog import Posthog
from functools import wraps
import os

app = Flask(__name__)
CORS(app)
app.config["SECRET_KEY"] = os.getenv("FLASK_API_SECRET_KEY")

posthog = Posthog(POSTHOG_API_KEY, host="https://us.i.posthog.com", sync_mode=True)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[f"{API_RATE_LIMIT} per minute"],
    storage_uri="memory://",
)

logger = StructuredLogger()


def get_config():
    from op_brains.config import (
        DEFAULT_DBS,
    )
    from op_brains.chat.prompts import PROMPT_BUILDER, PROMPT_BUILDER_EXPANDER

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


def handle_question(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        data = request.json
        if data is not None:
            question = data.get("question")
            memory = data.get("memory", [])
            rag_structure = data.get("rag_structure", DEFAULT_RAG_STRUCTURE)
        else:
            question = None
            memory = []
            rag_structure = DEFAULT_RAG_STRUCTURE

        if not question:
            return jsonify({"error": "No question provided"}), 400

        return func(question, memory, rag_structure, *args, **kwargs)

    return wrapper


@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, UnsupportedVectorstoreError):
        return jsonify({"error": str(e)}), 400
    return jsonify({"error": "An unexpected error occurred during prediction"}), 500


@app.route("/predict", methods=["POST"])
@limiter.limit(f"{API_RATE_LIMIT} per minute")
@handle_question
def predict(question, memory, rag_structure):
    result = process_question(question, memory, rag_structure)

    user_token = request.headers.get("x-user-id")
    posthog.capture(
        user_token,
        "MODEL_PREDICTED_ANSWER",
        {
            "endpoint": "predict",
            "question": question,
            "answer": result.get("answer"),
            "error": result.get("error"),
            "rag_structure": rag_structure,
        },
    )
    posthog.shutdown()

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3123)
