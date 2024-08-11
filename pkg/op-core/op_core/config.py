import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Common configurations
    DATABASE_URL = os.getenv("DATABASE_URL", "")

    # Paths
    BASE_PATH = os.getenv("OP_CHAT_BASE_PATH", os.path.expanduser("../../data"))

    # Model configurations
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    CHAT_MODEL_OPENAI = os.getenv("CHAT_MODEL_OPENAI", "gpt-4o")
    CHAT_MODEL_CLAUDE = os.getenv("CHAT_MODEL_CLAUDE", "claude-3-sonnet-20240229")

    @classmethod
    def get_tortoise_config(cls):
        return {
            "connections": {"default": cls.DATABASE_URL},
            "apps": {
                "models": {
                    "models": ["op_data.db.models"],
                    "default_connection": "default",
                },
            },
        }


config = Config()
