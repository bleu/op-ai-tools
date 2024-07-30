import json
from typing import List, Dict
from forum_dl import ExtractorOptions, SessionOptions, WriterOptions, extractors
from op_forum_agg.db.models import RawForumPost
from op_forum_agg.utils.forum_dl_reader import ReadWriter
from op_forum_agg.utils.helpers import fetch_info

FORUM_URL = "https://gov.optimism.io"
CATEGORY_URL = f"{FORUM_URL}/c/{{category_slug}}.json"


class RawThreadsService:
    @staticmethod
    async def fetch_raw_threads(url: str) -> List[Dict]:
        session_options = SessionOptions(
            get_urls=False,
            timeout=5,
            retries=4,
            retry_sleep=1,
            retry_sleep_multiplier=2,
            warc_output="",
            user_agent="Forum-DL",
        )
        extractor_options = ExtractorOptions(path=False)
        writer_options = WriterOptions(
            output_path="out.json",
            files_output_path="teste",
            write_board_objects=False,
            write_thread_objects=True,
            write_post_objects=True,
            write_file_objects=False,
            textify=False,
            content_as_title=False,
            author_as_addr_spec=False,
            write_outside_file_objects=True,
        )

        extractor = extractors.find(url, session_options, extractor_options)

        if extractor:
            extractor.fetch()
            writer = ReadWriter(extractor, writer_options)
            data = writer.write(url)
            if data:
                return [json.loads(load_data) for load_data in data if load_data]

        return []

    @staticmethod
    def parse_thread_data(thread_data: Dict) -> Dict:
        return thread_data["item"]["data"]

    @staticmethod
    async def sync_raw_threads(category_slug: str):
        url = CATEGORY_URL.format(category_slug=category_slug)
        threads_data = await RawThreadsService.fetch_raw_threads(url)
        for thread_data in threads_data:
            parsed_data = RawThreadsService.parse_thread_data(thread_data)
            await RawForumPost.update_or_create(
                externalId=str(parsed_data["id"]),
                defaults={
                    "url": thread_data["item"]["url"],
                    "type": thread_data["type"],
                    "rawData": thread_data["item"]["data"],
                },
            )

    @staticmethod
    async def sync_all_raw_threads():
        categories_json = await fetch_info("https://gov.optimism.io/categories.json")
        forum_categories = categories_json["category_list"]["categories"]
        for category in forum_categories:
            try:
                print(f"Starting to fetch threads for {category['slug']}")
                await RawThreadsService.sync_raw_threads(category["slug"])
                print(f"Finished fetching threads for {category['slug']}")
            except Exception as e:
                print(f"Failed to download {category['slug']}: {e}")
                raise e
