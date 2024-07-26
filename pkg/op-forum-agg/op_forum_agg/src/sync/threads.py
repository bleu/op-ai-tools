from forum_dl import ExtractorOptions, SessionOptions, WriterOptions, extractors
from forum_dl.extractors.discourse import DiscourseExtractor
from psycopg2.extras import execute_values
from op_forum_agg.src.queries import UPSERT_THREADS
from op_forum_agg.src.utils import fetch_info, store_data_in_db, ReadWriter
import json
from psycopg2.extras import Json
from datetime import datetime, timezone

FORUM_URL = "https://gov.optimism.io"
SITE_INFO_URL = f"{FORUM_URL}/site.json"
CATEGORY_URL = f"{FORUM_URL}/c/{{category_slug}}.json"

def fetch_threads(category_slug: str):
    url = CATEGORY_URL.format(category_slug=category_slug)
    session_options=SessionOptions(
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
    writer_options=WriterOptions(
            output_path=f"out.json", # unused
            files_output_path="teste", # unused
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
        return data
    
    return []

    # with open('data.json', 'r') as json_file:
    #     data = json.load(json_file)

    # return data

def parse_data(threads_data):
    loaded_data = [json.loads(load_data) for load_data in threads_data]

    parsed_data = []
    for data in loaded_data:
        post_data = data['item']['data']
        parsed_data.append(
            (
                str(post_data['id']),
                data['item']['url'],
                data['type'],
                json.dumps(post_data),
            ),
        )
    
    return parsed_data

def fetch_and_store_thread_data(category_slug: str):
    threads_data = fetch_threads(category_slug)
    parsed_data = parse_data(threads_data)
    store_data_in_db(parsed_data, UPSERT_THREADS)

def execute_threads_sync():
    site_info_raw_json = fetch_info(SITE_INFO_URL)
    forum_categories = site_info_raw_json["categories"]

    for category in forum_categories[1:]:
        try:
            print("Starting to fetch threads for", category["slug"], datetime.now(timezone.utc))
            # this should be an async task
            fetch_and_store_thread_data(category["slug"])
            print("Finished fetching threads for", category["slug"], datetime.now(timezone.utc))
        except Exception as e:
            print(f"Failed to download {category['slug']}: {e}")

if __name__ == "__main__":
    execute_threads_sync()

