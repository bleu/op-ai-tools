from typing import Tuple, Any, Callable
from op_chat_brains.chat import model_utils

import re

class RAG_system:
    REASONING_LIMIT : int
    models_to_use : list
    retriever : Callable
    context_filter : Callable
    system_prompt_preprocessor : str
    system_prompt_responder : str
    system_prompt_final_responder : str

    llm: list = []
    number_of_models: int = 2

    def __init__(self, **kwargs):
            self.REASONING_LIMIT = kwargs.get("REASONING_LIMIT", 3)
            self.models_to_use = kwargs.get("models_to_use")
            self.retriever = kwargs.get("retriever")
            self.context_filter = kwargs.get("context_filter")
            self.system_prompt_preprocessor = kwargs.get("system_prompt_preprocessor")
            self.system_prompt_responder = kwargs.get("system_prompt_responder")
            self.system_prompt_final_responder = kwargs.get("system_prompt_final_responder")

            assert len(self.models_to_use) == self.number_of_models

            for m in self.models_to_use:
                m, pars = m
                self.llm += [model_utils.access_APIs.get_llm(m, **pars)]

    def query_preprocessing_LLM(self, query : str, memory : list, LLM : Any = None) -> Tuple[bool, str|Tuple[str, list]]:
        if LLM is None:
            LLM = self.llm[0]

        output_LLM = LLM.invoke(self.system_prompt_preprocessor.format(
            QUERY = query,
            conversation_history = memory
        )).content

        xml_tag_pattern = re.compile(r"<(\w+)(\s[^>]*)?>(.*?)</\1>", re.DOTALL)
        xml_tags = xml_tag_pattern.findall(output_LLM)
        tags = {tag[0]: (tag[1], tag[2]) for tag in xml_tags}

        if "answer" in tags.keys():
            return False, tags["answer"]
        else:
            if "user_knowledge" in tags.keys():
                user_knowledge = tags["user_knowledge"][1]
            else:
                user_knowledge = ""
            
            if "queries" in tags.keys():
                queries_tags = tags["queries"][1]
                queries_tags = xml_tag_pattern.findall(queries_tags)

                keywords = [q[2] for q in queries_tags if q[0] == "keywords"]
                if len(keywords) > 0:
                    keywords = [k.strip().lower() for k in keywords[0].split(",")]
                    kws = []
                    for k in keywords:
                        kws.append({"keyword": re.sub(r'[^\w\s]', '', k)})
                        if "#" in k:
                            kws[-1]["instance"] = k.split("#")[1]
                    keywords = kws

                questions = [q[2] for q in queries_tags if q[0] == "question"]
                if len(questions) > 0:
                    questions = [{"question": q} for q in questions]
        
                type_search = [q[2] for q in queries_tags if q[0] == "type_search"][0]

            return True, (user_knowledge, keywords + questions, type_search)

    def responder_LLM(self, query : str, context : str, user_knowledge : str, summary_of_explored_contexts : str, final : bool = False, LLM : Any = None):# -> Tuple[str|list, bool]:
        if LLM is None:
            LLM = self.llm[1]

        if not final:
            output_LLM = LLM.invoke(self.system_prompt_responder.format(
                QUERY = query,
                CONTEXT = context,
                USER_KNOWLEDGE = user_knowledge,
                SUMMARY_OF_EXPLORED_CONTEXTS = summary_of_explored_contexts
            )).content

            xml_tag_pattern = re.compile(r"<(\w+)(\s[^>]*)?>(.*?)</\1>", re.DOTALL)
            xml_tags = xml_tag_pattern.findall(output_LLM)
            tags = {tag[0]: tag[2] for tag in xml_tags}

            if "answer" in tags.keys():
                return tags["answer"], True
            else:
                print(tags)
                knowledge_summary = ""
                new_questions = ""
                type_search = ""
                if "knowledge_summary" in tags.keys():
                    knowledge_summary = tags["knowledge_summary"]
                if "new_questions" in tags.keys():
                    queries_tags = tags["new_questions"]
                    queries_tags = xml_tag_pattern.findall(queries_tags)

                    questions = [q[2] for q in queries_tags if q[0] == "question"]
                    if len(questions) > 0:
                        questions = [{"question": q} for q in questions]
            
                    type_search = [q[2] for q in queries_tags if q[0] == "type_search"][0]

                return [knowledge_summary, new_questions, type_search], False
        else:
            output_LLM = LLM.invoke(self.system_prompt_final_responder.format(
                QUERY = query,
                CONTEXT = context,
                USER_KNOWLEDGE = user_knowledge,
                SUMMARY_OF_EXPLORED_CONTEXTS = summary_of_explored_contexts
            )).content

            xml_tag_pattern = re.compile(r"<(\w+)(\s[^>]*)?>(.*?)</\1>", re.DOTALL)
            xml_tags = xml_tag_pattern.findall(output_LLM)
            tags = {tag[0]: tag[2] for tag in xml_tags}

            return tags["answer"], True
                
    def predict(self, query : str, memory : list = [], verbose : bool = False) -> str:
        needs_info, preprocess_reasoning = self.query_preprocessing_LLM(query, memory=memory)
        history_reasoning = {"query": query, "needs_info": needs_info, "preprocess_reasoning": preprocess_reasoning, "reasoning" : {}}
        if verbose:
            print(f"-------------------\nQuery: {query}\nNeeds info: {needs_info}\nPreprocess reasoning: {preprocess_reasoning}\n")
        if needs_info:
            is_enough = False
            explored_contexts = []
            user_knowledge, questions, type_search = preprocess_reasoning
            result = "", questions, type_search
            reasoning_level = 0
            while not is_enough:
                summary_of_explored_contexts, questions, type_search = result

                context_list = [self.retriever(q, reasoning_level=reasoning_level) for q in questions]
                print(type(context_list))
                context_dict = {c.metadata['url']:c for cc in context_list for c in cc}

                context, context_urls = self.context_filter(context_dict, explored_contexts, query, type_search)
                explored_contexts.extend(context_urls)

                if verbose:
                    print(f"-------Reasoning level {reasoning_level}\nExplored Context URLS: {context_urls}")

                result, is_enough = self.responder_LLM(query, context, user_knowledge, summary_of_explored_contexts, final = reasoning_level > self.REASONING_LIMIT)
                
                if verbose:
                    print(f"-------Result: {result}\n")
                    if is_enough:
                        print(f"END!!!\n")

                reasoning_level += 1
                history_reasoning["reasoning"][reasoning_level] = {"context": context, "result": result}
            answer = result
        else:
            answer = preprocess_reasoning
        history_reasoning["answer"] = answer
        return history_reasoning
    
    