import logging
from fastapi import FastAPI
from services.pdf_loader import load_and_chunk_directory
from services.embeddings import embed_texts, get_embedding_dim
from services.vector_store import FaissStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ingest")

from dotenv import load_dotenv
load_dotenv() 

app = FastAPI(title="NXB KB Ingestion")

DATA_DIR = "data"


@app.post("/ingest")
async def ingest():
    """
    Loads all PDFs from data/, chunks them, embeds via Ollama,
    and (re)builds the FAISS index on disk.
    """
    logger.info("Loading and chunking PDFs from %s", DATA_DIR)
    chunks = load_and_chunk_directory(DATA_DIR)

    if not chunks:
        return {"status": "no_pdfs_found", "chunks_indexed": 0}

    texts = [c["text"] for c in chunks]
    logger.info("Embedding %d chunks via Ollama", len(texts))

    dim = await get_embedding_dim()
    embeddings = await embed_texts(texts)

    store = FaissStore(dim=dim)
    store.add(embeddings, chunks)
    store.save()

    logger.info("Indexed %d chunks into FAISS", len(chunks))
    return {
        "status": "success",
        "chunks_indexed": len(chunks),
        "index_path": store.index_path,
    }


@app.get("/health")
async def health():
    return {"status": "ok"}