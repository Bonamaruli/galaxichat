"""Menyaring dataset instruksi agar kualitasnya lebih seragam.

Membuang pasangan yang jawabannya terlalu pendek, pertanyaannya menyalin
kalimat dokumen, atau isinya duplikat.
"""

import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "instruction_dataset.jsonl"
OUTPUT_FILE = BASE_DIR / "data" / "instruction_dataset_clean.jsonl"

MIN_ANSWER_CHARS = 80
MIN_ANSWER_SENTENCES = 1
MIN_QUESTION_CHARS = 20
MAX_OVERLAP_RATIO = 0.85


def count_sentences(text: str) -> int:
    return len([s for s in re.split(r"[.!?]+", text) if s.strip()])


def word_overlap(question: str, answer: str) -> float:
    """Seberapa besar kata pertanyaan muncul lagi di jawaban.

    Nilai tinggi menandakan pertanyaan hanya membalik kalimat jawaban,
    bukan pertanyaan alami dari orang awam.
    """
    q_words = set(re.findall(r"\w+", question.lower()))
    a_words = set(re.findall(r"\w+", answer.lower()))

    if not q_words:
        return 1.0
    return len(q_words & a_words) / len(q_words)


def main() -> None:
    pairs = []
    with INPUT_FILE.open(encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                pairs.append(json.loads(line))

    print(f"Pasangan awal: {len(pairs)}\n")

    kept = []
    seen_questions = set()
    reasons = {
        "jawaban terlalu pendek": 0,
        "jawaban kurang dari 2 kalimat": 0,
        "pertanyaan terlalu pendek": 0,
        "pertanyaan menyalin jawaban": 0,
        "duplikat": 0,
    }

    for pair in pairs:
        question = pair["instruction"]
        answer = pair["output"]

        if len(answer) < MIN_ANSWER_CHARS:
            reasons["jawaban terlalu pendek"] += 1
            continue

        if count_sentences(answer) < MIN_ANSWER_SENTENCES:
            reasons["jawaban kurang dari 2 kalimat"] += 1
            continue

        if len(question) < MIN_QUESTION_CHARS:
            reasons["pertanyaan terlalu pendek"] += 1
            continue

        if word_overlap(question, answer) > MAX_OVERLAP_RATIO:
            reasons["pertanyaan menyalin jawaban"] += 1
            continue

        key = question.lower().strip()
        if key in seen_questions:
            reasons["duplikat"] += 1
            continue

        seen_questions.add(key)
        kept.append(pair)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        for pair in kept:
            file.write(json.dumps(pair, ensure_ascii=False) + "\n")

    print("Dibuang:")
    for reason, count in reasons.items():
        if count:
            print(f"  {reason:<32} {count:>4}")

    total_removed = sum(reasons.values())
    print(f"\nTotal dibuang : {total_removed}")
    print(f"Tersisa       : {len(kept)}  ({len(kept) / len(pairs) * 100:.1f}%)")

    lengths = [len(p["output"]) for p in kept]
    print(f"Panjang jawaban: rata-rata {sum(lengths) // len(lengths)} karakter, "
          f"terpendek {min(lengths)}, terpanjang {max(lengths)}")
    print(f"\nTersimpan: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()