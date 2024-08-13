from typing import List, Callable, Tuple
import time
import json
import faiss
import numpy as np

from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from op_brains.retriever import connect_faiss
from op_brains.config import (
    QUESTIONS_INDEX_JSON,
    QUESTIONS_INDEX_NPZ,
    SCOPE,
    KEYWORDS_INDEX_JSON,
    KEYWORDS_INDEX_NPZ,
    EMBEDDING_MODEL,
)
from op_brains.documents import optimism

TODAY = time.strftime("%Y-%m-%d")
all_contexts_df = optimism.DataExporter.get_dataframe()


class Prompt:
    responder_start = f"""
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

Follow these steps:

1. Analyze the user's question, the provided context and your previous knowledge. Keep in mind the user's knowledge.

2. Summarize the information you have that is relevant to the user's query. Take it from the context and from your previous knowledge. Include this summary inside <knowledge_summary></knowledge_summary> tags. Cite the source URL using the format [1] within the text and list the url references at the end. Every claim should be supported by a reference. References must come from the provided context or your previous knowledge. Never cite urls that were not provided.

3. Check if you have enough information to answer the user's query. 

4. If you have enough information to the question, provide an answer inside <answer></answer> tags. Your answer should:
   - Directly address the user's question. Never write "according to the context", "based on the provided context" or similar phrases.
   - Cite the source URL using the format [1] within the text.
   - List the url references at the end of the answer.
   - Write the complete URL of the source, not just the domain.
   - Be polite, informative, assertive, objective, and brief.
   - Avoid jargon and explain any technical terms.
   - Never refer to past events as if they were happening now or in the future.
"""

    responder = (
        responder_start
        + """
5. If you think more information is necessary to fully answer the query, formulate questions about that encompasses the information you think is missing. These questions are going to be used by the system to retrieve the information. The user won't see them. Include these questions within <new_questions> tags, following this format:
    <new_questions>
        <question>[Your question here]</question>
        <question>[Your question here]</question>
        ...
        <type_search>[type_search]</type_search>
    </new_questions>
When formulating questions, adhere to these guidelines:
    - Try to divide the lack of information into the smallest possible parts
    - Make questions concise and not redundant
    - Focus on gathering information directly related to answering the user's query
    - Avoid unnecessary questions
    - Do not ask questions that you already know the answer to (considering the context and your previous knowledge)
    - Classify the search as one of the following types:
        - "factual": the default case, will search the definition of terms and concepts
        - "ocurrence": in the case of question about a specific event or ocurrence that happened
        - "recent": in the case of questions about recent events, the current state of something or the most recent information available

6. Format your entire response as follows:
   <knowledge_summary>
   [Your summary here, with in-text citations]

   References:
   [1] url
   [2] url
   ...
   </knowledge_summary>
   [Either the <new_questions> section if there's insufficient information, or:]

   <answer>
   [Your answer here, with in-text citations]

   References:
   [1] url
   [2] url
   ...
   </answer>

Remember to be helpful, polite, and informative while maintaining assertiveness, objectivity, and brevity in your response.
"""
    )

    final_responder = (
        responder_start
        + """
5. If you don't have enough information, start the <answer> tag with "I couldn't find all the information I wanted to provide a complete answer." And provide some context about the information you have, how it relates to the query and what you think is missing to properly answer the user's query.

6. Format your entire response as follows:
   <knowledge_summary>
   [Your summary here, with in-text citations]

   References:
   [1] url
   [2] url
   ...
   </knowledge_summary>

   <answer>
   [Your answer here, with in-text citations]

   References:
   [1] url
   [2] url
   ...
   </answer>

Remember to be helpful, polite, and informative while maintaining assertiveness, objectivity, and brevity in your response.
"""
    )

    preprocessor = f"""
You are a part of a helpful chatbot assistant system that provides information about {SCOPE}. Your task is to help responding to user input appropriately based on the following information and guidelines:

<user_input>
{{QUERY}}
</user_input>

<conversation_history>
{{conversation_history}}
</conversation_history>

First, determine if this input is within the scope of {SCOPE} and if you have enough information to answer it based on the conversation history.

If you are absolutely sure that the input has no relation with {SCOPE}, its forum or its documentation, respond with the following message within <answer> tags: "I'm sorry, but I can only answer questions about {SCOPE}. Is there anything specific about {SCOPE} you'd like to know?".

Most of the time, the user will ask a question related to {SCOPE}. If you are not 100% sure, don't discard the question. Some terms as "Cycle", "Airdrop", "Citizens' House", "Token House", "Grant", "Proposal", "Retro Funding" are related to {SCOPE}. If a person is referred to, it is likely to be a member of the Optimism Collective.

If the input is a simple interaction or you have all the necessary information in the conversation history to answer it, provide your response within <answer> tags. Don't make up information.

If you need additional information to answer the input accurately, do not use <answer> tags. Instead, follow these steps:

1. Analyze the conversation history to determine what the user seems to know well about {SCOPE}. Include this information within <user_knowledge> tags. If you can't assume any knowledge, return just <user_knowledge></user_knowledge>.

2. Formulate queries to allow gathering the necessary information to answer the user's input. These are going to be used by the system to retrieve the information. The user won't see them. The queries have two distinct parts: questions and keywords. You will also specify the type of search to be performed. Use the following format:

<queries>
    <question>[Your question here]</question>
    <question>[Your question here]</question>
    ...
    <keywords>[keyword 1], [keyword 2], ...</keywords>
    <type_search>[type_search]</type_search>
</queries>

When formulating questions, adhere to these guidelines:
- Try to divide the user's input into the smallest possible parts
- Search for the definition of terms linked to the user's input 
- If you are not sure, ask if the user's input is related to {SCOPE}
- Make questions concise and not redundant
- Focus on gathering information directly related to answering the user's input
- Avoid unnecessary questions
After formulating the questions, generate keywords that represent the points you have identified. 
- Add the name of the main concepts or topics that the questions are about. Every question is about {SCOPE}, so don't need to add it as a keyword. The keywords should be just specific terms.
- If the text mentions an occurrence or instance of something (very commonly adding a number at the end), sinalize it by using "#" followed by the number of the occurrence. For example, if the question mentions "Airdrop 3", use "Airdrop #3" as a keyword.
- If the text mentions an occurrence or instance of something, use only the specific term. For example, if the question mentions "Season 6", don't use "Season" as a keyword, use only "Season #3".
- If the question is about the general term, and doesn't mention any specific instance, use only the general term. For example, if the question is about "Cycle", use only " Voting Cycle" as a keyword.

The type of search can be one of the following:
- "factual": the default case, will search the definition of terms and concepts
- "ocurrence": in the case of question about a specific event or ocurrence that happened
- "recent": in the case of questions about recent events, the current state of something or the most recent information available
"""


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
        query: str | None = None,
        type_search: str = "factual",
        k: int = 3,
    ) -> Tuple[str, list]:
        contexts_to_be_explored = {}
        for question, contexts in question_context.items():
            new_contexts = [
                c for c in contexts if c.metadata.get("url") not in explored_contexts
            ]
            contexts_to_be_explored[question] = new_contexts

            if query is not None:
                k = min(k, len(new_contexts))
                if k > 0:
                    new_contexts = ContextHandling.reordering(
                        new_contexts, query, k=k, type_search=type_search
                    )

        c = contexts_to_be_explored.values()
        if len(c) > 0:
            max_c = max([len(cc) for cc in c])
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
    def reordering(context: list, query: str, k: int, type_search: str) -> list:
        if type_search == "factual" or type_search == "ocurrence":
            return context[:k]
        elif type_search == "recent":
            urls = [c.metadata["url"] for c in context]
            contexts = all_contexts_df[all_contexts_df["url"].isin(urls)].iloc[:k]
            return contexts.content.tolist()


class RetrieverBuilder:
    @staticmethod
    def build_faiss_retriever(
        dbs_name: List[str],
        **retriever_pars,
    ):
        db = connect_faiss.DatabaseLoader.load_db(dbs_name)
        return lambda query: db.similarity_search(query, **retriever_pars)

    @staticmethod
    def build_index(json_file, npz_file, k_max, treshold):
        embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

        with open(json_file, "r") as f:
            index = json.load(f)
        index_keys = list(index.keys())

        if treshold < 1 and treshold > 0:
            if not npz_file.suffix == ".npz":
                raise ValueError("npz_file must be a .npz file")
            with npz_file.open("rb") as f:
                index_embed = next(x for x in np.load(f).items())
            index_embed = index_embed[1]
            index_faiss = faiss.IndexFlatIP(index_embed.shape[1])
            index_faiss.add(index_embed)

        def find_similar(query: str, criteria: Callable = lambda x: x, **kwargs):
            if treshold < 1:
                if treshold > 0:
                    query_embed = np.array(embeddings.embed_documents([query]))
                    D, I = index_faiss.search(query_embed, k_max)

                    similar = [index_keys[i] for i in I[0]]
                    dists = D[0]

                    dists = [d for d in dists if d >= treshold]
                    similar = [s for s, d in zip(similar, dists) if d >= treshold]
                else:
                    similar = index_keys
            else:
                similar = [query]

            similar = criteria(similar)

            print(similar)
            urls = [u for s in similar for u in index[s]]

            contexts = all_contexts_df
            if "type_db_info" in kwargs:
                contexts = contexts[
                    contexts["type_db_info"].isin(kwargs["type_db_info"])
                ]
            contexts = contexts[contexts["url"].isin(urls)]

            return [contexts[contexts["url"] == u].content.tolist()[0] for u in urls]

        return find_similar

    @staticmethod
    def build_questions_index(k_max=2, treshold=0.9):
        return RetrieverBuilder.build_index(
            QUESTIONS_INDEX_JSON, QUESTIONS_INDEX_NPZ, k_max, treshold
        )

    @staticmethod
    def build_keywords_index(k_max=5, treshold=0.95):
        return RetrieverBuilder.build_index(
            KEYWORDS_INDEX_JSON, KEYWORDS_INDEX_NPZ, k_max, treshold
        )


class access_APIs:
    def get_llm(model: str = "gpt-4o-mini", **kwargs):
        if "gpt" in model:
            return ChatOpenAI(model=model, **kwargs)
        elif "claude" in model:
            return ChatAnthropic(model=model, **kwargs)
        else:
            raise ValueError(f"Model {model} not recognized")
