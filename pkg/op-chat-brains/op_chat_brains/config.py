DOCS_PATH = "../../data/001-initial-dataset-governance-docs/file.txt"
FORUM_PATH = "../../data/002-governance-forum-202406014/dataset/_out.jsonl"
DEFAULT_DBS = ["fragments_docs", "posts_forum"]
VECTORSTORE = "faiss"
EMBEDDING_MODEL = "text-embedding-ada-002"
CHAT_MODEL = "gpt-4o"
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
