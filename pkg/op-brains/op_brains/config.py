import os
import importlib.resources
import op_artifacts.dbs
import op_artifacts
from dotenv import load_dotenv

load_dotenv()

BASE_PATH = os.getenv("OP_CHAT_BASE_PATH", os.path.expanduser("../../data"))

DOCS_PATH = os.path.join(BASE_PATH, "001-initial-dataset-governance-docs/file.txt")
SNAPSHOT_PATH = os.path.join(
    BASE_PATH, "003-snapshot-spaces-proposals-20240711/dataset.jsonl"
)
VECTORSTORE = os.getenv("VECTORSTORE", "faiss")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
CHAT_MODEL_OPENAI = os.getenv("CHAT_MODEL_OPENAI", "gpt-4o")
CHAT_MODEL_CLAUDE = os.getenv("CHAT_MODEL_CLAUDE", "claude-3-sonnet-20240229")
CHAT_TEMPERATURE = float(os.getenv("CHAT_TEMPERATURE", "0"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "2"))
K_RETRIEVER = int(os.getenv("K_RETRIEVER", "8"))
LOG_FILE = os.path.join(BASE_PATH, "logs.csv")

SUMMARIZER_MODEL = os.getenv("SUMMARIZER_MODEL", CHAT_MODEL_OPENAI)

DB_STORAGE_PATH = importlib.resources.files(op_artifacts.dbs)
POSTHOG_API_KEY = os.getenv("POSTHOG_API_KEY", "")

RAW_FORUM_DB = "RawForumPost"
FORUM_SUMMARY_DB = "ForumPost"


QUESTIONS_INDEX_JSON = importlib.resources.files(op_artifacts) / "index_questions.json"
QUESTIONS_INDEX_NPZ = importlib.resources.files(op_artifacts) / "index_questions.npz"

KEYWORDS_INDEX_JSON = importlib.resources.files(op_artifacts) / "index_keywords.json"
KEYWORDS_INDEX_NPZ = importlib.resources.files(op_artifacts) / "index_keywords.npz"

SCOPE = "OPTIMISM GOVERNANCE/OPTIMISM COLLECTIVE/OPTIMISM L2"

os.makedirs(BASE_PATH, exist_ok=True)
