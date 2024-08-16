import asyncio
import logging
from typing import Callable, Dict
from tortoise import Tortoise
from op_data.sources.agora import AgoraProposalService
from op_data.sources.discourse.categories import CategoryScraper
from op_data.sources.discourse.raw_topics import RawTopicsService
from op_data.sources.discourse.topics import TopicsService
from op_data.sources.snapshot import SnapshotService
from op_data.sources.summary import RawTopicSummaryService
from op_core.config import Config

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


async def init_db():
    logger.debug("Initializing database")
    await Tortoise.init(config=Config.get_tortoise_config(), use_tz=False)


async def close_db():
    logger.debug("Closing database connections")
    await Tortoise.close_connections()


async def generic_sync(sync_function: Callable):
    logger.debug(f"Starting generic sync with function: {sync_function.__name__}")
    await init_db()
    await sync_function()
    await close_db()
    logger.debug(f"Finished generic sync with function: {sync_function.__name__}")


def run_sync(sync_function: Callable):
    logger.debug(f"Running sync function: {sync_function.__name__}")
    asyncio.run(generic_sync(sync_function))


async def sync_categories():
    logger.debug("Syncing categories")
    await CategoryScraper.acquire_and_save()
    await CategoryScraper.update_relationships()


async def sync_raw_topics():
    logger.debug("Syncing raw topics")
    await RawTopicsService.acquire_and_save_all()
    await RawTopicsService.update_relationships()


async def sync_topics():
    logger.debug("Syncing forum posts")
    await TopicsService.acquire_and_save()
    await TopicsService.update_relationships()


async def sync_snapshot():
    logger.debug("Syncing snapshot proposals")
    await SnapshotService.acquire_and_save()
    await SnapshotService.update_relationships()


async def sync_agora():
    logger.debug("Syncing Agora proposals")
    await AgoraProposalService.acquire_and_save()
    await AgoraProposalService.update_relationships()


async def sync_summaries():
    await RawTopicSummaryService.acquire_and_save()
    await RawTopicSummaryService.update_relationships()


SYNC_COMMANDS: Dict[str, Callable] = {
    "categories": sync_categories,
    "raw_topics": sync_raw_topics,
    "topics": sync_topics,
    "snapshot": sync_snapshot,
    "agora": sync_agora,
    "summaries": sync_summaries,
}


def main():
    import sys

    logger.debug(f"CLI called with arguments: {sys.argv}")

    if len(sys.argv) <= 1:
        logger.warning("No command specified")
        print(f"Please specify a command: {', '.join(SYNC_COMMANDS.keys())}")
        return

    command = sys.argv[1]
    if command not in SYNC_COMMANDS:
        logger.error(f"Unknown command: {command}")
        print(f"Unknown command: {command}")
        print(f"Available commands: {', '.join(SYNC_COMMANDS.keys())}")
        return

    logger.info(f"Executing command: {command}")
    try:
        run_sync(SYNC_COMMANDS[command])
    except Exception as e:
        logger.exception(f"Error executing command {command}: {str(e)}")
        print(f"Error executing command {command}: {str(e)}")


if __name__ == "__main__":
    main()
