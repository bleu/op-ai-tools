import os
import re
import json

from langchain_openai import OpenAIEmbeddings
from langchain_core.documents.base import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_community.vectorstores import FAISS

from op_chat_brains.config import (
    DB_STORAGE_PATH,
    EMBEDDING_MODEL,
)


class DocumentLoader:
    @staticmethod
    def load_fragments(docs_path: str):
        with open(docs_path, "r") as f:
            docs_read = f.read()

        docs_read = re.split(r"==> | <==", docs_read)
        docs = []
        path = []
        for d in docs_read:
            if "\n" not in d:
                path = d.split("/")
            else:
                docs.append(
                    {
                        "path": "/".join(path[:-1]),
                        "document_name": path[-1],
                        "content": d,
                    }
                )

        docs = [d for d in docs if d["content"].strip() != ""]

        headers_to_split_on = [
            ("##", "header 2"),
            ("###", "header 3"),
            ("####", "header 4"),
            ("#####", "header 5"),
            ("######", "header 6"),
        ]
        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on
        )

        fragments_docs = []
        for d in docs:
            f = markdown_splitter.split_text(d["content"])
            for fragment in f:
                fragment.metadata["path"] = d["path"]
                fragment.metadata["document_name"] = d["document_name"]
                fragments_docs.append(fragment)

        embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        db = FAISS.from_documents(fragments_docs, embeddings)
        db_path = os.path.join(
            DB_STORAGE_PATH, f"fragments_docs_db/faiss/{EMBEDDING_MODEL}"
        )
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        db.save_local(db_path)

    @staticmethod
    def load_forum_posts(file_path: str):
        with open(file_path, "r") as file:
            boards, threads, posts = {}, {}, {}
            for line in file:
                data_line = json.loads(line)
                type_line = data_line["type"]
                try:
                    id = data_line["item"]["data"]["id"]
                    if type_line == "board":
                        boards[id] = {"name": data_line["item"]["data"]["name"]}
                    elif type_line == "thread":
                        threads[id] = {
                            "title": data_line["item"]["data"]["title"],
                            "category_id": data_line["item"]["data"]["category_id"],
                            "created_at": data_line["item"]["data"]["created_at"],
                            "views": data_line["item"]["data"]["views"],
                            "like_count": data_line["item"]["data"]["like_count"],
                        }
                    elif type_line == "post":
                        posts[id] = {
                            "url": data_line["item"]["url"],
                            "created_at": data_line["item"]["data"]["created_at"],
                            "username": data_line["item"]["data"]["username"],
                            "score": data_line["item"]["data"]["score"],
                            "readers_count": data_line["item"]["data"]["readers_count"],
                            "moderator": data_line["item"]["data"]["moderator"],
                            "admin": data_line["item"]["data"]["admin"],
                            "staff": data_line["item"]["data"]["staff"],
                            "trust_level": data_line["item"]["data"]["trust_level"],
                            "content": data_line["item"]["content"],
                            "creation_time": data_line["item"]["creation_time"],
                            "path": data_line["item"]["path"],
                            "download_time": data_line["download_time"],
                        }
                except KeyError:
                    pass

        for id_post, post in posts.items():
            path = post["path"]
            try:
                id_board = int(path[0])
                post["board_name"] = boards[id_board]["name"]
                post["board_id"] = id_board
            except:
                post["board_name"] = None

            try:
                id_thread = int(path[1])
                post["thread_title"] = threads[id_thread]["title"]
                post["thread_id"] = id_thread
            except:
                post["thread_title"] = None

        posts_forum = [
            Document(
                page_content=d["content"],
                metadata={
                    "board_name": d["board_name"],
                    "thread_title": d["thread_title"],
                    "creation_time": d["creation_time"],
                    "username": d["username"],
                    "moderator": d["moderator"],
                    "admin": d["admin"],
                    "staff": d["staff"],
                    "trust_level": d["trust_level"],
                    "id": ".".join(d["path"]) + "." + str(id),
                },
            )
            for id, d in posts.items()
        ]

        embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        db = FAISS.from_documents(posts_forum, embeddings)
        db_path = os.path.join(
            DB_STORAGE_PATH, f"posts_forum_db/faiss/{EMBEDDING_MODEL}"
        )
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        db.save_local(db_path)
