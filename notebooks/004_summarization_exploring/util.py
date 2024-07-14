import pandas as pd
import random, time
random.seed(42)

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

import load_optimism

forum_path = "../../data/002-governance-forum-202406014/dataset/_out.jsonl"
snapshot_path = "../../data/003-snapshot-spaces-proposals-20240711/dataset.jsonl"

chat_models_openai = ["gpt-3.5-turbo-0125", "gpt-4o"]
chat_models_anthropic = ["claude-3-sonnet-20240229", "claude-3-haiku-20240307", "claude-3-opus-20240229", "claude-3-5-sonnet-20240620"]

today = pd.to_datetime("today").strftime("%Y%m%d")

def llm_builder(model_name):
    if model_name in chat_models_openai:
        llm = ChatOpenAI(temperature=0, model_name=model_name)
    elif model_name in chat_models_anthropic:
        llm = ChatAnthropic(temperature=0, model_name=model_name)
    return llm


class Prompt:
    @staticmethod
    def tldr(thread_content, orginal_chain=[]):
        return orginal_chain+[
            (
                "system",
                "Return a TLDR about the content of this forum thread. This is going to be exhibited right before the actual thread, so just summarize the content in AT MOST 3 sentences. Return in the format '**TLDR:** Text'"
            ),
            (
                "user",
                thread_content
            )
        ]
    
    @staticmethod
    def first_post(thread_content, orginal_chain=[]):
        return orginal_chain+[
            (
                "system",
                "Return ONE short paragraph encapsulating the main ideas of the first post of this forum thread. This is going to be exhibited right before the thread to give some general context. Return in the format '**Main Post:** Text'"
            ),
            (
                "user",
                thread_content
            )
        ]
    
    @staticmethod
    def general_reaction(thread_content, orginal_chain=[]):
        return orginal_chain+[
            (
                "system",
                "Return ONE short paragraph encapsulating the general reaction of the users to the first post of this forum thread. This is going to be exhibited right before the thread to give some general context. Return in the format '**General Reaction:** Text'"
            ),
            (
                "user",
                thread_content
            )
        ]
    
    @staticmethod
    def snapshot_summarize(snapshot_content, thread_content, orginal_chain=[]):
        return orginal_chain+[
            (
                "system",
                f"You are going to have access to a proposal related to the Optimism Collective and the forum thread that discuss it. Return a text explaining the proposal discussed. This is going to be exhibited right before the actual thread, so just summarize the content in AT MOST 3 short paragraphs. Do not include users opinions. If the decision was already made, start by mentioning it. Return in the format '**Proposal:** Text'"
            ),
            (
                "user",
                snapshot_content + thread_content
            )
        ]
    
    @staticmethod
    def opinions(orginal_chain=[]):
        return orginal_chain+[
            (
                "user",
                "Now list UP TO 5 short paragraphs that summarize the most interessant opinions expressed in the thread. Do not include the users' name. Return only as a markdown list"
            )
        ]

    @staticmethod
    def tldr_response(content):
        return [
            (
                "system",
                "Return a TLDR about the text. This is going to be exhibited right before the actual text, so just summarize the content in AT MOST 5 sentences. Return in the format '**TLDR:** Text'"
            ),
            (
                "user",
                content
            )
        ]