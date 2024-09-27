import pandas as pd

from typing import Dict, Any, Union, Optional, List, Tuple
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.documents.base import Document

TODAY = pd.to_datetime("today").strftime("%Y-%m-%d")

chat_models_openai = ["gpt-3.5-turbo-0125", "gpt-4o"]
chat_models_anthropic = [
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307",
    "claude-3-opus-20240229",
    "claude-3-5-sonnet-20240620",
]


class Prompt:
    default_summarizer = f"""
    You are tasked with summarizing and classifying a thread from the Optimism documentation forum. The content of the thread is provided below:

    <thread_content>
    {{THREAD_CONTENT}}
    </thread_content>

    Formatting guidelines:
    - Do not use complete sentences; instead, use concise phrases.
    - Do not be redundant. Never add unnecessary phrases or bullet points.
    - Do not mention specific usernames in your summary.
    - Pay attention to time-related topics. Today is {TODAY}. Past events must be informed as such.
    """

    proposal_summarizer = (
        default_summarizer
        + f"""
    This thread is a proposal discussion. Details about the proposal are provided below:

    <proposal_snapshot>
    {{PROPOSAL}}
    </proposal_snapshot>

    Highlight the results and if it is already closed. If it is still open, mention the deadline.
    """
    )

    question_classifier = """
        You are tasked with classifying a question from the Optimism documentation forum. The content of the question is provided below:
        
        Previous conversation thread:
        {THREAD_CONTENT}
        
        Current question:
        <question_content>
        {QUESTION_CONTENT}
        </question_content>
        
        Formatting guidelines:
        - Just classify the question. Do not provide a summary.
        - Do not use complete sentences; instead, use concise classification.
    """

    @staticmethod
    def proposal(llm: Any, thread: Document, snapshot_proposals: Dict[str, Any]):
        url = thread.metadata["url"]
        for k in snapshot_proposals.keys():
            if url in k:
                url = k

        summary = llm.invoke(
            Prompt.proposal_summarizer.format(
                PROPOSAL=snapshot_proposals[url]["str"],
                THREAD_CONTENT=thread.page_content,
            )
        )

        return summary.dict()

    @staticmethod
    def format_chat_thread(thread: List) -> str:
        """
        Format the thread (conversation history) for the prompt.

        Args:
            thread: A list of tuples where the first element is either 'user' or 'chat'
                    and the second element is the respective content.

        Returns:
            A formatted string that can be injected into the prompt.
        """

        formatted_thread = ""
        for entry in thread:
            if entry["name"] == "user":
                formatted_thread += f"User: {entry["message"]}\n"
            elif entry["name"] == "chat":
                formatted_thread += f"Chat: {entry["message"]}\n"

        if formatted_thread == "":
            return "Empty thread."
        return formatted_thread.strip()


class SummaryStructured(BaseModel):
    classification: str = Field(
        description="""The classification of the thread content. Determine the type of thread and provide a single-word classification:
    - "discussion": if the first post introduces a topic and the following posts discuss it bringing their points of view
    - "feedback": if it is a feedback section
    - "announcement": if the first post is an announcement and the following are reactions to it
    - "guide": if the thread contains a guide or tutorial
    - "informative": if is a thread with relevant instructions or information given by an official source
    - "unimportant": if someone with low trust level (smallest trust level is 0 and highest is 4) is talking alone, if it just talks about forum structure, if people are just chatting, if it is a welcome page, if someone is just saying hi everyone...
    - "other": for cases that don't fit the above categories
"""
    )

    about: str = Field(
        description="Write up to 2 paragraphs summarizing what the thread content is about. If the thread is classified as 'unimportant' or 'other', provide instead a brief explanation of why it falls into this category."
    )

    overview: str = Field(
        description="""Summarize some details about the content in some short and concise bullet points. Try to list these in chronological order. If there are any useful links in the content, include them in the bullet points as [link to url abc](URL). If there are any important dates, deadlines, or events, also include them in the bullet points. Try to talk about every theme that was discussed.
                                    
    If it is classified as a guide or informative thread: Summarize the instructions, ideas, or steps provided. If some new relevant information (as acknowledged corrections or clarifications) is given in the comments, add them at the last bullet point.
    """
    )

    reaction: str = Field(
        description="Summarize general opinions from others WITHOUT MENTIONING USERS. Do this in ideally no more than 5 short and concise bullet points. If there is no relevant content, return an empty string."
    )

    tldr: str = Field(
        description="A short and concise paragraph that encompasses the most important information from what you wrote. If this is an old thread (and its information can be outdated), open the text with 'This is an old thread and the information may be outdated'."
    )


class QuestionClassificationStructured(BaseModel):
    classification: str = Field(
        description="""The classification of the question. Determine the type of question and provide a single-word classification:
    - "delegates": if the question is about info and discussions on voting, delegation, and the Token House.
    - "general_discussions": if the question is about topics that don't need a category, or don't fit into any other existing category.
    - "mission_grants": if the question is about how to get a grant from the Governance Fund and keep up with key info.
    - "updates_and_announcements": if the question is about updates and announcements.
    - "retro_funding": if the question is about Retroactive Public Goods Funding rounds and related information.
    - "citizens": if the question is about things relating to Citizens, or citizen-related activities.
    - "elected_representatives": if the question is about any Elected Representative Structure, like info related to representatives or their responsibilities.
    - "technical_proposals": if the question is about non-grant related structural, technical, or governance proposals.
    - "policies_and_templates": if the question is about governance policies or finding proposal templates.
    - "collective_strategy": if the question relates to collective strategy, intent, or future planning for the collective.
    - "governance_design": if the question is about the collective's metagovernance strategy or structural design.
    - "accountability": if the question is related to posts that increase transparency or ensure accountability within the system.
    - "feedback": if the question seeks feedback or suggestions on specific topics.
    - "get_started": if the question is about initial information or how to get started with the governance forum or platform.
"""
    )
