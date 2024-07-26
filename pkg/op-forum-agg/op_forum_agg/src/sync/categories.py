from psycopg2.extras import execute_values
from op_forum_agg.src.queries import UPSERT_CATEGORIES
from op_forum_agg.src.utils import fetch_info, store_data_in_db

FORUM_URL = "https://gov.optimism.io"
SITE_INFO_URL = f"{FORUM_URL}/site.json"


def parse_categories(site_info_raw_json):
    categories = site_info_raw_json["categories"]

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


def execute_categories_sync():
    site_info_raw_json = fetch_info(SITE_INFO_URL)
    parsed_categories = parse_categories(site_info_raw_json)
    store_data_in_db(parsed_categories, UPSERT_CATEGORIES)


if __name__ == "__main__":
    execute_categories_sync()
