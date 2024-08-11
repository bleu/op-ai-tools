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


class DocumentProcessorFactory(ABC):
    @abstractmethod
    def create_processor(self, doc_type: str) -> DocumentProcessingStrategy:
        pass

    @abstractmethod
    def get_document_types(self) -> Dict[str, str]:
        pass


class DocumentLoader:
    def __init__(self, factory: DocumentProcessorFactory):
        self.factory = factory

    def load_documents(self, doc_type: str, file_path: str):
        processor = self.factory.create_processor(doc_type)
        documents = processor.process_document(file_path)
        embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        db = FAISS.from_documents(documents, embeddings)
        db_name = processor.get_db_name()
        db_path = os.path.join(DB_STORAGE_PATH, f"{db_name}/faiss/{EMBEDDING_MODEL}")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        db.save_local(db_path)
        return db_path
