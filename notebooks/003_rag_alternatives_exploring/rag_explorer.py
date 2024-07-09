import streamlit as st

"""
# RAG Structures Explorer

This notebook is used to explore the different structures of RAG models. 
- We will be using the OpenAI API for embeddings and chat models. 
- We will be using the Anthropic API for the Claude chat model. 
- We will be using the FAISS vectorstore for storing the embeddings. 
- We will be using the Weave library for tracking the metrics. 
"""

# models
import model_builder

# general
import pandas as pd
import numpy as np
import os, asyncio, time, re
from getpass import getpass
from datetime import datetime
import tiktoken # metrics
import nest_asyncio
nest_asyncio.apply()
from typing import Callable

# embedding and chat
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_anthropic import ChatAnthropic

openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

# for tracking
import weave

st.sidebar.write("# General Configs")

dbs = [
    "full_docs",
    "fragments_docs",
    "posts_forum",
    "threads_forum",
]

dbs = st.sidebar.multiselect("Select databases", dbs, default=["fragments_docs", "posts_forum"])

embedding_models = ["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"] # we are going to test the open ai api for embeddings
embedding_model = st.sidebar.selectbox("Select embedding model", embedding_models, index=2)

chat_models_openai = ["gpt-3.5-turbo-0125", "gpt-4o"]
chat_models_anthropic = ["claude-3-sonnet-20240229", "claude-3-haiku-20240307", "claude-3-opus-20240229", "claude-3-5-sonnet-20240620"]

temperature = st.sidebar.number_input("Chat Temperature", 0.0, 1.0, 0.0, 0.1)
max_retries = st.sidebar.number_input("Chat Max Retries", 0, 20, 2)

archs = [
    "simple-openai",
    "multi_retriever-openai",
    "contextual_compression-openai",
    "simple-claude",
    "query_expansion-claude",
]

tabs = st.tabs(archs)
for i, tab in enumerate(tabs):
    arch = archs[i]
    with tab:
        kwargs = {}
        structures = arch.split('-')

        if "multi_retriever" in structures:
            retriever_pars = {db: {"search_kwargs" : {} } for db in dbs}
            for db in dbs:
                k = st.number_input(f"Number of Context Elements for {db}", 1, 10, 3, key=f'{arch}_{db}_k')
                retriever_pars[db]["search_kwargs"]['k'] = k
                if db == "posts_forum":
                    trust_level = st.multiselect(f"Select {db} Trust Levels", [0, 1, 2, 3, 4], [2, 3, 4], key=f'{arch}_{db}_trust_level')
                    retriever_pars[db]["search_kwargs"]['filter'] = {"trust_level": trust_level}
        else:
            k = st.number_input("Number of Context Elements", 1, 10, 5, key=f'{arch}_k')
            retriever_pars = {
                "search_kwargs" : {'k': k+1}
            }

        if "openai" in structures:
            chat_model = st.selectbox("Select chat model", chat_models_openai, index=1, key=f'{arch}_chat_model')

            prompt_template = f"Answer politely the question at the end, using only the following context. The user is not necessarily a specialist, so please avoid jargon and explain any technical terms. \n\n<context> \n{{context}} \n</context> \n\nQuestion: {{question}}"
            prompt_template = st.text_area("Prompt Template", prompt_template, height=250, key=f'{arch}_prompt_template')
        elif "claude" in structures:
            chat_model = st.selectbox("Select chat model", chat_models_anthropic, index=0, key=f'{arch}_chat_model')
            def prompt_template(context, question):
                return [
                    (
                        "system",
                        f"You are a helpful assistant that helps access information about the Optimism Governance. Please provide polite and informative answers. Be assertive. The human is not necessarily a specialist, so please avoid jargon and explain any technical terms. \n\n Following there are some fragments retrieved from the Optimism Governance Forum and Optimism Documentation. This is expected to contain relevant information to answer the human question: \n\n {context}"
                    ),
                    (
                        "human",
                        question
                    )
                ]
            if "query_expansion" in structures:
                def prompt_expander(question):
                    return [
                        (
                            "system",
                            f"You are a machine that helps people to find information about the Optimism Governance. Your task is not to provide an answer. Expand the user prompt in order to clarify what the human wants to know. The output will be used to search algorithmically for relevant information."
                        ),
                        (
                            "human",
                            question
                        )
                    ]
                kwargs['prompt_expander'] = prompt_expander

        
        RAGModel = model_builder.RAG_model(arch, **kwargs)
        rag = RAGModel(
            dbs_name = dbs,
            embeddings_name = embedding_model,
            chat_pars={
                "model": chat_model,
                "temperature": temperature,
                "max_retries": max_retries,
                "max_tokens": 1024,
                "timeout": 60,
            },
            prompt_template = prompt_template,
            retriever_pars = retriever_pars,
        )

        st.write("## Single Prediction Test")
        question = st.text_input("Question", "what is optimism?", key=f'{arch}_question')
        if st.button("Predict", key=f'{arch}_predict'):
            start = time.time()
            answer = rag.predict(question)
            end = time.time()
            st.write(f"(took {end-start:.2f} seconds)")
            st.write(answer)
