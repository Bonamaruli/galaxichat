"""Memotong dokumen bersih menjadi chunk yang sadar struktur.

Judul bagian tidak dibuang, melainkan ditempelkan sebagai konteks
pada setiap chunk agar potongan tetap bermakna saat berdiri sendiri.
"""

import json
import re
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "data" / "documents"
OUTPUT_FILE = BASE_DIR / "data" / "chunks.json"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
MIN_CONTENT_CHARS = 120


def parse_header(raw: str) -> tuple[dict, str]:
    """Memisahkan keterangan sumber dari isi dokumen."""
    if "---" not in raw:
        return {}, raw

    header_text, body = raw.split("---", 1)
    metadata = {}

    for line in header_text.strip().split("\n"):
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip().lower()] = value.strip()

    return metadata, body.strip()


def looks_like_heading(line: str) -> bool:
    """Menebak apakah sebuah baris adalah judul bagian, bukan kalimat isi."""
    text = line.strip()

    if not text or len(text) > 80:
        return False
    if len(text.split()) > 8:
        return False
    if text.endswith((".", ",", ";", ":", "!", "?")):
        return False
    if not re.search(r"[a-zA-Z\u00C0-\u024F]", text):
        return False

    return True


def split_into_sections(body: str) -> list[tuple[str, str]]:
    """Memecah dokumen menjadi pasangan (judul bagian, isi)."""
    sections = []
    current_heading = ""
    buffer: list[str] = []

    for line in body.split("\n"):
        if looks_like_heading(line):
            if buffer:
                sections.append((current_heading, "\n".join(buffer).strip()))
                buffer = []
            current_heading = line.strip()
        else:
            buffer.append(line)

    if buffer:
        sections.append((current_heading, "\n".join(buffer).strip()))

    return [(h, t) for h, t in sections if t]


def build_title(metadata: dict, fallback: str) -> str:
    """Mengambil judul dokumen yang ringkas dari keterangan sumber."""
    source = metadata.get("sumber", fallback)
    return source.split(" - ")[-1].strip() if " - " in source else source


def main() -> None:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    files = sorted(DOCS_DIR.glob("*.txt"))
    if not files:
        raise SystemExit(f"Tidak ada file .txt di {DOCS_DIR}")

    all_chunks = []
    total_skipped = 0

    print(f"{'File':<45} {'Chunk':>7} {'Dibuang':>8}")
    print("-" * 63)

    for path in files:
        raw = path.read_text(encoding="utf-8")
        metadata, body = parse_header(raw)
        title = build_title(metadata, path.stem)

        kept = 0
        skipped = 0
        index = 0

        for heading, section_text in split_into_sections(body):
            for piece in splitter.split_text(section_text):
                if len(piece.strip()) < MIN_CONTENT_CHARS:
                    skipped += 1
                    continue

                context = f"{title} > {heading}" if heading else title
                enriched = f"[{context}]\n\n{piece.strip()}"

                all_chunks.append({
                    "id": f"{path.stem}::{index}",
                    "text": enriched,
                    "heading": heading,
                    "source_file": path.name,
                    "source": metadata.get("sumber", path.stem),
                    "url": metadata.get("url", ""),
                    "chunk_index": index,
                    "char_count": len(enriched),
                })
                index += 1
                kept += 1

        total_skipped += skipped
        print(f"{path.name:<45} {kept:>7} {skipped:>8}")

    OUTPUT_FILE.write_text(
        json.dumps(all_chunks, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    sizes = [c["char_count"] for c in all_chunks]
    print("-" * 63)
    print(f"Total chunk       : {len(all_chunks)}")
    print(f"Dibuang           : {total_skipped} (terlalu pendek)")
    print(f"Rata-rata ukuran  : {sum(sizes) // len(sizes)} karakter")
    print(f"Terkecil          : {min(sizes)} karakter")
    print(f"Terbesar          : {max(sizes)} karakter")
    print(f"Tersimpan di      : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()