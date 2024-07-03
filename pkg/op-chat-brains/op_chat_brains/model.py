from typing import List, Dict, Any

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
import weave


class DatabaseLoader:
    @staticmethod
    def load_db(
        dbs: List[str], model_embeddings: str, vectorstore: str = "faiss"
    ) -> FAISS:
        embeddings = OpenAIEmbeddings(model=model_embeddings)
        if vectorstore == "faiss":
            db_paths = [f"dbs/{name}_db/faiss/{model_embeddings}" for name in dbs]
            loaded_dbs = [
                FAISS.load_local(
                    db_path, embeddings, allow_dangerous_deserialization=True
                )
                for db_path in db_paths
            ]
            merged_db = loaded_dbs[0]
            for db in loaded_dbs[1:]:
                merged_db.merge_from(db)
            return merged_db
        raise ValueError(f"Unsupported vectorstore: {vectorstore}")


class ChatBuilder:
    @staticmethod
    def build_chat(chat_pars: Dict[str, Any], prompt_template: str):
        prompt = ChatPromptTemplate.from_template(prompt_template)
        llm = ChatOpenAI(**chat_pars)
        return prompt | llm, llm


class RetrieverBuilder:
    @staticmethod
    def build_retriever(
        dbs_name: List[str],
        embeddings_name: str,
        vectorstore: str = "faiss",
        retriever_pars: Dict[str, Any] = {},
    ):
        db = DatabaseLoader.load_db(dbs_name, embeddings_name, vectorstore)
        if vectorstore == "faiss":
            return db.as_retriever(**retriever_pars)
        raise ValueError(f"Unsupported vectorstore: {vectorstore}")


class RAGModel(weave.Model):
    structure: str = "simple-rag"
    dbs_name: List[str]
    embeddings_name: str
    vectorstore: str
    retriever_pars: Dict[str, Any]
    prompt_template: str
    chat_pars: Dict[str, Any]

    def predict(self, question: str) -> Dict[str, Any]:
        retriever = RetrieverBuilder.build_retriever(
            self.dbs_name, self.embeddings_name, self.vectorstore, self.retriever_pars
        )
        chain, _ = ChatBuilder.build_chat(self.chat_pars, self.prompt_template)

        context = retriever.invoke(question)
        response = chain.invoke({"context": context, "question": question})

        return {"context": context, "answer": response.content}
