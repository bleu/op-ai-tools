import click
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

import load_optimism, util

DEFAULT_LLM = "gpt-4o"

def get_thread_from_url(url):
    posts = load_optimism.ForumPostsProcessingStrategy.process_document(util.forum_path)
    df_posts = pd.DataFrame(posts).T
    threads = load_optimism.ForumPostsProcessingStrategy.return_threads(df_posts)
    threads_url = [t.metadata['url'] for t in threads]
    thread = threads[threads_url.index(url)]
    return thread

def summarize(thread, model_name):
    llm = util.llm_builder(model_name)

    snapshot_proposals = load_optimism.ForumPostsProcessingStrategy.return_snapshot_proposals(util.snapshot_path)
    if thread.metadata["url"] in '\t'.join(snapshot_proposals.keys()):
        summary = util.InternalDialogue.proposal(llm, thread, snapshot_proposals)
    else:
        type_thread = llm.invoke(util.Prompt.classify_thread(thread.page_content)).content
        match type_thread.upper():
            case "FEEDBACK":
                topic, opinions, summary = util.InternalDialogue.feedback(llm, thread)
            case "ANNOUNCEMENT":
                topic, opinions, summary = util.InternalDialogue.announcement(llm, thread)
            case "DISCUSSION":
                topic, first_opinion, reactions, summary = util.InternalDialogue.discussion(llm, thread)
            case _:
                summary = util.InternalDialogue.other(llm, thread)

    print(summary)
    return summary
    
def test_summarize():
    urls = [
        "https://gov.optimism.io/t/special-voting-cycle-9a-grants-council/4198",
        "https://gov.optimism.io/t/airdrop-1-feedback-thread/80",
        "https://gov.optimism.io/t/retro-funding-4-onchain-builders-round-details/7988",
        "https://gov.optimism.io/t/the-future-of-optimism-governance/6471"
    ]

    for url in urls:
        main(url, DEFAULT_LLM)
        print("\n\n----\n\n")

@click.command()
@click.argument("url")
@click.option("--rag-llm", default=DEFAULT_LLM)
def main(url : str, rag_llm : str) -> str:
    thread = get_thread_from_url(url)
    return summarize(thread, rag_llm)

if __name__ == "__main__":
    main()