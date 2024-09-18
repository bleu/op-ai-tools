from typing import List, Callable, Tuple, Dict, Any, Union, Optional
import time
import json
import faiss
import numpy as np
import io
import pandas as pd
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.embeddings import HuggingFaceEmbeddings
from .test_chat_model import TestChatModel
from op_brains.retriever import connect_faiss
from op_brains.config import (
    QUESTIONS_INDEX_JSON,
    QUESTIONS_INDEX_NPZ,
    SCOPE,
    KEYWORDS_INDEX_JSON,
    KEYWORDS_INDEX_NPZ,
    EMBEDDING_MODEL,
    CHAT_MODEL,
)
from op_brains.documents import DataExporter

TODAY = time.strftime("%Y-%m-%d")


class Prompt:
    class NewSearch(BaseModel):
        user_knowledge: str = Field(
            f"""Analyze the conversation history to determine what the user seems to know well about {SCOPE}. If you can't assume any knowledge, return just an empty string."""
        )

        questions: List[str] = (
            Field(f"""Formulate questions about that encompasses the information that is missing. These questions are going to be used by the system to retrieve a context that can provide this information. The user won't see these questions.
                                     
When formulating questions, adhere to these guidelines:
    - Try to divide the lack of information into the smallest possible parts
    - Make questions concise and not redundant
    - Focus on gathering information directly related to answering the user's query
    - Avoid unnecessary questions
    - Do not ask questions that you already know the answer to.
    - Search for the definition of terms linked to the user's input in the context of {SCOPE}.
    """)
        )

        keywords: List[str] = (
            Field(f"""List some keywords that are relevant to the user's query. These keywords are going to be used by the system to retrieve a context that can provide this information. The user won't see these keywords. 
                                    
When adding keywords, adhere to these guidelines:
    - Add the name of the main concepts or topics that the questions are about. Every question is about {SCOPE}, so don't need to add the words from {SCOPE} as a keyword. The keywords should be just specific terms.
    - If the text mentions an occurrence or instance of something (very commonly adding a number at the end), sinalize it by using "#" followed by the number of the occurrence. For example, if the question mentions "Airdrop 3", use "Airdrop #3" as a keyword.
    - If the text mentions an occurrence or instance of something, use only the specific term. For example, if the question mentions "Season 6", don't use "Season" as a keyword, use only "Season #3".
    - If the question is about the general term, and doesn't mention any specific instance, use only the general term. For example, if the question is about "Cycle", use only "Voting Cycle" as a keyword.""")
        )

        type_search: str = Field(f"""Classify the search as one of the following types:
                                 
- "factual": the default case, will search the definition of terms and concepts.
- "ocurrence": in the case of question about a specific event or ocurrence that happened.
- "recent": in the case of questions about recent events, the current state of something or the most recent information available.""")

    class JustifiedClaim(BaseModel):
        claim: str = Field("The information you have.")
        url_supporting: str = Field(
            description="The URL source of the information you have. Never cite URLS that were not exactly provided."
        )

    class Answer(BaseModel):
        answer: str = Field("""Provide an answer. Some guidelines to follow:
- Directly address the user's question. Never write "according to the context", "based on the provided context" or similar phrases.
- Be polite, informative, assertive, objective, and brief.
- Avoid jargon and explain any technical terms.
- Never refer to past events as if they were happening now or in the future.
- Keep in mind the <query>. Don't answer an user question if you don't know the answer to this question. What you know is listed in the knowledge_summary.
- Never make up information.""")
        url_supporting: List[str] = Field(
            default=[],
            description="""The URL sources of the information you have. Never cite URLS that were not exactly provided.""",
        )

    @staticmethod
    def preprocessor(llm: ChatOpenAI | ChatAnthropic, **kwargs):
        preprocessor_header = f"""
You are a part of a helpful chatbot assistant system that provides information about {SCOPE}.

The context of the conversation is as follows: 

<conversation_history>
{{CONVERSATION_HISTORY}}
</conversation_history>

The user now provided the following query:

<user_input>
{{QUERY}}
</user_input>
"""

        class Preprocessor(BaseModel):
            related_to_scope: bool = Field(
                default=False,
                description=f"""Return False if you are 100% sure that the user's query is not related to the scope of {SCOPE}. Keep in mind that, most of the time, the user will ask a question related to the scope. 
                                           
            Some terms as "Cycle", "Airdrop", "Citizens' House", "Token House", "Grant", "Proposal", "Retro Funding", "OP", "NERD", "Law of Chains"... are related to the scope. If a person/user is referred to, it is likely to be a member of the Optimism Collectiv Community.""",
            )

            needs_info: bool = Field(
                default=False,
                description=f"""If related_to_scope is False, needs_info should be False. Else, return True if the user is not asking you to provide any information or if all the infor you need is in the <conversation_history>. Never make up information. If you don't have enough information to answer the user's query, needs_info should be True.""",
            )

            answer: str = Field(
                default=None,
                description=f"""Only if needs_info is False, that is, if you have enough information to answer the user's query, provide an answer to the user's query. Don't make up information. If related_to_scope is False, answer should be 'I'm sorry, but I can only answer questions about {SCOPE}. Is there anything specific about {SCOPE} you'd like to know?'""",
            )

            expansion: Prompt.NewSearch = Field(
                default=None,
                description=f"""Only if needs_info is True, that is, if you don't have enough information to answer the user's query, provide a new search that encompasses the information that is missing. The system will perform a search. This is going to be used by the system to retrieve a context that can provide this information. The user won't see this.""",
            )

        llm = llm.with_structured_output(Preprocessor)
        return llm.invoke(preprocessor_header.format(**kwargs)).dict()

    @staticmethod
    def responder(llm: ChatOpenAI | ChatAnthropic, final: bool = False, **kwargs):
        responder_header = f"""
You are a helpful assistant that provides information about {SCOPE}. Your goal is to give polite, informative, assertive, objective, and brief answers. Avoid jargon and explain any technical terms, as the user may not be a specialist.

An user inserted the following query:
<query>
{{QUERY}}
<query>

You have the following context information:
<context>
{{CONTEXT}}
</context>

The user seems to know the following:
<user_knowledge>
{{USER_KNOWLEDGE}}
</user_knowledge>

From past interactions, you have the following knowledge:
<your_previous_knowledge>
{{SUMMARY_OF_EXPLORED_CONTEXTS}}
</your_previous_knowledge>

Today's date is {TODAY}. Be aware of information that might be outdated.
"""

        class Responder(BaseModel):
            knowledge_summary: List[Prompt.JustifiedClaim] = Field(
                f"""Summarize the information you have that is relevant to the user's query. Do not mention what's lacking and you don't know. Take it from the context and from your previous knowledge. Every claim should be supported by a reference. References must come from the provided context or your previous knowledge. Never cite URLS that were not provided."""
            )

            if final:
                answer: Prompt.Answer = Field(
                    """If you don't have enough information to answer the query properly, start with "I couldn't find all the information I wanted to provide a complete answer." And provide some context about the information you have, how it relates to the query and what you think is missing to properly answer the user's query."""
                )
            else:
                answer: Prompt.Answer = Field(
                    default=None,
                    description="""Only if you have enough information to answer the query properly, provide an answer.""",
                )

                search: Prompt.NewSearch = Field(
                    default=None,
                    description="""If you didn't write an answer, provide a new search that encompasses the information that is missing. The system will perform a search. This is going to be used by the system to retrieve a context that can provide this information. The user won't see this.""",
                )

        llm = llm.with_structured_output(Responder)
        try:
            out = llm.invoke(responder_header.format(**kwargs))
        except:
            return None
        print(out)
        return out.dict()


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
        question_context: dict,
        explored_contexts: list,
        contexts_df: pd.DataFrame,
        query: str | None = None,
        type_search: str = "factual",
        k: int = 10,
    ) -> Tuple[str, list]:
        contexts_to_be_explored = {}
        for question, contexts in question_context.items():
            new_contexts = contexts
            # TODO: is this used anywhere?
            # new_contexts = [c for c in contexts if c.metadata.get("url") not in explored_contexts]

            if query is not None:
                k_i = min(k, len(new_contexts))
                if k_i > 0:
                    new_contexts = ContextHandling.reordering(
                        new_contexts,
                        query,
                        contexts_df=contexts_df,
                        k=k_i,
                        type_search=type_search,
                    )

            contexts_to_be_explored[question] = new_contexts

        c = list(contexts_to_be_explored.values())[:k]
        if len(c) > 0:
            try:
                max_c = max([len(cc) for cc in c])
            except Exception:
                max_c = 0
            contexts_to_be_explored = []
            for i in range(max_c):
                for cc in c:
                    if i < len(cc):
                        contexts_to_be_explored.append(cc[i])
            contexts_to_be_explored = {
                c.metadata.get("url"): c
                for c in contexts_to_be_explored
                if c.metadata.get("url")
            }

        return ContextHandling.format(contexts_to_be_explored, question_context)

    @staticmethod
    def format(context: dict, context_dict: dict) -> Tuple[str, list]:
        urls = list(context.keys())
        out = []
        for c in context.values():
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

        return "".join(out), urls

    @staticmethod
    def reordering(
        context: list, query: str, k: int, type_search: str, contexts_df: pd.DataFrame
    ) -> list:
        if type_search == "factual" or type_search == "ocurrence":
            return context[:k]
        elif type_search == "recent":
            urls = [c.metadata["url"] for c in context]
            contexts = all_contexts_df[all_contexts_df["url"].isin(urls)].iloc[:k]
            return contexts.content.tolist()


class RetrieverBuilder:
    @staticmethod
    def build_faiss_retriever(
        **retriever_pars,
    ):
        db = connect_faiss.CachedDatabaseLoader.load_db()
        return lambda query: db.similarity_search(query, **retriever_pars)

    @staticmethod
    def build_index(index, index_embed, k_max, treshold):
        embeddings = access_APIs.get_embedding(EMBEDDING_MODEL)

        index_keys = list(index.keys())

        if treshold < 1 and treshold > 0:
            index_faiss = faiss.IndexFlatIP(index_embed.shape[1])
            index_faiss.add(index_embed)

        async def find_similar(
            query: str,
            contexts_df: pd.DataFrame,
            criteria: Callable = lambda x: x,
            **kwargs,
        ):
            if treshold < 1:
                if treshold > 0:
                    query_embed = np.array(embeddings.embed_documents([query]))
                    distances, indices = index_faiss.search(query_embed, k_max)

                    similar = [index_keys[i] for i in indices[0]]
                    dists = distances[0]

                    dists = [d for d in dists if d >= treshold]
                    similar = [s for s, d in zip(similar, dists) if d >= treshold]
                else:
                    similar = index_keys
            else:
                similar = [query]

            similar = criteria(similar)

            urls = [u for s in similar for u in index[s]]

            contexts = contexts_df
            if "type_db_info" in kwargs:
                contexts = contexts[
                    contexts["type_db_info"].isin(kwargs["type_db_info"])
                ]
            contexts = contexts[contexts["url"].isin(urls)]

            return [contexts[contexts["url"] == u].content.tolist()[0] for u in urls]

        return find_similar


class access_APIs:
    def get_llm(model: str = CHAT_MODEL, **kwargs):
        if "gpt" in model:
            return ChatOpenAI(model=model, **kwargs)
        elif "claude" in model:
            return ChatAnthropic(model=model, **kwargs)
        elif "free" in model:
            return TestChatModel(n=10, model_name="testing")
        else:
            raise ValueError(f"Model {model} not recognized")

    @staticmethod
    def get_embedding(model: str = EMBEDDING_MODEL, **kwargs):
        # return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        if "free" in model:
            return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        else:
            return OpenAIEmbeddings(model=model, **kwargs)
