from celery import shared_task
from op_data.sources.discourse.categories import CategoriesService
from op_data.sources.discourse.raw_topics import RawTopicsService
from op_data.sources.discourse.topics import TopicsService


@shared_task
async def sync_categories():
    await CategoriesService.sync_categories()


@shared_task
async def sync_raw_topics():
    await RawTopicsService.sync_all_raw_topics()


@shared_task
async def sync_forum_posts():
    await TopicsService.sync_forum_posts()


@shared_task
async def sync_all():
    await sync_categories()
    await sync_raw_topics()
    await sync_forum_posts()
