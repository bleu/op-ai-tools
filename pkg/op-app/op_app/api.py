from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from op_brains.exceptions import UnsupportedVectorstoreError
from op_brains.structured_logger import StructuredLogger
from op_brains.config import (
    POSTHOG_API_KEY,
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
    default_limits=["100 per minute"],
    storage_uri="memory://",
)

logger = StructuredLogger()


def handle_question(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        data = request.json
        if data is not None:
            question = data.get("question")
            memory = data.get("memory", [])
        else:
            question = None
            memory = []

        if not question:
            return jsonify({"error": "No question provided"}), 400

        return func(question, memory, *args, **kwargs)

    return wrapper


@app.errorhandler(Exception)
def handle_exception(e):
    raise e
    if isinstance(e, UnsupportedVectorstoreError):
        return jsonify({"error": str(e)}), 400
    return jsonify({"error": "An unexpected error occurred during prediction"}), 500


@app.route("/predict", methods=["POST"])
@limiter.limit("100 per minute")
@handle_question
def predict(question, memory):
    result = process_question(question, memory)

    user_token = request.headers.get("x-user-id")
    # posthog.capture(
    #     user_token,
    #     "MODEL_PREDICTED_ANSWER",
    #     {
    #         "endpoint": "predict",
    #         "question": question,
    #         "answer": result.get("answer"),
    #         "error": result.get("error"),
    #     },
    # )
    # posthog.shutdown()

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3123, debug=True)
