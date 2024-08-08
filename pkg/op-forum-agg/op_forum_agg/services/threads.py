import re
import os
from typing import List, Dict
import asyncio
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
    async def acquire_and_save():
        # Fetch all data in parallel
        summaries, raw_posts, categories = await asyncio.gather(
            ThreadsService.fetch_summaries(),
            RawForumPost.all(),
            ForumPostCategory.all(),
        )

        # Parse summaries
        parsed_summaries = [
            await ThreadsService.parse_summary(summary) for summary in summaries
        ]

        # Create a lookup for raw posts and categories
        raw_posts_lookup = {post.url: post for post in raw_posts}
        categories_lookup = {cat.externalId: cat for cat in categories}

        forum_posts = []
        for summary in parsed_summaries:
            raw_post = raw_posts_lookup.get(summary["url"])
            if not raw_post:
                continue

            first_post = raw_posts_lookup.get(f"{summary['url']}/1")
            if not first_post:
                continue

            category = categories_lookup.get(raw_post.rawData["category_id"])

            all_text = " ".join(
                [
                    summary["about"],
                    summary["first_post"],
                    summary["reaction"],
                    summary["overview"],
                    summary["tldr"],
                    summary["classification"],
                ]
            )
            read_time = estimate_reading_time(all_text)

            forum_posts.append(
                ForumPost(
                    externalId=raw_post.externalId,
                    url=raw_post.url,
                    title=raw_post.rawData["title"],
                    username=first_post.rawData.get("username", ""),
                    displayUsername=first_post.rawData.get("display_username", "")
                    or first_post.rawData.get("username", ""),
                    category=category,
                    rawForumPost=raw_post,
                    about=summary["about"],
                    firstPost=summary["first_post"],
                    reaction=summary["reaction"],
                    overview=summary["overview"],
                    tldr=summary["tldr"],
                    classification=summary["classification"],
                    lastActivity=raw_post.rawData["last_posted_at"],
                    readTime=read_time,
                    createdAt=raw_topic.rawData["created_at"],
                )
            )

        # Bulk create or update forum posts
        await ForumPost.bulk_create(
            forum_posts,
            update_fields=[
                "url",
                "title",
                "username",
                "displayUsername",
                "about",
                "firstPost",
                "reaction",
                "overview",
                "tldr",
                "classification",
                "lastActivity",
                "readTime",
                "createdAt",
            ],
            on_conflict=["externalId"],
        )

        print(f"Acquired and saved {len(forum_posts)} forum posts")

    @staticmethod
    async def update_relationships():
        # If there are any relationships to update, implement them here
        pass
