"""Modul pencarian: mengubah pertanyaan jadi vektor lalu mencari chunk termirip."""

import chromadb
from sentence_transformers import SentenceTransformer

from app.core.config import settings


class Retriever:
    """Mencari potongan dokumen yang paling relevan dengan sebuah pertanyaan.

    Model dan koneksi database dimuat sekali saat objek dibuat,
    lalu dipakai berulang. Inilah yang membuat pencarian berikutnya cepat.
    """

    def __init__(self) -> None:
        self._model = SentenceTransformer(
            settings.EMBEDDING_MODEL,
            device=settings.EMBEDDING_DEVICE,
        )
        client = chromadb.PersistentClient(path=settings.CHROMA_DIR)
        self._collection = client.get_collection(settings.CHROMA_COLLECTION)

    def search(self, question: str, top_k: int = 5) -> list[dict]:
        """Mengembalikan top_k chunk paling relevan, terurut dari yang termirip."""
        query_vector = self._model.encode(
            question,
            normalize_embeddings=True,
        ).tolist()

        result = self._collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
        )

        chunks = []
        for i in range(len(result["ids"][0])):
            distance = result["distances"][0][i]
            chunks.append({
                "id": result["ids"][0][i],
                "text": result["documents"][0][i],
                "metadata": result["metadatas"][0][i],
                "similarity": round(1 - distance, 4),
            })

        return chunks

    def count(self) -> int:
        return self._collection.count()