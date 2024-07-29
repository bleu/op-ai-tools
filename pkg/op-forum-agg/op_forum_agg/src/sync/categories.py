from psycopg2.extras import execute_values

from op_forum_agg.src.queries import UPSERT_CATEGORIES
from op_forum_agg.src.sync.base import DataIngestInterface
from op_forum_agg.src.utils.db import store_data_in_db
from op_forum_agg.src.utils.helpers import fetch_info

FORUM_URL = "https://gov.optimism.io"
SITE_INFO_URL = f"{FORUM_URL}/site.json"


class CategoriesImport(DataIngestInterface):
    def fetch(self):
        return fetch_info(self.url)

    def transform(self, data):
        categories = data["categories"]
        # categories = data["category_list"]["categories"]

        parsed_categories = []
        for category in categories:
            parsed_categories.append(
                (
                    category.get("id"),
                    category.get("name", ""),
                    category.get("color", ""),
                    category.get("slug", ""),
                    category.get("description", ""),
                    category.get("topic_url", ""),
                )
            )

        return parsed_categories


def execute_categories_import():
    categories_migrate = CategoriesImport(UPSERT_CATEGORIES, SITE_INFO_URL)
    # categories_migrate = CategoriesImport(UPSERT_CATEGORIES, "https://gov.optimism.io/categories.json")
    categories_migrate.execute()


if __name__ == "__main__":
    execute_categories_import()
