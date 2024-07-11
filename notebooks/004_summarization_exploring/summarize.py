import streamlit as st
import pandas as pd
import random, time
random.seed(42)

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

import load_optimism

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
    def opinions(thread_content, orginal_chain=[]):
        return orginal_chain+[
            (
                "system",
                "List UP TO 5 sentences that encapsulate the main opinions expressed in this thread. Try to follow a chronological order, listing first the opinions that appeared first. Return each sentence in the format '- Some users think...'. Do not include the user's name. Return in the format '**Users' Considerations:** Text"
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

st.title("Summarize")

forum_path = "../../data/002-governance-forum-202406014/dataset/_out.jsonl"
posts = load_optimism.ForumPostsProcessingStrategy.process_document(forum_path)
df_posts = pd.DataFrame(posts).T

st.write("Collected Posts")
st.write(df_posts)

threads = load_optimism.ForumPostsProcessingStrategy.return_threads(df_posts)

if st.checkbox("Random Selection"):
    minimum_posts = st.number_input("Minimum number of posts in a thread", 1, 20, 10)
    threads = [t for t in threads if t.metadata["num_posts"] >= minimum_posts]
    num_threads = st.number_input("Number of Threads to explore", 1, 20, 3)
    threads = random.sample(threads, num_threads)
else:
    thread_urls = st.multiselect("Thread URLs", [t.metadata["url"] for t in threads], ["https://gov.optimism.io/t/airdrop-1-feedback-thread/80/1", "https://gov.optimism.io/t/upgrade-proposal-6-multi-chain-prep-mcp-l1/7677/1"])
    threads = [t for t in threads if t.metadata["url"] in thread_urls]

chat_models_openai = ["gpt-3.5-turbo-0125", "gpt-4o"]
chat_models_anthropic = ["claude-3-sonnet-20240229", "claude-3-haiku-20240307", "claude-3-opus-20240229", "claude-3-5-sonnet-20240620"]
chat_models = chat_models_openai + chat_models_anthropic
model_name = st.multiselect("Model Name", chat_models, default=["gpt-4o", "claude-3-haiku-20240307", "claude-3-opus-20240229", "claude-3-5-sonnet-20240620"])

if st.button("Summarize Threads"):   
    str_out = "## Summarized Threads\n"
    st.write("## Summarized Threads")
    for thread in threads:
        st.write("----")
        st.write(thread.metadata)
        st.write(thread.metadata["url"])
        str_out += f"----\n### Thread: {thread.metadata['url']}\n {thread.metadata}\n"
        for m in model_name:
            llm = llm_builder(m)
            st.write(f"### Model: {m}")
            start = time.time()
            
            tldr = llm.invoke(Prompt.tldr(thread.page_content)).content
            #opinions = llm.invoke(Prompt.opinions(thread.page_content)).content
            first_post = llm.invoke(Prompt.first_post(thread.page_content)).content
            general_reaction = llm.invoke(Prompt.general_reaction(thread.page_content)).content

            end = time.time()
            st.write(tldr)
            st.write(first_post)
            st.write(general_reaction)

            #st.write(opinions)
            st.write(f"(Time taken: {end-start}s)")
            #str_out += f"#### Model: {m}, Chain: {c}\n{result['output_text']}\n(Time taken: {end-start}s)\n"

    st.download_button(
        label="Download Summarized Threads",
        data=str_out,
        file_name="summarized_threads.md",
        mime="text/markdown"
    )
        