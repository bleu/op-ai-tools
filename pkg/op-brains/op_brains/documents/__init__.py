import os
from abc import ABC, abstractmethod
from typing import Dict, List

from langchain_openai import OpenAIEmbeddings
from langchain_core.documents.base import Document
from langchain_community.vectorstores import FAISS

from op_brains.config import DB_STORAGE_PATH, EMBEDDING_MODEL


class DocumentProcessingStrategy(ABC):
    @abstractmethod
    def process_document(self, file_path: str) -> List[Document]:
        pass

    @abstractmethod
    def get_db_name(self) -> str:
        pass
