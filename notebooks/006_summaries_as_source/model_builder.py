from typing import Iterator, List, Dict, Any, Callable, Tuple
import os, re
from datetime import date

TODAY = date.today()

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_anthropic import ChatAnthropic
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
import weave


def load_db(dbs, model_embeddings, vectorstore="faiss"):
    embeddings = OpenAIEmbeddings(model=model_embeddings)
    if vectorstore == "faiss":
        dbs = [f"dbs/{name}_db/faiss/{model_embeddings}" for name in dbs]
        dbs = [
            FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
            for db_path in dbs
        ]
        db = dbs[0]
        for db_ in dbs[1:]:
            db.merge_from(db_)

    return db


@weave.op()
def build_retriever(dbs_name, embeddings_name, retriever_pars={}):
    db = load_db(dbs_name, embeddings_name)

    retriever = db.as_retriever(**retriever_pars)

    return retriever


class TemplateLLM:
    summay = """
<summary_from_forum_post>
<title>{TITLE}</title>
<created_at>{CREATED_AT}</created_at>
<last_posted_at>{LAST_POST_AT}</last_posted_at>
<context_url>{URL}</context_url>

<content>{CONTENT}</content>
</summary_from_forum_post>

"""


def RAG_model(structure_name: str, **kwargs):
    structures = structure_name.split("-")

    class RAGModel(weave.Model):
        structure_str: str = structure_name

        dbs_name: List
        embeddings_name: str

        prompt_template: Callable
        final_prompt_template: Callable
        chat_pars: Dict[str, Any]

        retriever_pars: Dict | List

        reasoning_limit: int

        # placeholders
        llm: Any = None
        structures: List = None
        retriever: Any = None
        reasoning_level: int = 0
        reasoning_history: List = []

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            if "openai" in structures:
                self.llm = ChatOpenAI(**self.chat_pars)
            elif "claude" in structures:
                self.llm = ChatAnthropic(**self.chat_pars)

            if "multi_retriever" in structures:
                self.retriever = self.multi_retriever
            else:
                self.retriever = self.single_retriever

        def single_retriever(self, question: str):
            retriever = build_retriever(
                self.dbs_name, self.embeddings_name, self.retriever_pars
            )
            context = retriever.invoke(question)
            context = {"-".join(self.dbs_name): context}

            return context

        def multi_retriever(self, question: str):
            retrievers = {}
            for name, retriever_pars in self.retriever_pars.items():
                retriever = build_retriever(
                    [name], self.embeddings_name, retriever_pars
                )
                retrievers[name] = retriever

            context = {}
            for name, retriever in retrievers.items():
                context[name] = retriever.invoke(question)

            return context

        def contextual_compression(self, retriever, question: str):
            compressor = LLMChainExtractor.from_llm(self.llm)
            compression_retriever = ContextualCompressionRetriever(
                base_compressor=compressor, base_retriever=retriever
            )
            context = compression_retriever.invoke(question)

            return context

        def answer(self, context: str, question: str, prompt=None):
            if prompt is None:
                prompt = self.prompt_template
            response = self.llm.invoke(prompt(context=context, question=question))

            return response.content

        def single_reasoning(self, question, original_question):
            self.reasoning_level += 1
            context = self.retriever(question)
            str_context = ""
            if "summaries" in context:
                for r in context["summaries"]:
                    str_context += TemplateLLM.summay.format(
                        TITLE=r.metadata["thread_title"],
                        URL=r.metadata["url"],
                        CREATED_AT=r.metadata["created_at"],
                        LAST_POST_AT=r.metadata["last_posted_at"],
                        CONTENT=r.page_content,
                    )
                if not question == original_question:
                    question = f"<original_question>{original_question}</original_question> \n\n <some_aspects_to_may_consider>{question}</some_aspects_to_may_consider>"
                    # question = original_question
                if self.reasoning_level > self.reasoning_limit:
                    answer = self.answer(
                        str_context, question, self.final_prompt_template
                    )
                else:
                    answer = self.answer(str_context, question)
                return context, answer

        @weave.op()
        def predict(self, question: str):
            self.reasoning_history = []
            self.reasoning_level = 0
            out = self.internal_reasoning(question)
            return {"reasoning_history": self.reasoning_history, "final_answer": out}

        def internal_reasoning(self, question, original_question=None):
            if original_question is None:
                original_question = question

            context, answer = self.single_reasoning(question, original_question)

            xml_tag_pattern = re.compile(r"<(\w+)>(.+?)</\1>", re.DOTALL)
            xml_tags = xml_tag_pattern.findall(answer)
            tags = [tag[0] for tag in xml_tags]

            out = {"context": context, "answer": answer}
            if "answer" in tags:
                return out
            else:
                self.reasoning_history.append(out)
                new_question = "\n".join([tag[1] for tag in xml_tags])
                if "need_to_know" in tags:
                    if self.reasoning_level > self.reasoning_limit:
                        return {"context": context, "answer": answer}
                    else:
                        return self.internal_reasoning(new_question, original_question)

    return RAGModel(**kwargs)
