from typing import Dict, List


class Prompt:
    @staticmethod
    def classify_thread(thread_content: str) -> List[Dict[str, str]]:
        return [
            {
                "role": "system",
                "content": "Classify the forum thread in one of the following categories: **Announcement**, **Discussion**, **Feedback**, **Other**. Return only one word, the category.",
            },
            {"role": "user", "content": thread_content},
        ]

    @staticmethod
    def snapshot_summarize(
        snapshot_content: str, thread_content: str
    ) -> List[Dict[str, str]]:
        return [
            {
                "role": "system",
                "content": "You are going to have access to a proposal related to the Optimism Collective and the forum thread that discuss it. Return a text explaining the proposal discussed. This is going to be exhibited right before the actual thread, so just summarize the content in AT MOST 3 short paragraphs. Be concise and direct, prefer short phrases. Do not include users opinions. If the decision was already made, start by mentioning it. Return in the format '**Proposal:** Text'",
            },
            {
                "role": "user",
                "content": f"Snapshot proposal:\n{snapshot_content}\n\nForum thread:\n{thread_content}",
            },
        ]

    @staticmethod
    def opinions(context: str) -> List[Dict[str, str]]:
        return [
            {
                "role": "system",
                "content": "List UP TO 5 short paragraphs that summarize the most interesting opinions expressed in the thread. Be concise and direct, prefer short phrases. Do not include the users' names. Return only as a markdown list.",
            },
            {"role": "user", "content": context},
        ]

    @staticmethod
    def feedbacking_what(thread_content: str) -> List[Dict[str, str]]:
        return [
            {
                "role": "system",
                "content": "You are going to have access to a forum thread that is classified as **Feedback**. Return a text explaining what the users are giving feedback about. This is going to be exhibited right before the actual thread, so just summarize the content in AT MOST 3 short paragraphs. Be concise and direct, prefer short phrases. Do not include users opinions. Return in the format '**Feedback Session:** Text'",
            },
            {"role": "user", "content": thread_content},
        ]

    @staticmethod
    def announcing_what(thread_content: str) -> List[Dict[str, str]]:
        return [
            {
                "role": "system",
                "content": "You are going to have access to a forum thread that is classified as **Announcement**. Return a text explaining what is being announced. This is going to be exhibited right before the actual thread, so just summarize the content in AT MOST 3 short paragraphs. Be concise and direct, prefer short phrases. Do not include users opinions. Return in the format '**Announcement:** Text'",
            },
            {"role": "user", "content": thread_content},
        ]

    @staticmethod
    def discussing_what(thread_content: str) -> List[Dict[str, str]]:
        return [
            {
                "role": "system",
                "content": "You are going to have access to a forum thread that is classified as **Discussion**. Return a text explaining what is being discussed. This is going to be exhibited right before the actual thread, so just summarize the content in AT MOST 3 short paragraphs. Be concise and direct, prefer short phrases. Do not include users opinions. Return in the format '**Discussion:** Text'",
            },
            {"role": "user", "content": thread_content},
        ]

    @staticmethod
    def first_opinion(thread_content: str) -> List[Dict[str, str]]:
        return [
            {
                "role": "system",
                "content": "Return the opinion of the first user that started the discussion by making the first post. Be concise and direct, prefer short phrases. Return in the format '**First Opinion:** Text'",
            },
            {"role": "user", "content": thread_content},
        ]

    @staticmethod
    def reactions(thread_content: str) -> List[Dict[str, str]]:
        return [
            {
                "role": "system",
                "content": "List UP TO 5 short paragraphs that summarize the most interesting reactions to the first opinion. Be concise and direct, prefer short phrases. Do not include the users' names. Return only as a markdown list.",
            },
            {"role": "user", "content": thread_content},
        ]

    @staticmethod
    def tldr(thread_content: str) -> List[Dict[str, str]]:
        return [
            {
                "role": "system",
                "content": "Return a TLDR about the content of this forum thread. This is going to be exhibited right before the actual thread, so just summarize the content in AT MOST 3 sentences. Be concise and direct, prefer short phrases. Return in the format '**TLDR:** Text'",
            },
            {"role": "user", "content": thread_content},
        ]
