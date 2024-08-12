import os
from tqdm import tqdm
from typing import List, Dict
import concurrent.futures
import multiprocessing
import datetime as dt

from op_brains.config import SUMMARIZER_MODEL, USE_SUMMARY_MOCK_DATA
from op_brains.documents.optimism import ForumPostsProcessingStrategy
from op_brains.summarizer.summarizer import summarize_thread
from op_brains.exceptions import OpChatBrainsException
from op_brains.structured_logger import StructuredLogger

from op_data.db.models import RawForumPost, RawTopicSummary
from op_data.cli import run_sync

logger = StructuredLogger()


def summarize_single_thread(url: str, model_name: str) -> Dict[str, str]:
    try:
        summary = summarize_thread(url, model_name, use_mock_data=USE_SUMMARY_MOCK_DATA)
        logger.log_summary(url, summary)
        return {"url": url, "data": {"summary": summary}, "error": None}
    except OpChatBrainsException as e:
        logger.logger.error(f"Error summarizing thread {url}: {str(e)}")
        return {"url": url, "data": {"error": str(e)}, "error": str(e)}


def get_thread_urls() -> List[str]:
    threads = ForumPostsProcessingStrategy.get_threads_documents_not_summarized()
    return [thread.metadata["url"] for thread in threads if thread.metadata["url"]]


def summarize_out_of_date_threads(
    model_name: str = SUMMARIZER_MODEL,
) -> List[Dict[str, str]]:
    thread_urls = get_thread_urls()
    summaries = []

    if not thread_urls:
        logger.logger.info("No threads to summarize.")
        return summaries

    max_workers = min(32, multiprocessing.cpu_count() * 2)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {
            executor.submit(summarize_single_thread, url, model_name): url
            for url in thread_urls
        }

        for future in tqdm(
            concurrent.futures.as_completed(future_to_url),
            total=len(thread_urls),
            desc="Summarizing threads",
        ):
            url = future_to_url[future]
            try:
                result = future.result()
                summaries.append(result)
            except Exception as exc:
                logger.logger.error(f"Thread {url} generated an exception: {exc}")
                summaries.append(
                    {"url": url, "data": {"error": str(exc)}, "error": str(exc)}
                )

    return summaries


async def upsert_summaries(summaries: List[Dict[str, str]]):
    raw_summaries = [
        RawTopicSummary(
            url=summary["url"],
            data=summary["data"],
            lastGeneratedAt=dt.datetime.now(),
        )
        for summary in summaries
        if summary["error"] is None
    ]

    await RawTopicSummary.bulk_create(
        raw_summaries,
        update_fields=["data", "lastGeneratedAt"],
        on_conflict=["url"],
    )


async def update_raw_threads_as_summarized(urls: List[str]) -> bool:
    await RawForumPost.filter(url__in=urls).update(needsSummarize=False)


async def main():
    logger.logger.info(
        "Starting parallel summarization of out-of-date forum threads..."
    )
    summaries = summarize_out_of_date_threads()

    if not summaries:
        logger.logger.info("No threads to summarize. Exiting.")
        return

    logger.logger.info(f"Upserting {len(summaries)} summaries into the database...")
    result = await upsert_summaries(summaries)

    logger.logger.info("Updating threads as summarized...")
    urls = [s["url"] for s in summaries]
    result = await update_raw_threads_as_summarized(urls)

    logger.logger.info("Summarization and upsert complete.")


if __name__ == "__main__":
    run_sync(main)
