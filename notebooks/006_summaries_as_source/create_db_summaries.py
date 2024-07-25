import streamlit as st
from op_chat_brains.documents.optimism import SummaryProcessingStrategy

with st.echo():
    # libraries for embedding model and vectorstore
    from langchain_openai import OpenAIEmbeddings
    embedding_models = ["text-embedding-ada-002"]
    from langchain_community.vectorstores import FAISS
    vectorstores = ['faiss']


with st.echo():
    # paths to the data
    summary_path = "../../data/summaries/all_thread_summaries.txt"
    forum_path = "../../data/002-governance-forum-202406014/dataset/_out.jsonl"


divide = st.checkbox("Divide by board name", value=True)
if divide:
    data_sources = SummaryProcessingStrategy.process_document(summary_path, forum_path, divide="board_name")
else:
    summaries = SummaryProcessingStrategy.process_document(summary_path, forum_path)
    data_sources = {
        "summaries": summaries
    }

st.write(data_sources)

if st.button("Create DBs"):
    for model_embeddings in embedding_models:
        embeddings = OpenAIEmbeddings(model=model_embeddings)
        for store in vectorstores:
            for name, d in data_sources.items():
                if store == 'faiss':
                    with st.spinner(f"Creating {name} db for {model_embeddings}"):
                        db = FAISS.from_documents(d, embeddings)
                        db.save_local(f"dbs/{name}_db/faiss/{model_embeddings}")
