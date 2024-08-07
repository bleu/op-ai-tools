import asyncio
import logging
from typing import Callable, Dict
from tortoise import Tortoise
from op_forum_agg.config import config
from op_forum_agg.services.agora_proposals import AgoraProposalsService
from op_forum_agg.services.categories import CategoriesService
from op_forum_agg.services.raw_threads import RawThreadsService
from op_forum_agg.services.threads import ThreadsService
from op_forum_agg.services.snapshot import SnapshotService
from op_forum_agg.services.sync_all import run_sync as run_full_sync

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


async def init_db():
    logger.debug("Initializing database")
    await Tortoise.init(config=config["TORTOISE_ORM"], use_tz=False)


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
    await CategoriesService.acquire_and_save()
    await CategoriesService.update_relationships()


async def sync_raw_threads():
    logger.debug("Syncing raw threads")
    await RawThreadsService.acquire_and_save_all()
    await RawThreadsService.update_relationships()


async def sync_forum_posts():
    logger.debug("Syncing forum posts")
    await ThreadsService.acquire_and_save()
    await ThreadsService.update_relationships()


async def sync_snapshot_proposals():
    logger.debug("Syncing snapshot proposals")
    await SnapshotService.acquire_and_save()
    await SnapshotService.update_relationships()


async def sync_agora_proposals():
    logger.debug("Syncing Agora proposals")
    await AgoraProposalsService.acquire_and_save()
    await AgoraProposalsService.update_relationships()


# Dictionary mapping command names to their corresponding sync functions
SYNC_COMMANDS: Dict[str, Callable] = {
    "categories": sync_categories,
    "raw_threads": sync_raw_threads,
    "forum_posts": sync_forum_posts,
    "snapshot_proposals": sync_snapshot_proposals,
    "agora_proposals": sync_agora_proposals,
    "full_sync": run_full_sync,
}


def main():
    import sys

    logger.debug(f"CLI called with arguments: {sys.argv}")

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command in SYNC_COMMANDS:
            logger.info(f"Executing command: {command}")
            run_sync(SYNC_COMMANDS[command])
        else:
            logger.error(f"Unknown command: {command}")
            print(f"Unknown command: {command}")
    else:
        logger.warning("No command specified")
        print(f"Please specify a command: {', '.join(SYNC_COMMANDS.keys())}")


if __name__ == "__main__":
    main()
