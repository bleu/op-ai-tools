from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.documents.base import Document

from op_brains.documents.optimism import ForumPostsProcessingStrategy
from op_brains.exceptions import OpChatBrainsException
from op_brains.summarizer.utils import Prompt, SummaryStructured

threads = ForumPostsProcessingStrategy.get_threads_documents()


def get_thread_from_url(url: str) -> Document:
    thread = next((t for t in threads if t.metadata["url"] == url), None)
    if not thread:
        raise OpChatBrainsException(f"Thread not found for URL: {url}")
    return thread


def load_snapshot_proposals() -> Dict[str, Any]:
    return ForumPostsProcessingStrategy.return_snapshot_proposals()


def summarize_thread(url: str, model_name: str) -> str:
    thread = get_thread_from_url(url)
    snapshot_proposals = load_snapshot_proposals()

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

if __name__ == "__main__":
    urls = [
        "https://gov.optimism.io/t/special-voting-cycle-9a-grants-council/4198",
        "https://gov.optimism.io/t/airdrop-1-feedback-thread/80",
        "https://gov.optimism.io/t/retro-funding-4-onchain-builders-round-details/7988",
        "https://gov.optimism.io/t/the-future-of-optimism-governance/6471",
        "https://gov.optimism.io/t/optimism-community-call-recaps-recordings-thread/6937",
        "https://gov.optimism.io/t/how-to-start-a-project-at-optimism/7220",
        "https://gov.optimism.io/t/grant-misuse-reporting-process/7346",
        "https://gov.optimism.io/t/how-to-stay-up-to-date/6124"
    ]
    model_name = "gpt-4o"
    for url in urls:
        out = summarize_thread(url, model_name)
        for key, value in out.items():
            print(f"{key}: {value}")
        print("-------")