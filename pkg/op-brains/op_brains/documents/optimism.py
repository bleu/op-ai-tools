import re
import json
import time
import pandas as pd
from typing import Any, Dict, List

from langchain_core.documents.base import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter

from op_brains.documents import (
    DocumentProcessingStrategy,
    DocumentProcessorFactory,
)
from op_brains.retriever import connect_db

from op_brains.config import (
    RAW_FORUM_DB,
    FORUM_SUMMARY_DB,
    DOCS_PATH,
)

NOW = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())


class FragmentsProcessingStrategy(DocumentProcessingStrategy):
    def process_document(
        self, file_path: str, headers_to_split_on: List | None = None
    ) -> List[Document]:
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
                fragment.metadata["url"] = (
                    "https://community.optimism.io/docs/"
                    + d["path"]
                    + "/"
                    + d["document_name"][:-3]
                )
                fragment.metadata["path"] = d["path"]
                fragment.metadata["document_name"] = d["document_name"]
                fragment.metadata["type_db_info"] = "docs_fragment"
                fragments_docs.append(fragment)

        return fragments_docs

    def get_db_name(self) -> str:
        return "fragments_docs_db"


class ForumPostsProcessingStrategy(DocumentProcessingStrategy):
    @staticmethod
    def retrieve():
        out_db = connect_db.retrieve_data(
            f'select "rawData", url, type, "externalId" from "{RAW_FORUM_DB}"'
        )
        posts, threads = {}, {}
        for line in out_db:
            id = int(line[3])
            type_line = line[2]
            url_line = line[1]
            data_line = line[0]
            for post in data_line["post_stream"]["posts"]:
                posts[post["id"]] = post
                posts[post["id"]]["url"] = f"{url_line}/{post["id"]}"
                posts[post["id"]]["thread_id"] = int(id)

            threads[id] = data_line
            threads[id]["url"] = url_line

        #     if type_line == "post":
        #         posts[id] = data_line
        #         posts[id]["url"] = url_line
        #         posts[id]["thread_id"] = int(url_line.split("/")[-2])
        #     elif type_line == "thread":
        #         threads[id] = data_line
        #         threads[id]["url"] = url_line

        # print(len(posts))
        to_del = []
        for key in posts:
            try:
                posts[key]["thread_title"] = threads[posts[key]["thread_id"]]["title"]
                posts[key]["category_id"] = threads[posts[key]["thread_id"]][
                    "category_id"
                ]
            except KeyError:
                to_del.append(p)
        posts = {k: v for k, v in posts.items() if k not in to_del}
        # print(len(posts))

        return posts, threads

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
category: {CATEGORY_NAME}
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
    def return_threads() -> List:
        posts, threads_info = ForumPostsProcessingStrategy.retrieve()
        df_posts = pd.DataFrame(posts).T
        threads = []
        category_names = connect_db.retrieve_data(
            'select "externalId", "name" from "ForumPostCategory"'
        )
        category_names = {int(c[0]): c[1] for c in category_names}
        for t in df_posts["thread_id"].unique():
            posts_thread = df_posts[df_posts["thread_id"] == t].sort_values(
                by="created_at"
            )
            url = posts_thread["url"].iloc[0]
            url = url.split("/")[:-1]
            url = "/".join(url)
            t_i = threads_info[int(t)]
            category_name = category_names[t_i["category_id"]]

            str_thread = ForumPostsProcessingStrategy.template_thread.format(
                CATEGORY_NAME=category_name,
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
                    POST_NUMBER=post["post_number"],
                    USERNAME=post["username"],
                    CREATED_AT=post["created_at"],
                    TRUST_LEVEL=post["trust_level"],
                    IS_REPLY=f"(reply to post #{post['reply_to_post_number']})\n"
                    if post["reply_to_post_number"] != None
                    else "",
                    CONTENT=post["cooked"]
                    .replace("<\\content_user_input>", "")
                    .replace("<content_user_input>", ""),
                    MODERATOR=post["moderator"],
                    ADMIN=post["admin"],
                    STAFF=post["staff"],
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
                "category_name": category_name,
                "url": url,
                "num_posts": len(posts_thread),
                "users": list(posts_thread["username"].unique()),
                "length_str_thread": len(str_thread),
                "type_db_info": "forum_thread",
            }
            threads.append([str_thread, metadata])

        return threads

    @staticmethod
    def get_threads_documents() -> List[Document]:
        threads = ForumPostsProcessingStrategy.return_threads()
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
    def retrieve() -> List:
        out_db = connect_db.retrieve_data(
            f'select url, tldr, about, overview, reaction from "{FORUM_SUMMARY_DB}"'
        )

        ret = []
        for o in out_db:
            str_summary = SummaryProcessingStrategy.template_summary.format(
                TLDR=o[1],
                ABOUT=o[2],
                OVERVIEW=o[3],
                REACTION=o[4],
            )
            item = {"content": str_summary, "url": o[0], "classification": ""}
            ret.append(item)
        threads = ForumPostsProcessingStrategy.return_threads()

        for entry in ret:
            url = entry["url"]
            thread = next((t for t in threads if t[1]["url"] == url), None)
            entry["metadata"] = thread[1]
            entry["metadata"]["whole_thread"] = thread[0]
            entry["metadata"]["classification"] = entry["classification"]
            entry["metadata"]["type_db_info"] = "forum_thread_summary"

        ret = [x for x in ret if x is not None]
        ret = [x for x in ret if "metadata" in x.keys()]

        return ret

    @staticmethod
    def langchain_process(divide: str | None = None) -> Dict[str, List[Document]]:
        data = SummaryProcessingStrategy.retrieve()

        if isinstance(divide, str):
            classes = set([entry["metadata"][divide] for entry in data])
            docs = {c: [] for c in classes}
            for entry in data:
                c = entry["metadata"][divide]
                docs[c].append(
                    Document(page_content=entry["content"], metadata=entry["metadata"])
                )
            return docs
        else:
            docs = [
                Document(page_content=entry["content"], metadata=entry["metadata"])
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


class DataframeBuilder:
    @staticmethod
    def build_dataframes():
        summaries = SummaryProcessingStrategy.langchain_process(divide="category_name")
        pattern = r"[^A-Za-z0-9_]+"
        summaries = [
            (s.metadata["url"], s.metadata["last_posted_at"], s, re.sub(pattern, "", k))
            for k, v in summaries.items()
            for s in v
        ]

        last_posted_at = [
            time.strptime(s[1], "%Y-%m-%dT%H:%M:%S.%fZ")
            for s in summaries
            if s[1] is not None
        ]
        most_recent = max(last_posted_at)
        print(f"Most recent post date: {most_recent}")

        last_posted_at = [
            time.strptime(s[1], "%Y-%m-%dT%H:%M:%S.%fZ")
            for s in summaries
            if s[1] is not None
        ]
        most_recent = max(last_posted_at)
        print(f"Most recent post date: {most_recent}")

        fragments_loader = FragmentsProcessingStrategy()
        fragments = fragments_loader.process_document(DOCS_PATH, headers_to_split_on=[])

        data = [(f.metadata["url"], NOW, f, "fragments_docs") for f in fragments]
        data.extend(summaries)
        context_df = pd.DataFrame(
            data, columns=["url", "last_date", "content", "type_db_info"]
        )

        context_df = context_df.sort_values(by="last_date", ascending=False)

        return context_df
