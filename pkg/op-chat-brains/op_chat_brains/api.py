from flask import Flask, Response, stream_with_context, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from op_chat_brains.exceptions import UnsupportedVectorstoreError, OpChatBrainsException
from op_chat_brains.structured_logger import StructuredLogger
from op_chat_brains.config import (
    API_RATE_LIMIT,
    API_SECRET_KEY,
    DEFAULT_RAG_STRUCTURE,
    SUMMARIZER_MODEL,
)
from op_chat_brains.chat.utils import process_question_stream, process_question
from op_chat_brains.summarizer.summarizer import summarize_thread
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


@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, UnsupportedVectorstoreError):
        return jsonify({"error": str(e)}), 400
    return jsonify({"error": "An unexpected error occurred during prediction"}), 500


@app.route("/predict", methods=["POST"])
@limiter.limit(f"{API_RATE_LIMIT} per minute")
def predict():
    data = request.json
    question = data.get("question")
    rag_structure = data.get("rag_structure", DEFAULT_RAG_STRUCTURE)

    if not question:
        return jsonify({"error": "No question provided"}), 400

    try:
        result = process_question(question, rag_structure, logger, get_config())
        return jsonify(result)
    except OpChatBrainsException as e:
        return jsonify({"error": str(e)}), 400


@app.route("/predict_stream", methods=["POST"])
@limiter.limit(f"{API_RATE_LIMIT} per minute")
def predict_stream():
    data = request.json
    question = data.get("question")
    rag_structure = data.get("rag_structure", DEFAULT_RAG_STRUCTURE)

    if not question:
        return jsonify({"error": "No question provided"}), 400

    def generate():
        try:
            for chunk in process_question_stream(
                question, rag_structure, logger, get_config()
            ):
                if chunk["error"]:
                    yield f"error: {chunk['error']}\n"
                    break
                yield chunk["answer"]
            yield "[DONE]\n"
        except OpChatBrainsException as e:
            yield f"error: {str(e)}\n"

    return Response(stream_with_context(generate()), content_type="text/plain")


@app.route("/summarize", methods=["POST"])
@limiter.limit(f"{API_RATE_LIMIT} per minute")
def summarize():
    data = request.json
    url = data.get("url")
    model = data.get("model", SUMMARIZER_MODEL)

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        summary = summarize_thread(url, model)
        logger.log_summary(url, summary)
        return jsonify({"summary": summary})
    except OpChatBrainsException as e:
        return jsonify({"error": str(e)}), 400


def get_config():
    from op_chat_brains.config import (
        DEFAULT_DBS,
        EMBEDDING_MODEL,
        K_RETRIEVER,
        VECTORSTORE,
        CHAT_MODEL_CLAUDE,
        CHAT_MODEL_OPENAI,
        CHAT_TEMPERATURE,
        MAX_RETRIES,
    )
    from op_chat_brains.chat.prompts import PROMPT_BUILDER, PROMPT_BUILDER_EXPANDER

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3123)
