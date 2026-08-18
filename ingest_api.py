import logging
from fastapi import FastAPI
from services.pdf_loader import load_and_chunk_directory
from services.embeddings import embed_texts, get_model
from services.vector_store import FaissStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ingest")

import os
from livekit import api

from dotenv import load_dotenv
load_dotenv()

LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "")
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "")

app = FastAPI(title="NXB KB Ingestion")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = "data"


@app.get("/token")
async def get_token(identity: str = "user", room: str = "nxb-support"):
    token = (
        api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        .with_identity(identity)
        .with_name(identity)
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=room,
                can_publish=True,
                can_subscribe=True,
            )
        )
    )
    return {
        "token": token.to_jwt(),
        "url": LIVEKIT_URL,
    }


@app.post("/ingest")
async def ingest():
    logger.info("Loading and chunking PDFs from %s", DATA_DIR)
    chunks = load_and_chunk_directory(DATA_DIR)

    if not chunks:
        return {"status": "no_pdfs_found", "chunks_indexed": 0}

    texts = [c["text"] for c in chunks]
    logger.info("Embedding %d chunks", len(texts))
    embeddings = embed_texts(texts)

    dim = get_model().get_sentence_embedding_dimension()
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