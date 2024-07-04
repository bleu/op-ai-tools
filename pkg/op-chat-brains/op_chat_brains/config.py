DOCS_PATH = "../../data/001-initial-dataset-governance-docs/file.txt"
FORUM_PATH = "../../data/002-governance-forum-202406014/dataset/_out.jsonl"
DEFAULT_DBS = ["fragments_docs", "posts_forum"]
DEFAULT_RAG_STRUCTURE = "claude-expander"
VECTORSTORE = "faiss"
EMBEDDING_MODEL = "text-embedding-ada-002"
CHAT_MODEL_OPENAI = "gpt-4o"
CHAT_MODEL_CLAUDE = "claude-3-sonnet-20240229"
CHAT_TEMPERATURE = 0
MAX_RETRIES = 2
K_RETRIEVER = 8
LOG_FILE = "logs.csv"

PROMPT_TEMPLATE = """Answer politely the question at the end, using only context marked below. Context is formed by official Optimism documentation sections (more reliable) and forum posts/threads (less reliable)). Avoid technical jargon unless strictly necessary and explain any technical terms as the user is not technical. Be succint and condense your explanations. Your purpose is not to serve as a chatbot, so do not engage in longer conversations and press users for other questions.

<context>
{context} 
</context>

Question: {question}

"""

def PROMPT_BUILDER(context, question, expanded_question=None):
    return [
        (
            "system",
            f"You are a helpful assistant that helps access information about the Optimism Collective. Please provide polite and informative answers. Be assertive. The human is not necessarily a specialist, so please avoid jargon and explain any technical terms. \n\n Following there are some fragments retrieved from the Optimism Governance Forum and Optimism Documentation. This is expected to contain relevant information to answer the human question: \n\n {context}"
        ),
        (
            "human",
            question
        )
    ]

def PROMPT_BUILDER_EXPANDER(question):
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