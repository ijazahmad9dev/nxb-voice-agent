import json
import os
import faiss
import numpy as np


class FaissStore:
    def __init__(self, dim: int, index_dir: str = "data/faiss_index"):
        self.dim = dim
        self.index_dir = index_dir
        self.index_path = os.path.join(index_dir, "index.faiss")
        self.meta_path = os.path.join(index_dir, "metadata.json")

        os.makedirs(index_dir, exist_ok=True)

        # Inner product on normalized vectors = cosine similarity
        self.index = faiss.IndexFlatIP(dim)
        self.metadata: list[dict] = []

    def add(self, embeddings: np.ndarray, metadatas: list[dict]):
        self.index.add(embeddings)
        self.metadata.extend(metadatas)

    def save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w") as f:
            json.dump(self.metadata, f)

    def load(self) -> bool:
        """Returns True if an existing index was loaded."""
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, "r") as f:
                self.metadata = json.load(f)
            return True
        return False

    def search(self, query_embedding: np.ndarray, top_k: int = 3) -> list[dict]:
        if self.index.ntotal == 0:
            return []

        query_embedding = np.expand_dims(query_embedding, axis=0)
        scores, indices = self.index.search(query_embedding, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            meta = self.metadata[idx]
            results.append({
                "text": meta["text"],
                "source": meta["source"],
                "page": meta["page"],
                "score": float(score),  # cosine similarity, 0-1
            })
        return results