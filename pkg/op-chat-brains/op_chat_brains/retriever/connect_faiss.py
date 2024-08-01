from typing import Tuple
import os

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from op_chat_brains.config import DB_STORAGE_PATH, EMBEDDING_MODEL


class DatabaseLoader:
    @staticmethod
    def load_db(
        dbs: Tuple[str, ...], vectorstore: str = "faiss"
    ) -> FAISS:
        embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        if vectorstore == "faiss":
            db_paths = [
                os.path.join(DB_STORAGE_PATH, f"{name}_db/faiss/{EMBEDDING_MODEL}")
                for name in dbs
            ]
            loaded_dbs = [
                FAISS.load_local(
                    db_path, embeddings, allow_dangerous_deserialization=True
                )
                for db_path in db_paths
            ]
            merged_db = loaded_dbs[0]
            for db in loaded_dbs[1:]:
                merged_db.merge_from(db)
            return merged_db
        raise ValueError(f"Unsupported vectorstore: {vectorstore}")

