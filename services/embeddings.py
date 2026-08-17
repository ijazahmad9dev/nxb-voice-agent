import os
import httpx
import numpy as np

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "https://herb-petite-era-glasses.trycloudflare.com")
EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "mistral-nemo:latest")

_dim_cache: int | None = None


async def embed_text(text: str) -> np.ndarray:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/embeddings",
            json={"model": EMBED_MODEL, "prompt": text},
        )
        response.raise_for_status()
        data = response.json()
    return np.array(data["embedding"], dtype="float32")


def _normalize(vec: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(vec)
    if norm == 0:
        norm = 1e-10
    return (vec / norm).astype("float32")


async def embed_texts(texts: list[str]) -> np.ndarray:
    """Ollama's /api/embeddings takes one prompt at a time, so we loop."""
    vectors = []
    for t in texts:
        vec = await embed_text(t)
        vectors.append(_normalize(vec))
    return np.vstack(vectors)


async def embed_query(query: str) -> np.ndarray:
    vec = await embed_text(query)
    return _normalize(vec)


async def get_embedding_dim() -> int:
    global _dim_cache
    if _dim_cache is None:
        vec = await embed_text("dimension probe")
        _dim_cache = len(vec)
    return _dim_cache