from quart import Quart, request, jsonify
from quart_cors import cors
from quart_rate_limiter import RateLimiter, rate_limit
from op_brains.exceptions import UnsupportedVectorstoreError
from op_brains.config import POSTHOG_API_KEY
from op_brains.chat.utils import process_question
from posthog import Posthog
from datetime import timedelta
from functools import wraps
import os
from op_core.config import Config
from tortoise.contrib.quart import register_tortoise
from quart_tasks import QuartTasks
import asyncio
from op_data.cli import (
    sync_categories,
    sync_raw_topics,
    sync_topics,
    sync_summaries,
    sync_snapshot,
    sync_agora,
)
from honeybadger import honeybadger


app = Quart(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_API_SECRET_KEY")
app.config["HONEYBADGER_ENVIRONMENT"] = os.getenv("ENV")
app.config["HONEYBADGER_API_KEY"] = os.getenv("HONEYBADGER_API_KEY")

app = cors(app)
tasks = QuartTasks(app)
posthog = Posthog(POSTHOG_API_KEY, host="https://us.i.posthog.com", sync_mode=True)
limiter = RateLimiter(app)

honeybadger.configure(
    api_key=app.config["HONEYBADGER_API_KEY"],
    environment=app.config["HONEYBADGER_ENVIRONMENT"],
)

register_tortoise(
    app,
    config=Config.get_tortoise_config(),
    generate_schemas=False,
)


def handle_question(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        data = await request.get_json()
        if data is not None:
            question = data.get("question")
            memory = data.get("memory", [])
        else:
            question = None
            memory = []

        if not question:
            return jsonify({"error": "No question provided"}), 400

        return await func(question, memory, *args, **kwargs)

    return wrapper


@app.errorhandler(Exception)
def handle_exception(e):
    honeybadger.notify(e)
    if isinstance(e, UnsupportedVectorstoreError):
        return jsonify({"error": str(e)}), 400
    return jsonify({"error": "An unexpected error occurred during prediction"}), 500


@app.route("/predict", methods=["POST"])
@rate_limit(100, timedelta(minutes=1))
@handle_question
async def predict(question, memory):
    result = await process_question(question, memory)

    user_token = request.headers.get("x-user-id")
    posthog.capture(
        user_token,
        "MODEL_PREDICTED_ANSWER",
        {
            "endpoint": "predict",
            "question": question,
            "answer": result.get("answer"),
            "error": result.get("error"),
        },
    )

    return jsonify(result)


@app.after_request
def after_request(response):
    posthog.flush()
    return response


@tasks.cron("0 */6 * * *")
async def sync_all():
    await asyncio.gather(
        sync_categories(),
        sync_raw_topics(),
        sync_topics(),
        sync_summaries(),
        sync_snapshot(),
        sync_agora(),
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0")
