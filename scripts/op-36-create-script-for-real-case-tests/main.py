# general
import pandas as pd
import os
import re
import sys
import json
from datetime import datetime
# nest_asyncio.apply()

# embedding and chat
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents.base import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter

# vectorstore
from langchain_community.vectorstores import FAISS
import weave

# optimism governance docs
docs_path = "../../data/001-initial-dataset-governance-docs/file.txt"
# optimism governance forum
forum_path = "../../data/002-governance-forum-202406014/dataset/_out.jsonl"

# default system parameters
dbs = [
    "fragments_docs",
    "posts_forum",
]
vectorstore = "faiss"
embedding_model = "text-embedding-ada-002"
chat_model = "gpt-4o"
chat_temperature = 0
max_retries = 2
k_retriever = 8
log_file = "logs.csv"
prompt_template = """Answer politely the question at the end, using only the following context (that may contain docuentation parts, more reliable, and forum posts, less reliable). The user is not necessarily a specialist, so please avoid jargon and explain any technical terms. Be assertive. This is not a chatbot, so do not engage in longer conversations.

<context>
{context} 
</context>

Question: {question}
"""


# functions
def load_db(dbs, model_embeddings, vectorstore="faiss"):
    """
    load the dbs from the local path. Default is dbs/{db_name}_db/faiss/{model_embeddings}.

    :dbs: list of dbs names
    :model_embeddings: model name for the embeddings
    :vectorstore: type of vectorstore used, default is 'faiss'
    """
    embeddings = OpenAIEmbeddings(model=model_embeddings, openai_api_key=openai_api_key)
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


def build_chat(chat_pars, prompt_template):
    """
    build the chat chain with the prompt template and the chat parameters

    :chat_pars: chat parameters, reference: https://api.python.langchain.com/en/latest/chat_models/langchain_openai.chat_models.base.ChatOpenAI.html
    :prompt_template: prompt template
    """
    prompt = ChatPromptTemplate.from_template(prompt_template)
    llm = ChatOpenAI(**chat_pars, openai_api_key=openai_api_key)
    chain = prompt | llm

    return chain, llm


def build_retriever(dbs_name, embeddings_name, vectorstore="faiss", retriever_pars={}):
    """
    build the retriever from the dbs

    :dbs_name: list of dbs names
    :embeddings_name: model name for the embeddings
    :vectorstore: type of vectorstore used, default is 'faiss'
    :retriever_pars: parameters for the retriever, reference: https://python.langchain.com/v0.1/docs/modules/data_connection/retrievers/vectorstore/
    """
    db = load_db(dbs_name, embeddings_name, vectorstore)
    if vectorstore == "faiss":
        retriever = db.as_retriever(**retriever_pars)

    return retriever


def log(question, output, log_file=log_file):
    """
    log the question, answer, context and timestamp in a csv file

    :question: question asked
    :output: output from the model, containing the answer and context
    :log_file: path to the log file
    """
    if not os.path.exists(log_file):
        df = pd.DataFrame(columns=["question", "answer", "context", "timestamp"])
    else:
        df = pd.read_csv(log_file)

    answer = output["answer"]
    context = output["context"]

    line = pd.DataFrame(
        {
            "question": [question],
            "answer": [answer],
            "context": [context],
            "timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        }
    )
    df = pd.concat([df, line], ignore_index=True)

    df.to_csv(log_file, index=False)


def load_fragments(docs_path):
    """
    load the fragments from the markdown file, save the db in dbs/fragments_docs_db/faiss/{embedding_model}

    :docs_path: path to the markdown file
    """

    # load the documentation
    with open(docs_path, "r") as f:
        docs_read = f.read()

    # split "==> " and " <==" (to get the name of the files)
    docs_read = re.split(r"==> | <==", docs_read)

    docs = []
    path = []
    for d in docs_read:
        if "\n" not in d:
            # if it's a path
            path = d.split("/")
        else:
            # if it's a text document
            docs.append(
                {"path": "/".join(path[:-1]), "document_name": path[-1], "content": d}
            )

    # remove entries where content is just whitespace or '\n'
    docs = [d for d in docs if d["content"].strip() != ""]

    # split the markdown file into sections
    headers_to_split_on = [
        ("##", "header 2"),
        ("###", "header 3"),
        ("####", "header 4"),
        ("#####", "header 5"),
        ("######", "header 6"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on
    )

    # incorporate the doc metadata into the fragments
    fragments_docs = []
    for d in docs:
        f = markdown_splitter.split_text(d["content"])
        for fragment in f:
            fragment.metadata["path"] = d["path"]
            fragment.metadata["document_name"] = d["document_name"]
            fragments_docs.append(fragment)

    embeddings = OpenAIEmbeddings(model=embedding_model, openai_api_key=openai_api_key)
    if vectorstore == "faiss":
        db = FAISS.from_documents(fragments_docs, embeddings)
        db.save_local(f"dbs/fragments_docs_db/faiss/{embedding_model}")


def load_forum_posts(file_path):
    """
    load the forum posts from the jsonl file, save the db in dbs/posts_forum_db/faiss/{embedding_model}

    :file_path: path to the jsonl file
    """
    with open(file_path, "r") as file:
        boards = {}
        threads = {}
        posts = {}
        for line in file:
            data_line = json.loads(line)
            type_line = data_line["type"]
            try:
                id = data_line["item"]["data"]["id"]
                match type_line:
                    case "board":
                        boards[id] = {
                            "name": data_line["item"]["data"]["name"],
                            # "created_at": data_line['item']['data']['created_at'],
                        }
                    case "thread":
                        threads[id] = {
                            "title": data_line["item"]["data"]["title"],
                            "category_id": data_line["item"]["data"]["category_id"],
                            "created_at": data_line["item"]["data"]["created_at"],
                            "views": data_line["item"]["data"]["views"],
                            "like_count": data_line["item"]["data"]["like_count"],
                        }
                    case "post":
                        posts[id] = {
                            # "cooked": data_line['item']['data']['cooked'],
                            "url": data_line["item"]["url"],
                            # "link_counts": data_line['item']['data']['link_counts'],
                            "created_at": data_line["item"]["data"]["created_at"],
                            "username": data_line["item"]["data"]["username"],
                            "score": data_line["item"]["data"]["score"],
                            "readers_count": data_line["item"]["data"]["readers_count"],
                            "moderator": data_line["item"]["data"]["moderator"],
                            "admin": data_line["item"]["data"]["admin"],
                            "staff": data_line["item"]["data"]["staff"],
                            "trust_level": data_line["item"]["data"]["trust_level"],
                            "content": data_line["item"]["content"],
                            "creation_time": data_line["item"]["creation_time"],
                            "path": data_line["item"]["path"],
                            "download_time": data_line["download_time"],
                        }
                    case _:
                        print(f"Unknown type: {type_line}")
            except KeyError:
                None

    for id_post in posts:
        path = posts[id_post]["path"]

        try:
            id_board = int(path[0])
            posts[id_post]["board_name"] = boards[id_board]["name"]
            posts[id_post]["board_id"] = id_board
        except:
            posts[id_post]["board_name"] = None

        try:
            id_thread = int(path[1])
            posts[id_post]["thread_title"] = threads[id_thread]["title"]
            posts[id_post]["thread_id"] = id_thread
        except:
            posts[id_post]["thread_title"] = None

    posts_forum = [
        Document(
            page_content=d["content"],
            metadata={
                "board_name": d["board_name"],
                "thread_title": d["thread_title"],
                "creation_time": d["creation_time"],
                "username": d["username"],
                "moderator": d["moderator"],
                "admin": d["admin"],
                "staff": d["staff"],
                "trust_level": d["trust_level"],
                "id": ".".join(d["path"]) + "." + str(id),
            },
        )
        for id, d in posts.items()
    ]

    embeddings = OpenAIEmbeddings(model=embedding_model, openai_api_key=openai_api_key)
    if vectorstore == "faiss":
        db = FAISS.from_documents(posts_forum, embeddings)
        db.save_local(f"dbs/posts_forum_db/faiss/{embedding_model}")


# the model
class RAGModel(weave.Model):
    structure: str = "simple-rag"  # just a retriever and a llm

    dbs_name: list
    embeddings_name: str

    vectorstore: str
    retriever_pars: dict

    prompt_template: str
    chat_pars: dict[str, str | int]

    def predict(self, question: str):
        """
        get the output from the model

        :question: question asked
        """
        retriever = build_retriever(
            self.dbs_name, self.embeddings_name, self.vectorstore, self.retriever_pars
        )
        chain, llm = build_chat(self.chat_pars, self.prompt_template)

        if self.vectorstore == "faiss":
            context = retriever.invoke(question)

        response = chain.invoke(
            {
                "context": context,
                "question": question,
            }
        )

        return {"context": context, "answer": response.content}


# main
if __name__ == "__main__":
    if "OPENAI_API_KEY" in os.environ:
        openai_api_key = os.environ["OPENAI_API_KEY"]
    else:
        print("Error: OPENAI_API_KEY not found in environment variables.")
        print('Run: export OPENAI_API_KEY="..."')
        sys.exit(1)

    if len(sys.argv) != 2:
        print("ERROR. Usage: python main.py <question>")
        sys.exit(1)

    # if the dbs are not loaded, load them
    if not os.path.exists("dbs/fragments_docs_db/faiss/text-embedding-ada-002"):
        print(
            "Loading documentation... (This might take some minutes but will happen only once)"
        )
        load_fragments(docs_path)
    if not os.path.exists("dbs/posts_forum_db/faiss/text-embedding-ada-002"):
        print(
            "Loading forum posts... (This might take some minutes but will happen only once)"
        )
        load_forum_posts(forum_path)

    question = sys.argv[1]

    chat_pars = {
        "model": chat_model,
        "temperature": chat_temperature,
        "max_retries": max_retries,
    }

    rag = RAGModel(
        dbs_name=dbs,
        embeddings_name=embedding_model,
        chat_pars=chat_pars,
        prompt_template=prompt_template,
        retriever_pars={"search_kwargs": {"k": k_retriever}},
        vectorstore=vectorstore,
    )

    output = rag.predict(question)

    print(output["answer"])
    log(question, output)
