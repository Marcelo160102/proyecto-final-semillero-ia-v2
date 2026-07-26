import re
import time
from pathlib import Path

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from chromadb.errors import NotFoundError

from app.config import obtener_config
from app.services.chroma_service import _obtener_cliente
from app.services.llm_service import obtener_embeddings


def cargar_documento(ruta: str) -> str:
    return Path(ruta).read_text(encoding="utf-8")


def chunkear_por_seccion(texto: str) -> list[str]:
    cabeceras = list(re.finditer(r"^\d+\.\s", texto, flags=re.MULTILINE))
    chunks = []
    for i, m in enumerate(cabeceras):
        ini = m.start()
        fin = cabeceras[i + 1].start() if i + 1 < len(cabeceras) else len(texto)
        chunks.append(texto[ini:fin].strip())
    return chunks


def resumen_chunks(chunks: list[str]):
    print(f"  Total chunks: {len(chunks)}")
    total_car = sum(len(c) for c in chunks)
    print(f"  Tamaño promedio: {total_car // len(chunks)} caracteres")
    print(f"  Tamaño min/max: {min(len(c) for c in chunks)} / {max(len(c) for c in chunks)} caracteres")
    for i, c in enumerate(chunks):
        print(f"    ch_{i}: {c[:80].replace(chr(10), ' ')}...")


def indexar_documento(
    ruta: str,
    coleccion: str,
    embeddings: GoogleGenerativeAIEmbeddings,
    pausa_seg: float = 0.3,
):
    texto = cargar_documento(ruta)
    chunks = chunkear_por_seccion(texto)

    print(f"  Caracteres totales: {len(texto):,}")
    resumen_chunks(chunks)

    client = _obtener_cliente()
    try:
        client.delete_collection(coleccion)
    except (ValueError, NotFoundError):
        pass

    vectorstore = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        metadatas=[{"seccion": i, "fuente": ruta} for i in range(len(chunks))],
        collection_name=coleccion,
        client=client,
        collection_metadata={"hnsw:space": "cosine"},
    )

    print(f"  ✅ {vectorstore._collection.count()} chunks indexados en '{coleccion}'")
    time.sleep(pausa_seg)
    return vectorstore


COLECCIONES_REQUERIDAS = ["contratos", "proteccion_datos", "cumplimiento"]


def verificar_indexacion():
    import logging

    config = obtener_config()
    if not config.google_api_key:
        logging.warning("GOOGLE_API_KEY no configurada, omitiendo indexacion")
        return

    try:
        client = _obtener_cliente()
        existentes = {c.name for c in client.list_collections()}

        faltan = [c for c in COLECCIONES_REQUERIDAS if c not in existentes]
        vacias = []
        for nombre in COLECCIONES_REQUERIDAS:
            if nombre in existentes:
                col = client.get_collection(nombre)
                if col.count() == 0:
                    vacias.append(nombre)

        if not faltan and not vacias:
            logging.info("Colecciones ChromaDB ya indexadas")
            return

        if faltan:
            logging.info("Colecciones faltantes: %s", ", ".join(faltan))
        if vacias:
            logging.info("Colecciones vacias: %s", ", ".join(vacias))

        logging.info("Indexando documentos automaticamente...")
        embeddings = obtener_embeddings()
        indexar_todos(embeddings)
        logging.info("Indexacion automatica completada")
    except Exception as e:
        logging.warning("No se pudo verificar/indexar ChromaDB: %s", e)


DOCS = [
    {"ruta": "data/01_Clausulas_Contractuales.txt", "nombre": "Contratos", "coleccion": "contratos"},
    {"ruta": "data/02_Proteccion_Datos.txt", "nombre": "Protección de Datos", "coleccion": "proteccion_datos"},
    {"ruta": "data/03_Cumplimiento_Etica.txt", "nombre": "Cumplimiento Normativo", "coleccion": "cumplimiento"},
]


def indexar_todos(embeddings: GoogleGenerativeAIEmbeddings):
    for doc in DOCS:
        print(f"\n{'='*60}")
        print(f"Documento: {doc['nombre']}  ({doc['ruta']})")
        print('='*60)
        indexar_documento(doc["ruta"], doc["coleccion"], embeddings)
    print("\n✅ Todos los documentos indexados.")
