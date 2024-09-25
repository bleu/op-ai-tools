import os
import importlib.resources
import op_artifacts.dbs
import op_artifacts
from dotenv import load_dotenv

load_dotenv()

BASE_PATH = os.getenv("OP_CHAT_BASE_PATH", os.path.expanduser("../../data"))

DOCS_PATH = importlib.resources.files(op_artifacts) / "governance_docs.txt"
VECTORSTORE = os.getenv("VECTORSTORE", "faiss")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")

# CHAT_MODEL = os.getenv("CHAT_MODEL", "claude-3-sonnet-20240229")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")

CHAT_TEMPERATURE = float(os.getenv("CHAT_TEMPERATURE", "0"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "2"))
K_RETRIEVER = int(os.getenv("K_RETRIEVER", "8"))
LOG_FILE = os.path.join(BASE_PATH, "logs.csv")

CHAT_MODEL_OPENAI = os.getenv("CHAT_MODEL_OPENAI", "gpt-4o")
SUMMARIZER_MODEL = os.getenv("SUMMARIZER_MODEL", CHAT_MODEL_OPENAI)

DB_STORAGE_PATH = importlib.resources.files(op_artifacts.dbs)
POSTHOG_API_KEY = os.getenv("POSTHOG_API_KEY", "")

RAW_FORUM_DB = "RawTopic"
FORUM_SUMMARY_DB = "Topic"
USE_SUMMARY_MOCK_DATA = os.getenv("USE_SUMMARY_MOCK_DATA", "False") == "True"
SNAPSHOT_DB = "SnapshotProposal"

SCOPE = "OPTIMISM GOVERNANCE/OPTIMISM COLLECTIVE/OPTIMISM L2"
