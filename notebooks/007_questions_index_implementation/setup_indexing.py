from typing import Tuple, Any, Callable, Iterable
import re, json

from op_chat_brains.documents.optimism import SummaryProcessingStrategy, FragmentsProcessingStrategy
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic


MODEL_EMBEDDING = "text-embedding-ada-002"

SUMMARY_PATH = "../../data/summaries/all_thread_summaries.txt"
FORUM_PATH = "../../data/002-governance-forum-202406014/dataset/_out.jsonl"
DOCS_PATH = "../../data/001-initial-dataset-governance-docs/file.txt"

def get_llm(model:str = "gpt-4o-mini"):
    if "gpt" in model:
        llm = ChatOpenAI(model=model)
    elif "claude" in model:
        llm = ChatAnthropic(model=model)
    else:
        raise ValueError(f"Model {model} not recognized")
    return llm


def load_data(SUMMARY_PATH: str, FORUM_PATH: str, DOCS_PATH: str) -> Tuple:
    summary = SummaryProcessingStrategy.langchain_process(divide='category_name')
    summary = {f'summary of a forum thread from "{key}" board at the optimism governance forum': value for key, value in summary.items()}
    fragments_loader = FragmentsProcessingStrategy()
    fragments = fragments_loader.process_document(DOCS_PATH, headers_to_split_on=[])

    data = {"governance documentation": fragments}
    data.update(summary)
    return data

prompt_question_generation = f"""
You are tasked with generating general questions that a non-specialist user might ask about a given fragment of text. The fragment is related to a specific type and scope, which will be provided. Your goal is to create questions that are relevant, interesting, and could realistically be asked by someone unfamiliar with the content.

Here is the fragment you will be working with:

<fragment>
{{CONTEXT}}
</fragment>

This fragment is from {{TYPE}} and is related to {{SCOPE}}.

When generating questions, follow these criteria:
1. Questions should be relevant to the {{SCOPE}} mentioned in the fragment.
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

Here are examples of good and bad questions:

Good question example:
<question>What are the main factors contributing to [topic explained in the fragment]?</question>

Bad question example:
<question>What is the author's favorite color?</question> (This is unrelated to the content and too silly)

Additional guidelines:
- Aim to generate at least 3 questions, depending on the complexity and richness of the fragment.
- If the fragment doesn't contain enough substantial information, it's acceptable to generate fewer questions or even return an empty list.
- If the fragment information is unimportant or irrelevant, return an empty list.
- Focus on creating questions that encourage understanding and exploration of the main ideas presented in the fragment.
- Consider questions that ask about definitions, causes, effects, comparisons, or applications of concepts mentioned in the text.

Remember, your goal is to create questions that a non-specialist user would find interesting and relevant based on the given fragment. Avoid questions that require knowledge beyond what's provided in the text.
</questions>
"""
def generate_question_index(list_contexts : Iterable, llm : Any, type_contexts : str) -> dict:
    index = {}
    
    for context in list_contexts:
        prompt = prompt_question_generation.format(
            CONTEXT=context.page_content,
            TYPE=type_contexts.upper(),
            SCOPE="OPTIMISM GOVERNANCE"
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
                index[q].append(context.metadata['url'])

            
    return list_contexts, index

def main(model:str):
    data = load_data(SUMMARY_PATH, FORUM_PATH, DOCS_PATH)
    llm = get_llm(model)
    
    questions_index = {}
    for key, value in data.items():
        list_contexts, index = generate_question_index(value, llm, key)

        k = key.replace("of a forum thread from ", "").replace(" board at the optimism governance forum", "").strip().replace(" ", "_").replace('"', "").lower()
        pattern = r'[^A-Za-z0-9_]+'
        k = re.sub(pattern, '', k)

        questions_index[k] = index

        embeddings = OpenAIEmbeddings(model=MODEL_EMBEDDING)
        db = FAISS.from_documents(list_contexts, embeddings)
        db.save_local(f"dbs/{k}_db/faiss/{MODEL_EMBEDDING}")

    output_dict = {}
    for category, questions in questions_index.items():
        for question, urls in questions.items():
            for url in urls:
                if question not in output_dict:
                    output_dict[question] = []
                output_dict[question].append((url, category))

    with open("questions_index.json", "w") as f:
        json.dump(output_dict, f, indent=4)
        
if __name__ == "__main__":
    main("gpt-4o-mini")