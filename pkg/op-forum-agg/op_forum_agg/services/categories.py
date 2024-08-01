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
                "externalId": str(category.get("id")),
                "name": category.get("name", ""),
                "color": category.get("color", ""),
                "slug": category.get("slug", ""),
                "description": category.get("description", ""),
                "topicUrl": category.get("topic_url", ""),
                "filterable": category.get("id") in DEFAULT_FILTERABLE_IDS,
            }
            for category in categories
        ]

    @staticmethod
    async def acquire_and_save():
        categories = await CategoriesService.fetch_categories()
        category_objects = [ForumPostCategory(**category) for category in categories]

        await ForumPostCategory.bulk_create(
            category_objects,
            update_fields=[
                "name",
                "color",
                "slug",
                "description",
                "topicUrl",
                "filterable",
            ],
            on_conflict=["externalId"],
        )

        print(f"Acquired and saved {len(categories)} categories")

    @staticmethod
    async def update_relationships():
        # If there are any relationships to update, implement them here
        pass
