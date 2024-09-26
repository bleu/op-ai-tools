from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.embeddings import HuggingFaceEmbeddings
from .test_chat_model import GroqLLM
from op_brains.config import (
    EMBEDDING_MODEL,
    CHAT_MODEL,
)

class access_APIs:
    def get_llm(model: str = CHAT_MODEL, **kwargs):
        if "gpt" in model:
            return ChatOpenAI(model=model, **kwargs)
        elif "claude" in model:
            return ChatAnthropic(model=model, **kwargs)
        elif "free" in model:
            return GroqLLM()
        else:
            raise ValueError(f"Model {model} not recognized")

    @staticmethod
    def get_embedding(model: str = EMBEDDING_MODEL, **kwargs):
        if "free" in model:
            return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        else:
            return OpenAIEmbeddings(model=model, **kwargs)
