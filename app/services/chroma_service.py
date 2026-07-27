import chromadb
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config.config import obtener_config

config = obtener_config()


def _obtener_cliente():
    if config.chroma_host != "localhost":
        return chromadb.HttpClient(
            host=config.chroma_host, port=config.chroma_port
        )
    return chromadb.PersistentClient(path="./chroma_data")


def obtener_retriever(
    coleccion: str,
    embeddings: GoogleGenerativeAIEmbeddings,
    k: int = 3,
):
    client = _obtener_cliente()
    vectorstore = Chroma(
        client=client,
        collection_name=coleccion,
        embedding_function=embeddings,
    )
    return vectorstore.as_retriever(search_kwargs={"k": k})