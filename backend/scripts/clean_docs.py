"""Membersihkan dokumen mentah agar layak diproses menjadi chunk.

Membaca dari data/raw/, menulis hasil bersih ke data/documents/.
Data mentah tidak pernah diubah.
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
CLEAN_DIR = BASE_DIR / "data" / "documents"

MIN_WORDS = 200

# Bagian Wikipedia yang isinya hanya daftar tautan, tidak berguna untuk chatbot.
STOP_SECTIONS = {
    "referensi", "rujukan", "pranala luar", "lihat pula",
    "catatan kaki", "catatan", "bacaan lebih lanjut",
    "daftar pustaka", "galeri", "sumber",
}


def remove_latex_blocks(text: str) -> str:
    """Menghapus blok {\\displaystyle ...} termasuk kurung bersarang."""
    result = []
    i = 0
    while True:
        start = text.find("{\\displaystyle", i)
        if start == -1:
            result.append(text[i:])
            break
        result.append(text[i:start])
        depth = 0
        j = start
        while j < len(text):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1
        i = j
    return "".join(result)


def is_junk_line(line: str) -> bool:
    """Mendeteksi baris sisa rumus: terlalu pendek atau tanpa huruf sama sekali."""
    stripped = line.strip()
    if not stripped:
        return False
    if not re.search(r"[a-zA-Z\u00C0-\u024F]", stripped):
        return True
    if len(stripped) < 4 and not stripped.endswith((".", ":", "?")):
        return True
    return False


def cut_stop_sections(text: str) -> str:
    """Memotong dokumen saat mencapai bagian seperti Referensi atau Pranala luar."""
    lines = text.split("\n")
    for index, line in enumerate(lines):
        heading = line.strip().strip("=").strip().lower()
        if heading in STOP_SECTIONS:
            return "\n".join(lines[:index])
    return text


def clean(text: str) -> str:
    text = remove_latex_blocks(text)
    text = re.sub(r"\\[a-zA-Z]+\{?", " ", text)      # sisa perintah LaTeX
    text = cut_stop_sections(text)

    lines = [line for line in text.split("\n") if not is_junk_line(line)]
    lines = [re.sub(r"[ \t]+", " ", line).rstrip() for line in lines]

    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)            # maksimal satu baris kosong
    return text.strip()


def main() -> None:
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(RAW_DIR.glob("*.txt"))

    if not files:
        raise SystemExit(f"Tidak ada file .txt di {RAW_DIR}")

    print(f"{'File':<45} {'Sebelum':>9} {'Sesudah':>9}  Status")
    print("-" * 80)

    kept = 0
    for path in files:
        raw = path.read_text(encoding="utf-8")

        # Header sumber di 4 baris pertama dipertahankan apa adanya.
        parts = raw.split("---", 1)
        header, body = (parts[0], parts[1]) if len(parts) == 2 else ("", raw)

        cleaned = clean(body)
        before = len(body.split())
        after = len(cleaned.split())

        if after < MIN_WORDS:
            print(f"{path.name:<45} {before:>9} {after:>9}  DILEWATI (terlalu pendek)")
            continue

        output = f"{header.strip()}\n---\n\n{cleaned}\n"
        (CLEAN_DIR / path.name).write_text(output, encoding="utf-8")
        removed_pct = round((1 - after / before) * 100) if before else 0
        print(f"{path.name:<45} {before:>9} {after:>9}  bersih (-{removed_pct}%)")
        kept += 1

    print("-" * 80)
    print(f"{kept} dari {len(files)} file siap dipakai. Lokasi: {CLEAN_DIR}")


if __name__ == "__main__":
    main()