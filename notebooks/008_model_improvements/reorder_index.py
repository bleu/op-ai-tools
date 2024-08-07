from ragatouille import RAGPretrainedModel
RAG = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")
RAG = RAG.as_langchain_document_compressor()

import time, json, faiss, re
import numpy as np
import pandas as pd

from op_chat_brains.documents import optimism
all_contexts_df = optimism.DataframeBuilder.build_dataframes()

from op_chat_brains.config import (
    QUESTIONS_INDEX_JSON,
    QUESTIONS_INDEX_NPY,
    KEYWORDS_INDEX_JSON,
    KEYWORDS_INDEX_NPY,
    EMBEDDING_MODEL
)

def reorder_index(index_dict):
    output_dict = {}
    for key, urls in index_dict.items():
        print(key)
        print(urls)
        contexts = all_contexts_df[all_contexts_df["url"].isin(urls)].content.tolist()
        k = len(contexts)
        if k > 1:
            contexts = RAG.compress_documents(query=key, documents=contexts, k=k)
            urls = [context.metadata["url"] for context in contexts]
            print(urls)
        output_dict[key] = urls

    return output_dict

def reorder_file(path):
    with open(path, "r") as f:
        index = json.load(f)
    index = reorder_index(index)
    with open(path, "w") as f:
        json.dump(index, f, indent=4)

def main():
    reorder_file(QUESTIONS_INDEX_JSON)
    reorder_file(KEYWORDS_INDEX_JSON)

if __name__ == "__main__":
    main()

