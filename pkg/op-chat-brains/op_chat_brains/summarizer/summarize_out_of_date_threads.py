import os
import json
from tqdm import tqdm
from typing import List, Dict
import concurrent.futures
import multiprocessing
from psycopg.rows import dict_row
from psycopg.errors import Error as PsycopgError
from datetime import datetime

from op_chat_brains.config import FORUM_PATH, SUMMARIZER_MODEL, BASE_PATH, USE_SUMMARY_MOCK_DATA
from op_chat_brains.documents.optimism import ForumPostsProcessingStrategy
from op_chat_brains.summarizer.summarizer import summarize_thread
from op_chat_brains.exceptions import OpChatBrainsException
from op_chat_brains.structured_logger import StructuredLogger
from op_chat_brains.retriever.connect_db import update_data, update_single_param, UPSERT_SUMMARIES_QUERY, UPDATE_URLS_AS_SUMMARIZED

logger = StructuredLogger()

def summarize_single_thread(url: str, model_name: str) -> Dict[str, str]:
    try:
        summary = summarize_thread(url, model_name, use_mock_data=USE_SUMMARY_MOCK_DATA)
        logger.log_summary(url, summary)
        return {"url": url, "data": json.dumps({"summary": summary}), "generated_at": datetime.now(), "error": None}
    except OpChatBrainsException as e:
        logger.logger.error(f"Error summarizing thread {url}: {str(e)}")
        return {"url": url, "data": json.dumps({"error": str(e)}), "generated_at": datetime.now(), "error": str(e)}

def get_thread_urls() -> List[str]:
    threads = ForumPostsProcessingStrategy.get_threads_documents_not_summarized()
    return [
        thread.metadata["url"] for thread in threads if thread.metadata["url"]
    ]

def summarize_out_of_date_threads(model_name: str = SUMMARIZER_MODEL) -> List[Dict[str, str]]:
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
                summaries.append({"url": url, "data": json.dumps({"error": str(exc)}), "generated_at": datetime.now(), "error": str(exc)})

    return summaries

def upsert_summaries(summaries: List[Dict[str, str]]):
    try:
        data = [
            {
                "url": s['url'],
                "data": s['data'],
                "lastGeneratedAt": s['generated_at']
            }
            for s in summaries if s['error'] is None
        ]
        return update_data(UPSERT_SUMMARIES_QUERY, data)
    except Exception as e:
        logger.logger.error(f"Error upserting summaries: {str(e)}")
        return False

def update_raw_threads_as_summarized(urls: List[str]) -> bool:
    try:
        return update_single_param(UPDATE_URLS_AS_SUMMARIZED, (urls,))
    except Exception as e:
        logger.error(f"Error updating threads as summarized: {str(e)}")
        return False

def main():
    print("Starting parallel summarization of out-of-date forum threads...")
    summaries = summarize_out_of_date_threads()

    if not summaries:
        print("No threads to summarize. Exiting.")
        return

    print(f"Upserting {len(summaries)} summaries into the database...")
    result = upsert_summaries(summaries)

    print("Updating threads as summarized...")
    urls = [s['url'] for s in summaries]
    result = update_raw_threads_as_summarized(urls)

    print("Summarization and upsert complete.")

if __name__ == "__main__":
    main()