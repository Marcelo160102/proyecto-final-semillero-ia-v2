#!/usr/bin/env python3
"""Indexa los documentos de conocimiento en colecciones ChromaDB.

Uso:
    python scripts/indexar.py

Requisito: GOOGLE_API_KEY configurada en .env o variable de entorno.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config import obtener_config
from app.services.embedding_service import indexar_todos


def main():
    config = obtener_config()

    if not config.google_api_key:
        print("❌ GOOGLE_API_KEY no configurada. Crea un archivo .env con:")
        print('   GOOGLE_API_KEY="tu-api-key"')
        sys.exit(1)

    print(f"📦 Embeddings: {config.embedding_model}")
    embeddings = GoogleGenerativeAIEmbeddings(
        model=config.embedding_model,
        google_api_key=config.google_api_key,
    )
    indexar_todos(embeddings)


if __name__ == "__main__":
    main()
