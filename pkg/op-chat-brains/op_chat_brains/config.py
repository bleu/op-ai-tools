import os

BASE_PATH = os.getenv("OP_CHAT_BASE_PATH", os.path.expanduser("../../data"))

DOCS_PATH = os.path.join(BASE_PATH, "001-initial-dataset-governance-docs/file.txt")
FORUM_PATH = os.path.join(
    BASE_PATH, "002-governance-forum-202406014/dataset/_out.jsonl"
)
SNAPSHOT_PATH = os.path.join(
    BASE_PATH, "003-snapshot-spaces-proposals-20240711/dataset.jsonl"
)
DEFAULT_DBS = ("fragments_docs", "posts_forum")
DEFAULT_RAG_STRUCTURE = os.getenv("DEFAULT_RAG_STRUCTURE", "claude-expander")
VECTORSTORE = os.getenv("VECTORSTORE", "faiss")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
CHAT_MODEL_OPENAI = os.getenv("CHAT_MODEL_OPENAI", "gpt-4o")
CHAT_MODEL_CLAUDE = os.getenv("CHAT_MODEL_CLAUDE", "claude-3-sonnet-20240229")
CHAT_TEMPERATURE = float(os.getenv("CHAT_TEMPERATURE", "0"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "2"))
K_RETRIEVER = int(os.getenv("K_RETRIEVER", "8"))
LOG_FILE = os.path.join(BASE_PATH, "logs.csv")
API_RATE_LIMIT = int(os.getenv("API_RATE_LIMIT", "100"))
API_SECRET_KEY = os.getenv("API_SECRET_KEY", "your-secret-key-here")
SUMMARIZER_MODEL = os.getenv("SUMMARIZER_MODEL", CHAT_MODEL_OPENAI)

DB_STORAGE_PATH = "dbs"#os.path.join(BASE_PATH, "dbs")
POSTHOG_API_KEY = os.getenv("POSTHOG_API_KEY", "")

RAW_FORUM_DB = "RawForumPost"
FORUM_SUMMARY_DB = "ForumPost"

QUESTIONS_INDEX_JSON = "index/questions.json"
QUESTIONS_INDEX_NPY = "index/questions.npy"

KEYWORDS_INDEX_JSON = "index/keywords.json"

SCOPE = "OPTIMISM GOVERNANCE/OPTIMISM COLLECTIVE/OPTIMISM L2"

os.makedirs(BASE_PATH, exist_ok=True)
