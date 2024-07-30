import re
import os
from typing import List, Dict
from op_forum_agg.db.models import ForumPost, ForumPostCategory, RawForumPost


def estimate_reading_time(text: str, WPM: int = 200) -> str:
    total_words = len(re.findall(r"\w+", text))
    time_minutes = total_words // WPM + 1
    if time_minutes < 60:
        return f"{time_minutes} min"
    else:
        hours = time_minutes // 60
        return f"{hours} hour" if hours == 1 else f"{hours} hours"


class ThreadsService:
    @staticmethod
    async def fetch_summaries() -> List[str]:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        relative_summaries_path = os.path.normpath(
            os.path.join(
                current_dir, "../../../../data/summaries/all_thread_summaries.txt"
            )
        )
        with open(relative_summaries_path, "r", encoding="utf-8") as file:
            data = file.read()

        return [
            post.strip()
            for post in data.split(
                "--------------------------------------------------------------------------------"
            )
            if post.strip()
        ]

    @staticmethod
    async def parse_summary(summary: str) -> Dict:
        url_match = re.search(r"URL:\s*(.*)", summary)
        about_match = re.search(r"<about>\s*([\s\S]*?)<\/about>", summary)
        first_post_match = re.search(
            r"<first_post>\s*([\s\S]*?)<\/first_post>", summary
        )
        reaction_match = re.search(r"<reaction>\s*([\s\S]*?)<\/reaction>", summary)
        overview_match = re.search(r"<overview>\s*([\s\S]*?)<\/overview>", summary)
        tldr_match = re.search(r"<tldr>\s*([\s\S]*?)<\/tldr>", summary)
        classification_match = re.search(
            r"<classification>\s*([\s\S]*?)<\/classification>", summary
        )

        return {
            "url": url_match.group(1).strip() if url_match else "",
            "about": about_match.group(1).strip() if about_match else "",
            "first_post": first_post_match.group(1).strip() if first_post_match else "",
            "reaction": reaction_match.group(1).strip() if reaction_match else "",
            "overview": overview_match.group(1).strip() if overview_match else "",
            "tldr": tldr_match.group(1).strip() if tldr_match else "",
            "classification": classification_match.group(1).strip()
            if classification_match
            else "",
        }

    @staticmethod
    async def get_first_thread_post(thread_url: str):
        return await RawForumPost.get_or_none(url=f"{thread_url}/1")

    @staticmethod
    async def sync_forum_posts():
        summaries = await ThreadsService.fetch_summaries()
        for summary in summaries:
            parsed_data = await ThreadsService.parse_summary(summary)

            raw_post = await RawForumPost.get_or_none(url=parsed_data["url"])
            if not raw_post:
                continue

            first_post = await ThreadsService.get_first_thread_post(parsed_data["url"])
            if not first_post:
                continue

            category = await ForumPostCategory.get_or_none(
                externalId=raw_post.rawData["category_id"]
            )

            all_text = " ".join(
                [
                    parsed_data["about"],
                    parsed_data["first_post"],
                    parsed_data["reaction"],
                    parsed_data["overview"],
                    parsed_data["tldr"],
                    parsed_data["classification"],
                ]
            )
            read_time = estimate_reading_time(all_text)

            await ForumPost.update_or_create(
                externalId=raw_post.externalId,
                defaults={
                    "url": raw_post.url,
                    "title": raw_post.rawData["title"],
                    "username": first_post.rawData.get("username", ""),
                    "displayUsername": first_post.rawData.get("display_username", "")
                    or first_post.rawData.get("username", ""),
                    "category": category,
                    "rawForumPost": raw_post,
                    "about": parsed_data["about"],
                    "firstPost": parsed_data["first_post"],
                    "reaction": parsed_data["reaction"],
                    "overview": parsed_data["overview"],
                    "tldr": parsed_data["tldr"],
                    "classification": parsed_data["classification"],
                    "lastActivity": raw_post.rawData["last_posted_at"],
                    "readTime": read_time,
                },
            )
