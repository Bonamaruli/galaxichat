"""Mengubah chunk menjadi vektor dan menyimpannya ke ChromaDB.

Dijalankan MANUAL, hanya saat dokumen atau konfigurasi berubah.
Backend tidak pernah menjalankan proses ini.
"""

import json
import sys
import time
from pathlib import Path

# Agar skrip di folder scripts/ bisa mengimpor modul dari app/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import chromadb
from sentence_transformers import SentenceTransformer

from app.core.config import settings

BASE_DIR = Path(__file__).resolve().parent.parent
CHUNKS_FILE = BASE_DIR / "data" / "chunks.json"

BATCH_SIZE = 8


def load_chunks() -> list[dict]:
    if not CHUNKS_FILE.exists():
        raise SystemExit(
            f"{CHUNKS_FILE} tidak ditemukan. Jalankan chunk_docs.py terlebih dahulu."
        )
    return json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))


def main() -> None:
    chunks = load_chunks()
    print(f"Memuat {len(chunks)} chunk dari chunks.json")

    print(f"\nMemuat model: {settings.EMBEDDING_MODEL}")
    print(f"Perangkat   : {settings.EMBEDDING_DEVICE}")
    start = time.perf_counter()

    model = SentenceTransformer(
        settings.EMBEDDING_MODEL,
        device=settings.EMBEDDING_DEVICE,
    )

    print(f"Model siap dalam {time.perf_counter() - start:.1f} detik")
    print(f"Dimensi vektor: {model.get_embedding_dimension()}")

    texts = [c["text"] for c in chunks]

    print(f"\nMenghitung embedding untuk {len(texts)} chunk...")
    start = time.perf_counter()

    vectors = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    elapsed = time.perf_counter() - start
    print(f"Selesai dalam {elapsed:.1f} detik ({len(texts) / elapsed:.1f} chunk/detik)")

    # Menyimpan ke ChromaDB
    client = chromadb.PersistentClient(path=settings.CHROMA_DIR)

    existing = [c.name for c in client.list_collections()]
    if settings.CHROMA_COLLECTION in existing:
        print(f"\nMenghapus koleksi lama: {settings.CHROMA_COLLECTION}")
        client.delete_collection(settings.CHROMA_COLLECTION)

    collection = client.create_collection(
        name=settings.CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )

    print("Menyimpan ke ChromaDB...")

    for i in range(0, len(chunks), 100):
        batch = chunks[i:i + 100]
        collection.add(
            ids=[c["id"] for c in batch],
            embeddings=vectors[i:i + 100].tolist(),
            documents=[c["text"] for c in batch],
            metadatas=[
                {
                    "source": c["source"],
                    "url": c["url"],
                    "heading": c["heading"],
                    "source_file": c["source_file"],
                }
                for c in batch
            ],
        )

    print(f"\nTersimpan: {collection.count()} chunk")
    print(f"Lokasi    : {settings.CHROMA_DIR}")


if __name__ == "__main__":
    main()