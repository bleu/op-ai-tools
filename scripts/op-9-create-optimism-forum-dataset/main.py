# scripts/op-9-create-optimism-forum-dataset/main.py
# Description: This script creates the Optimism Forum dataset.


from forum_dl import ExtractorOptions, ForumDl, SessionOptions, WriterOptions, logging
import httpx
import json

FORUM_URL = "https://gov.optimism.io"
SITE_INFO_URL = f"{FORUM_URL}/site.json"
CATEGORY_URL = f"{FORUM_URL}/c/{{category_slug}}.json"

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


def get_site_info():
    with httpx.Client() as client:
        response = client.get(SITE_INFO_URL)
        response.raise_for_status()
        return response.json()


def save_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def ensure_out_dir_exists():
    import os

    if not os.path.exists("out"):
        os.makedirs("out")


def download_category(category_slug):
    url = CATEGORY_URL.format(category_slug=category_slug)
    forumdl = ForumDl()
    forumdl.download(
        urls=[url],
        output_format="jsonl",
        session_options=SessionOptions(
            get_urls=False,
            timeout=5,
            retries=4,
            retry_sleep=1,
            retry_sleep_multiplier=2,
            warc_output="",
            user_agent="Forum-DL",
        ),
        extractor_options=ExtractorOptions(
            path=False,
        ),
        writer_options=WriterOptions(
            output_path=f"out/{category_slug}_out.jsonl",
            files_output_path="",
            write_board_objects=True,
            write_thread_objects=True,
            write_post_objects=True,
            write_file_objects=True,
            textify=False,
            content_as_title=False,
            author_as_addr_spec=False,
            write_outside_file_objects=True,
        ),
    )


def main():
    ensure_out_dir_exists()

    site_info = get_site_info()

    save_json(site_info, "out/site_info.json")

    forum_categories = site_info["categories"]

    for category in forum_categories[1:]:
        try:
            download_category(category["slug"])
        except Exception as e:
            logging.error(f"Failed to download {category['slug']}: {e}")


if __name__ == "__main__":
    main()
