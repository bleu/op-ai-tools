import json
from datetime import datetime, timezone

from forum_dl import (ExtractorOptions, SessionOptions, WriterOptions,
                      extractors)
from forum_dl.extractors.discourse import DiscourseExtractor

from op_forum_agg.src.queries import UPSERT_THREADS
from op_forum_agg.src.sync.base import DataIngestInterface
from op_forum_agg.src.utils.db import store_data_in_db
from op_forum_agg.src.utils.forum_dl_reader import ReadWriter
from op_forum_agg.src.utils.helpers import fetch_info

FORUM_URL = "https://gov.optimism.io"
SITE_INFO_URL = f"{FORUM_URL}/site.json"
CATEGORY_URL = f"{FORUM_URL}/c/{{category_slug}}.json"


class RawThreadsImport(DataIngestInterface):
    def fetch(self):
        session_options = SessionOptions(
            get_urls=False,
            timeout=5,
            retries=4,
            retry_sleep=1,
            retry_sleep_multiplier=2,
            warc_output="",
            user_agent="Forum-DL",
        )
        extractor_options = ExtractorOptions(
            path=False,
        )
        writer_options = WriterOptions(
            output_path=f"out.json",  # unused
            files_output_path="teste",  # unused
            write_board_objects=False,
            write_thread_objects=True,
            write_post_objects=True,
            write_file_objects=False,
            textify=False,
            content_as_title=False,
            author_as_addr_spec=False,
            write_outside_file_objects=True,
        )

        extractor = extractors.find(self.url, session_options, extractor_options)
        if extractor:
            extractor.fetch()
            writer = ReadWriter(extractor, writer_options)
            data = writer.write(self.url)
            return data

        return []

    def transform(self, data):
        loaded_data = [json.loads(load_data) for load_data in data]

        parsed_data = []
        for threads_data in loaded_data:
            post_data = threads_data["item"]["data"]
            parsed_data.append(
                {
                    "external_id": str(post_data["id"]),
                    "url": threads_data["item"]["url"],
                    "type": threads_data["type"],
                    "raw_data": json.dumps(post_data),
                }
            )

        return parsed_data


def execute_threads_sync():
    # site_info_raw_json = fetch_info(SITE_INFO_URL)
    site_info_raw_json = fetch_info("https://gov.optimism.io/categories.json")
    forum_categories = site_info_raw_json["category_list"]["categories"]

    # for category in forum_categories[1:]:
    for category in forum_categories:
        try:
            print(
                "Starting to fetch threads for",
                category["slug"],
                datetime.now(timezone.utc),
            )
            # this should be an async task
            # fetch_and_store_thread_data(category["slug"])
            threads_migrate = RawThreadsImport(
                UPSERT_THREADS, CATEGORY_URL.format(category_slug=category["slug"])
            )
            threads_migrate.execute()
            print(
                "Finished fetching threads for",
                category["slug"],
                datetime.now(timezone.utc),
            )
        except Exception as e:
            print(f"Failed to download {category['slug']}: {e}")


if __name__ == "__main__":
    execute_threads_sync()
