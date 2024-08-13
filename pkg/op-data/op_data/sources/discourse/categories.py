from typing import List, Dict
from op_data.db.models import TopicCategory
from op_data.utils.base_scraper import BaseScraper

FORUM_URL = "https://gov.optimism.io"
SITE_INFO_URL = f"{FORUM_URL}/site.json"

DEFAULT_FILTERABLE_IDS = [41, 1, 69, 48, 46]


class CategoryScraper(BaseScraper):
    def __init__(self, forum_url: str):
        super().__init__(forum_url)

    async def fetch_categories(self) -> List[Dict]:
        data = await self.retry_request("/site.json")
        categories = data["categories"]
        return [
            {
                "externalId": str(category.get("id")),
                "name": category.get("name", ""),
                "color": category.get("color", ""),
                "slug": category.get("slug", ""),
                "description": category.get("description", ""),
                "topicUrl": category.get("topic_url", ""),
                "filterable": category.get("id") in [41, 1, 69, 48, 46],
            }
            for category in categories
        ]

    @staticmethod
    async def acquire_and_save():
        categories = await CategoryScraper(FORUM_URL).fetch_categories()
        category_objects = [TopicCategory(**category) for category in categories]

        await TopicCategory.bulk_create(
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
