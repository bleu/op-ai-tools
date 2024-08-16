import pandas as pd


from typing import Dict, Any
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

    Your task is to analyze this thread and provide a summary according to the following instructions:

    1. Classification:
    First, determine the type of thread and provide a single-word classification inside <classification> tags. The categories are:
    - "discussion": if the first post introduces a topic and the following posts discuss it bringing their points of view
    - "feedback": if it is a feedback section
    - "announcement": if the first post is an announcement and the following are reactions to it
    - "guide": if the thread contains a guide or tutorial
    - "informative": if is a thread with relevant instructions or information given by an official source
    - "unimportant": if someone with low trust level (0-4) is talking alone, if it just talks about forum structure, if people are just chatting, if it is a welcome page, if someone is just saying hi everyone...
    - "other": for cases that don't fit the above categories

    2. Summary:
    Based on the classification, provide a summary using the following structure:

    For "discussion":
    <about>: Summarize what the discussion is about
    <first_post>: Summarize what the first user thinks
    <reaction>: Summarize general opinions from others WITHOUT MENTIONING USERS. If there is no relevant content, you can skip this section.

    For "feedback" or "announcement":
    <about>: Summarize what the feedback or announcement is about
    <overview>: Summarize some details about the feedback or announcement
    <reaction>: Summarize general opinions WITHOUT MENTIONING USERS. If there is no relevant content, you can skip this section.

    For "guide" or "informative":
    <about>: Summarize what the guide helps with or what the information is about
    <overview>: Summarize the instructions, ideas or steps provided. If some new relevant information (as acknowledged corrections or clarifications) is given in the comments, add them at the last bullet point. DO NOT ADD SUGGESTIONS OR OPINIONS.

    For "unimportant" or "other":
    Provide a brief <about> section explaining why it falls into this category

    3. Formatting guidelines:
    - <classification> tag should contain only one word.
    - <about> section should contain no more than 2 short paragraphs.
    - All other sections should contain ideally no more than 5 short and concise bullet points.
    - Do not use complete sentences; instead, use concise phrases.
    - Do not be redundant. Never add unnecessary phrases or bullet points.
    - Do not mention specific usernames in your summary.
    - Pay attention to time-related topics. Today is {TODAY}. Past events must be informed as such.
    - If there are important links in the thread, include them in the summary in markdown format, like [this link to forum](https://gov.optimism.io/).

    4. TLDR:
    At the end of your summary, provide a <tldr> section with a short and concise paragraph that encompasses the most important information from the thread. If this is an old thread (and its information can be outdated), open the text with "This is an old thread and the information may be outdated.".

    Remember to enclose each section of your response in the appropriate XML tags as shown above. Your final output should look like this:

    <classification>category</classification>

    <about>
    TEXT
    </about>

    <overview> (if applicable)
    - Bullet point 1
    - Bullet point 2
    - ...
    </overview>

    <first_post> (if applicable)
    - Bullet point 1
    - Bullet point 2
    - ...
    </first_post>

    <reaction> (if applicable)
    - Bullet point 1
    - Bullet point 2
    - ...
    </reaction>

    <tldr>
    TEXT
    </tldr>

    Analyze the provided thread content and generate your summary following these instructions.
    """

    proposal_summarizer = f"""
    You will be given a proposal related to the Optimism Collective and the forum thread discussing it. Your task is to analyze this information and provide a structured summary. Here's the content:

    <proposal_snapshot>
    {{PROPOSAL}}
    </proposal_snapshot>

    <forum_thread>
    {{FORUM_THREAD}}
    </forum_thread>

    Carefully read and analyze the proposal and the forum thread discussion. Then, provide a summary structured in the following sections:

    1. <about>
    Summarize what the discussion is about. Provide a brief overview of the proposal and the main points being discussed in the forum thread. Mention the results and if it is already closed.

    2. <overview>
    Summarize some details about the changes suggested.

    3. <reaction>
    Summarize the general opinions and reactions from other users in the thread. Focus on common themes, agreements, disagreements, and any notable suggestions or concerns raised. Do not mention any specific usernames or identify individual users in this section. If there are no relevant reactions or responses in the thread, you may omit this section.

    Formatting guidelines:
        - <about> section should contain no more than 2 short paragraphs.
        - All other sections should contain ideally no more than 5 short and concise bullet points.
        - Do not use complete sentences; instead, use concise phrases.
        - Do not mention specific usernames in your summary.
        - Pay attention to time-related topics. Today is {TODAY}. Past events must be informed as such.

    4. <tldr>
    At the end of your summary, provide a <tldr> section with a short and concise paragraph that encompasses the most important information.

    For each section, use the appropriate XML tags as shown above. Ensure that your summaries are clear, concise, and accurately represent the content of the proposal and forum thread.

    Remember, in the <reaction> section, do not mention or identify any specific users. Focus on the overall sentiment and key points raised by the community as a whole.

    Your final output should look like this:

    <about>
    TEXT
    </about>

    <overview>
    - Bullet point 1
    - Bullet point 2
    - ...
    </overview>

    <reaction>
    - Bullet point 1
    - Bullet point 2
    - ...
    </reaction>

    <tldr>
    TEXT
    </tldr>

    Begin your analysis and provide the structured summary now.
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
                FORUM_THREAD=thread.page_content,
            )
        ).content

        return summary
