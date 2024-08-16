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
