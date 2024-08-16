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
import os
import time
import nest_asyncio

nest_asyncio.apply()

# embedding and chat

openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

# for tracking

st.sidebar.write("# General Configs")

dbs = [
    "full_docs",
    "fragments_docs",
    "posts_forum",
    "threads_forum",
]

dbs = st.sidebar.multiselect(
    "Select databases", dbs, default=["fragments_docs", "posts_forum"]
)

embedding_models = [
    "text-embedding-3-small",
    "text-embedding-3-large",
    "text-embedding-ada-002",
]  # we are going to test the open ai api for embeddings
embedding_model = st.sidebar.selectbox(
    "Select embedding model", embedding_models, index=2
)

chat_models_openai = ["gpt-3.5-turbo-0125", "gpt-4o"]
chat_models_anthropic = [
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307",
    "claude-3-opus-20240229",
    "claude-3-5-sonnet-20240620",
]

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
        structures = arch.split("-")

        if "multi_retriever" in structures:
            retriever_pars = {db: {"search_kwargs": {}} for db in dbs}
            for db in dbs:
                k = st.number_input(
                    f"Number of Context Elements for {db}",
                    1,
                    10,
                    3,
                    key=f"{arch}_{db}_k",
                )
                retriever_pars[db]["search_kwargs"]["k"] = k
                if db == "posts_forum":
                    trust_level = st.multiselect(
                        f"Select {db} Trust Levels",
                        [0, 1, 2, 3, 4],
                        [2, 3, 4],
                        key=f"{arch}_{db}_trust_level",
                    )
                    retriever_pars[db]["search_kwargs"]["filter"] = {
                        "trust_level": trust_level
                    }
        else:
            k = st.number_input("Number of Context Elements", 1, 10, 5, key=f"{arch}_k")
            retriever_pars = {"search_kwargs": {"k": k + 1}}

        if "openai" in structures:
            chat_model = st.selectbox(
                "Select chat model",
                chat_models_openai,
                index=1,
                key=f"{arch}_chat_model",
            )

            prompt_template = "Answer politely the question at the end, using only the following context. The user is not necessarily a specialist, so please avoid jargon and explain any technical terms. \n\n<context> \n{context} \n</context> \n\nQuestion: {question}"
            prompt_template = st.text_area(
                "Prompt Template",
                prompt_template,
                height=250,
                key=f"{arch}_prompt_template",
            )
        elif "claude" in structures:
            chat_model = st.selectbox(
                "Select chat model",
                chat_models_anthropic,
                index=0,
                key=f"{arch}_chat_model",
            )

            def prompt_template(context, question):
                return [
                    (
                        "system",
                        f"You are a helpful assistant that helps access information about the Optimism Governance. Please provide polite and informative answers. Be assertive. The human is not necessarily a specialist, so please avoid jargon and explain any technical terms. \n\n Following there are some fragments retrieved from the Optimism Governance Forum and Optimism Documentation. This is expected to contain relevant information to answer the human question: \n\n {context}",
                    ),
                    ("human", question),
                ]

            if "query_expansion" in structures:

                def prompt_expander(question):
                    return [
                        (
                            "system",
                            "You are a machine that helps people to find information about the Optimism Governance. Your task is not to provide an answer. Expand the user prompt in order to clarify what the human wants to know. The output will be used to search algorithmically for relevant information.",
                        ),
                        ("human", question),
                    ]

                kwargs["prompt_expander"] = prompt_expander

        RAGModel = model_builder.RAG_model(arch, **kwargs)
        rag = RAGModel(
            dbs_name=dbs,
            embeddings_name=embedding_model,
            chat_pars={
                "model": chat_model,
                "temperature": temperature,
                "max_retries": max_retries,
                "max_tokens": 1024,
                "timeout": 60,
            },
            prompt_template=prompt_template,
            retriever_pars=retriever_pars,
        )

        st.write("## Prediction Test")

        dataset = [
            "Are there any specific KYC requirements for grant recipients in the Optimism community?",
            "Can I refer to OP token grants in terms of their USD value?",
            "Can Optimism currently censor user transactions?",
            "Can projects that have already received a grant apply for more funding?",
            "Can the length of the challenge period be changed?",
            "Do I need to claim my tokens for Airdrop #2?",
            "Do I need to hold a minimum amount of tokens to submit a proposal?",
            "Does the Law of Chains create any formal relationships among participants?",
            "How are Mission Requests ranked and funded in the Optimism Governance system?",
            "How are the rubrics for reviewing Mission applications in Season 5 structured?",
            "How can I become a support NERD in the Optimism community?",
            "How can I find out who my current delegate is and see their voting record?",
            "How can I get involved in the Optimism Collective?",
            "How can I get test tokens on the OP Goerli network?",
            "How can I get testnet ETH to deploy a smart contract on OP Sepolia?",
            "How can I participate in Optimism's Demo Day?",
            "How can I participate in Token House governance without a significant time commitment?",
            "How can I report a bug or suggest a feature for the Optimism SDK?",
            "How can I start the process of becoming an Optimism Ambassador?",
            "How does Optimism ensure that its protocol remains sustainable?",
            "How does Optimism's bi-cameral governance system help prevent plutocratic governance?",
            "How does Retro Funding 4 plan to reward the use of Open Source licenses?",
            "How does funding public goods drive demand for blockspace in the Optimism ecosystem?",
            "How does one progress through the ambassador roles in Optimism Governance?",
            "How does the Citizens' House contribute to the governance of the Optimism Collective?",
            "How does the Impact Evaluation Framework assist badgeholders in reviewing RetroPGF applications?",
            "How does the OP Passport project enhance privacy and security for governance participants?",
            "How does the Optimism Collective generate value for its ecosystem?",
            "How does the Optimism Collective plan to align the community in Season 4?",
            "How does the Optimism Collective plan to fund public goods?",
            "How does the Optimism Collective plan to handle identity and reputation?",
            "How does the Pairwise voting system work in the context of RetroPGF?",
            "How does the voting schedule work in Optimism's Token House governance?",
            "How is Citizenship in the Citizens' House expected to evolve over time?",
            "How is the scope and voting process for Retro Funding determined?",
            "How long do I need to offer support before becoming a `support-NERD`?",
            "How many OP tokens were involved in the private token sale in March 2024?",
            "How much funding was allocated in the first round of Retroactive Public Goods Funding by the Optimism Collective?",
            "How should badgeholders measure the Council’s impact?",
            "How were the badgeholders for RetroPGF Round 2 selected?",
            "Is the Law of Chains a legally binding contract?",
            "Is there a beginner-friendly version of the TechNERD training?",
            "What actions can lead to losing my NERD status?",
            "What actions can lead to losing your Ambassador status?",
            "What are Retroactive Public Goods Funding (RetroPGF) rounds?",
            "What are some community concerns regarding the enforcement of the Code of Conduct?",
            "What are some concerns related to the cost of on-chain voting?",
            "What are some examples of projects that can be nominated for the Tooling & Utilities category?",
            "What are some of the key features and improvements that have been added to Agora based on user feedback?",
            "What are some of the key metrics used to evaluate the performance of growth experiment programs?",
            "Are Governance Fund grant applications currently being processed?",
            "Can I create NFTs on the OP Mainnet without knowing how to code?",
            "How are protocols selected for the Protocol Delegation Program?",
            "How can DAOs incentivize more thoughtful participation in governance votes?",
            "How can I contribute to translating Optimism's User Docs?",
            "How can I get involved in running local events for the Optimism community?",
            "How can I participate in general governance discussions for Optimism?",
            "How can I promote my project once it's deployed on the Superchain?",
            "How can limiting delegate voting power promote decentralization and new delegate inclusion?delegate",
            "How do I apply for a Mission Grant on Optimism?",
            "How do Missions relate to Retro Funding?",
            "How does a non-grant proposal proceed to a vote in the Optimism Governance Forum?",
            "How does the Delta network upgrade propose to reduce L1 costs for OP Chains?",
            "How does the Grants Council ensure the responsible allocation of funds?",
            "How does the Optimism Collective support builders with grants?",
            "How does the bicameral governance system of the Optimism Token House limit the influence of large token holders?",
            "How has the votable supply of OP tokens changed during Season 3?",
            "How many project grants were approved and how many were rejected in the first three voting cycles?",
            "Is there any reward for translating documents for Optimism?",
            "What accountability measures are in place for teams receiving grants from the Governance Fund?",
        ]

        if st.button("Predict", key=f"{arch}_predict"):
            answers = []
            for question in dataset:
                start = time.time()
                answer = rag.predict(question)
                end = time.time()
                st.write(f"(took {end-start:.2f} seconds)")
                st.write(answer)
                answers.append(
                    (question, answer["answer"], end - start, answer["context"])
                )

            df_answers = pd.DataFrame(
                answers, columns=["Question", "Answer", "Elapsed Time", "Context"]
            )
            df_answers.to_csv(f"{arch}_answers.csv", index=False)
