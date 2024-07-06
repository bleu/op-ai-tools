from flask import Flask, Response, stream_with_context, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from op_chat_brains.structured_logger import StructuredLogger
from op_chat_brains.config import (
    API_RATE_LIMIT,
    API_SECRET_KEY,
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
from op_chat_brains.utils import process_question_stream, process_question
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config["SECRET_KEY"] = API_SECRET_KEY

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[f"{API_RATE_LIMIT} per minute"],
    storage_uri="memory://",
)

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


@app.route("/predict", methods=["POST"])
@limiter.limit(f"{API_RATE_LIMIT} per minute")
def predict():
    data = request.json
    question = data.get("question")
    rag_structure = data.get("rag_structure", DEFAULT_RAG_STRUCTURE)

    if not question:
        return jsonify({"error": "No question provided"}), 400

    result = process_question(question, rag_structure, logger, get_config())
    return jsonify(result)


@app.route("/predict_stream", methods=["POST"])
@limiter.limit(f"{API_RATE_LIMIT} per minute")
def predict_stream():
    data = request.json
    question = data.get("question")
    rag_structure = data.get("rag_structure", DEFAULT_RAG_STRUCTURE)

    if not question:
        return jsonify({"error": "No question provided"}), 400

    def generate():
        for chunk in process_question_stream(
            question, rag_structure, logger, get_config()
        ):
            if chunk["error"]:
                yield f"error: {chunk['error']}\n"
                break
            yield chunk["answer"]
        yield "[DONE]\n"

    return Response(stream_with_context(generate()), content_type="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3123)
