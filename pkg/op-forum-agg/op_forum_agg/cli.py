import asyncio
from typing import Callable, Dict
from tortoise import Tortoise
from op_forum_agg.config import config
from op_forum_agg.services.agora_proposals import AgoraProposalsService
from op_forum_agg.services.categories import CategoriesService
from op_forum_agg.services.raw_threads import RawThreadsService
from op_forum_agg.services.threads import ThreadsService
from op_forum_agg.services.snapshot import SnapshotService


async def init_db():
    await Tortoise.init(config=config["TORTOISE_ORM"], use_tz=False)


async def close_db():
    await Tortoise.close_connections()


async def generic_sync(sync_function: Callable):
    await init_db()
    await sync_function()
    await close_db()


def run_sync(sync_function: Callable):
    asyncio.run(generic_sync(sync_function))


# Dictionary mapping command names to their corresponding sync functions
SYNC_COMMANDS: Dict[str, Callable] = {
    "categories": CategoriesService.sync_categories,
    "raw_threads": RawThreadsService.sync_all_raw_threads,
    "forum_posts": ThreadsService.sync_forum_posts,
    "snapshot_proposals": SnapshotService.sync_proposals,
    "agora_proposals": AgoraProposalsService.sync_proposals,
}


def main():
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command in SYNC_COMMANDS:
            run_sync(SYNC_COMMANDS[command])
        else:
            print(f"Unknown command: {command}")
    else:
        print(f"Please specify a command: {', '.join(SYNC_COMMANDS.keys())}")


if __name__ == "__main__":
    main()
