from typing import Iterator, List, Dict, Any, Callable, Tuple
import os

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_anthropic import ChatAnthropic
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
import weave

openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

def load_db(dbs, model_embeddings, vectorstore = 'faiss'):
    embeddings = OpenAIEmbeddings(model=model_embeddings, openai_api_key=openai_api_key)
    if vectorstore == 'faiss':
        dbs = [f"dbs/{name}_db/faiss/{model_embeddings}" for name in dbs]
        dbs = [FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True) for db_path in dbs]
        db = dbs[0]
        for db_ in dbs[1:]:
            db.merge_from(db_)
    
    return db

@weave.op()
def build_chat(chat_pars, prompt_template):
    prompt = ChatPromptTemplate.from_template(prompt_template)
    llm = ChatOpenAI(**chat_pars, openai_api_key=openai_api_key)
    chain = prompt | llm

    return chain, llm
    
@weave.op()
def build_retriever(dbs_name, embeddings_name, vectorstore = 'faiss', retriever_pars = {}):
    db = load_db(dbs_name, embeddings_name, vectorstore)
    if vectorstore == 'faiss':
        retriever = db.as_retriever(**retriever_pars)

    return retriever

def RAG_model(structure_name:str, **kwargs):
    structures = structure_name.split('-')
    if "openai" in structures:
        class RAGModel(weave.Model):
            structure : str = structure_name

            dbs_name : List
            embeddings_name : str

            vectorstore : str

            prompt_template : str
            chat_pars : Dict[str, Any]
            
            retriever_pars : Dict|List

            @weave.op()
            def predict(self, question: str):
                if "multi_retriever" in structures:
                    retrievers = {}
                    for name, retriever_pars in self.retriever_pars.items():
                        retriever = build_retriever([name], self.embeddings_name, self.vectorstore, retriever_pars)
                        retrievers[name] = retriever
                else:
                    retriever = build_retriever(self.dbs_name, self.embeddings_name, self.vectorstore, self.retriever_pars)

                chain, llm = build_chat(self.chat_pars, self.prompt_template)

                if self.vectorstore == 'faiss':
                    if "multi_retriever" in structures:
                        context = {}
                        for name, retriever in retrievers.items():
                            context[name] = retriever.invoke(question)
                    elif "contextual_compression" in structures:
                        compressor = LLMChainExtractor.from_llm(llm)
                        compression_retriever = ContextualCompressionRetriever(
                            base_compressor=compressor, base_retriever=retriever
                        )
                        context = compression_retriever.invoke(question)
                    else:
                        context = retriever.invoke(question)

                response = chain.invoke(
                    {
                        "context": context,
                        "question": question,
                    }
                )
                
                return {"context": context, "answer": response.content}
    elif "claude" in structures:
        class RAGModel(weave.Model):
            structure : str = structure_name

            dbs_name : list
            embeddings_name : str

            vectorstore : str
            retriever_pars : dict

            prompt_template : Callable
            chat_pars : dict[str, str|int]

            @weave.op()
            def predict(self, question: str):
                prompt_expander = kwargs.get("prompt_expander", None)
                retriever = build_retriever(self.dbs_name, self.embeddings_name, self.vectorstore, self.retriever_pars)
                llm = ChatAnthropic(**self.chat_pars)

                if "query_expansion" in structures:
                    expanded_question = llm.invoke(prompt_expander(question)).content
                    print(f"Expanded question: {expanded_question}")

                    if self.vectorstore == 'faiss':
                        context = retriever.invoke(expanded_question)
                else:
                    if self.vectorstore == 'faiss':
                        context = retriever.invoke(question)

                response = llm.invoke(self.prompt_template(context=context, question=question))
                
                return {"context": context, "answer": response.content}
            
            def ask(self, question: str):
                out = self.predict(question)
                return out["answer"]
                
                    
    return RAGModel
        