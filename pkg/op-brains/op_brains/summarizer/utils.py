import pandas as pd


from typing import Dict, Any, Union, Optional
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

    proposal_summarizer = default_summarizer + f"""
    This thread is a proposal discussion. Details about the proposal are provided below:

    <proposal_snapshot>
    {{PROPOSAL}}
    </proposal_snapshot>

    Highlight the results and if it is already closed. If it is still open, mention the deadline.
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


class SummaryStructured(BaseModel):
    classification: str = Field(description="""The classification of the thread content. Determine the type of thread and provide a single-word classification:
    - "discussion": if the first post introduces a topic and the following posts discuss it bringing their points of view
    - "feedback": if it is a feedback section
    - "announcement": if the first post is an announcement and the following are reactions to it
    - "guide": if the thread contains a guide or tutorial
    - "informative": if is a thread with relevant instructions or information given by an official source
    - "unimportant": if someone with low trust level (smallest trust level is 0 and highest is 4) is talking alone, if it just talks about forum structure, if people are just chatting, if it is a welcome page, if someone is just saying hi everyone...
    - "other": for cases that don't fit the above categories
""")

    about: str = Field(description="Write up to 2 paragraphs summarizing what the thread content is about. If the thread is classified as 'unimportant' or 'other', provide instead a brief explanation of why it falls into this category.")
    
    overview: str = Field(description="""Summarize some details about the content in some short and concise bullet points. Try to list these in chronological order. If there are any useful links in the content, include them in the bullet points as [link to url abc](URL). If there are any important dates, deadlines, or events, also include them in the bullet points. Try to talk about every theme that was discussed.
                                    
    If it is classified as a guide or informative thread: Summarize the instructions, ideas, or steps provided. If some new relevant information (as acknowledged corrections or clarifications) is given in the comments, add them at the last bullet point.
    """)

    reaction: str = Field(description="Summarize general opinions from others WITHOUT MENTIONING USERS. Do this in ideally no more than 5 short and concise bullet points. If there is no relevant content, return an empty string.")
    
    tldr: str = Field(description="A short and concise paragraph that encompasses the most important information from what you wrote. If this is an old thread (and its information can be outdated), open the text with 'This is an old thread and the information may be outdated'.")    

