"""Menghasilkan dataset instruksi dari chunk dokumen menggunakan LLM.

Dapat dijalankan berulang: chunk yang sudah pernah diproses akan dilewati,
dan hasil sebelumnya tidak tertimpa.
"""

import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.llm import LLMClient

BASE_DIR = Path(__file__).resolve().parent.parent
CHUNKS_FILE = BASE_DIR / "data" / "chunks.json"
OUTPUT_FILE = BASE_DIR / "data" / "instruction_dataset.jsonl"

TARGET_PAIRS = 300
GENERATOR_PROVIDER = "groq"   # penyedia khusus untuk membuat dataset
CHUNKS_TO_USE = 180           # tiap chunk menghasilkan ~2 pasangan
MIN_CHUNK_CHARS = 400
RANDOM_SEED = 42
REQUEST_DELAY = 0.3

GENERATOR_PROMPT = """Kamu adalah pembuat dataset latih untuk model bahasa.

Dari POTONGAN DOKUMEN yang diberikan, buat 2 pasangan pertanyaan-jawaban dalam bahasa Indonesia.

ATURAN:
1. Pertanyaan harus terdengar alami, seperti orang awam bertanya. Jangan menyalin kalimat dokumen menjadi pertanyaan.
2. Jawaban HARUS sepenuhnya berdasarkan potongan dokumen. Jangan menambahkan informasi dari luar.
3. Jawaban ringkas: 2 sampai 4 kalimat.
4. Kedua pertanyaan harus menanyakan hal yang berbeda.
5. Jika potongan tidak memuat informasi yang cukup untuk membuat pertanyaan bermakna, kembalikan array kosong.

Balas HANYA dengan JSON array, tanpa penjelasan apa pun, tanpa tanda kutip markdown:
[{"instruction": "...", "output": "..."}, {"instruction": "...", "output": "..."}]"""


def parse_response(text: str) -> list[dict]:
    """Membersihkan pagar markdown lalu mengurai JSON."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        return []

    if not isinstance(data, list):
        return []

    valid = []
    for item in data:
        if not isinstance(item, dict):
            continue
        question = item.get("instruction", "").strip()
        answer = item.get("output", "").strip()
        if len(question) > 10 and len(answer) > 30:
            valid.append({"instruction": question, "output": answer})
    return valid


def load_existing() -> tuple[list[dict], set[str]]:
    """Membaca hasil sebelumnya agar tidak diproses ulang."""
    if not OUTPUT_FILE.exists():
        return [], set()

    pairs = []
    with OUTPUT_FILE.open(encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                pairs.append(json.loads(line))

    done = {p["source_chunk"] for p in pairs if "source_chunk" in p}
    return pairs, done


def main() -> None:
    chunks = json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))
    usable = [c for c in chunks if len(c["text"]) >= MIN_CHUNK_CHARS]

    existing_pairs, done_chunks = load_existing()

    random.seed(RANDOM_SEED)
    all_selected = random.sample(usable, min(CHUNKS_TO_USE, len(usable)))

    # Lewati chunk yang sudah pernah menghasilkan pasangan.
    selected = [c for c in all_selected if c["id"] not in done_chunks]

    generator = LLMClient(provider=GENERATOR_PROVIDER)

    print(f"Penyedia generator : {generator.provider}")
    print(f"Chunk tersedia     : {len(usable)}")
    print(f"Sudah diproses     : {len(done_chunks)}")
    print(f"Sisa antrean       : {len(selected)}")
    print(f"Pasangan terkumpul : {len(existing_pairs)}")
    print(f"Target             : {TARGET_PAIRS}\n")

    pairs = list(existing_pairs)
    failed = 0

    for index, chunk in enumerate(selected, start=1):
        if len(pairs) >= TARGET_PAIRS:
            print("\nTarget tercapai, berhenti.")
            break

        message = f"POTONGAN DOKUMEN:\n{chunk['text']}"

        try:
            response = generator.generate(
                user_message=message,
                system_prompt=GENERATOR_PROMPT,
            )
            new_pairs = parse_response(response)
        except Exception as error:
            print(f"  [{index}] gagal: {error}")
            failed += 1
            time.sleep(3)
            continue

        for pair in new_pairs:
            pair["source_chunk"] = chunk["id"]
        pairs.extend(new_pairs)

        print(f"  [{index}/{len(selected)}] +{len(new_pairs)} pasangan "
              f"(total {len(pairs)})")

        time.sleep(REQUEST_DELAY)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        for pair in pairs:
            file.write(json.dumps(pair, ensure_ascii=False) + "\n")

    print(f"\nTotal pasangan : {len(pairs)}")
    print(f"Chunk gagal    : {failed}")
    print(f"Tersimpan      : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()