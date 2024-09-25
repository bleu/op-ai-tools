import asyncio
import code
import sys
from quart import Quart
from op_brains.config import POSTHOG_API_KEY
from posthog import Posthog
from op_core.config import Config
from tortoise.contrib.quart import register_tortoise
from quart_tasks import QuartTasks
from op_data.sources.incremental_indexer import IncrementalIndexerService
from tortoise import Tortoise

# Initialize your Quart app and other components
app = Quart(__name__)
app.config["SECRET_KEY"] = "your_secret_key"  # Replace with your actual secret key
tasks = QuartTasks(app)
posthog = Posthog(POSTHOG_API_KEY, host="https://us.i.posthog.com", sync_mode=True)

# Register Tortoise
register_tortoise(
    app,
    config=Config.get_tortoise_config(),
    generate_schemas=False,
)


# Initialize Tortoise ORM
async def init_db():
    await Tortoise.init(config=Config.get_tortoise_config())


# Run the initialization
loop = asyncio.get_event_loop()
loop.run_until_complete(init_db())


def run_async(coro):
    return loop.run_until_complete(coro)


preloaded_objects = {
    "app": app,
    "IncrementalIndexerService": IncrementalIndexerService,
    "run_async": run_async,
}

banner = """
Welcome to the Quart App Interactive Console!

Available objects:
- app: The Quart application instance
- IncrementalIndexerService: Service for incremental indexing

To run async functions, use the run_async() helper:
e.g., run_async(process_question("Your question here"))

Type 'exit()' or press Ctrl-D to exit the console.
"""

# Start the interactive console
code.interact(banner=banner, local=dict(globals(), **preloaded_objects))
