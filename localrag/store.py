import hashlib
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from .chunker import Chunk


def fingerprint(docs) -> str:
    """Hash of the document contents, used to detect a stale index."""
    h = hashlib.sha256()
    for d in docs:
        h.update(d.name.encode())
        h.update(d.text.encode())
    return h.hexdigest()


class VectorStore:
    """Plain numpy matrix with cosine similarity.

    Vectors are L2-normalized on save, so a search is one matrix-vector product.
    """

    def __init__(self, vectors: np.ndarray, chunks: list[Chunk], fp: str = ""):
        self.vectors = vectors
        self.chunks = chunks
        self.fp = fp

    @staticmethod
    def _normalize(v: np.ndarray) -> np.ndarray:
        v = np.asarray(v, dtype=np.float32)
        norms = np.linalg.norm(v, axis=-1, keepdims=True)
        return v / np.clip(norms, 1e-12, None)

    @classmethod
    def build(cls, embeddings: list[list[float]], chunks: list[Chunk], fp: str):
        return cls(cls._normalize(np.array(embeddings)), chunks, fp)

    def search(self, query_vec: list[float], k: int) -> list[tuple[Chunk, float]]:
        q = self._normalize(np.array(query_vec))
        scores = self.vectors @ q
        top = np.argsort(-scores)[:k]
        return [(self.chunks[i], float(scores[i])) for i in top]

    # --- persistence ---
    def save(self, folder: Path):
        folder.mkdir(parents=True, exist_ok=True)
        np.save(folder / "vectors.npy", self.vectors)
        meta = {"fingerprint": self.fp, "chunks": [asdict(c) for c in self.chunks]}
        (folder / "chunks.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8"
        )

    @classmethod
    def load(cls, folder: Path) -> "VectorStore | None":
        vec_path, meta_path = folder / "vectors.npy", folder / "chunks.json"
        if not (vec_path.exists() and meta_path.exists()):
            return None
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        chunks = [Chunk(**c) for c in meta["chunks"]]
        return cls(np.load(vec_path), chunks, meta.get("fingerprint", ""))
