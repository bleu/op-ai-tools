import datetime as dt
from typing import Any, Dict, List, Tuple

from op_data.db.models import RawTopic

import asyncio
import json
import os
from abc import ABC, abstractmethod
from typing import Optional, Set

import aiofiles
from op_data.utils.base_scraper import BaseScraper


from op_core.logger import get_logger

logger = get_logger(__name__)


class TopicRepository:
    async def get_existing_topics(self) -> Dict[str, dt.datetime]:
        existing_topics = await RawTopic.all().values("externalId", "lastUpdatedAt")
        return {
            topic["externalId"]: topic["lastUpdatedAt"] for topic in existing_topics
        }

    async def save_topic(self, topic_id: int, topic_data: Dict[str, Any]):
        raw_post = [
            RawTopic(
                externalId=str(topic_id),
                url=topic_data.get("url", ""),
                type="topic",
                rawData=topic_data,
                lastUpdatedAt=dt.datetime.now(dt.UTC),
            )
        ]
        await RawTopic.bulk_create(
            raw_post,
            update_fields=["url", "type", "rawData", "lastUpdatedAt"],
            on_conflict=["externalId"],
        )
        return raw_post

    async def bulk_save_topics(self, topics: List[Tuple[int, Dict[str, Any]]]):
        raw_topics = [
            RawTopic(
                externalId=str(topic_id),
                url=topic_data.get("url", ""),
                type="topic",
                rawData=topic_data,
                lastUpdatedAt=dt.datetime.now(dt.UTC),
            )
            for topic_id, topic_data in topics
        ]
        await RawTopic.bulk_create(
            raw_topics,
            update_fields=["url", "type", "rawData", "lastUpdatedAt"],
            on_conflict=["externalId"],
        )


class TopicUpdateChecker:
    def __init__(self, repository: TopicRepository):
        self.repository = repository
        self.existing_topics = {}

    async def initialize(self):
        self.existing_topics = await self.repository.get_existing_topics()

    async def should_update_topic(
        self, topic_id: int, topic_data: Dict[str, Any]
    ) -> bool:
        if str(topic_id) not in self.existing_topics:
            return True

        lastInternalUpdatedAt = self.existing_topics[str(topic_id)]

        lastExternalPostedAt = dt.datetime.strptime(
            topic_data["last_posted_at"], "%Y-%m-%dT%H:%M:%S.%fZ"
        )

        return lastInternalUpdatedAt < lastExternalPostedAt


class Saver(ABC):
    @abstractmethod
    async def save(self, topic_id: int, topic_data: Dict[str, Any]):
        pass

    @abstractmethod
    async def bulk_save(self, topics: List[Tuple[int, Dict[str, Any]]]):
        pass


class DatabaseSaver(Saver):
    def __init__(self, repository: TopicRepository):
        self.repository = repository

    async def save(self, topic_id: int, topic_data: Dict[str, Any]):
        created = await self.repository.bulk_save_topics([(topic_id, topic_data)])
        if created:
            logger.info(f"Created new topic {topic_id} in database")
        else:
            logger.info(f"Updated existing topic {topic_id} in database")

    async def bulk_save(self, topics: List[Tuple[int, Dict[str, Any]]]):
        created_count = await self.repository.bulk_save_topics(topics)
        logger.info(f"Bulk saved/updated {created_count} posts in database")


class JsonSaver(Saver):
    def __init__(self, output_dir: str = "data"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    async def save(self, topic_id: int, topic_data: Dict[str, Any]):
        filename = os.path.join(self.output_dir, f"{topic_id}.json")
        async with aiofiles.open(filename, "w") as f:
            await f.write(json.dumps(topic_data, indent=2))
        logger.info(f"Saved topic {topic_id} to {filename}")

    async def bulk_save(self, topics: List[Tuple[int, Dict[str, Any]]]):
        for topic_id, topic_data in topics:
            await self.save(topic_id, topic_data)
        logger.info(f"Bulk saved {len(topics)} topics to JSON files")


class DiscourseTopicScraper(BaseScraper):
    def __init__(
        self,
        hostname: str,
        saver: Saver,
        update_checker: Optional[TopicUpdateChecker] = None,
        max_concurrency: int = 10,
    ):
        super().__init__(f"https://{hostname}", requests_per_minute=200)
        self.saver = saver
        self.update_checker = update_checker
        self.max_concurrency = max_concurrency
        logger.info(f"Initialized DiscourseTopicScraper for {self.base_url}")

    async def fetch_topic_data(self, topic_id: int) -> Optional[Dict[str, Any]]:
        logger.info(f"Fetching topic data for topic ID: {topic_id}")
        return await self.retry_request(f"/t/{topic_id}.json")

    async def fetch_missing_posts(
        self,
        topic_id: int,
        missing_ids: Set[int],
        topic_url: str,
    ) -> List[Dict[str, Any]]:
        logger.info(
            f"Fetching {len(missing_ids)} missing posts for topic ID: {topic_id}"
        )
        post_data = await self.retry_request(
            f"/t/{topic_id}/posts.json",
            params={"post_ids": ",".join(str(post_id) for post_id in missing_ids)},
        )

        if not post_data:
            return []

        returned_posts = post_data.get("post_stream", {}).get("posts", [])
        return [
            {**post, "url": f"{topic_url}/{post['id']}"}
            for post in returned_posts
            if post["id"] in missing_ids
        ]

    async def fetch_topic_and_posts(self, topic_id: int) -> Optional[Dict[str, Any]]:
        topic_data = await self.fetch_topic_data(topic_id)

        if not topic_data:
            logger.warning(f"No data found for topic ID: {topic_id}")
            return None

        topic_url = f"{self.base_url}/t/{topic_data['slug']}/{topic_id}"
        topic_data["url"] = topic_url

        stream_ids = set(topic_data.get("post_stream", {}).get("stream", []))
        post_ids = set(
            post["id"] for post in topic_data.get("post_stream", {}).get("posts", [])
        )
        missing_ids = stream_ids - post_ids

        if missing_ids:
            added_posts = await self.fetch_missing_posts(
                topic_id, missing_ids, topic_url
            )
            topic_data["post_stream"]["posts"].extend(added_posts)
            logger.info(
                f"Added {len(added_posts)} missing posts to topic ID: {topic_id}"
            )

        return topic_data

    async def get_topics(self, period: str = "all") -> List[int]:
        topic_ids = []
        page = 0
        logger.info(f"Fetching topics for period: {period}")

        while True:
            logger.debug(f"Fetching page {page} of topics")
            content = await self.retry_request(
                "/top.json", params={"period": period, "page": page}
            )

            if not content:
                logger.warning(f"No content received for page {page}")
                break

            topics = content.get("topic_list", {}).get("topics", [])

            if not topics:
                logger.info(f"No more topics found after page {page}")
                break

            new_ids = [topic["id"] for topic in topics]
            topic_ids.extend(new_ids)
            logger.info(f"Found {len(new_ids)} topics on page {page}")
            page += 1

        logger.info(f"Total topics found: {len(topic_ids)}")
        return topic_ids

    async def process_topic(self, topic_id: int):
        topic = await self.fetch_topic_and_posts(topic_id)

        if self.update_checker and not await self.update_checker.should_update_topic(
            topic_id=topic_id, topic_data=topic
        ):
            logger.info(f"Skipping topic {topic_id} as it's up to date")
            return

        if topic:
            await self.saver.save(topic_id, topic)
        else:
            logger.warning(f"Failed to fetch topic {topic_id}")

    async def scrape_and_save(self):
        if self.update_checker:
            await self.update_checker.initialize()

        topic_ids = await self.get_topics()
        total_topics = len(topic_ids)

        tasks = []
        for index, topic_id in enumerate(topic_ids, 1):
            logger.info(f"Queueing topic {index}/{total_topics}: ID {topic_id}")
            task = asyncio.create_task(self.process_topic(topic_id))
            tasks.append(task)

            if len(tasks) >= self.max_concurrency:
                await asyncio.gather(*tasks)
                tasks = []

        if tasks:
            await asyncio.gather(*tasks)

        logger.info("Scraping completed")


class RawTopicsService:
    @staticmethod
    async def acquire_and_save_all():
        repository = TopicRepository()
        db_saver = DatabaseSaver(repository)
        update_checker = TopicUpdateChecker(repository)
        scraper = DiscourseTopicScraper("gov.optimism.io", db_saver, update_checker)
        await scraper.scrape_and_save()

    @staticmethod
    async def update_relationships():
        pass
