import system_structure, model_utils
import os, json, time
import streamlit as st

with st.echo():
    list_dbs = os.listdir("dbs")
    list_dbs = [db[:-3] for db in list_dbs if db[-3:] == "_db"]
    filter_out_dbs = ["summaries", 'ARCHIVED  & OLD Missions']
    dbs = [db for db in list_dbs if db not in filter_out_dbs]

    embedding_model = "text-embedding-ada-002"

    retriever = model_utils.build_retriever(
        dbs, 
        embedding_model,
        k = 20,
    )

    test_queries = [
        "Are Governance Fund grant applications currently being processed?",
        "Who is the Grants Council Lead?",
        "Who is Gonna?",
        "What is optimism?",
        "what about Diego's vote rationale for RF3?",
    ]

    models2test = [
        "gpt-4o-mini",
        #"gpt-4o",
        "claude-3-sonnet-20240229"
        #"claude-3-opus-20240229",
    ]

    

if st.button("Run test queries"):
    with st.echo():
        answers = {}
        for m in models2test:
            chat_model = (
                m,
                {
                    "temperature": 0.0,
                    "max_retries": 5,
                    "max_tokens": 1024,
                    "timeout": 60,
                }
            )

            system = system_structure.RAG_system(
                REASONING_LIMIT = 1,
                models_to_use = [chat_model, chat_model],
                factual_retriever = retriever,
                temporal_retriever = retriever,
                context_filter = model_utils.ContextHandling.filter,
                system_prompt_preprocessor = model_utils.Prompt.preprocessor,
                system_prompt_responder = model_utils.Prompt.responder,
                system_prompt_final_responder = model_utils.Prompt.final_responder
            )
            
            answers[m] = []
            for query in test_queries:
                start = time.time()
                out = system.predict(query, True)
                end = time.time()
                out["time_taken"] = end - start
                answers[m].append(out)

    st.write(answers)

    st.download_button(
        label="Download results",
        data=json.dumps(answers),
        file_name="results.json",
        mime="application/json"
    )