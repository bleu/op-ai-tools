import streamlit as st
import pandas as pd
import random
import time

random.seed(42)

import load_optimism
import util

"""
# Summarization Script
This script allows you to summarize the threads from the Optimism Governance Forum testing different LLM models.

## Main Steps:
"""

"""
----
- Load the forum posts from the loaded dataset
"""
forum_path = util.forum_path
posts = load_optimism.ForumPostsProcessingStrategy.get_posts(forum_path)
df_posts = pd.DataFrame(posts).T
with st.expander("Posts Info"):
    st.write(f"Number of Loaded Posts: {len(df_posts)}")
    st.write(df_posts)

    df_posts["content_length"] = df_posts["content"].apply(lambda x: len(x))
    st.write("Number of Characters per Post:")
    st.write(df_posts["content_length"].describe())

    largest_post = df_posts.loc[df_posts["content_length"].idxmax()]
    st.write(f"Largest Post (len {largest_post['content_length']}):")
    st.write(largest_post)

"""
----
- Get the threads from the forum posts.
"""
threads = load_optimism.ForumPostsProcessingStrategy.return_threads(forum_path)
with st.expander("Threads Info"):
    st.write("Threads Metadata:")
    st.write(threads[0].metadata.keys())

    st.write("Template that will be used for inserting threads into the LLMs:")
    st.text(load_optimism.ForumPostsProcessingStrategy.template_thread)
    st.text(load_optimism.ForumPostsProcessingStrategy.template_post)

    df_threads = pd.DataFrame([t.metadata for t in threads])
    st.write(f"Number of Loaded Threads: {len(threads)}")

    st.write("Number of Threads per Board:")
    st.write(df_threads["board_name"].value_counts())

    st.write("Number of Posts per Thread:")
    st.write(df_threads["num_posts"].describe())

    st.write("Number of Characters per Thread:")
    st.write(df_threads["length_str_thread"].describe())


"""
----
- Select the threads to explore
    - If chosen the random selection, selects a random number of threads with a minimum number of posts instead of selecting the threads manually from their URLs
"""
selection_type = st.selectbox(
    "Select Threads", ["Manual Selection", "Random Selection"], index=0
)
if selection_type == "Random Selection":
    minimum_posts = st.number_input("Minimum number of posts in a thread", 1, 20, 10)
    threads = [t for t in threads if t.metadata["num_posts"] >= minimum_posts]
    num_threads = st.number_input("Number of Threads to explore", 1, 20, 3)
    threads = random.sample(threads, num_threads)
else:
    defalut_threads = []
    if st.checkbox("Add Snapshot Example"):
        snapshot_example = (
            "https://gov.optimism.io/t/special-voting-cycle-9a-grants-council/4198"
        )
        defalut_threads.append(snapshot_example)
    if st.checkbox("Add Feedback Example"):
        feedback_example = "https://gov.optimism.io/t/airdrop-1-feedback-thread/80"
        defalut_threads.append(feedback_example)
    if st.checkbox("Add Announcement Example"):
        announcement_example = "https://gov.optimism.io/t/retro-funding-4-onchain-builders-round-details/7988"
        defalut_threads.append(announcement_example)
    if st.checkbox("Add Discussion Example"):
        discussion_example = (
            "https://gov.optimism.io/t/how-to-start-a-project-at-optimism/7220"
        )
        defalut_threads.append(discussion_example)
    if st.checkbox("Add Guide Example"):
        guide_example = "https://gov.optimism.io/t/grant-misuse-reporting-process/7346"
        defalut_threads.append(guide_example)
    if st.checkbox("Add Unimportant Example"):
        unimportant_example = "https://gov.optimism.io/t/how-to-stay-up-to-date/6124"
        defalut_threads.append(unimportant_example)

    thread_urls = st.multiselect(
        "Thread URLs", [t.metadata["url"] for t in threads], default=defalut_threads
    )
    threads = [t for t in threads if t.metadata["url"] in thread_urls]

"""
----
- Select the models to try for summarization
"""
chat_models_openai = util.chat_models_openai
chat_models_anthropic = util.chat_models_anthropic
chat_models = chat_models_openai + chat_models_anthropic
# defalut_models = ["gpt-4o", "claude-3-haiku-20240307", "claude-3-opus-20240229", "claude-3-5-sonnet-20240620"]
defalut_models = ["claude-3-opus-20240229"]
defalut_models = ["gpt-4o"]
model_name = st.multiselect("Model Name", chat_models, default=defalut_models)


"""
----
## Special Threads

- Snapshot Proposals: Threads that are discussing Snapshot Proposals
    - We rely on the Snapshot dataset to get the proposals
    - We will load the snapshot data and check if the marked discussion page is the same as the thread URL
"""
snapshot_path = util.snapshot_path
snapshot_proposals = (
    load_optimism.ForumPostsProcessingStrategy.return_snapshot_proposals(snapshot_path)
)


"""
----
## Run
"""
if st.button("Summarize Threads"):
    str_out = ""

    def append_text(*text):
        global str_out
        for t in text:
            str_out += str(t) + "\n"
            st.write(t)

    append_text("## Summarized Threads")

    for thread in threads:
        append_text(f"\n----\n### Thread: {thread.metadata['url']}", thread.metadata)
        for m in model_name:
            append_text(f"### Model: {m}")

            llm = util.llm_builder(m)
            start = time.time()

            if thread.metadata["url"] in "\t".join(snapshot_proposals.keys()):
                summary = util.InternalDialogue.proposal(
                    llm, thread, snapshot_proposals
                )
            else:
                summary = llm.invoke(
                    util.Prompt.default_summarizer.format(
                        THREAD_CONTENT=thread.page_content
                    )
                ).content

            end = time.time()
            append_text(
                summary, f"len(summary): {len(summary)}", f"(Time taken: {end-start}s)"
            )

    st.download_button(
        label="Download Summarized Threads",
        data=str_out,
        file_name="summarized_threads.md",
        mime="text/markdown",
    )
