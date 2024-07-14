import re
import json
from typing import Dict, List, Any

from langchain_core.documents.base import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter

from op_chat_brains.documents import (
    DocumentProcessingStrategy,
    DocumentProcessorFactory,
)


class FragmentsProcessingStrategy(DocumentProcessingStrategy):
    def process_document(self, file_path: str) -> List[Document]:
        with open(file_path, "r") as f:
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

        return fragments_docs

    def get_db_name(self) -> str:
        return "fragments_docs_db"


class ForumPostsProcessingStrategy(DocumentProcessingStrategy):
    @staticmethod
    def process_document(file_path: str) -> List[Document]:
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
                            "reply_to_post_number": data_line["item"]["data"]["reply_to_post_number"],
                            "post_number": data_line["item"]["data"]["post_number"],
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

        return posts
    
    @staticmethod
    def return_posts(file_path: str) -> List[Document]:
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
            for id, d in ForumPostsProcessingStrategy.process_document(file_path).items()
        ]

        return posts_forum
    
    template_snapshot_proposal = """
    PROPOSAL
    {title}

    space_id: {space_id}
    space_name: {space_name}
    snapshot: {snapshot}
    state: {state}
    
    type: {type}
    body: {body}

    start: {start}
    end: {end}

    votes: {votes}
    choices: {choices}
    scores: {scores}

    winning_option: {winning_option}

    ----
    """

    @staticmethod
    def return_snapshot_proposals(file_path: str) -> Dict[str, Any]:
        with open(file_path, "r") as file:
            proposals = {}
            for line in file:
                data_line = json.loads(line)
                discussion = data_line["discussion"]
                proposals[discussion] = data_line
                proposals[discussion]["str"] = ForumPostsProcessingStrategy.template_snapshot_proposal.format(
                    title=data_line["title"],
                    space_id=data_line["space_id"],
                    space_name=data_line["space_name"],
                    snapshot=data_line["snapshot"],
                    state=data_line["state"],
                    type=data_line["type"],
                    body=data_line["body"],
                    start=data_line["start"],
                    end=data_line["end"],
                    votes=data_line["votes"],
                    choices=data_line["choices"],
                    scores=data_line["scores"],
                    winning_option=data_line["winning_option"],
                )
        return proposals
    
    template_thread = """
    OPTIMISM FORUM 
    board: BOARD NAME
    thread: THREAD TITLE

    ---

    POST #1 
    user: X (moderator) (admin) (staff)
    created_at: 2023-06-16T11:17:47.837Z 
    trust_level (0-4): 4

    <p>SOME TEXT</p>

    ---

    POST #2 
    user: Y
    created_at: 2023-06-16T11:17:56.495Z 
    trust_level (0-4): 1

    <p>SOME TEXT</p>
    """
    @staticmethod
    def return_threads(df_posts) -> List[Document]:
        threads =[]
        for t in df_posts['thread_id'].unique():
            posts_thread = df_posts[df_posts['thread_id'] == t].sort_values(by='created_at')
            try:
                url = posts_thread['url'].iloc[0]
                url = url.split("/")[:-1]
                url = "/".join(url)

                title = posts_thread['thread_title'].iloc[0]
                board = posts_thread['board_name'].iloc[0]
            except:
                url = None
                title = None
                board = None
            try:
                str_thread = f"OPTIMISM FORUM \n board: {posts_thread['board_name'].iloc[0]}\n thread: {posts_thread['thread_title'].iloc[0]}\n\n"
                for i, post in posts_thread.iterrows():
                    str_thread += f"---\n\nPOST #{post['post_number']} \n user: {post['username']}" 
                    if post['moderator']:
                        str_thread += " (moderator)"
                    if post['admin']:
                        str_thread += " (admin)"
                    if post['staff']:
                        str_thread += " (staff)"
                    str_thread += f"\n created_at: {post['created_at']} \n trust_level (0-4): {post['trust_level']}\n\n"
                    if post['reply_to_post_number'] != None:
                        str_thread += f"(reply to post number {post['reply_to_post_number']})\n"
                    str_thread += f"{post['content']}\n\n"
            except:
                None

            metadata = {
                "thread_id": t,
                "thread_title": title,
                "board_name": board,
                "url": url,
                "num_posts": len(posts_thread),
                "users": list(posts_thread['username'].unique()),
                'length_str_thread': len(str_thread),
            }
            threads.append([str_thread, metadata])

        threads_forum = [
            Document(
                page_content = t[0],
                metadata = t[1]
            ) for t in threads
        ]

        return threads_forum

    def get_db_name(self) -> str:
        return "posts_forum_db"


class OptimismDocumentProcessorFactory(DocumentProcessorFactory):
    def create_processor(self, doc_type: str) -> DocumentProcessingStrategy:
        if doc_type == "fragments":
            return FragmentsProcessingStrategy()
        elif doc_type == "forum_posts":
            return ForumPostsProcessingStrategy()
        else:
            raise ValueError(f"Unsupported document type: {doc_type}")

    def get_document_types(self) -> Dict[str, str]:
        return {
            "fragments": "001-initial-dataset-governance-docs/file.txt",
            "forum_posts": "002-governance-forum-202406014/dataset/_out.jsonl",
        }
