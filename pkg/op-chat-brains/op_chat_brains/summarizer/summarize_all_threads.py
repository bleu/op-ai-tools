import pandas as pd
import os, random
from tqdm import tqdm
from typing import List, Dict
import concurrent.futures
import multiprocessing

from op_chat_brains.config import FORUM_PATH, SUMMARIZER_MODEL, BASE_PATH
from op_chat_brains.documents.optimism import ForumPostsProcessingStrategy
from op_chat_brains.summarizer.summarizer import summarize_thread
from op_chat_brains.exceptions import OpChatBrainsException
from op_chat_brains.structured_logger import StructuredLogger

logger = StructuredLogger()
threads = ForumPostsProcessingStrategy.return_threads(FORUM_PATH)


def get_some_thread_urls(proportion: float) -> List[str]:
    all_threads = [
        thread.metadata["url"] for thread in threads if thread.metadata["url"]
    ]

    random.shuffle(all_threads)
    return all_threads[: int(len(all_threads) * proportion)]


def summarize_single_thread(url: str, model_name: str) -> Dict[str, str]:
    try:
        summary = summarize_thread(url, model_name)
        logger.log_summary(url, summary)
        return {url: summary}
    except OpChatBrainsException as e:
        logger.logger.error(f"Error summarizing thread {url}: {str(e)}")
        return {url: f"Error: {str(e)}"}


def summarize_some_threads(
    proportion: float, model_name: str = SUMMARIZER_MODEL
) -> Dict[str, str]:
    thread_urls = get_some_thread_urls(proportion)
    summaries = {}

    # Determine the number of workers based on CPU cores
    max_workers = min(
        32, multiprocessing.cpu_count() * 2
    )  # Limit to 32 workers maximum

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
                summaries.update(result)
            except Exception as exc:
                logger.logger.error(f"Thread {url} generated an exception: {exc}")
                summaries[url] = f"Error: {str(exc)}"

    return summaries


summarize_all_threads = lambda model_name: summarize_some_threads(1.0, model_name)


def save_summaries(summaries: Dict[str, str], output_file: str):
    with open(output_file, "w", encoding="utf-8") as f:
        for url, summary in summaries.items():
            f.write(f"URL: {url}\n\n")
            f.write(f"Summary:\n{summary}\n\n")
            f.write("-" * 80 + "\n\n")


def main():
    output_dir = os.path.join(BASE_PATH, "summaries")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "all_thread_summaries.txt")

    print("Starting parallel summarization of all forum threads...")
    summaries = summarize_some_threads(1)

    print(f"Saving summaries to {output_file}")
    save_summaries(summaries, output_file)

    print(f"Summarization complete. Total threads summarized: {len(summaries)}")
    print(f"Summaries saved to: {output_file}")


if __name__ == "__main__":
    main()
