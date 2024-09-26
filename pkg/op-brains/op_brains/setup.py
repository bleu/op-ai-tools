from op_brains.documents import DataExporter

from typing import Any, Iterable
import json
import re
import asyncio
import re
import random
import numpy as np

import op_artifacts
from op_brains.config import SCOPE, EMBEDDING_MODEL
import importlib.resources
from langchain_community.vectorstores import FAISS
from langchain_voyageai import VoyageAIRerank
import datetime as dt
from op_data.db.models import RawTopic
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from voyageai.error import RateLimitError
from voyageai.client import Client as VoyageClient

reranker_voyager = VoyageAIRerank(model="rerank-1")
lite_reranker_voyager = VoyageAIRerank(model="rerank-lite-1")
vo = VoyageClient()


prompt_question_generation = """
You are tasked with generating keywords and FAQ to help users to find information about {SCOPE}. Your goal is to create keywords that are useful and questions that are relevant, interesting, and could realistically be asked by someone unfamiliar with the content.

Here is the fragment you will be working with:

<fragment>
{CONTEXT}
</fragment>

{TYPE_GUIDELINES}

First, write some bullet points presenting the structure and content of the post. Try to mention the whole structure. They should be presented as:
<bullet_points>
- [Your bullet point here]
- [Your bullet point here]
- [Your bullet point here]
...
</bullet_points>

Then, generate keywords that represent the points you have identified. Try to always add the name of the concepts or topics that the question is about. Do not use too broad (for example, "Optimism") keywords. If the text mentions an occurrence or instance of something, use both the general term and the specific term. For example, if the question mentions "Airdrop 3", use both "Airdrop" and "Airdrop 3" as keywords.

Use the following format:
<keywords>
[Your keyword here], [Your keyword here], [Your keyword here], ...
</keywords>

Finally, generate questions, follow these criteria:
1. Questions should be relevant to the {SCOPE}.
2. Avoid questions that are too silly or unrelated to the main topic.
3. Ensure that the questions can be well-answered using the information provided in the fragment.
4. Avoid repetitive or overly specific questions.
5. Generate questions that a real user might actually ask without having read the text before.
6. Questions have to make sense independently. Do not refereence other questions.
7. Keep questions as atomic as possible, focusing on one concept or piece of information at a time. Avoid compound questions using 'and'.
8. Avoid questions that refer to information that can change over time, such as current events or statistics.

Present your questions in the following format:
<questions>
<question>[Your question here]</question> 
<question>[Your question here]</question>
<question>[Your question here]</question>
...
</questions>

Bad examples (not necessarily related to the fragment) (DO NOT DO SOMETHING SIMILAR):
<question>What the script cited on the document does?</question> (This implies the user has read the document)
<question>What the user example123 thinks about the OP distribution?</question> (This is too specific)
<question>What was discussed on the forum in december 2023?</question> (This is not relevant)
<question>When the proposal was made?</question> (This is too vague, there are many proposals)
<question>In which cycle are we?</question> (This information can change over time)
<question>What are the three principles recommended for making meaningful contributions to the Optimism Collective?</question> (This is too specific and not a question that an user would ask)

Good question examples (not necessarily related to the fragment):
<question>What is an Airdrop?</question>
<question>How a proposal is approved?</question>
<question>When the proposal about XYZ was made?</question>
<question>Was the proposal about XYZ approved?</question>
<question>When the voting cycle 5 started and ended?</question>
<question>How to make meaningful contributions to the Optimism Collective?</question>
<question>What is Optimism?</question>

Additional guidelines:
- Questions don't need to refer the whole fragment, but they should be answerable based on the information provided.
- Focus on creating questions that encourage understanding and exploration of the main ideas presented in the fragment.
- Consider questions that ask about definitions, causes, effects, comparisons, or applications of concepts mentioned in the text.
- Try to make questions as general as possible, that could be asked by anyone interested in the topic, without requiring specialized knowledge.

Remember, your goal is to create questions that a non-specialist user would find interesting and relevant based on the given fragment. Do not make questions that require knowledge beyond what's provided in the text.
"""


@retry(
    stop=stop_after_attempt(10),
    wait=wait_exponential(multiplier=1, min=10, max=320),
    retry=retry_if_exception_type(RateLimitError),
)
async def rate_limited_llm_invoke(llm, prompt):
    try:
        await asyncio.sleep(random.uniform(0.1, 0.5))  # Add some jitter
        return await llm.ainvoke(prompt)
    except Exception as e:
        if "429" in str(exception):
            raise RateLimitError(str(e))
        raise e


async def process_context(context, llm, semaphore):
    async with semaphore:  # Limit concurrency
        type_db = context.metadata["type_db_info"]

        if type_db == "docs_fragment":
            TYPE_GUIDELINES = "It is a post from the Optimism Governance Documentation. As the documentation is a place for official information, the content should be relevant and important. Try to encapsulate the whole content in your questions. Aim to generate at least 5 questions, depending on the complexity and richness of the fragment."
        elif type_db == "forum_thread_summary":
            TYPE_GUIDELINES = "It is a summary of a forum thread from the Optimism Governance Forum. As the forum is a place for community discussion, the content may vary. If you understand that the content is unimportant or irrelevant, return <nothing>."

        prompt = prompt_question_generation.format(
            CONTEXT=context.page_content, SCOPE=SCOPE, TYPE_GUIDELINES=TYPE_GUIDELINES
        )

        try:
            out = await rate_limited_llm_invoke(llm, prompt)
            return out.content, context.metadata["url"]
        except RateLimitError as e:
            print(f"Rate limit exceeded after all retries. Error: {str(e)}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            raise


async def generate_indexes_from_fragment(
    list_contexts: Iterable, llm: Any, max_concurrency=20
) -> dict:
    kw_index = {}
    q_index = {}

    semaphore = asyncio.Semaphore(max_concurrency)
    tasks = [process_context(context, llm, semaphore) for context in list_contexts]
    results = await asyncio.gather(*tasks)

    for out, url in results:
        xml_tag_pattern = re.compile(r"<(\w+)(\s[^>]*)?>(.*?)</\1>", re.DOTALL)
        xml_tags = xml_tag_pattern.findall(out)
        tags = {tag[0]: tag[2] for tag in xml_tags}

        if "questions" in tags:
            questions = [
                (q[2], q[1]) for q in xml_tag_pattern.findall(tags["questions"])
            ]
            for q in questions:
                q = q[0]
                q_index.setdefault(q, []).append(url)

        if "keywords" in tags:
            keywords = [k.strip().lower() for k in tags["keywords"].split(",")]
            keywords = [re.sub(r"[^\w\s]", "", k) for k in keywords]
            for k in keywords:
                kw_index.setdefault(k, []).append(url)

        print("done for ", url)

    return q_index, kw_index


async def reorder_index(index_dict, updated_urls=[]):
    all_contexts_df = await DataExporter.get_dataframe(only_not_embedded=False)
    output_dict = {}

    semaphore = asyncio.Semaphore(15)

    @retry(
        stop=stop_after_attempt(15),
        wait=wait_exponential(multiplier=1, min=15, max=320),
        retry=retry_if_exception_type(RateLimitError),
    )
    async def rate_limited_reranker(query, documents, check_count=False):
        reranker = reranker_voyager
        if check_count:
            count = vo.count_tokens([doc.page_content for doc in documents], "rerank-1")
            if count > 100000:
                reranker = lite_reranker_voyager

        return await reranker.acompress_documents(query=query, documents=documents)

    async def process_key(key, urls):
        async with semaphore:
            if any(
                url in updated_urls for url in urls
            ):  # Check if the URLs are updated
                contexts = all_contexts_df[
                    all_contexts_df["url"].isin(urls)
                ].content.tolist()
                k = len(contexts)
                if k > 1:
                    try:
                        check_count = True if k > 250 else False
                        contexts = await rate_limited_reranker(
                            query=key, documents=contexts, check_count=check_count
                        )
                        urls = [context.metadata["url"] for context in contexts]
                    except Exception as e:
                        print(f"Keu: {key} Error: {str(e)}")

            return key, urls

    tasks = [process_key(key, urls) for key, urls in index_dict.items()]
    results = await asyncio.gather(*tasks)
    for key, urls in results:
        output_dict[key] = urls
    return output_dict
