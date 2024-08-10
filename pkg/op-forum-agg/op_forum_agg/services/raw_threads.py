from datetime import timedelta, datetime
import datetime as dt
from typing import Dict, List, Tuple, Any
import json
from op_forum_agg.db.models import RawForumPost
import asyncio


import os
import time
import logging
import aiohttp
import aiofiles
from typing import Optional
from abc import ABC, abstractmethod

from urllib.parse import urljoin

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Saver(ABC):
    @abstractmethod
    async def save(self, topic_id: int, topic_data: Dict[str, Any]):
        pass

    @abstractmethod
    async def bulk_save(self, topics: List[Tuple[int, Dict[str, Any]]]):
        pass


class TopicRepository:
    async def get_existing_topics(self) -> Dict[str, dt.datetime]:
        existing_topics = await RawForumPost.all().values("externalId", "lastUpdatedAt")
        return {
            topic["externalId"]: topic["lastUpdatedAt"] for topic in existing_topics
        }

    async def save_topic(self, topic_id: int, topic_data: Dict[str, Any]):
        raw_post = [
            RawForumPost(
                externalId=str(topic_id),
                url=topic_data.get("url", ""),
                type="topic",
                rawData=topic_data,
                lastUpdatedAt=dt.datetime.now(dt.UTC),
                needsSummarize=True
            )
        ]
        await RawForumPost.bulk_create(
            raw_post,
            update_fields=["url", "type", "rawData", "lastUpdatedAt", "needsSummarize"],
            on_conflict=["externalId"],
        )
        return raw_post

    async def bulk_save_topics(self, topics: List[Tuple[int, Dict[str, Any]]]):
        raw_posts = [
            RawForumPost(
                externalId=str(topic_id),
                url=topic_data.get("url", ""),
                type="topic",
                rawData=topic_data,
                lastUpdatedAt=dt.datetime.now(dt.UTC),
                needsSummarize=True
            )
            for topic_id, topic_data in topics
        ]
        await RawForumPost.bulk_create(
            raw_posts,
            update_fields=["url", "type", "rawData", "lastUpdatedAt", "needsSummarize"],
            on_conflict=["externalId"],
        )


class TopicUpdateChecker:
    def __init__(self, repository: TopicRepository):
        self.repository = repository
        self.existing_topics = {}

    async def initialize(self):
        self.existing_topics = await self.repository.get_existing_topics()

    async def should_update_topic(self, topic_id: int, topic_data: Dict[str, Any]) -> bool:
        if str(topic_id) not in self.existing_topics:
            return True
        
        lastInternalUpdatedAt = self.existing_topics[str(topic_id)]

        lastExternalPostedAt = datetime.strptime(topic_data["last_posted_at"], '%Y-%m-%dT%H:%M:%S.%fZ')
                
        return lastInternalUpdatedAt < lastExternalPostedAt


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


class AsyncDiscourseScraperV3:
    def __init__(
        self,
        hostname: str,
        saver: Saver,
        update_checker: Optional[TopicUpdateChecker] = None,
        max_concurrency: int = 10,
    ):
        self.base_url = f"https://{hostname}"
        self.saver = saver
        self.update_checker = update_checker
        self.rate_limiter = AsyncRateLimiter(requests_per_minute=200)
        self.max_concurrency = max_concurrency
        logger.info(f"Initialized AsyncDiscourseScraperV3 for {self.base_url}")

    async def retry_request(
        self,
        session: aiohttp.ClientSession,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        max_retries: int = 5,
    ) -> Optional[Dict[str, Any]]:
        for attempt in range(max_retries):
            try:
                return await self.make_request(session, endpoint, params)
            except aiohttp.ClientResponseError as e:
                if e.status == 429:  # Too Many Requests
                    wait_time = 2**attempt  # Exponential backoff
                    logger.warning(
                        f"Rate limit exceeded. Retrying in {wait_time} seconds..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    raise
        logger.error(f"Max retries reached for endpoint: {endpoint}")
        return None

    async def make_request(
        self,
        session: aiohttp.ClientSession,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        url = urljoin(self.base_url, endpoint)
        await self.rate_limiter.wait()

        logger.debug(f"Making request to {url} with params {params}")
        try:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                logger.debug(f"Successful request to {url}")
                return await response.json()
        except aiohttp.ClientResponseError as e:
            if e.status == 429:
                raise  # Let retry_request handle this
            logger.error(f"Request failed: {e}")
            return None
        except aiohttp.ClientError as e:
            logger.error(f"Request failed: {e}")
            return None

    async def fetch_topic_and_posts(
        self, session: aiohttp.ClientSession, topic_id: int
    ) -> Optional[Dict[str, Any]]:
        logger.info(f"Fetching topic and posts for topic ID: {topic_id}")
        topic_data = await self.retry_request(session, f"/t/{topic_id}.json")

        if not topic_data:
            logger.warning(f"No data found for topic ID: {topic_id}")
            return None

        topic_url = f"{self.base_url}/t/{topic_data["slug"]}/{topic_id}"
        topic_data["url"] = topic_url

        stream_ids = set(topic_data.get("post_stream", {}).get("stream", []))
        post_ids = set(
            post["id"] for post in topic_data.get("post_stream", {}).get("posts", [])
        )
        missing_ids = stream_ids - post_ids

        if missing_ids:
            logger.info(
                f"Fetching {len(missing_ids)} missing posts for topic ID: {topic_id}"
            )
            post_data = await self.retry_request(
                session,
                f"/t/{topic_id}/posts.json",
                params={"post_ids[]": list(missing_ids)},
            )

            if post_data:
                returned_posts = post_data.get("post_stream", {}).get("posts", [])
                added_posts = [
                    {**post, "url": f"{topic_url}/{post['id']}"}
                    for post in returned_posts
                    if post["id"] in missing_ids
                ]
                topic_data["post_stream"]["posts"].extend(added_posts)
                logger.info(
                    f"Added {len(added_posts)} missing posts to topic ID: {topic_id}"
                )

        return topic_data

    async def get_topics(
        self, session: aiohttp.ClientSession, period: str = "all"
    ) -> List[int]:
        topic_ids = []
        page = 0
        logger.info(f"Fetching topics for period: {period}")

        while True:
            logger.debug(f"Fetching page {page} of topics")
            content = await self.make_request(
                session, "/top.json", params={"period": period, "page": page}
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

    async def process_topic(self, session: aiohttp.ClientSession, topic_id: int):
        topic = await self.fetch_topic_and_posts(session, topic_id)

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
        async with aiohttp.ClientSession() as session:
            topic_ids = await self.get_topics(session)
            total_topics = len(topic_ids)

            tasks = []
            for index, topic_id in enumerate(topic_ids, 1):
                logger.info(f"Queueing topic {index}/{total_topics}: ID {topic_id}")
                task = asyncio.create_task(self.process_topic(session, topic_id))
                tasks.append(task)

                if len(tasks) >= self.max_concurrency:
                    await asyncio.gather(*tasks)
                    tasks = []

            if tasks:
                await asyncio.gather(*tasks)

        logger.info("Scraping completed")


class AsyncRateLimiter:
    def __init__(self, requests_per_minute: int):
        self.interval = 60 / requests_per_minute
        self.last_request_time = 0
        logger.info(
            f"AsyncRateLimiter initialized with {requests_per_minute} requests per minute"
        )

    async def wait(self):
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.interval:
            sleep_time = self.interval - time_since_last_request
            logger.debug(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds")
            await asyncio.sleep(sleep_time)

        self.last_request_time = time.time()


class RawThreadsService:
    @staticmethod
    async def acquire_and_save_all():
        repository = TopicRepository()
        db_saver = DatabaseSaver(repository)
        update_checker = TopicUpdateChecker(repository)
        scraper = AsyncDiscourseScraperV3("gov.optimism.io", db_saver, update_checker)
        await scraper.scrape_and_save()

    @staticmethod
    async def update_relationships():
        pass
