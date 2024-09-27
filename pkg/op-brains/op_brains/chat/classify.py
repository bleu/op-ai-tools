from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from typing import List, Tuple
from op_brains.summarizer.utils import Prompt, QuestionClassificationStructured
from op_brains.chat.apis import access_APIs


async def classify_question(question: str, thread: List = []) -> str:
    thread_content = Prompt.format_chat_thread(thread)
    full_prompt = Prompt.question_classifier.format(
        THREAD_CONTENT=thread_content, QUESTION_CONTENT=question
    )

    llm = access_APIs.get_llm(temperature=0, max_tokens=300)
    llm = llm.with_structured_output(QuestionClassificationStructured, strict=True)

    result = await llm.ainvoke(full_prompt)

    return result.dict()
