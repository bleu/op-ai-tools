from typing import Dict, Any
from langchain_core.documents.base import Document

from op_chat_brains.summarizer.prompts import Prompt


class InternalDialogue:
    @staticmethod
    def proposal(llm: Any, thread: Document, snapshot_proposals: Dict[str, Any]) -> str:
        url = thread.metadata["url"]
        for k in snapshot_proposals.keys():
            if url in k:
                url = k

        snapshot_content = snapshot_proposals[url]["str"]
        snapshot_tldr = llm.invoke(
            Prompt.snapshot_summarize(snapshot_content, thread.page_content)
        )
        opinions = llm.invoke(Prompt.opinions(thread.page_content))

        summary = (
            f"{snapshot_tldr.content}\n\n**Some user opinions:**\n{opinions.content}\n"
        )
        return summary

    @staticmethod
    def feedback(llm: Any, thread: Document) -> str:
        topic = llm.invoke(Prompt.feedbacking_what(thread.page_content))
        opinions = llm.invoke(Prompt.opinions(thread.page_content))

        summary = f"{topic.content}\n\n**Some user opinions:**\n{opinions.content}\n"
        return summary

    @staticmethod
    def announcement(llm: Any, thread: Document) -> str:
        topic = llm.invoke(Prompt.announcing_what(thread.page_content))
        opinions = llm.invoke(Prompt.opinions(thread.page_content))

        summary = f"{topic.content}\n\n**Some user opinions:**\n{opinions.content}\n"
        return summary

    @staticmethod
    def discussion(llm: Any, thread: Document) -> str:
        topic = llm.invoke(Prompt.discussing_what(thread.page_content))
        first_opinion = llm.invoke(Prompt.first_opinion(thread.page_content))
        reactions = llm.invoke(Prompt.reactions(thread.page_content))

        summary = f"{topic.content}\n\n{first_opinion.content}\n\n**Reactions:**\n{reactions.content}\n"
        return summary

    @staticmethod
    def other(llm: Any, thread: Document) -> str:
        return llm.invoke(Prompt.tldr(thread.page_content)).content
