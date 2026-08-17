from services.embeddings import embed_query, get_embedding_dim
from services.vector_store import FaissStore


class KBClient:
    def __init__(self):
        self.store: FaissStore | None = None
        self.loaded = False

    async def _ensure_loaded(self):
        if self.store is None:
            dim = await get_embedding_dim()
            self.store = FaissStore(dim=dim)
            self.loaded = self.store.load()

    async def search(self, query: str, top_k: int = 3) -> list[dict]:
        await self._ensure_loaded()
        if not self.loaded:
            return []

        query_vec = await embed_query(query)
        return self.store.search(query_vec, top_k=top_k)


kb_client = KBClient()