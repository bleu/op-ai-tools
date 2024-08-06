from typing import Tuple, Any, Callable, Iterable
import re, json, faiss, re
import numpy as np

from op_chat_brains.documents.optimism import (
    SummaryProcessingStrategy,
    FragmentsProcessingStrategy,
)
from op_chat_brains.chat import model_utils
from op_chat_brains.config import DOCS_PATH, SCOPE

from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic

MODEL_EMBEDDING = "text-embedding-ada-002"

prompt_question_generation = f"""
You are tasked with generating general questions that a non-specialist user might ask about a given fragment of text. The fragment is related to {{SCOPE}}. Your goal is to create questions that are relevant, interesting, and could realistically be asked by someone unfamiliar with the content.

Here is the fragment you will be working with:

<fragment>
{{CONTEXT}}
</fragment>

When generating questions, follow these criteria:
1. Questions should be relevant to the {{SCOPE}}.
2. Avoid questions that are too silly or unrelated to the main topic.
3. Ensure that the questions can be well-answered using the information provided in the fragment.
4. Avoid repetitive or overly specific questions.
5. Generate questions that a real user might actually ask without having read the text before.
6. Questions have to make sense independently. Do not refereence other questions.
7. Keep questions as atomic as possible, focusing on one concept or piece of information at a time. Avoid compound questions using 'and'.

Present your questions in the following format:
<questions>
<question>[Your question here]</question>
<question>[Your question here]</question>
<question>[Your question here]</question>
</questions>

Bad question example (DO NOT DO SOMETHING SIMILAR):
<question>What the script cited on the document does?</question> (This implies the user has read the document)
<question>

Additional guidelines:
- Aim to generate at least 3 questions, depending on the complexity and richness of the fragment.
- If the fragment doesn't contain enough substantial information, it's acceptable to generate fewer questions or even return an empty list.
- If the fragment information is unimportant or irrelevant, return an empty list.
- Questions don't need to refer the whole fragment, but they should be answerable based on the information provided.
- Focus on creating questions that encourage understanding and exploration of the main ideas presented in the fragment.
- Consider questions that ask about definitions, causes, effects, comparisons, or applications of concepts mentioned in the text.

Remember, your goal is to create questions that a non-specialist user would find interesting and relevant based on the given fragment. Do not make questions that require knowledge beyond what's provided in the text.
"""


def generate_question_index(list_contexts: Iterable, llm: Any) -> dict:
    index = {}
    for context in list_contexts:
        prompt = prompt_question_generation.format(
            CONTEXT=context.page_content, SCOPE=SCOPE
        )

        questions = llm.invoke(prompt).content

        xml_tag_pattern = re.compile(r"<(\w+)(\s[^>]*)?>(.*?)</\1>", re.DOTALL)
        xml_tags = xml_tag_pattern.findall(questions)
        tags = {tag[0]: tag[2] for tag in xml_tags}

        if "questions" in tags.keys():
            questions = tags["questions"]
            questions = [q[2] for q in xml_tag_pattern.findall(questions)]

            context.metadata["index_questions"] = questions

            print(questions)

            for q in questions:
                if q not in index:
                    index[q] = []
                index[q].append(context.metadata["url"])

    return list_contexts, index


def main(model: str):
    summary = SummaryProcessingStrategy.langchain_process(divide="category_name")
    summary = {f'summary_"{key}': value for key, value in summary.items()}

    fragments_loader = FragmentsProcessingStrategy()
    fragments = fragments_loader.process_document(DOCS_PATH, headers_to_split_on=[])

    data = {"documentation": fragments}
    data.update(summary)

    llm = model_utils.access_APIs.get_llm(model)
    embeddings = OpenAIEmbeddings(model=MODEL_EMBEDDING)

    questions_index = {}
    for key, value in data.items():
        list_contexts, index = generate_question_index(value, llm)

        questions_index[key] = index

        db = FAISS.from_documents(list_contexts, embeddings)
        db.save_local(f"dbs/{key}_db/faiss/{MODEL_EMBEDDING}")

    output_dict = {}
    for category, questions in questions_index.items():
        for question, urls in questions.items():
            for url in urls:
                if question not in output_dict:
                    output_dict[question] = []
                output_dict[question].append((url, category))

    with open("questions_index.json", "w") as f:
        json.dump(output_dict, f, indent=4)

    index_questions = list(output_dict.keys())
    index_questions_embed = np.array(embeddings.embed_documents(index_questions))

    # export
    np.save("questions_index.npy", index_questions_embed)


if __name__ == "__main__":
    main("gpt-4o-mini")
