from typing import List, Dict
from op_forum_agg.db.models import ForumPostCategory
from op_forum_agg.utils.helpers import fetch_info

FORUM_URL = "https://gov.optimism.io"
SITE_INFO_URL = f"{FORUM_URL}/site.json"

DEFAULT_FILTERABLE_IDS = [41, 1, 69, 48, 46]


class CategoriesService:
    @staticmethod
    async def fetch_categories() -> List[Dict]:
        data = await fetch_info(SITE_INFO_URL)
        categories = data["categories"]
        return [
            {
                "external_id": category.get("id"),
                "name": category.get("name", ""),
                "color": category.get("color", ""),
                "slug": category.get("slug", ""),
                "description": category.get("description", ""),
                "topic_url": category.get("topic_url", ""),
            }
            for category in categories
        ]

    @staticmethod
    async def sync_categories():
        categories = await CategoriesService.fetch_categories()
        for category_data in categories:
            category_data["filterable"] = (
                category_data["external_id"] in DEFAULT_FILTERABLE_IDS
            )
            await ForumPostCategory.update_or_create(
                externalId=category_data["external_id"], defaults=category_data
            )
