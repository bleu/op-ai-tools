from flask import Flask, Response, stream_with_context, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from op_chat_brains.exceptions import UnsupportedVectorstoreError
from op_chat_brains.structured_logger import StructuredLogger
from op_chat_brains.config import (
    API_RATE_LIMIT,
    API_SECRET_KEY,
    DEFAULT_DBS,
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
from op_chat_brains.prompts import PROMPT_BUILDER, PROMPT_BUILDER_EXPANDER
from op_chat_brains.utils import process_question_stream, process_question
from flask_cors import CORS
from posthog import Posthog
from functools import wraps

app = Flask(__name__)
CORS(app)
app.config["SECRET_KEY"] = API_SECRET_KEY

posthog = Posthog(POSTHOG_API_KEY, host="https://us.i.posthog.com")

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


def handle_question(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        data = request.json
        if data is not None:
            question = data.get("question")
            rag_structure = data.get("rag_structure", DEFAULT_RAG_STRUCTURE)
        else:
            question = None
            rag_structure = DEFAULT_RAG_STRUCTURE

        if not question:
            return jsonify({"error": "No question provided"}), 400

        return func(question, rag_structure, *args, **kwargs)

    return wrapper


def capture_posthog_event(event_name, properties):
    user_token = request.headers.get("X-User-ID")
    if user_token:
        posthog.capture(
            distinct_id=user_token,
            event=event_name,
            properties=properties,
        )


@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, UnsupportedVectorstoreError):
        return jsonify({"error": str(e)}), 400
    return jsonify({"error": "An unexpected error occurred during prediction"}), 500


@app.route("/predict", methods=["POST"])
@limiter.limit(f"{API_RATE_LIMIT} per minute")
@handle_question
def predict(question, rag_structure):
    result = process_question(question, rag_structure, logger, get_config())

    capture_posthog_event(
        "MODEL_PREDICTION",
        {
            "endpoint": "predict",
            "question": question,
            "answer": result.get("answer"),
            "error": result.get("error"),
            "rag_structure": rag_structure,
        },
    )

    return jsonify(result)


@app.route("/predict_stream", methods=["POST"])
@limiter.limit(f"{API_RATE_LIMIT} per minute")
@handle_question
def predict_stream(question, rag_structure):
    def generate():
        full_answer = ""
        error = None
        for chunk in process_question_stream(
            question, rag_structure, logger, get_config()
        ):
            if chunk["error"]:
                error = chunk["error"]
                yield f"error: {error}\n"
                break
            chunk_answer = chunk["answer"]
            full_answer += chunk_answer
            yield chunk_answer
        yield "[DONE]\n"

        capture_posthog_event(
            "MODEL_PREDICTION",
            {
                "endpoint": "predict_stream",
                "question": question,
                "answer": full_answer,
                "error": error,
                "rag_structure": rag_structure,
            },
        )

    return Response(stream_with_context(generate()), content_type="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3123)
