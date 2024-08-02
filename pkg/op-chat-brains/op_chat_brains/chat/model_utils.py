from typing import Iterator, List, Dict, Any, Callable, Tuple
import time, json, faiss, re
import numpy as np
import pandas as pd

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic

from op_chat_brains.retriever import connect_faiss
from op_chat_brains.config import (
    QUESTIONS_INDEX_JSON,
    QUESTIONS_INDEX_NPY,
    DOCS_PATH,
    SCOPE,
)
from op_chat_brains.documents import optimism

TODAY = time.strftime("%Y-%m-%d")

class ContextHandling:
    summary_template = """
<summary_from_forum_thread>
<title>{TITLE}</title>
<created_at>{CREATED_AT}</created_at>
<last_posted_at>{LAST_POST_AT}</last_posted_at>
<context_url>{URL}</context_url>

<content>{CONTENT}</content>
</summary_from_forum_thread>

"""

    @staticmethod
    def filter(
        context_dict: dict,
        explored_contexts: list,
        query: str | None = None,
        k: int = 5,
    ) -> Tuple[str, list]:
        urls = context_dict.keys()
        context = [c for c in context_dict.values() if c not in explored_contexts]

        if query is not None:
            k = min(k, len(context))
            if k > 0:
                context = ContextHandling.reordering(context, query, k=k)

        return ContextHandling.format(context, context_dict, urls)

    @staticmethod
    def format(context: list, context_dict: dict, urls: list) -> Tuple[str, list]:
        out = []
        for c in context:
            type_db = c.metadata["type_db_info"]
            match type_db:
                case "forum_thread_summary":
                    out.append(
                        ContextHandling.summary_template.format(
                            TITLE=c.metadata["thread_title"],
                            CREATED_AT=c.metadata["created_at"],
                            LAST_POST_AT=c.metadata["last_posted_at"],
                            URL=c.metadata["url"],
                            CONTENT=c.page_content,
                        )
                    )
                case _:
                    pass

        urls = [url for url in urls if context_dict[url] in context]
        return "".join(out), urls

    @staticmethod
    def reordering(context: list, query: str, k: int = 5) -> list:
        return context[:k]


class RetrieverBuilder:
    @staticmethod
    def build_faiss_retriever(
        dbs_name: List[str],
        embeddings_name: str,
        **retriever_pars,
    ):
        db = connect_faiss.DatabaseLoader.load_db(dbs_name, embeddings_name)
        return lambda query: db.similarity_search(query, **retriever_pars)

    def build_index(embeddings_name, k_max=10, treshold=0.95):
        embeddings = OpenAIEmbeddings(model=embeddings_name)

        # load json index
        with open(QUESTIONS_INDEX_JSON, "r") as f:
            index = json.load(f)

        index_questions = list(index.items())
        index_questions_embed = np.load(QUESTIONS_INDEX_NPY)
        index_faiss = faiss.IndexFlatIP(index_questions_embed.shape[1])
        index_faiss.add(index_questions_embed)

        summaries = optimism.SummaryProcessingStrategy.langchain_process(
            divide="category_name"
        )
        pattern = r"[^A-Za-z0-9_]+"
        summaries = [
            (s.metadata["url"], s, re.sub(pattern, "", k))
            for k, v in summaries.items()
            for s in v
        ]

        fragments_loader = optimism.FragmentsProcessingStrategy()
        fragments = fragments_loader.process_document(DOCS_PATH, headers_to_split_on=[])

        data = [(f.metadata["url"], f, "fragments_docs") for f in fragments]
        data.extend(summaries)
        context_df = pd.DataFrame(data, columns=["url", "content", "type_db_info"])

        def find_similar_questions(query):
            query_embed = np.array(embeddings.embed_documents([query]))
            D, I = index_faiss.search(query_embed, k_max)

            similar_questions = [index_questions[i] for i in I[0]]
            dists = D[0]

            dists = [d for d in dists if d >= treshold]
            similar_questions = [
                q for q, d in zip(similar_questions, dists) if d >= treshold
            ]

            return similar_questions

        def find_contexts(query, db_type_info=None):
            similar_questions = find_similar_questions(query)
            urls = [s[1] for s in similar_questions]
            urls = [x[0] for xs in urls for x in xs]

            contexts = context_df
            if db_type_info is not None:
                contexts = contexts[contexts["type_db_info"] == db_type_info]

            contexts = contexts[contexts["url"].isin(urls)]
            content = contexts["content"].tolist()
            return content

        return find_contexts


class access_APIs:
    def get_llm(model: str = "gpt-4o-mini", **kwargs):
        if "gpt" in model:
            return ChatOpenAI(model=model, **kwargs)
        elif "claude" in model:
            return ChatAnthropic(model=model, **kwargs)
        else:
            raise ValueError(f"Model {model} not recognized")
