import asyncio
from services.vector_store import FaissStore

class KBClient:
    def __init__(self):
        self.store = None
        self.loaded = False
        self._model = None

    def _ensure_loaded(self):
        if self._model is None:
            # Import + model load happens here — post-fork, inside the job process
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer("all-MiniLM-L6-v2")

        if self.store is None:
            dim = self._model.get_sentence_embedding_dimension()
            self.store = FaissStore(dim=dim)
            self.loaded = self.store.load()

    async def search(self, query: str, top_k: int = 3) -> list[dict]:
        def _search():
            self._ensure_loaded()
            if not self.loaded:
                return []
            query_vec = self._model.encode(
                [query], convert_to_numpy=True, normalize_embeddings=True
            ).astype("float32")[0]
            return self.store.search(query_vec, top_k=top_k)

        return await asyncio.to_thread(_search)


kb_client = KBClient()  # cheap — no model, no torch, no threads yet