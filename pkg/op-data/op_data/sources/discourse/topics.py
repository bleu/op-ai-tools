import re
from typing import List, Dict
import asyncio
from op_data.db.models import Topic, TopicCategory, RawTopic, RawTopicSummary
from tortoise.functions import Max


def estimate_reading_time(text: str, WPM: int = 200) -> str:
    total_words = len(re.findall(r"\w+", text))
    time_minutes = total_words // WPM + 1
    if time_minutes < 60:
        return f"{time_minutes} min"
    else:
        hours = time_minutes // 60
        return f"{hours} hour" if hours == 1 else f"{hours} hours"


class TopicsService:
    @staticmethod
    async def fetch_summaries() -> List[str]:
        latest_summaries = (
            await RawTopicSummary.annotate(latest_created=Max("createdAt"))
            .group_by("url")
            .order_by("-latest_created")
        )

        return await RawTopicSummary.filter(
            id__in=[s.id for s in latest_summaries]
        ).order_by("-createdAt")

    @staticmethod
    def parse_summary(summary: RawTopicSummary) -> Dict:
        if summary.error:
            return {
                "url": summary.url,
                "about": "",
                "first_post": "",
                "reaction": "",
                "overview": "",
                "tldr": "",
                "classification": "",
            }

        summary_data = summary.data.get("summary", {})

        about_match = re.search(r"<about>\s*([\s\S]*?)<\/about>", summary_data)
        first_post_match = re.search(
            r"<first_post>\s*([\s\S]*?)<\/first_post>", summary_data
        )
        reaction_match = re.search(r"<reaction>\s*([\s\S]*?)<\/reaction>", summary_data)
        overview_match = re.search(r"<overview>\s*([\s\S]*?)<\/overview>", summary_data)
        classification_match = re.search(
            r"<classification>\s*([\s\S]*?)<\/classification>", summary_data
        )

        tldr_match = re.search(r"<tldr>\s*([\s\S]*?)<\/tldr>", summary_data)
        tldr = tldr_match.group(1).strip() if tldr_match else ""
        if not tldr:
            start_index = summary_data.find("<tldr>\n") + len("<tldr>\n")
            tldr = summary_data[start_index:].strip() or ""

        return {
            "url": summary.url,
            "about": about_match.group(1).strip() if about_match else "",
            "first_post": first_post_match.group(1).strip() if first_post_match else "",
            "reaction": reaction_match.group(1).strip() if reaction_match else "",
            "overview": overview_match.group(1).strip() if overview_match else "",
            "tldr": tldr,
            "classification": classification_match.group(1).strip()
            if classification_match
            else "",
        }

    @staticmethod
    async def acquire_and_save():
        # Fetch all data in parallel
        summaries, raw_topics, categories = await asyncio.gather(
            TopicsService.fetch_summaries(),
            RawTopic.all(),
            TopicCategory.all(),
        )

        # Parse summaries
        parsed_summaries = [
            TopicsService.parse_summary(summary) for summary in summaries
        ]

        # Create a lookup for raw posts and categories
        # raw_posts_lookup = {post.url: post for post in raw_posts}
        summary_lookup = {summary["url"]: summary for summary in parsed_summaries}
        categories_lookup = {cat.externalId: cat for cat in categories}

        forum_topics = []
        for raw_topic in raw_topics:
            summary = summary_lookup.get(raw_topic.url)

            if not summary:
                continue

            category = categories_lookup.get(
                str(raw_topic.rawData.get("category_id", ""))
            )

            all_text = " ".join(
                [
                    summary.get("about", ""),
                    summary.get("first_post", ""),
                    summary.get("reaction", ""),
                    summary.get("overview", ""),
                    summary.get("tldr", ""),
                    summary.get("classification", ""),
                ]
            )

            read_time = estimate_reading_time(all_text)
            created_by = raw_topic.rawData.get("details", {}).get("created_by", {})

            forum_topics.append(
                Topic(
                    externalId=raw_topic.externalId,
                    url=raw_topic.url,
                    title=raw_topic.rawData.get("title"),
                    username=created_by.get("username", ""),
                    displayUsername=created_by.get("name", "")
                    or created_by.get("username", ""),
                    category=category,
                    rawTopic=raw_topic,
                    firstPost=summary.get("first_post", ""),
                    about=summary.get("about", ""),
                    reaction=summary.get("reaction", ""),
                    overview=summary.get("overview", ""),
                    tldr=summary.get("tldr", ""),
                    classification=summary.get("classification", ""),
                    lastActivity=raw_topic.rawData.get("last_posted_at"),
                    readTime=read_time,
                    createdAt=raw_topic.rawData.get("created_at"),
                )
            )

        # Bulk create or update topics
        await Topic.bulk_create(
            forum_topics,
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

        print(f"Acquired and saved {len(forum_topics)} forum topics.")

    @staticmethod
    async def update_relationships():
        # If there are any relationships to update, implement them here
        pass
