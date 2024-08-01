from typing import Tuple, Any, Callable, Iterable
import re, json, faiss, re
import numpy as np

from op_chat_brains.documents.optimism import SummaryProcessingStrategy, FragmentsProcessingStrategy
from op_chat_brains.chat import model_utils
from op_chat_brains.config import (
    DOCS_PATH,
    SCOPE,
    EMBEDDING_MODEL
)

from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic



prompt_question_generation = f"""
You are tasked with generating general questions that a non-specialist user might ask about a given fragment of text. The fragment is related to {{SCOPE}}. Your goal is to create questions that are relevant, interesting, and could realistically be asked by someone unfamiliar with the content.

Here is the fragment you will be working with.:

<fragment>
{{CONTEXT}}
</fragment>

{{TYPE_GUIDELINES}}

Before generating questions, write some bullet points summarizing the structure and content of the post. When generating questions, consider the main topics and concepts covered in. They should be presented as:
<bullet_points>
- [Your bullet point here]
- [Your bullet point here]
- [Your bullet point here]
...
</bullet_points>

When generating questions, follow these criteria:
1. Questions should be relevant to the {{SCOPE}}.
2. Avoid questions that are too silly or unrelated to the main topic.
3. Ensure that the questions can be well-answered using the information provided in the fragment.
4. Avoid repetitive or overly specific questions.
5. Generate questions that a real user might actually ask without having read the text before.
6. Questions have to make sense independently. Do not refereence other questions.
7. Keep questions as atomic as possible, focusing on one concept or piece of information at a time. Avoid compound questions using 'and'.
8. Avoid questions that refer to information that can change over time, such as current events or statistics.
9. Add keywords to your questions to help categorize them for future reference. Try to always add the name of the concepts or topics that the question is about. Do not use too broad (for example, "Optimism") or too specific keywords. If the question mentions an occurrence or instance of something, use both the general term and the specific term. For example, if the question mentions "Airdrop 3", use both "Airdrop" and "Airdrop 3" as keywords.

Present your questions in the following format:
<questions>
<question keywords="[your keywords, separated by commas]">[Your question here]</question> 
<question keywords="[your keywords, separated by commas]">[Your question here]</question>
<question keywords="[your keywords, separated by commas]">[Your question here]</question>
...
</questions>

Bad examples (not necessarily related to the fragment) (DO NOT DO SOMETHING SIMILAR):
<question keywords="">What the script cited on the document does?</question> (This implies the user has read the document)
<question keywords="OP distribution">What the user example123 thinks about the OP distribution?</question> (This is too specific)
<question keywords="forum, december 2023">What was discussed on the forum in december 2023?</question> (This is not relevant)
<question keywords="proposal">When the proposal was made?</question> (This is too vague, there are many proposals)
<question keywords="cycle">In which cycle are we?</question> (This information can change over time)
<question keywords="contributing, Optimism Collective">What are the three principles recommended for making meaningful contributions to the Optimism Collective?</question> (This is too specific and not a question that an user would ask)
<question keywords="Optimism">What is Optimism?</question> (The question is ok, the keyword is too broad)

Good question examples (not necessarily related to the fragment):
<question keywords="Airdrop">What is an Airdrop?</question>
<question keywords="proposal">How a proposal is approved?</question>
<question keywords="proposal, proposal XYZ">When the proposal about XYZ was made?</question>
<question keywords="proposal, proposal XYZ">Was the proposal about XYZ approved?</question>
<question keywords="voting cycle, voting cycle 5">When the voting cycle 5 started and ended?</question>
<question keywords="contributing, Optimism Collective">How to make meaningful contributions to the Optimism Collective?</question>
<question keywords="">What is Optimism?</question>

Additional guidelines:
- Questions don't need to refer the whole fragment, but they should be answerable based on the information provided.
- Focus on creating questions that encourage understanding and exploration of the main ideas presented in the fragment.
- Consider questions that ask about definitions, causes, effects, comparisons, or applications of concepts mentioned in the text.
- Try to make questions as general as possible, that could be asked by anyone interested in the topic, without requiring specialized knowledge.

Remember, your goal is to create questions that a non-specialist user would find interesting and relevant based on the given fragment. Do not make questions that require knowledge beyond what's provided in the text.
"""


def generate_question_index(list_contexts : Iterable, llm : Any) -> dict:
    index = {}
    for context in list_contexts:
        type_db = context.metadata['type_db_info']

        if type_db == "docs_fragment":
            TYPE_GUIDELINES = "It is a post from the Optimism Governance Documentation. As the documentation is a place for official information, the content should be relevant and important. Try to encapsulate the whole content in your questions. Aim to generate at least 5 questions, depending on the complexity and richness of the fragment."
        if type_db == "forum_thread_summary":
            TYPE_GUIDELINES = "It is a summary of a forum thread from the Optimism Governance Forum. As the forum is a place for community discussion, the content may vary. If you understand that the content is unimportant or irrelevant, return <nothing>."

        prompt = prompt_question_generation.format(
            CONTEXT=context.page_content,
            SCOPE=SCOPE,
            TYPE_GUIDELINES=TYPE_GUIDELINES
        )

        questions = llm.invoke(prompt).content

        xml_tag_pattern = re.compile(r"<(\w+)(\s[^>]*)?>(.*?)</\1>", re.DOTALL)
        xml_tags = xml_tag_pattern.findall(questions)
        tags = {tag[0]: tag[2] for tag in xml_tags}
        
        if "questions" in tags.keys():
            questions = tags["questions"]
            questions = [(q[2],q[1]) for q in xml_tag_pattern.findall(questions)]

            context.metadata["index_questions"] = questions

            for q in questions:
                keyw = q[1].split("=")[1].replace('"', '').split(",")
                keyw = [k.strip() for k in keyw]
                q = q[0]
                if q not in index:
                    index[q] = []
                index[q].extend([
                    context.metadata['url'],
                    keyw
                ])

                print(q, index[q])
            
    return list_contexts, index

def main(model:str):
    summary = SummaryProcessingStrategy.langchain_process(divide='category_name')
    summary = {f'summary_"{key}': value for key, value in summary.items()}

    fragments_loader = FragmentsProcessingStrategy()
    fragments = fragments_loader.process_document(DOCS_PATH, headers_to_split_on=[])

    data = {"documentation": fragments}
    data.update(summary)

    llm = model_utils.access_APIs.get_llm(model)
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    
    questions_index = {}
    for key, value in data.items():
        list_contexts, index = generate_question_index(value, llm)

        questions_index[key] = index

        db = FAISS.from_documents(list_contexts, embeddings)
        db.save_local(f"dbs/{key}_db/faiss/{EMBEDDING_MODEL}")

    output_dict = {}
    for category, questions in questions_index.items():
        for question, outs in questions.items():
            if question not in output_dict:
                output_dict[question] = []
            outs.append(category)
            output_dict[question].append(outs)


    with open("index/questions.json", "w") as f:
        json.dump(output_dict, f, indent=4)

    index_questions = list(output_dict.keys())
    index_questions_embed = np.array(embeddings.embed_documents(index_questions))

    # export
    np.save("index/questions.npy", index_questions_embed)

    keyws_index = {}
    for question, outs in output_dict.items():
        keyws = [o[1] for o in outs]
        keyws = set([k for sublist in keyws for k in sublist])
        for k in keyws:
            if k not in keyws_index:
                keyws_index[k] = []
            keyws_index[k].append(question)

    with open("index/keywords.json", "w") as f:
        json.dump(keyws_index, f, indent=4)
        
if __name__ == "__main__":
    main("gpt-4o-mini")