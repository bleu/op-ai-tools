from typing import Tuple, Any, Callable
from op_chat_brains.chat import model_utils

import re


class RAGModel:
    REASONING_LIMIT: int
    models_to_use: list
    index_retriever: Callable
    factual_retriever: Callable
    temporal_retriever: Callable
    context_filter: Callable
    system_prompt_preprocessor: str
    system_prompt_responder: str
    system_prompt_final_responder: str

    llm: list = []
    number_of_models: int = 2

    def __init__(self, **kwargs):
        self.REASONING_LIMIT = kwargs.get("REASONING_LIMIT", 3)
        self.models_to_use = kwargs.get("models_to_use")
        self.index_retriever = kwargs.get("index_retriever")
        self.factual_retriever = kwargs.get("factual_retriever")
        self.temporal_retriever = kwargs.get("temporal_retriever")
        self.context_filter = kwargs.get("context_filter")
        self.system_prompt_preprocessor = kwargs.get("system_prompt_preprocessor")
        self.system_prompt_responder = kwargs.get("system_prompt_responder")
        self.system_prompt_final_responder = kwargs.get("system_prompt_final_responder")

        assert len(self.models_to_use) == self.number_of_models

        for m in self.models_to_use:
            m, pars = m
            self.llm += [model_utils.access_APIs.get_llm(m, **pars)]

    def query_preprocessing_LLM(
        self, query: str, memory: list, LLM: Any = None
    ) -> Tuple[bool, str | Tuple[str, list]]:
        if LLM is None:
            LLM = self.llm[0]

        output_LLM = LLM.invoke(
            self.system_prompt_preprocessor.format(
                QUERY=query, conversation_history=memory
            )
        ).content

        xml_tag_pattern = re.compile(r"<(\w+)(\s[^>]*)?>(.*?)</\1>", re.DOTALL)
        xml_tags = xml_tag_pattern.findall(output_LLM)
        tags = {tag[0]: (tag[1], tag[2]) for tag in xml_tags}

        if "answer" in tags.keys():
            return False, tags["answer"]
        else:
            try:
                user_knowledge = tags["user_knowledge"][1]
            except KeyError:
                user_knowledge = ""
            questions = [
                {"text": q[2], "type": q[1]}
                for q in xml_tag_pattern.findall(tags["questions"][1])
            ]
            return True, (user_knowledge, questions)

    def retrivier(self, query: str, info_type: str, reasoning_level) -> list:
        if reasoning_level == 0:
            context = self.index_retriever(query)
            if len(context) == 0:
                return self.factual_retriever(query)
            return context
        else:
            return self.factual_retriever(query)

    def responder_LLM(
        self,
        query: str,
        context: str,
        user_knowledge: str,
        summary_of_explored_contexts: str,
        final: bool = False,
        LLM: Any = None,
    ):  # -> Tuple[str|list, bool]:
        if LLM is None:
            LLM = self.llm[1]

        if not final:
            output_LLM = LLM.invoke(
                self.system_prompt_responder.format(
                    QUERY=query,
                    CONTEXT=context,
                    USER_KNOWLEDGE=user_knowledge,
                    SUMMARY_OF_EXPLORED_CONTEXTS=summary_of_explored_contexts,
                )
            ).content

            print(output_LLM)

            xml_tag_pattern = re.compile(r"<(\w+)(\s[^>]*)?>(.*?)</\1>", re.DOTALL)
            xml_tags = xml_tag_pattern.findall(output_LLM)
            tags = {tag[0]: tag[2] for tag in xml_tags}

            if "answer" in tags.keys():
                return tags["answer"], True
            else:
                knowledge_summary = ""
                new_questions = ""
                if "knowledge_summary" in tags.keys():
                    knowledge_summary = tags["knowledge_summary"]
                if "new_questions" in tags.keys():
                    new_questions = tags["new_questions"]
                    new_questions = [
                        {"text": q[2], "type": q[1]}
                        for q in xml_tag_pattern.findall(new_questions)
                    ]

                return [knowledge_summary, new_questions], False
        else:
            output_LLM = LLM.invoke(
                self.system_prompt_final_responder.format(
                    QUERY=query,
                    CONTEXT=context,
                    USER_KNOWLEDGE=user_knowledge,
                    SUMMARY_OF_EXPLORED_CONTEXTS=summary_of_explored_contexts,
                )
            ).content

            xml_tag_pattern = re.compile(r"<(\w+)(\s[^>]*)?>(.*?)</\1>", re.DOTALL)
            xml_tags = xml_tag_pattern.findall(output_LLM)
            tags = {tag[0]: tag[2] for tag in xml_tags}

            return tags["answer"], True

    def predict(self, query: str, memory: list = [], verbose: bool = False) -> str:
        needs_info, preprocess_reasoning = self.query_preprocessing_LLM(
            query, memory=memory
        )
        history_reasoning = {
            "query": query,
            "needs_info": needs_info,
            "preprocess_reasoning": preprocess_reasoning,
            "reasoning": {},
        }
        if verbose:
            print(
                f"-------------------\nQuery: {query}\nNeeds info: {needs_info}\nPreprocess reasoning: {preprocess_reasoning}\n"
            )
        if needs_info:
            is_enough = False
            explored_contexts = []
            user_knowledge, questions = preprocess_reasoning
            result = None, questions
            reasoning_level = 0
            while not is_enough:
                summary_of_explored_contexts, questions = result

                context_list = [
                    self.retrivier(
                        q["text"], info_type=q["type"], reasoning_level=reasoning_level
                    )
                    for q in questions
                ]
                context_dict = {c.metadata["url"]: c for cc in context_list for c in cc}

                context, context_urls = self.context_filter(
                    context_dict, explored_contexts, query
                )
                explored_contexts.extend(context_urls)

                if verbose:
                    print(
                        f"-------Reasoning level {reasoning_level}\nExplored Context URLS: {context_urls}"
                    )

                result, is_enough = self.responder_LLM(
                    query,
                    context,
                    user_knowledge,
                    summary_of_explored_contexts,
                    final=reasoning_level > self.REASONING_LIMIT,
                )

                if verbose:
                    print(f"-------Result: {result}\n")
                    if is_enough:
                        print(f"END!!!\n")

                reasoning_level += 1
                history_reasoning["reasoning"][reasoning_level] = {
                    "context": context,
                    "result": result,
                }
            answer = result
        else:
            answer = preprocess_reasoning
        history_reasoning["answer"] = answer
        return history_reasoning

    def predict_stream(self, query: str, verbose: bool = False, memory: list = []) -> str:
        needs_info, preprocess_reasoning = self.query_preprocessing_LLM(
            query, memory=memory
        )
        history_reasoning = {
            "query": query,
            "needs_info": needs_info,
            "preprocess_reasoning": preprocess_reasoning,
            "reasoning": {},
        }
        if verbose:
            print(
                f"-------------------\nQuery: {query}\nNeeds info: {needs_info}\nPreprocess reasoning: {preprocess_reasoning}\n"
            )
        if needs_info:
            is_enough = False
            explored_contexts = []
            user_knowledge, questions = preprocess_reasoning
            result = None, questions
            reasoning_level = 0
            while not is_enough:
                summary_of_explored_contexts, questions = result

                context_list = [
                    self.retrivier(
                        q["text"], info_type=q["type"], reasoning_level=reasoning_level
                    )
                    for q in questions
                ]
                context_dict = {c.metadata["url"]: c for cc in context_list for c in cc}

                context, context_urls = self.context_filter(
                    context_dict, explored_contexts, query
                )
                explored_contexts.extend(context_urls)

                if verbose:
                    print(
                        f"-------Reasoning level {reasoning_level}\nExplored Context URLS: {context_urls}"
                    )

                result, is_enough = self.responder_LLM(
                    query,
                    context,
                    user_knowledge,
                    summary_of_explored_contexts,
                    final=reasoning_level > self.REASONING_LIMIT,
                )

                if verbose:
                    print(f"-------Result: {result}\n")
                    if is_enough:
                        print(f"END!!!\n")

                reasoning_level += 1
                history_reasoning["reasoning"][reasoning_level] = {
                    "context": context,
                    "result": result,
                }
                answer = result
        else:
            answer = preprocess_reasoning
        
        history_reasoning["answer"] = answer
        yield history_reasoning
