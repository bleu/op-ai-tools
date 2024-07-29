import re

from op_forum_agg.src.queries import (CREATE_FORUM_POSTS, LIST_CATEGORIES,
                                      RETRIEVE_RAW_THREAD_BY_URL)
from op_forum_agg.src.sync.base import Category, DataIngestInterface, Thread
from op_forum_agg.src.utils.db import (filter_data_from_db,
                                       retrieve_data_from_db)


def get_thread(thread_url: str):
    return filter_data_from_db(RETRIEVE_RAW_THREAD_BY_URL, (thread_url,), Thread)


def get_first_thread_post(thread_url: str):
    return filter_data_from_db(RETRIEVE_RAW_THREAD_BY_URL, (f"{thread_url}/1",), Thread)


def get_categories():
    return retrieve_data_from_db(LIST_CATEGORIES, Category)


def get_category_by_external_id(categories, category_id):
    for category in categories:
        if str(category.external_id) == str(category_id):
            return category.id
    return None


class ThreadsImport(DataIngestInterface):
    def fetch(self):
        file_path = "/Users/victor/Documents/GitHub/op-ai-tools/data/summaries/all_thread_summaries.txt"
        with open(file_path, "r", encoding="utf-8") as file:
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
            forum_post_data = {
                "external_id": thread.external_id,
                "title": thread.rawData["title"],
                "url": thread.url,
                "lastPostedAt": thread.rawData["last_posted_at"],
                "externalId": thread.external_id,
                "category": internal_category_id,
                "about": about_match.group(1).strip() if about_match else "",
                "firstPost": (
                    first_post_match.group(1).strip() if first_post_match else ""
                ),
                "reaction": reaction_match.group(1).strip() if reaction_match else "",
                "overview": overview_match.group(1).strip() if overview_match else "",
                "tldr": tldr_match.group(1).strip() if tldr_match else "",
                "username": fisrt_thread_post.rawData["username"] or "",
                "displayUsername": fisrt_thread_post.rawData["display_username"] or "",
            }

            parsed_data.append(forum_post_data)

        return parsed_data


if __name__ == "__main__":
    raw_threads = ThreadsImport(CREATE_FORUM_POSTS, "")
    raw_threads.execute()
