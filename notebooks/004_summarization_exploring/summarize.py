import streamlit as st
import pandas as pd
import random, time
import matplotlib.pyplot as plt
random.seed(42)

import load_optimism, util

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
posts = load_optimism.ForumPostsProcessingStrategy.process_document(forum_path)
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
threads = load_optimism.ForumPostsProcessingStrategy.return_threads(df_posts)
with st.expander("Threads Info"):
    st.write(f"Threads Metadata:")
    st.write(threads[0].metadata.keys())
    
    st.write(f"Template that will be used for inserting threads into the LLMs:")
    st.text(load_optimism.ForumPostsProcessingStrategy.template_thread)

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
selection_type = st.selectbox("Select Threads", ["Manual Selection", "Random Selection"], index=0)
if selection_type == "Random Selection":
    minimum_posts = st.number_input("Minimum number of posts in a thread", 1, 20, 10)
    threads = [t for t in threads if t.metadata["num_posts"] >= minimum_posts]
    num_threads = st.number_input("Number of Threads to explore", 1, 20, 3)
    threads = random.sample(threads, num_threads)
else:
    defalut_threads = []
    if st.checkbox("Add Snapshot Example"):
        snapshot_example = "https://gov.optimism.io/t/special-voting-cycle-9a-grants-council/4198"
        defalut_threads.append(snapshot_example)
    if st.checkbox("Add Feedback Example"):
        feedback_example = "https://gov.optimism.io/t/airdrop-1-feedback-thread/80"
        defalut_threads.append(feedback_example)
    if st.checkbox("Add Announcement Example"):
        announcement_example = "https://gov.optimism.io/t/retro-funding-4-onchain-builders-round-details/7988"
        defalut_threads.append(announcement_example)
    if st.checkbox("Add Discussion Example"):
        discussion_example = "https://gov.optimism.io/t/the-future-of-optimism-governance/6471"
        defalut_threads.append(discussion_example)

    thread_urls = st.multiselect("Thread URLs", [t.metadata["url"] for t in threads], default=defalut_threads)
    threads = [t for t in threads if t.metadata["url"] in thread_urls]

"""
----
- Select the models to try for summarization
"""
chat_models_openai = util.chat_models_openai
chat_models_anthropic = util.chat_models_anthropic
chat_models = chat_models_openai + chat_models_anthropic
#defalut_models = ["gpt-4o", "claude-3-haiku-20240307", "claude-3-opus-20240229", "claude-3-5-sonnet-20240620"]
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
snapshot_proposals = load_optimism.ForumPostsProcessingStrategy.return_snapshot_proposals(snapshot_path)


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
        append_text(f"----\n### Thread: {thread.metadata['url']}", thread.metadata)
        for m in model_name:
            append_text(f"### Model: {m}")

            llm = util.llm_builder(m)
            start = time.time()

            if thread.metadata["url"] in '\t'.join(snapshot_proposals.keys()):
                url = thread.metadata["url"]
                for k in snapshot_proposals.keys():
                    if url in k:
                        url = k

                prompt = util.Prompt.snapshot_summarize(
                    snapshot_content = snapshot_proposals[url]['str'], 
                    thread_content = thread.page_content
                )
                snapshot_tldr = llm.invoke(prompt).content
                prompt = util.Prompt.opinions(
                    orginal_chain = prompt + [('assistant', snapshot_tldr)]
                )
                opinions = llm.invoke(prompt).content
                
                summary = f"{snapshot_tldr}\n\n**Some user opinions:**\n{opinions}\n"
                tldr = llm.invoke(util.Prompt.tldr_response(summary)).content
                summary = f"{tldr}\n\n{summary}"
            else:
                type_thread = llm.invoke(util.Prompt.classify_thread(thread.page_content)).content
                st.write(type_thread.upper().strip())
                match type_thread.upper():
                    case "FEEDBACK":
                        prompt = util.Prompt.feedbacking_what(thread.page_content)
                        topic = llm.invoke(prompt).content
                        prompt = util.Prompt.opinions(
                            orginal_chain = prompt + [('assistant', topic)]
                        )
                        opinions = llm.invoke(prompt).content

                        summary = f"{topic}\n\n**Some user opinions:**\n{opinions}\n"

                        tldr = llm.invoke(util.Prompt.tldr_response(summary)).content
                        summary = f"{tldr}\n\n{summary}"
                    case "ANNOUNCEMENT":
                        prompt = util.Prompt.announcing_what(thread.page_content)
                        topic = llm.invoke(prompt).content
                        prompt = util.Prompt.opinions(
                            orginal_chain = prompt + [('assistant', topic)]
                        )
                        opinions = llm.invoke(prompt).content

                        summary = f"{topic}\n\n**Some user opinions:**\n{opinions}\n"

                        tldr = llm.invoke(util.Prompt.tldr_response(summary)).content
                        summary = f"{tldr}\n\n{summary}"
                    case "DISCUSSION":
                        prompt = util.Prompt.discussing_what(thread.page_content)
                        topic = llm.invoke(prompt).content

                        prompt = util.Prompt.first_opinion(
                            orginal_chain = prompt + [('assistant', topic)]
                        )
                        first_opinion = llm.invoke(prompt).content

                        prompt = util.Prompt.reactions(
                            orginal_chain = prompt + [('assistant', first_opinion)]
                        )
                        reactions = llm.invoke(prompt).content

                        summary = f"{topic}\n\n{first_opinion}\n\n**Reactions:**\n{reactions}\n"

                        tldr = llm.invoke(util.Prompt.tldr_response(summary)).content
                        summary = f"{tldr}\n\n{summary}"
                    case _:
                        summary = llm.invoke(util.Prompt.tldr(thread.page_content)).content


            end = time.time()
            append_text(summary, f"(Time taken: {end-start}s)")

    st.download_button(
        label="Download Summarized Threads",
        data=str_out,
        file_name="summarized_threads.md",
        mime="text/markdown"
    )
        