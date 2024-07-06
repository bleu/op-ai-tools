import os

from op_chat_brains.config import (
    DOCS_PATH,
    FORUM_PATH,
    DB_STORAGE_PATH,
    EMBEDDING_MODEL,
    BASE_PATH,
)
from op_chat_brains.documents import DocumentLoader


def create_directory_structure():
    directories = [
        os.path.dirname(DOCS_PATH),
        os.path.dirname(FORUM_PATH),
        DB_STORAGE_PATH,
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def main():
    create_directory_structure()

    fragments_db_path = os.path.join(
        DB_STORAGE_PATH, f"fragments_docs_db/faiss/{EMBEDDING_MODEL}"
    )
    posts_db_path = os.path.join(
        DB_STORAGE_PATH, f"posts_forum_db/faiss/{EMBEDDING_MODEL}"
    )

    if not os.path.exists(fragments_db_path):
        print(
            "Loading documentation... (This might take some minutes but will happen only once)"
        )
        DocumentLoader.load_fragments(DOCS_PATH)
    if not os.path.exists(posts_db_path):
        print(
            "Loading forum posts... (This might take some minutes but will happen only once)"
        )
        DocumentLoader.load_forum_posts(FORUM_PATH)

    print(f"Setup complete. Data stored in {BASE_PATH}")


if __name__ == "__main__":
    main()
