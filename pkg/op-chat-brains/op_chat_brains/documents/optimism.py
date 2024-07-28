import re, json
import pandas as pd
from typing import Any, Dict, List
from collections import defaultdict

from langchain_core.documents.base import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter

from op_chat_brains.documents import (
    DocumentProcessingStrategy,
    DocumentProcessorFactory,
)


class FragmentsProcessingStrategy(DocumentProcessingStrategy):
    def process_document(self, file_path: str, headers_to_split_on: List|None = None) -> List[Document]:
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

        if headers_to_split_on is None:
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
                fragment.metadata["url"] = "https://community.optimism.io/docs/" + d["path"] + "/" + d["document_name"][:-3]
                fragment.metadata["path"] = d["path"] 
                fragment.metadata["document_name"] = d["document_name"]
                fragment.metadata["type_db_info"] = "docs_fragment"
                fragments_docs.append(fragment)

        return fragments_docs

    def get_db_name(self) -> str:
        return "fragments_docs_db"

class ForumPostsProcessingStrategy(DocumentProcessingStrategy):
    @staticmethod
    def process_document(file_path: str, return_types: str = "posts") -> Any:
        with open(file_path, "r") as file:
            boards, threads, posts = {}, {}, {}
            for line in file:
                data_line = json.loads(line)
                type_line = data_line["type"]
                try:
                    id = data_line["item"]["data"]["id"]
                    if type_line == "board":
                        boards[id] = data_line["item"]["data"]
                    elif type_line == "thread":
                        threads[id] = data_line["item"]["data"]
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
                            "reply_to_post_number": data_line["item"]["data"][
                                "reply_to_post_number"
                            ],
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

        if return_types == "posts":
            return posts
        elif return_types == "posts_threads":
            return posts, threads

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
                    "type_db_info": "forum_post",
                },
            )
            for id, d in ForumPostsProcessingStrategy.process_document(
                file_path
            ).items()
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
                proposals[discussion]["str"] = (
                    ForumPostsProcessingStrategy.template_snapshot_proposal.format(
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
                )
        return proposals

    template_thread = """
OPTIMISM GOVERNANCE FORUM 
board: {BOARD_NAME}
thread: {THREAD_TITLE}

--- THREAD INFO ---
created_at: {CREATED_AT}
last_posted_at: {LAST_POSTED_AT}
tags: {TAGS}
pinned: {PINNED}
visible: {VISIBLE}
closed: {CLOSED}
archived: {ARCHIVED}
    """

    template_post = """
--- NEW POST ---
POST #{POST_NUMBER}
user: {USERNAME}
moderator: {MODERATOR}
admin: {ADMIN}
staff: {STAFF}
created_at: {CREATED_AT}
trust_level (0-4): {TRUST_LEVEL}

{IS_REPLY}<content_user_input>
{CONTENT}
<\\content_user_input>
    """

    @staticmethod
    def return_threads(file_path: str) -> List[Document]:
        posts, threads_info = ForumPostsProcessingStrategy.process_document(
            file_path, return_types="posts_threads"
        )
        df_posts = pd.DataFrame(posts).T
        threads = []
        for t in df_posts["thread_id"].unique():
            posts_thread = df_posts[df_posts["thread_id"] == t].sort_values(
                by="created_at"
            )
            try:
                url = posts_thread["url"].iloc[0]
                url = url.split("/")[:-1]
                url = "/".join(url)
                board = posts_thread["board_name"].iloc[0]
                t_i = threads_info[int(t)]

                str_thread = ForumPostsProcessingStrategy.template_thread.format(
                    BOARD_NAME=board,
                    THREAD_TITLE=t_i["title"],
                    TAGS=t_i["tags"],
                    CREATED_AT=t_i["created_at"],
                    LAST_POSTED_AT=t_i["last_posted_at"],
                    PINNED=t_i["pinned"],
                    VISIBLE=t_i["visible"],
                    CLOSED=t_i["closed"],
                    ARCHIVED=t_i["archived"],
                )
                for i, post in posts_thread.iterrows():
                    str_thread += ForumPostsProcessingStrategy.template_post.format(
                        POST_NUMBER=post['post_number'],
                        USERNAME=post['username'],
                        CREATED_AT=post['created_at'],
                        TRUST_LEVEL=post['trust_level'],
                        IS_REPLY=f"(reply to post #{post['reply_to_post_number']})\n" if post['reply_to_post_number'] != None else "",
                        CONTENT=post['content'].replace("<\\content_user_input>", "").replace("<content_user_input>", ""),
                        MODERATOR=post['moderator'],
                        ADMIN=post['admin'],
                        STAFF=post['staff'],
                    )

                metadata = {
                    "thread_id": t,
                    "thread_title": t_i["title"],
                    "created_at": t_i["created_at"],
                    "last_posted_at": t_i["last_posted_at"],
                    "tags": t_i["tags"],
                    "pinned": t_i["pinned"],
                    "visible": t_i["visible"],
                    "closed": t_i["closed"],
                    "archived": t_i["archived"],
                    "board_name": board,
                    "url": url,
                    "num_posts": len(posts_thread),
                    "users": list(posts_thread['username'].unique()),
                    'length_str_thread': len(str_thread),
                    "type_db_info": "forum_thread",
                }
                threads.append([str_thread, metadata])
            except:
                None

        threads_forum = [Document(page_content=t[0], metadata=t[1]) for t in threads]

        return threads_forum

    def get_db_name(self) -> str:
        return "posts_forum_db"

class SummaryProcessingStrategy(DocumentProcessingStrategy):
    template_summary = """
    <tldr>{TLDR}</tldr>
    <about>{ABOUT}</about>
    <overview>{OVERVIEW}</overview>
    <reaction>{REACTION}</reaction>
    """
    @staticmethod
    def process_document(summary_path: str, forum_path: str, divide:str|None=None) -> List[Dict]|Dict:
        with open(summary_path, 'r') as file:
            content = file.read()
            
        sections = content.split("\n\n--------------------------------------------------------------------------------\n\n")
        data = []

        url_pattern = re.compile(r"URL: (https?://[^\s]+)")
        xml_tag_pattern = re.compile(r"<(\w+)>(.+?)</\1>", re.DOTALL)

        for section in sections:
            entry = defaultdict(lambda: None)  # Use defaultdict to handle missing keys gracefully

            # Extract the URL
            url_match = url_pattern.search(section)
            if url_match:
                entry["URL"] = url_match.group(1)
            
            # Extract all XML tags and their content
            for match in xml_tag_pattern.findall(section):
                tag, content = match
                entry[tag.lower()] = content.strip()  # Capitalize tag names for uniform keys

            data.append(dict(entry))  # Convert defaultdict back to regular dict before appending

        threads = ForumPostsProcessingStrategy.return_threads(forum_path)

        for entry in data:
            try:
                url = entry["URL"]
                thread = next((t for t in threads if t.metadata["url"] == url), None)
                entry['metadata'] = thread.metadata
                entry['metadata']['whole_thread'] = thread.page_content
                entry['metadata']['classification'] = entry['classification']
                entry['metadata']['type_db_info'] = 'forum_thread_summary'
            except:
                entry = None

        data = [x for x in data if x is not None]
        data = [x for x in data if 'metadata' in x.keys()]

        if isinstance(divide, str):
            classes = set([entry['metadata'][divide] for entry in data])
            docs = {c : [] for c in classes}
            for entry in data:
                c = entry['metadata'][divide]
                docs[c].append(
                    Document(
                        page_content=SummaryProcessingStrategy.template_summary.format(
                            TLDR=entry["tldr"] if "tldr" in entry else "",
                            ABOUT=entry["about"] if "about" in entry else "",
                            OVERVIEW=entry["overview"] if "overview" in entry else "",
                            REACTION=entry["reaction"] if "reaction" in entry else "",
                        ),
                        metadata=entry["metadata"] if "metadata" in entry else {},
                    )
                )
            return docs
        else:
            docs = [
                Document(
                    page_content=SummaryProcessingStrategy.template_summary.format(
                        TLDR=entry["tldr"] if "tldr" in entry else "",
                        ABOUT=entry["about"] if "about" in entry else "",
                        OVERVIEW=entry["overview"] if "overview" in entry else "",
                        REACTION=entry["reaction"] if "reaction" in entry else "",
                    ),
                    metadata=entry["metadata"] if "metadata" in entry else {},
                )
                for entry in data
            ]
            
            return docs

class OptimismDocumentProcessorFactory(DocumentProcessorFactory):
    def create_processor(self, doc_type: str) -> DocumentProcessingStrategy:
        if doc_type == "fragments":
            return FragmentsProcessingStrategy()
        elif doc_type == "forum_posts":
            return ForumPostsProcessingStrategy()
        elif doc_type == "summaries":
            return SummaryProcessingStrategy()
        else:
            raise ValueError(f"Unsupported document type: {doc_type}")

    def get_document_types(self) -> Dict[str, str]:
        return {
            "fragments": "001-initial-dataset-governance-docs/file.txt",
            "forum_posts": "002-governance-forum-202406014/dataset/_out.jsonl",
        }
