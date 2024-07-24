import system_structure, model_utils

embedding_model = "text-embedding-ada-002"
dbs = ["summaries"]
retriever = model_utils.build_retriever(dbs, embedding_model)

chat_model = (
    "gpt-4o-mini",
    #"gpt-4o",
    #"claude-3-sonnet-20240229",
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
    factual_retriever = retriever.invoke,
    temporal_retriever = retriever.invoke,
    context_filter = lambda x, y: x,
    system_prompt_preprocessor = model_utils.Prompt.preprocessor,
    system_prompt_responder = model_utils.Prompt.responder,
    system_prompt_final_responder = model_utils.Prompt.final_responder
)
test_queries = [
    "Are Governance Fund grant applications currently being processed?",
    "Who is the leader of mission grants?",
    "What is optimism?",
    "what about Diego's vote rationale for RF3?"
]

for query in test_queries:
    out = system.predict(query)