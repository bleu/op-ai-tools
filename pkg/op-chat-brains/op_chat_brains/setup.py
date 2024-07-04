import os

from op_chat_brains.config import (
    DOCS_PATH,
    FORUM_PATH,
)
from op_chat_brains.documents import DocumentLoader


def main():
    if not os.path.exists("dbs/fragments_docs_db/faiss/text-embedding-ada-002"):
        print(
            "Loading documentation... (This might take some minutes but will happen only once)"
        )
        DocumentLoader.load_fragments(DOCS_PATH)
    if not os.path.exists("dbs/posts_forum_db/faiss/text-embedding-ada-002"):
        print(
            "Loading forum posts... (This might take some minutes but will happen only once)"
        )
        DocumentLoader.load_forum_posts(FORUM_PATH)


if __name__ == "__main__":
    main()
