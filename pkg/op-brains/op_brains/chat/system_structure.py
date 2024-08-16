from typing import Tuple, Any, Callable
from op_brains.chat import model_utils

import re


class RAGSystem:
    REASONING_LIMIT: int
    models_to_use: list
    retriever: Callable
    context_filter: Callable
    system_prompt_preprocessor: Callable
    system_prompt_responder: Callable

    llm: list = []
    number_of_models: int = 2

    def __init__(self, **kwargs):
        self.REASONING_LIMIT = kwargs.get("REASONING_LIMIT", 3)
        self.models_to_use = kwargs.get("models_to_use")
        self.retriever = kwargs.get("retriever")
        self.context_filter = kwargs.get("context_filter")
        self.system_prompt_preprocessor = kwargs.get("system_prompt_preprocessor")
        self.system_prompt_responder = kwargs.get("system_prompt_responder")

        assert len(self.models_to_use) == self.number_of_models

        for m in self.models_to_use:
            m, pars = m
            self.llm += [model_utils.access_APIs.get_llm(m, **pars)]

    def query_preprocessing_LLM(
        self, query: str, memory: list, LLM: Any = None
    ) -> Tuple[bool, str | Tuple[str, list]]:
        if LLM is None:
            LLM = self.llm[0]

        output_LLM = self.system_prompt_preprocessor(LLM,
            QUERY=query, 
            CONVERSATION_HISTORY=memory)
        
        print(output_LLM)

        if not output_LLM["needs_info"]:
            return False, output_LLM["answer"]
        else:
            user_knowledge = output_LLM["expansion"]["user_knowledge"]
            type_search = output_LLM["expansion"]["type_search"]

            keywords = output_LLM["expansion"]["keywords"]
            keywords = [{"keyword": k} for k in keywords]

            questions = output_LLM["expansion"]["questions"]
            questions = [{"question": q} for q in questions]

            return True, (user_knowledge, keywords + questions, type_search)

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

            output_LLM = self.system_prompt_responder(LLM, final=final,
                QUERY=query, 
                CONTEXT=context, 
                USER_KNOWLEDGE=user_knowledge, 
                SUMMARY_OF_EXPLORED_CONTEXTS=summary_of_explored_contexts
            )

            print(output_LLM)

            if not output_LLM["answer"] is None:
                return output_LLM["answer"], True
            else:
                knowledge_summary = output_LLM["search"]["knowledge_summary"]
                
                new_questions = output_LLM["search"]["questions"]
                new_questions = [{"question": q} for q in new_questions]

                type_search = output_LLM["search"]["type_search"]

                return [knowledge_summary, new_questions, type_search], False

            raise Exception("ERROR: Unexpected error during prediction")

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
            explored_contexts_urls = []
            user_knowledge, questions, type_search = preprocess_reasoning
            result = "", questions, type_search
            reasoning_level = 0
            while not is_enough:
                summary_of_explored_contexts, questions, type_search = result
                try:
                    questions = [{"query": query}] + questions
                except:
                    pass

                context_dict = {
                    list(q.values())[0]: self.retriever(
                        q, reasoning_level=reasoning_level
                    )
                    for q in questions
                }
                # context_dict = {c.metadata['url']:c for cc in context_list for c in cc}

                context, context_urls = self.context_filter(
                    context_dict, explored_contexts_urls, query, type_search
                )
                explored_contexts_urls.extend(context_urls)

                if verbose:
                    print(
                        f"-------Reasoning level {reasoning_level}\nExploring Context URLS: {context_urls}"
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
                        print("END!!!\n")

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
