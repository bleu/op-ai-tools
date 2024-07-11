import streamlit as st
import pandas as pd
import random, time
random.seed(42)

from langchain.chains.summarize import load_summarize_chain
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

import load_optimism

def summarize_thread(thread, model_name, chain_type):
    if model_name in chat_models_openai:
        llm = ChatOpenAI(temperature=0, model_name=model_name)
    elif model_name in chat_models_anthropic:
        llm = ChatAnthropic(temperature=0, model_name=model_name)

    chain = load_summarize_chain(llm, chain_type=chain_type)
    result = chain.invoke([thread])

    return result

st.title("Summarize")

forum_path = "../../data/002-governance-forum-202406014/dataset/_out.jsonl"
posts = load_optimism.ForumPostsProcessingStrategy.process_document(forum_path)
df_posts = pd.DataFrame(posts).T

st.write("Collected Posts")
st.write(df_posts)

threads = load_optimism.ForumPostsProcessingStrategy.return_threads(df_posts)
minimum_posts = st.number_input("Minimum number of posts in a thread", 1, 20, 10)
threads = [t for t in threads if t.metadata["num_posts"] >= minimum_posts]
num_threads = st.number_input("Number of Threads to explore", 1, 20, 3)
threads = random.sample(threads, num_threads)

chat_models_openai = ["gpt-3.5-turbo-0125", "gpt-4o"]
chat_models_anthropic = ["claude-3-sonnet-20240229", "claude-3-haiku-20240307", "claude-3-opus-20240229", "claude-3-5-sonnet-20240620"]
chat_models = chat_models_openai + chat_models_anthropic
model_name = st.multiselect("Model Name", chat_models, default=["gpt-4o", "claude-3-sonnet-20240229"])

#chain_type = st.multiselect("Chain Type", ["stuff", "map_reduce", "refine"], default=["stuff"])
chain_type = ["stuff"]

if st.button("Summarize Threads"):   
    str_out = "## Summarized Threads\n"
    st.write("## Summarized Threads")
    for thread in threads:
        st.write("----")
        st.write(thread.metadata)
        st.write(thread.metadata["url"])
        str_out += f"----\n### Thread: {thread.metadata['url']}\n {thread.metadata}\n"
        for m in model_name:
            for c in chain_type:
                st.write(f"### Model: {m}, Chain: {c}")
                start = time.time()
                result = summarize_thread(thread, m, c)
                end = time.time()
                st.write(result['output_text'])
                st.write(f"(Time taken: {end-start}s)")
                str_out += f"#### Model: {m}, Chain: {c}\n{result['output_text']}\n(Time taken: {end-start}s)\n"

    st.download_button(
        label="Download Summarized Threads",
        data=str_out,
        file_name="summarized_threads.md",
        mime="text/markdown"
    )
        