import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Common configurations
    DATABASE_URL = os.getenv("DATABASE_URL", "")

    # Paths
    BASE_PATH = os.getenv("OP_CHAT_BASE_PATH", os.path.expanduser("../../data"))

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
