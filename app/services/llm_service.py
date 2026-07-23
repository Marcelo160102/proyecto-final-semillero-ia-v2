from functools import lru_cache

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from app.config import obtener_config


@lru_cache
def obtener_llm() -> ChatGoogleGenerativeAI:
    config = obtener_config()
    return ChatGoogleGenerativeAI(
        model=config.gemini_model,
        google_api_key=config.google_api_key,
        temperature=0,
    )


@lru_cache
def obtener_embeddings() -> GoogleGenerativeAIEmbeddings:
    config = obtener_config()
    return GoogleGenerativeAIEmbeddings(
        model=config.embedding_model,
        google_api_key=config.google_api_key,
    )
