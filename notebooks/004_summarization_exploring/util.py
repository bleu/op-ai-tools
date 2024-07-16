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
    def tldr(thread_content):
        return [
            (
                "system",
                "Return a TLDR about the content of this forum thread. This is going to be exhibited right before the actual thread, so just summarize the content in AT MOST 3 sentences. Be concise and direct, prefer short phrases. Return in the format '**TLDR:** Text'"
            ),
            (
                "user",
                thread_content
            )
        ]
    
    @staticmethod
    def snapshot_summarize(snapshot_content, thread_content):
        return [
            (
                "system",
                f"You are going to have access to a proposal related to the Optimism Collective and the forum thread that discuss it. Return a text explaining the proposal discussed. This is going to be exhibited right before the actual thread, so just summarize the content in AT MOST 3 short paragraphs. Be concise and direct, prefer short phrases. Do not include users opinions. If the decision was already made, start by mentioning it. Return in the format '**Proposal:** Text'"
            ),
            (
                "user",
                snapshot_content + thread_content
            )
        ]
    
    @staticmethod
    def opinions(orginal_chain):
        return orginal_chain+[
            (
                "user",
                "Now list UP TO 5 short paragraphs that summarize the most interessant opinions expressed in the thread. Be concise and direct, prefer short phrases. Do not include the users' name. Return only as a markdown list"
            )
        ]

    @staticmethod
    def tldr_response(content):
        return [
            (
                "system",
                "Return a TLDR about the text. This is going to be exhibited right before the actual text, so just summarize the content in AT MOST 5 sentences. Be concise and direct, prefer short phrases. Return in the format '**TLDR:** Text'"
            ),
            (
                "user",
                content
            )
        ]
    
    @staticmethod
    def classify_thread(thread_content):
        return [
            (
                "system",
                "Classify the forum thread in one of the following categories: **Announcment**, **Discussion**, **Feedback**, **Other**. Return only one word, the category."
            ),
            (
                "user",
                thread_content
            )
        ]
    

    @staticmethod
    def feedbacking_what(thread_content):
        return [
            (
                "system",
                f"You are going to have access to a forum thread that is classified as **Feedback**. Return a text explaining what the users are giving feedback about. This is going to be exhibited right before the actual thread, so just summarize the content in AT MOST 3 short paragraphs. Be concise and direct, prefer short phrases. Do not include users opinions. Return in the format '**Feedback Session:** Text'"
            ),
            (
                "user",
                thread_content
            )
        ]
    
    def announcing_what(thread_content):
        return [
            (
                "system",
                f"You are going to have access to a forum thread that is classified as **Announcement**. Return a text explaining what is being announced. This is going to be exhibited right before the actual thread, so just summarize the content in AT MOST 3 short paragraphs. Be concise and direct, prefer short phrases. Do not include users opinions. Return in the format '**Announcement:** Text'"
            ),
            (
                "user",
                thread_content
            )
        ]
    
    def discussing_what(thread_content):
        return [
            (
                "system",
                f"You are going to have access to a forum thread that is classified as **Discussion**. Return a text explaining what is being discussed. This is going to be exhibited right before the actual thread, so just summarize the content in AT MOST 3 short paragraphs. Be concise and direct, prefer short phrases. Do not include users opinions. Return in the format '**Discussion:** Text'"
            ),
            (
                "user",
                thread_content
            )
        ]
    
    def first_opinion(orginal_chain):
        return orginal_chain+[
            (
                "user",
                "Now return the opinion of the first user that started the discussion by making the first post. Be concise and direct, prefer short phrases. Return in the format '**First Opinion:** Text'"
            )
        ]
    
    def reactions(orginal_chain):
        return orginal_chain+[
            (
                "user",
                "Now list UP TO 5 short paragraphs that summarize the most interessant reactions to the first opinion. Be concise and direct, prefer short phrases. Do not include the users' name. Return only as a markdown list"
            )
        ]
    
class InternalDialogue:
    @staticmethod
    def proposal(llm, thread, snapshot_proposals):
        url = thread.metadata["url"]
        for k in snapshot_proposals.keys():
            if url in k:
                url = k
                
        prompt = Prompt.snapshot_summarize(
            snapshot_content = snapshot_proposals[url]['str'], 
            thread_content = thread.page_content
        )
        snapshot_tldr = llm.invoke(prompt).content
        prompt = Prompt.opinions(
            orginal_chain = prompt + [('assistant', snapshot_tldr)]
        )
        opinions = llm.invoke(prompt).content
        
        summary = f"{snapshot_tldr}\n\n**Some user opinions:**\n{opinions}\n"
        tldr = llm.invoke(Prompt.tldr_response(summary)).content
        summary = f"{tldr}\n\n{summary}"

        return summary

    @staticmethod
    def feedback(llm, thread):
        prompt = Prompt.feedbacking_what(thread.page_content)
        topic = llm.invoke(prompt).content
        prompt = Prompt.opinions(
            orginal_chain = prompt + [('assistant', topic)]
        )
        opinions = llm.invoke(prompt).content

        summary = f"{topic}\n\n**Some user opinions:**\n{opinions}\n"

        tldr = llm.invoke(Prompt.tldr_response(summary)).content
        summary = f"{tldr}\n\n{summary}"

        return topic, opinions, summary
    
    @staticmethod
    def announcement(llm, thread):
        prompt = Prompt.announcing_what(thread.page_content)
        topic = llm.invoke(prompt).content
        prompt = Prompt.opinions(
            orginal_chain = prompt + [('assistant', topic)]
        )
        opinions = llm.invoke(prompt).content

        summary = f"{topic}\n\n**Some user opinions:**\n{opinions}\n"

        tldr = llm.invoke(Prompt.tldr_response(summary)).content
        summary = f"{tldr}\n\n{summary}"

        return topic, opinions, summary
    
    @staticmethod
    def discussion(llm, thread):
        prompt = Prompt.discussing_what(thread.page_content)
        topic = llm.invoke(prompt).content

        prompt = Prompt.first_opinion(
            orginal_chain = prompt + [('assistant', topic)]
        )
        first_opinion = llm.invoke(prompt).content

        prompt = Prompt.reactions(
            orginal_chain = prompt + [('assistant', first_opinion)]
        )
        reactions = llm.invoke(prompt).content

        summary = f"{topic}\n\n{first_opinion}\n\n**Reactions:**\n{reactions}\n"

        tldr = llm.invoke(Prompt.tldr_response(summary)).content
        summary = f"{tldr}\n\n{summary}"

        return topic, first_opinion, reactions, summary
    
    @staticmethod
    def other(llm, thread):
        summary = llm.invoke(Prompt.tldr(thread.page_content)).content
        return summary