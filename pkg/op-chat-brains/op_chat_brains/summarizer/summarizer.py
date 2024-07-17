import pandas as pd
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.documents.base import Document

from op_chat_brains.config import FORUM_PATH, SNAPSHOT_PATH
from op_chat_brains.documents.optimism import ForumPostsProcessingStrategy
from op_chat_brains.exceptions import OpChatBrainsException
from op_chat_brains.summarizer.utils import Prompt


def get_thread_from_url(url: str) -> Document:
    posts = ForumPostsProcessingStrategy.process_document(FORUM_PATH)
    df_posts = pd.DataFrame(posts).T
    threads = ForumPostsProcessingStrategy.return_threads(df_posts)
    thread = next((t for t in threads if t.metadata["url"] == url), None)
    if not thread:
        raise OpChatBrainsException(f"Thread not found for URL: {url}")
    return thread


def load_snapshot_proposals() -> Dict[str, Any]:
    return ForumPostsProcessingStrategy.return_snapshot_proposals(SNAPSHOT_PATH)


def summarize_thread(url: str, model_name: str) -> str:
    thread = get_thread_from_url(url)
    snapshot_proposals = load_snapshot_proposals()

    llm = (
        ChatOpenAI(temperature=0, model_name=model_name)
        if "gpt" in model_name
        else ChatAnthropic(temperature=0, model_name=model_name)
    )

    if thread.metadata["url"] in "\t".join(snapshot_proposals.keys()):
        return Prompt.proposal(llm, thread, snapshot_proposals)
    return llm.invoke(Prompt.default_summarizer.format(THREAD_CONTENT=thread.page_content)).content
