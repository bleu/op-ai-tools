import asyncio
from tortoise import Tortoise
from op_forum_agg.config import config
from op_forum_agg.services.categories import CategoriesService
from op_forum_agg.services.raw_threads import RawThreadsService
from op_forum_agg.services.threads import ThreadsService
from op_forum_agg.services.snapshot import SnapshotService


async def init_db():
    await Tortoise.init(config=config["TORTOISE_ORM"], use_tz=False)


async def close_db():
    await Tortoise.close_connections()


async def sync_categories():
    await init_db()
    await CategoriesService.sync_categories()
    await close_db()


async def sync_raw_threads():
    await init_db()
    await RawThreadsService.sync_all_raw_threads()
    await close_db()


async def sync_forum_posts():
    await init_db()
    await ThreadsService.sync_forum_posts()
    await close_db()


async def sync_snapshot():
    await init_db()
    await SnapshotService.sync_proposals()
    await close_db()


def run_sync_categories():
    asyncio.run(sync_categories())


def run_sync_raw_threads():
    asyncio.run(sync_raw_threads())


def run_sync_forum_posts():
    asyncio.run(sync_forum_posts())


def run_sync_snapshot():
    asyncio.run(sync_snapshot())


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "sync_categories":
            run_sync_categories()
        elif command == "sync_raw_threads":
            run_sync_raw_threads()
        elif command == "sync_forum_posts":
            run_sync_forum_posts()
        elif command == "sync_snapshot":
            run_sync_snapshot()
        else:
            print(f"Unknown command: {command}")
    else:
        print(
            "Please specify a command: sync_categories, sync_raw_threads, sync_forum_posts, or sync_snapshot"
        )
