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
    async def acquire_and_save():
        # Fetch all data in parallel
        summaries, raw_topics, categories = await asyncio.gather(
            TopicsService.fetch_summaries(),
            RawTopic.all(),
            TopicCategory.all(),
        )

        # Create a lookup for raw posts and categories
        summary_lookup = {summary.url: summary for summary in summaries}
        categories_lookup = {cat.externalId: cat for cat in categories}

        forum_topics = []
        for raw_topic in raw_topics:
            summary = summary_lookup.get(raw_topic.url)
            summary_data = summary.data if summary else {}

            category = categories_lookup.get(
                str(raw_topic.rawData.get("category_id", ""))
            )

            all_text = " ".join(
                [
                    summary_data.get("about", ""),
                    summary_data.get("first_post", ""),
                    summary_data.get("reaction", ""),
                    summary_data.get("overview", ""),
                    summary_data.get("tldr", ""),
                    summary_data.get("classification", ""),
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
                    lastActivity=raw_topic.rawData.get("last_posted_at"),
                    readTime=read_time,
                    createdAt=raw_topic.rawData.get("created_at"),
                    firstPost=summary_data.get("first_post", ""),
                    about=summary_data.get("about", ""),
                    reaction=summary_data.get("reaction", ""),
                    overview=summary_data.get("overview", ""),
                    tldr=summary_data.get("tldr", ""),
                    classification=summary_data.get("classification", ""),
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
        topics = await Topic.all().prefetch_related('rawTopic')

        for topic in topics:
            raw_related_topics = topic.rawTopic.rawData.get("related_topics", None)

            if isinstance(raw_related_topics, list):
                related_topics_ids = [item['id'] for item in raw_related_topics]

                related_topics = await Topic.filter(externalId__in=related_topics_ids)

                await topic.relatedTopics.add(*related_topics)
