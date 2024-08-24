from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.documents.base import Document

from op_brains.documents.optimism import ForumPostsProcessingStrategy
from op_brains.exceptions import OpChatBrainsException
from op_brains.summarizer.sample import get_sample_summary
from op_brains.summarizer.utils import Prompt, SummaryStructured


async def get_thread_from_url(url: str) -> Document:
    threads = await ForumPostsProcessingStrategy.get_threads_documents()

    thread = next((t for t in threads if t.metadata["url"] == url), None)
    if not thread:
        raise OpChatBrainsException(f"Thread not found for URL: {url}")
    return thread


async def load_snapshot_proposals() -> Dict[str, Any]:
    return await ForumPostsProcessingStrategy.return_snapshot_proposals()


async def summarize_thread(
    url: str, model_name: str, use_mock_data: bool = False
) -> str:
    if use_mock_data:
        return get_sample_summary()

    thread = await get_thread_from_url(url)
    snapshot_proposals = await load_snapshot_proposals()

    llm = (
        ChatOpenAI(temperature=0, model_name=model_name)
        if "gpt" in model_name
        else ChatAnthropic(temperature=0, model_name=model_name)
    )

    llm = llm.with_structured_output(SummaryStructured, strict=True)

    if thread.metadata["url"] in "\t".join(snapshot_proposals.keys()):
        return Prompt.proposal(llm, thread, snapshot_proposals)
    return llm.invoke(
        Prompt.default_summarizer.format(THREAD_CONTENT=thread.page_content)
    ).dict()
