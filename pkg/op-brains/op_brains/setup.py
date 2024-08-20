from op_brains.documents import DataExporter

from typing import Any, Iterable
import json
import re
import numpy as np

import op_artifacts
from op_brains.chat import model_utils
from op_brains.config import SCOPE, EMBEDDING_MODEL
import importlib.resources
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_voyageai import VoyageAIRerank

reranker_voyager = VoyageAIRerank(model="rerank-1")
all_contexts_df = DataExporter.get_dataframe()


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


def generate_indexes_from_fragment(list_contexts: Iterable, llm: Any) -> dict:
    kw_index = {}
    q_index = {}
    for context in list_contexts:
        type_db = context.metadata["type_db_info"]

        if type_db == "docs_fragment":
            TYPE_GUIDELINES = "It is a post from the Optimism Governance Documentation. As the documentation is a place for official information, the content should be relevant and important. Try to encapsulate the whole content in your questions. Aim to generate at least 5 questions, depending on the complexity and richness of the fragment."
        if type_db == "forum_thread_summary":
            TYPE_GUIDELINES = "It is a summary of a forum thread from the Optimism Governance Forum. As the forum is a place for community discussion, the content may vary. If you understand that the content is unimportant or irrelevant, return <nothing>."

        prompt = prompt_question_generation.format(
            CONTEXT=context.page_content, SCOPE=SCOPE, TYPE_GUIDELINES=TYPE_GUIDELINES
        )

        out = llm.invoke(prompt).content

        xml_tag_pattern = re.compile(r"<(\w+)(\s[^>]*)?>(.*?)</\1>", re.DOTALL)
        xml_tags = xml_tag_pattern.findall(out)
        tags = {tag[0]: tag[2] for tag in xml_tags}

        if "questions" in tags.keys():
            questions = tags["questions"]
            questions = [(q[2], q[1]) for q in xml_tag_pattern.findall(questions)]

            for q in questions:
                q = q[0]
                if q not in q_index:
                    q_index[q] = []
                q_index[q].append(context.metadata["url"])
                print(q, q_index[q])

        if "keywords" in tags.keys():
            keywords = tags["keywords"]
            keywords = [k.strip().lower() for k in keywords.split(",")]
            keywords = [re.sub(r"[^\w\s]", "", k) for k in keywords]

            for k in keywords:
                if k not in kw_index:
                    kw_index[k] = []
                kw_index[k].append(context.metadata["url"])
                print(k, kw_index[k])

    return q_index, kw_index


def reorder_index(index_dict):
    output_dict = {}
    for key, urls in index_dict.items():
        print(key)
        print(urls)
        contexts = all_contexts_df[all_contexts_df["url"].isin(urls)].content.tolist()
        k = len(contexts)
        if k > 1:
            contexts = reranker_voyager.compress_documents(
                query=key, documents=contexts
            )
            urls = [context.metadata["url"] for context in contexts]
            print(urls)
        output_dict[key] = urls

    return output_dict


def reorder_file(path):
    with open(path, "r") as f:
        index = json.load(f)
    index = reorder_index(index)
    with open(path, "w") as f:
        json.dump(index, f, indent=4)


def main(model: str):
    data = DataExporter.get_langchain_documents()

    llm = model_utils.access_APIs.get_llm(model)
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    questions_index = {}
    keywords_index = {}
    for db_name, contexts in data.items():
        db = FAISS.from_documents(contexts, embeddings)
        db.save_local(f"dbs/{db_name}_db/faiss/{EMBEDDING_MODEL}")

        q_index, kw_index = generate_indexes_from_fragment(contexts, llm)

        for q, urls in q_index.items():
            if q not in questions_index:
                questions_index[q] = []
            questions_index[q].extend(urls)

        for k, urls in kw_index.items():
            if k not in keywords_index:
                keywords_index[k] = []
            keywords_index[k].extend(urls)

    op_artifacts_pkg = importlib.resources.files(op_artifacts)
    with open(op_artifacts_pkg.joinpath("index_questions.json"), "w") as f:
        json.dump(questions_index, f, indent=4)
    index_questions = list(questions_index.keys())
    index_questions_embed = np.array(embeddings.embed_documents(index_questions))
    np.savez_compressed(
        op_artifacts_pkg.joinpath("index_questions.npz"), index_questions_embed
    )

    with open(op_artifacts_pkg.joinpath("index_keywords.json"), "w") as f:
        json.dump(keywords_index, f, indent=4)
    index_keywords = list(keywords_index.keys())
    index_keywords_embed = np.array(embeddings.embed_documents(index_keywords))
    np.savez_compressed(
        op_artifacts_pkg.joinpath("index_keywords.npz"), index_keywords_embed
    )

    reorder_file(op_artifacts_pkg.joinpath("index_questions.json"))
    reorder_file(op_artifacts_pkg.joinpath("index_keywords.json"))


if __name__ == "__main__":
    main("gpt-4o-mini")
