from typing import Tuple
import time, json, faiss, re
import numpy as np
import pandas as pd

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from ragatouille import RAGPretrainedModel

TODAY = time.strftime("%Y-%m-%d")
scope="Optimism Governance/Optimism Collective/Optimism L2"
source="Optimism Governance Forum"

class Prompt:
    responder = f"""
You are a helpful assistant that provides information about {scope}. Your goal is to give polite, informative, assertive, objective, and brief answers. Avoid jargon and explain any technical terms, as the user may not be a specialist.

An user inserted the following query:
<query>
{{QUERY}}
<query>

You have the following context information, retrieved from the {source}:
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

2. Summarize the information you have, from the context and your previous knowledge, that is relevant to the user's query. Include this summary inside <knowledge_summary></knowledge_summary> tags. Cite the source URL using the format [1] within the text and list the url references at the end.

3. Check if you have enough information to answer the user's query. 

4. If you have enough information to respond at least partially the question, provide an answer inside <answer></answer> tags. Your answer should:
   - Directly address the user's question without saying "according to the context", "based on the provided context" or similar phrases.
   - Cite the source URL using the format [1] within the text.
   - List the url references at the end of the answer.
   - Be polite, informative, assertive, objective, and brief.
   - Avoid jargon and explain any technical terms.

5. Some questions can have a temporal aspect. If the user's query is about information that can change over time (e.g. "Is the Governance Fund grant application currently being processed?", "Who is the leader of mission grants right now?", "What was the last proposal that was approved?", "When will the next Cycle end?"), mention the date of the information. If the contexts are contradictory, provide the most recent information.

5. If you think more information is necessary to fully answer the query, formulate questions about that encompasses the information you think is missing. These questions are going to be used by the system to retrieve the information. The user won't see them. Include these questions within <new_questions> tags, following this format:
    <new_questions>
        <question type="[question_type]">[Your question here]</question>
        <question type="[question_type]">[Your question here]</question>
    </new_questions>
When formulating questions, adhere to these guidelines:
    - Try to divide the lack of information into the smallest possible parts
    - Make questions concise and not redundant
    - Focus on gathering information directly related to answering the user's query
    - Avoid unnecessary questions
    - Do not ask questions that you already know the answer to
    - Classify each question as one of the following types: factual, temporal or other.

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

    final_responder = f"""
You are a helpful assistant that provides information about {scope}. Your goal is to give polite, informative, assertive, objective, and brief answers. Avoid jargon and explain any technical terms, as the user may not be a specialist.

An user inserted the following query:
<query>
{{QUERY}}
<query>

You have the following context information, retrieved from the {source}:
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

2. Summarize the information you have, from the context and your previous knowledge, that is relevant to the user's query. Include this summary inside <knowledge_summary></knowledge_summary> tags. Cite the source URL using the format [1] within the text and list the url references at the end.

3. Check if you have enough information to answer the user's query. 

4. If you have enough information to respond at least partially the question, provide an answer inside <answer></answer> tags. Your answer should:
   - Directly address the user's question without saying "according to the context", "based on the provided context" or similar phrases.
   - Cite the source URL using the format [1] within the text.
   - List the url references at the end of the answer.
   - Be polite, informative, assertive, objective, and brief.
   - Avoid jargon and explain any technical terms.

5. Some questions can have a temporal aspect. If the user's query is about information that can change over time (e.g. "Is the Governance Fund grant application currently being processed?", "Who is the leader of mission grants right now?", "What was the last proposal that was approved?", "When will the next Cycle end?"), mention the date of the information. If the contexts are contradictory, provide the most recent information.

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
    
    preprocessor = f"""
You are a part of a helpful chatbot assistant system that provides information about {scope}. Your task is to help responding to user queries appropriately based on the given information and guidelines. You will return <answer> tags with the response to the user or <user_knowledge> and <questions> tags so the system can retrieve more information to properly answer the query.

<user_query>
{{query}}
</user_query>

<conversation_history>
{{conversation_history}}
</conversation_history>

First, determine if this query is within the scope of {scope} and if you have enough information to answer it based on the conversation history.

If you are absolutely sure that the query has no relation with {scope}, its forum or its documentation, respond with the following message within <answer> tags:
"I'm sorry, but I can only answer questions about {scope}. Is there anything specific about {scope} you'd like to know?". Most of the time, the user will ask a question related to {scope}. If you are not 100% sure, ask for more information. 

If the query is a simple interaction or you have all the necessary information in the conversation history to answer it, provide your response within <answer> tags. You have access to the Optimism Governance Forum and the Optimism Governance Documentation so don't make up information.

If you need additional information to answer the query accurately, do not use <answer> tags. Instead, follow these steps:

1. Analyze the conversation history to determine what the user seems to know well about {scope}. Include this information within <user_knowledge> tags. If you can't assume any knowledge, return just <user_knowledge></user_knowledge>.

2. Formulate questions that will help you gather the necessary information to answer the user's query. These questions are going to be used by the system to retrieve the information. The user won't see them. Include these questions within <questions> tags, following this format:

<questions>
    <question type="[question_type]">[Your question here]</question>
    <question type="[question_type]">[Your question here]</question>
</questions>

When formulating questions, adhere to these guidelines:
- Try to divide the user's query into the smallest possible parts
- Search for the definition of terms linked to the user's query 
- Make questions concise and not redundant
- Focus on gathering information directly related to answering the user's query
- Avoid unnecessary questions
- Classify each question as one of the following types:
  - factual: for questions about concepts or established facts. (e.g., "What is the Token House?", "What are the Retroactive Public Goods Funding?", "What is the Optimism Governance Forum?")
  - temporal: for questions about information that changes over time. (e.g., "Is the Governance Fund grant application currently being processed?", "Who is the leader of mission grants right now?", "What was the last proposal that was approved?", "When will the next Cycle end?")
  - other: for questions that don't fit the above categories

Remember, your goal is to provide accurate and helpful information about {scope} while staying within the defined scope and gathering necessary information when required.
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
    def filter(context_dict:dict, explored_contexts:list, query:str|None = None, k:int = 5) -> Tuple[str, list]:
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
                    out.append(ContextHandling.summary_template.format(
                        TITLE = c.metadata["thread_title"],
                        CREATED_AT = c.metadata["created_at"],
                        LAST_POST_AT = c.metadata["last_posted_at"],
                        URL = c.metadata["url"],
                        CONTENT = c.page_content
                    ))
                case _:
                    pass

        urls = [url for url in urls if context_dict[url] in context]
        return "".join(out), urls
    
    @staticmethod
    def reordering(context:list, query:str, k:int = 5) -> list:
        return context[:k]



def load_db(dbs, model_embeddings, vectorstore = 'faiss'):
    embeddings = OpenAIEmbeddings(model=model_embeddings)
    if vectorstore == 'faiss':
        dbs = [f"dbs/{name}_db/faiss/{model_embeddings}" for name in dbs]
        dbs = [FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True) for db_path in dbs]
        db = dbs[0]
        for db_ in dbs[1:]:
            db.merge_from(db_)
    
    return db

def build_retriever(dbs_name, embeddings_name, **retriever_pars):
    db = load_db(dbs_name, embeddings_name)
    return lambda query : db.similarity_search(query, **retriever_pars)


from op_chat_brains.documents.optimism import SummaryProcessingStrategy, FragmentsProcessingStrategy
SUMMARY_PATH = "../../data/summaries/all_thread_summaries.txt"
FORUM_PATH = "../../data/002-governance-forum-202406014/dataset/_out.jsonl"
DOCS_PATH = "../../data/001-initial-dataset-governance-docs/file.txt"
def load_data() -> Tuple:
    summary = SummaryProcessingStrategy.process_document(SUMMARY_PATH, FORUM_PATH, divide="board_name")
    summary = {f'summary {key}': value for key, value in summary.items()}
    fragments_loader = FragmentsProcessingStrategy()
    fragments = fragments_loader.process_document(DOCS_PATH, headers_to_split_on=[])

    data = {"governance documentation": fragments}
    data.update(summary)
    return data


def build_index(index, embeddings_name, k_max = 10, treshold = 0.9):
    embeddings = OpenAIEmbeddings(model=embeddings_name)

    # load json index
    with open(index, "r") as f:
        index = json.load(f)
    
    index_questions = list(index.keys())
    index_questions_embed = np.array(embeddings.embed_documents(index_questions))
    index_faiss = faiss.IndexFlatIP(index_questions_embed.shape[1])
    index_faiss.add(index_questions_embed)

    data = load_data()
    context_df = []
    for key, value in data.items():
        k = key.strip().replace(" ", "_").replace('"', "").lower()
        pattern = r'[^A-Za-z0-9_]+'
        k = re.sub(pattern, '', k)

        for context in value:
            url = context.metadata['url']
            content = context
            context_df.append((url, content))
    context_df = pd.DataFrame(context_df, columns=["url", "content"])

    def find_similar_questions(query):
        query_embed = np.array(embeddings.embed_documents([query]))
        D, I = index_faiss.search(query_embed, k_max)

        similar_questions = [index_questions[i] for i in I[0]]
        dists = D[0]

        dists = [d for d in dists if d >= treshold]
        similar_questions = [q for q, d in zip(similar_questions, dists) if d >= treshold]

        return similar_questions

    def find_contexts(query):
        similar_questions = find_similar_questions(query)
        urls = [index[q] for q in similar_questions]
        urls = [x[0] for xs in urls for x in xs]

        contexts = context_df[context_df["url"].isin(urls)]
        content = contexts["content"].tolist()
        return content

    return find_contexts

