import asyncio
import logging
from op_forum_agg.services.agora_proposals import AgoraProposalsService
from op_forum_agg.services.categories import CategoriesService
from op_forum_agg.services.raw_threads import RawThreadsService
from op_forum_agg.services.snapshot import SnapshotService
from op_forum_agg.services.threads import ThreadsService

logger = logging.getLogger(__name__)


async def acquire_and_save_bare_entities():
    logger.debug("Starting acquisition and saving of bare entities")
    tasks = [
        AgoraProposalsService.acquire_and_save(),
        SnapshotService.acquire_and_save(),
        CategoriesService.acquire_and_save(),
        RawThreadsService.acquire_and_save_all(),
    ]
    await asyncio.gather(*tasks)
    logger.debug("Finished acquisition and saving of bare entities")


async def process_relationships():
    logger.debug("Starting relationship processing")
    tasks = [
        AgoraProposalsService.update_relationships(),
        SnapshotService.update_relationships(),
        CategoriesService.update_relationships(),
        RawThreadsService.update_relationships(),
    ]
    await asyncio.gather(*tasks)
    logger.debug("Finished relationship processing")


async def sync_threads():
    logger.debug("Starting thread synchronization")
    await ThreadsService.acquire_and_save()
    await ThreadsService.update_relationships()
    logger.debug("Finished thread synchronization")


async def main_sync():
    logger.info("Starting main sync process")
    await acquire_and_save_bare_entities()
    await process_relationships()
    await sync_threads()
    logger.info("Finished main sync process")


async def run_sync():
    logger.debug("Entering run_sync function")
    await main_sync()
    logger.debug("Exiting run_sync function")
