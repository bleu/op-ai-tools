import re
from dataclasses import dataclass, field
import os

from op_forum_agg.src.queries import (
    CREATE_FORUM_POSTS,
    LIST_CATEGORIES,
    RETRIEVE_RAW_THREAD_BY_URL,
    RETRIEVE_RAW_THREADS,
)
from op_forum_agg.src.sync.base import Category, DataIngestInterface, Thread
from op_forum_agg.src.utils.db import (
    filter_data_from_db,
    retrieve_data_from_db,
    store_data_in_db,
)
from op_forum_agg.src.utils.helpers import fetch_info


def get_thread(thread_url: str):
    return filter_data_from_db(RETRIEVE_RAW_THREAD_BY_URL, (thread_url,), Thread)


def get_first_thread_post(thread_url: str):
    return filter_data_from_db(RETRIEVE_RAW_THREAD_BY_URL, (f"{thread_url}/1",), Thread)


def get_categories():
    return retrieve_data_from_db(LIST_CATEGORIES, Category)


def get_category_by_external_id(categories, category_id):
    for category in categories:
        if str(category.externalId) == str(category_id):
            return category.id
    return None


def estimate_reading_time(text: str, WPM: int = 200) -> str:
    # Inspiration: https://mfouesneau.github.io/posts/python_readtime_estimate.html
    total_words = len(re.findall(r"\w+", text))
    time_minutes = total_words // WPM + 1

    if time_minutes < 60:
        return f"{time_minutes} min"
    else:
        hours = time_minutes // 60
        return f"{hours} hour" if hours == 1 else f"{hours} hours"


def concatenate_strings(*args):
    strings = [arg for arg in args if arg]
    return " ".join(args)


class ThreadsImport(DataIngestInterface):
    def fetch(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        relative_summaries_path = os.path.normpath(
            os.path.join(
                current_dir, "../../../../../data/summaries/all_thread_summaries.txt"
            )
        )
        with open(relative_summaries_path, "r", encoding="utf-8") as file:
            data = file.read()

        posts = [
            post.strip()
            for post in data.split(
                "--------------------------------------------------------------------------------"
            )
            if post.strip()
        ]

        return posts

    def transform(self, data):
        categories = get_categories()

        parsed_data = []
        for post in data:
            url_match = re.search(r"URL:\s*(.*)", post)
            about_match = re.search(r"<about>\s*([\s\S]*?)<\/about>", post)
            first_post_match = re.search(
                r"<first_post>\s*([\s\S]*?)<\/first_post>", post
            )
            reaction_match = re.search(r"<reaction>\s*([\s\S]*?)<\/reaction>", post)
            overview_match = re.search(r"<overview>\s*([\s\S]*?)<\/overview>", post)
            tldr_match = re.search(r"<tldr>\s*([\s\S]*?)<\/tldr>", post)
            classification_match = re.search(
                r"<classification>\s*([\s\S]*?)<\/classification>", post
            )

            url = url_match.group(1).strip() if url_match else ""

            threads = get_thread(url)

            if len(threads) == 0:
                continue

            thread = threads[0]
            fisrt_thread_posts = get_first_thread_post(url)
            if len(fisrt_thread_posts) == 0:
                continue

            fisrt_thread_post = fisrt_thread_posts[0]
            internal_category_id = get_category_by_external_id(
                categories, thread.rawData["category_id"]
            )

            all_text = concatenate_strings(
                about_match.group(1) if about_match else "",
                first_post_match.group(1) if first_post_match else "",
                reaction_match.group(1) if reaction_match else "",
                overview_match.group(1) if overview_match else "",
                tldr_match.group(1) if tldr_match else "",
                classification_match.group(1) if classification_match else "",
            )
            read_time = estimate_reading_time(all_text)

            forum_post_data = {
                "external_id": thread.externalId,
                "title": thread.rawData["title"],
                "url": thread.url,
                "category_id": internal_category_id,
                "about": about_match.group(1).strip() if about_match else "",
                "first_post": (
                    first_post_match.group(1).strip() if first_post_match else ""
                ),
                "reaction": reaction_match.group(1).strip() if reaction_match else "",
                "overview": overview_match.group(1).strip() if overview_match else "",
                "tldr": tldr_match.group(1).strip() if tldr_match else "",
                "username": fisrt_thread_post.rawData["username"] or "",
                "display_username": fisrt_thread_post.rawData["display_username"] or "",
                "raw_forum_post_id": thread.id,
                "classification": (
                    classification_match.group(1).strip()
                    if classification_match
                    else ""
                ),
                "last_activity": thread.rawData["last_posted_at"],
                "read_time": read_time,
                "created_at": thread.rawData["created_at"],
            }

            parsed_data.append(forum_post_data)

        return parsed_data


if __name__ == "__main__":
    raw_threads = ThreadsImport(CREATE_FORUM_POSTS, "")
    raw_threads.execute()
