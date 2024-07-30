from celery import shared_task
from op_forum_agg.services.categories import CategoriesService
from op_forum_agg.services.raw_threads import RawThreadsService
from op_forum_agg.services.threads import ThreadsService


@shared_task
async def sync_categories():
    await CategoriesService.sync_categories()


@shared_task
async def sync_raw_threads():
    await RawThreadsService.sync_all_raw_threads()


@shared_task
async def sync_forum_posts():
    await ThreadsService.sync_forum_posts()


@shared_task
async def sync_all():
    await sync_categories()
    await sync_raw_threads()
    await sync_forum_posts()
