import re
import json
import time
import pandas as pd
from typing import Any, Dict, List, Tuple
import datetime as dt
from langchain_core.documents.base import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter
from op_data.db.models import RawTopic, Topic, TopicCategory, SnapshotProposal
from op_brains.config import RAW_FORUM_DB, FORUM_SUMMARY_DB, DOCS_PATH, SNAPSHOT_DB
import aiofiles
from tortoise.expressions import Q, F

NOW = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())


class FragmentsProcessingStrategy:
    name_source = "documentation"

    @staticmethod
    async def langchain_process(
        file_path: str = DOCS_PATH, headers_to_split_on: List | None = [], **kwargs
    ) -> List[Document]:
        async with aiofiles.open(file_path, "r") as f:
            docs_read = await f.read()

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

    @staticmethod
    async def dataframe_process(**kwargs) -> pd.DataFrame:
        fragments = await FragmentsProcessingStrategy.langchain_process(**kwargs)
        data = [(f.metadata["url"], NOW, f, "fragments_docs") for f in fragments]

        return pd.DataFrame(
            data, columns=["url", "last_date", "content", "type_db_info"]
        )


class ForumPostsProcessingStrategy:
    @staticmethod
    async def retrieve(
        only_not_summarized: bool = False, only_not_embedded: bool = False
    ) -> Tuple[Dict, Dict]:
        if only_not_summarized:
            raw_topics = await RawTopic.filter(
                Q(lastSummarizedAt__lt=F("lastUpdatedAt"))
                | Q(lastSummarizedAt__isnull=True)
            ).values("rawData", "url", "type", "externalId")
        elif only_not_embedded:
            raw_topics = await RawTopic.filter(
                Q(lastEmbeddedAt__lt=F("lastUpdatedAt"))
                | Q(lastEmbeddedAt__isnull=True)
            ).values("rawData", "url", "type", "externalId")
        else:
            raw_topics = await RawTopic.all().values(
                "rawData", "url", "type", "externalId"
            )

        posts, threads = {}, {}
        for line in raw_topics:
            id = int(line["externalId"])
            type_line = line["type"]
            url_line = line["url"]
            data_line = line["rawData"]
            for post in data_line.get("post_stream", {}).get("posts", []):
                post_id = post.get("id")
                posts[post_id] = post
                posts[post_id]["url"] = f"{url_line}/{post_id}"
                posts[post_id]["thread_id"] = int(id)

            threads[id] = data_line
            threads[id]["url"] = url_line

        to_del = []
        for key in posts:
            try:
                posts[key]["thread_title"] = threads[posts[key]["thread_id"]]["title"]
                posts[key]["category_id"] = threads[posts[key]["thread_id"]][
                    "category_id"
                ]
            except KeyError:
                to_del.append(posts[key]["thread_id"])
        posts = {k: v for k, v in posts.items() if k not in to_del}

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
    async def return_snapshot_proposals() -> Dict[str, Any]:
        snapshot_proposals = await SnapshotProposal.all().values(
            "discussion",
            "title",
            "spaceId",
            "spaceName",
            "snapshot",
            "state",
            "type",
            "body",
            "start",
            "end",
            "votes",
            "choices",
            "scores",
            "winningOption",
        )

        proposals = {}
        for line in snapshot_proposals:
            discussion = line["discussion"]
            proposals[discussion] = {
                "title": line["title"],
                "space_id": line["spaceId"],
                "space_name": line["spaceName"],
                "snapshot": line["snapshot"],
                "state": line["state"],
                "type": line["type"],
                "body": line["body"],
                "start": line["start"],
                "end": line["end"],
                "votes": line["votes"],
                "choices": line["choices"],
                "scores": line["scores"],
                "winning_option": line["winningOption"],
            }
            proposals[discussion]["str"] = (
                ForumPostsProcessingStrategy.template_snapshot_proposal.format(
                    title=line["title"],
                    space_id=line["spaceId"],
                    space_name=line["spaceName"],
                    snapshot=line["snapshot"],
                    state=line["state"],
                    type=line["type"],
                    body=line["body"],
                    start=line["start"],
                    end=line["end"],
                    votes=line["votes"],
                    choices=line["choices"],
                    scores=line["scores"],
                    winning_option=line["winningOption"],
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
    async def return_threads(
        only_not_summarized: bool = False, only_not_embedded: bool = False
    ) -> List:
        posts, threads_info = await ForumPostsProcessingStrategy.retrieve(
            only_not_summarized=only_not_summarized,
            only_not_embedded=only_not_embedded,
        )

        if not threads_info:
            return []

        df_posts = pd.DataFrame(posts).T
        threads = []
        categories = await TopicCategory.all().values("externalId", "name")
        category_names = {int(c["externalId"]): c["name"] for c in categories}

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
                    if post["reply_to_post_number"] is not None
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
    async def get_threads_documents() -> List[Document]:
        threads = await ForumPostsProcessingStrategy.return_threads()
        threads_forum = [Document(page_content=t[0], metadata=t[1], id=t[1]['thread_id']) for t in threads]

        return threads_forum

    @staticmethod
    async def get_threads_documents_not_summarized() -> List[Document]:
        threads = await ForumPostsProcessingStrategy.return_threads(
            only_not_summarized=True
        )
        threads_forum = [Document(page_content=t[0], metadata=t[1], id=t[1]['thread_id']) for t in threads]

        return threads_forum

    def get_db_name(self) -> str:
        return "posts_forum_db"


class SummaryProcessingStrategy:
    name_source = "summary"

    template_summary = """
    <tldr>{TLDR}</tldr>
    <about>{ABOUT}</about>
    <overview>{OVERVIEW}</overview>
    <reaction>{REACTION}</reaction>
    """

    @staticmethod
    async def retrieve(only_not_embedded: bool = False) -> List[dict]:
        out_db = await Topic.all().values(
            "url", "tldr", "about", "overview", "reaction"
        )

        ret = []
        for o in out_db:
            str_summary = SummaryProcessingStrategy.template_summary.format(
                TLDR=o["tldr"],
                ABOUT=o["about"],
                OVERVIEW=o["overview"],
                REACTION=o["reaction"],
            )
            item = {"content": str_summary, "url": o["url"], "classification": ""}
            ret.append(item)

        threads = await ForumPostsProcessingStrategy.return_threads(
            only_not_embedded=only_not_embedded
        )

        for entry in ret:
            url = entry["url"]
            thread = next((t for t in threads if t[1]["url"] == url), None)
            if thread:
                entry["metadata"] = thread[1]
                entry["metadata"]["whole_thread"] = thread[0]
                entry["metadata"]["classification"] = entry["classification"]
                entry["metadata"]["type_db_info"] = "forum_thread_summary"

        ret = [x for x in ret if x is not None]
        ret = [x for x in ret if "metadata" in x.keys()]

        return ret

    @staticmethod
    async def langchain_process(
        divide: str | None = "category_name",
        only_not_embedded: bool = False,
    ) -> Dict[str, List[Document]]:
        data = await SummaryProcessingStrategy.retrieve(
            only_not_embedded=only_not_embedded
        )

        if isinstance(divide, str):
            classes = set([entry["metadata"][divide] for entry in data])
            docs = {c: [] for c in classes}
            for entry in data:
                c = entry["metadata"][divide]
                docs[c].append(
                    Document(page_content=entry["content"], metadata=entry["metadata"], id=entry["metadata"]["thread_id"])
                )
            return docs
        else:
            docs = [
                Document(page_content=entry["content"], metadata=entry["metadata"], id=entry["metadata"]["thread_id"])
                for entry in data
            ]

            return docs

    @staticmethod
    async def dataframe_process(**kwargs) -> pd.DataFrame:
        summaries = await SummaryProcessingStrategy.langchain_process(**kwargs)
        pattern = r"[^A-Za-z0-9_]+"
        summaries = [
            (s.metadata["url"], s.metadata["last_posted_at"], s, re.sub(pattern, "", k))
            for k, v in summaries.items()
            for s in v
        ]

        return pd.DataFrame(
            summaries, columns=["url", "last_date", "content", "type_db_info"]
        )
