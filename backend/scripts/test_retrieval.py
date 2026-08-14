"""Menguji kualitas pencarian secara interaktif, tanpa melibatkan LLM."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.retriever import Retriever

TOP_K = 5
PREVIEW_CHARS = 200


def main() -> None:
    print("Memuat model dan database...")
    start = time.perf_counter()
    retriever = Retriever()
    print(f"Siap dalam {time.perf_counter() - start:.1f} detik")
    print(f"Total chunk tersedia: {retriever.count()}")
    print("\nKetik pertanyaan (kosongkan lalu Enter untuk keluar)\n")

    while True:
        question = input("Pertanyaan > ").strip()
        if not question:
            print("Selesai.")
            break

        start = time.perf_counter()
        results = retriever.search(question, top_k=TOP_K)
        elapsed = (time.perf_counter() - start) * 1000

        print(f"\n  Ditemukan {len(results)} chunk dalam {elapsed:.0f} ms\n")

        for rank, chunk in enumerate(results, start=1):
            meta = chunk["metadata"]
            preview = chunk["text"].replace("\n", " ")[:PREVIEW_CHARS]

            print(f"  [{rank}] skor {chunk['similarity']:.4f}  |  {meta['source']}")
            if meta.get("heading"):
                print(f"      bagian: {meta['heading']}")
            print(f"      {preview}...")
            print()

        print("-" * 70)


if __name__ == "__main__":
    main()