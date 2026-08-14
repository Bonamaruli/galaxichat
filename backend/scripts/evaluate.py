"""Menjalankan seluruh pertanyaan uji dan menghitung akurasi retrieval.

Dipakai untuk membandingkan konfigurasi (nilai K, ukuran chunk, model embedding)
secara terukur, bukan berdasarkan kesan.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.retriever import Retriever
from app.services.rag import MIN_SIMILARITY

BASE_DIR = Path(__file__).resolve().parent.parent
QUESTIONS_FILE = BASE_DIR / "data" / "eval_questions.json"
REPORT_FILE = BASE_DIR / "data" / "eval_report.json"

TOP_K = 5


def evaluate_one(retriever: Retriever, item: dict) -> dict:
    results = retriever.search(item["question"], top_k=TOP_K)
    top_score = results[0]["similarity"] if results else 0.0

    files = [r["metadata"]["source_file"] for r in results]
    expected = item.get("expected_source")
    category = item["category"]

    # Apakah dokumen yang benar ada di peringkat 1, dan di 5 besar?
    hit_at_1 = bool(expected) and files[0] == expected
    hit_at_k = bool(expected) and expected in files

    # Apakah sistem akan menolak pertanyaan ini sebelum memanggil LLM?
    rejected = top_score < MIN_SIMILARITY

    if category == "di_luar_topik":
        correct = rejected
    elif category == "tidak_ada_di_dokumen":
        # Idealnya ditolak; kalau lolos, pertahanan tinggal system prompt.
        correct = rejected
    else:
        correct = hit_at_k

    return {
        "id": item["id"],
        "question": item["question"],
        "category": category,
        "expected_source": expected,
        "top_file": files[0] if files else None,
        "top_score": round(top_score, 4),
        "hit_at_1": hit_at_1,
        "hit_at_k": hit_at_k,
        "rejected": rejected,
        "correct": correct,
    }


def main() -> None:
    items = json.loads(QUESTIONS_FILE.read_text(encoding="utf-8"))

    print("Memuat model dan database...")
    retriever = Retriever()
    print(f"Siap. {retriever.count()} chunk tersedia.")
    print(f"Konfigurasi: TOP_K={TOP_K}, ambang={MIN_SIMILARITY}\n")

    rows = [evaluate_one(retriever, item) for item in items]

    print(f"{'ID':>3} {'Skor':>7} {'@1':>4} {'@5':>4} {'Tolak':>6}  Pertanyaan")
    print("-" * 78)
    for r in rows:
        mark = lambda b: " ok " if b else "  - "
        print(
            f"{r['id']:>3} {r['top_score']:>7.4f} "
            f"{mark(r['hit_at_1'])} {mark(r['hit_at_k'])} "
            f"{mark(r['rejected']):>6}  {r['question'][:42]}"
        )

    # Ringkasan per kategori
    print("\n" + "=" * 78)
    categories = {}
    for r in rows:
        c = categories.setdefault(r["category"], {"total": 0, "correct": 0})
        c["total"] += 1
        c["correct"] += int(r["correct"])

    for name, c in categories.items():
        pct = c["correct"] / c["total"] * 100
        print(f"{name:<24} {c['correct']:>2}/{c['total']:<3} ({pct:5.1f}%)")

    in_doc = [r for r in rows if r["category"] == "ada_di_dokumen"]
    if in_doc:
        p1 = sum(r["hit_at_1"] for r in in_doc) / len(in_doc) * 100
        pk = sum(r["hit_at_k"] for r in in_doc) / len(in_doc) * 100
        print(f"\nPrecision@1  : {p1:5.1f}%")
        print(f"Recall@{TOP_K}     : {pk:5.1f}%")

    total_correct = sum(r["correct"] for r in rows)
    print(f"Akurasi total: {total_correct / len(rows) * 100:5.1f}%  ({total_correct}/{len(rows)})")

    REPORT_FILE.write_text(
        json.dumps(
            {"config": {"top_k": TOP_K, "min_similarity": MIN_SIMILARITY}, "results": rows},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nLaporan tersimpan: {REPORT_FILE}")


if __name__ == "__main__":
    main()