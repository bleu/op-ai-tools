import os

from op_chat_brains.config import (
    BASE_PATH,
    DB_STORAGE_PATH,
    EMBEDDING_MODEL,
)
from op_chat_brains.documents import (
    DocumentLoader,
)
from op_chat_brains.documents.optimism import OptimismDocumentProcessorFactory


def create_directory_structure(factory):
    document_types = factory.get_document_types()
    directories = [
        os.path.dirname(os.path.join(BASE_PATH, path))
        for path in document_types.values()
    ]
    directories.append(DB_STORAGE_PATH)
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def main():
    # You can easily switch to a different factory for other clients
    factory = OptimismDocumentProcessorFactory()
    create_directory_structure(factory)

    loader = DocumentLoader(factory)
    document_types = factory.get_document_types()

    for doc_type, relative_path in document_types.items():
        file_path = os.path.join(BASE_PATH, relative_path)
        db_path = os.path.join(
            DB_STORAGE_PATH, f"{doc_type}_db/faiss/{EMBEDDING_MODEL}"
        )

        if not os.path.exists(db_path):
            print(
                f"Loading {doc_type}... (This might take some minutes but will happen only once)"
            )
            loader.load_documents(doc_type, file_path)

    print(f"Setup complete. Data stored in {BASE_PATH}")


if __name__ == "__main__":
    main()
