import os
from tqdm import tqdm
from typing import List, Dict
import concurrent.futures
import multiprocessing
import datetime as dt
import asyncio

from op_brains.config import SUMMARIZER_MODEL, USE_SUMMARY_MOCK_DATA
from op_brains.documents.optimism import ForumPostsProcessingStrategy
from op_brains.summarizer.summarizer import summarize_thread
from op_brains.exceptions import OpChatBrainsException

from op_data.db.models import RawTopic, RawTopicSummary
from op_data.cli import run_sync

class RawTopicsSummaryService:
    def __init__(self, out_of_date: bool = True, model_name: str = SUMMARIZER_MODEL):
        self.out_of_date = out_of_date
        self.model_name = model_name

    def get_topics_to_summarize(self) -> List[str]:
        if self.out_of_date:
            topics = ForumPostsProcessingStrategy.get_threads_documents_not_summarized()
        else:
            topics = ForumPostsProcessingStrategy.get_threads_documents()

        return [topic.metadata["url"] for topic in topics if topic.metadata["url"]]
    
    @staticmethod
    def summarize_single_topic(url: str, model_name: str) -> Dict[str, str]:
        try:
            summary = summarize_thread(url, model_name, use_mock_data=USE_SUMMARY_MOCK_DATA)
            return {"url": url, "data": {"summary": summary}, "error": False}
        except OpChatBrainsException as e:
            return {"url": url, "data": {"error": str(e)}, "error": True}

    @staticmethod
    def bulk_save_summaries(summaries: List[Dict[str, str]]):
        raw_summaries = [
            RawTopicSummary(
                url=summary["url"],
                data=summary["data"],
                error=summary["error"],
                lastGeneratedAt=dt.datetime.now(),
            )
            for summary in summaries
        ]

        RawTopicSummary.bulk_create(raw_summaries)

    def summarize_topics(self) -> List[Dict[str, str]]:
        topics_urls = self.get_topics_to_summarize()
        summaries = []

        if not topics_urls:
            return summaries

        max_workers = min(32, multiprocessing.cpu_count() * 2)

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(RawTopicsSummarizer.summarize_single_topic, url, self.model_name): url
                for url in topics_urls
            }

            for future in tqdm(
                concurrent.futures.as_completed(future_to_url),
                total=len(topics_urls),
                desc="Summarizing threads",
            ):
                url = future_to_url[future]
                try:
                    result = future.result()
                    summaries.append(result)
                except Exception as exc:
                    summaries.append(
                        {"url": url, "data": {"error": str(exc)}, "error": True}
                    )

        return summaries

    @staticmethod
    def acquire_and_save():
        summaries = self.summarize_topics()
        self.bulk_save_summaries(summaries)

    async def update_raw_topics_as_summarized(urls: List[str]) -> bool:
      await RawTopic.filter(url__in=urls).update(lastSummarizedAt=dt.datetime.now())



# summaries = summarize_out_of_date_threads()

#     if not summaries:
#         return


#     # Run the functions in parallel
#     urls = [s["url"] for s in summaries]
#     await asyncio.gather(
#         insert_summaries(summaries),
#         update_raw_threads_as_summarized(urls)
#     )


# if __name__ == "__main__":
#     run_sync(main)
