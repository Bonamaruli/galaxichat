"""Mengambil dokumen astronomi dari sumber terbuka secara otomatis.

Dijalankan manual saat ingin menambah dokumen. Hasilnya disimpan
sebagai file .txt di data/documents/.
"""

import re
import time
from pathlib import Path

import trafilatura
import wikipediaapi

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "documents"
USER_AGENT = "Galaxichat/0.1 (proyek edukasi mahasiswa)"

WIKIPEDIA_TOPICS = [
    "Tata Surya",
    "Lubang hitam",
    "Bima Sakti",
    "Bintang",
    "Nebula",
    "Galaksi",
    "Ledakan Dahsyat",
    "Planet",
    "Matahari",
    "Bulan",
    "Supernova",
    "Eksoplanet",
]

OPENSTAX_URLS = [
    "https://openstax.org/books/astronomy-2e/pages/1-6-a-tour-of-the-universe",
    "https://openstax.org/books/astronomy-2e/pages/1-7-the-universe-on-the-large-scale",
]


def make_filename(prefix: str, title: str) -> str:
    """Mengubah judul jadi nama file yang aman: huruf kecil, tanpa spasi."""
    clean = re.sub(r"[^\w\s-]", "", title.lower())
    clean = re.sub(r"[\s_]+", "-", clean).strip("-")
    return f"{prefix}-{clean}.txt"


def save_document(filename: str, header: str, body: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    path.write_text(f"{header}\n---\n\n{body}\n", encoding="utf-8")
    word_count = len(body.split())
    print(f"  tersimpan: {filename} ({word_count} kata)")


def fetch_wikipedia() -> None:
    print("\n=== Wikipedia Indonesia ===")
    wiki = wikipediaapi.Wikipedia(user_agent=USER_AGENT, language="id")

    for topic in WIKIPEDIA_TOPICS:
        page = wiki.page(topic)

        if not page.exists():
            print(f"  DILEWATI (tidak ada): {topic}")
            continue

        if len(page.text.split()) < 200:
            print(f"  DILEWATI (terlalu pendek): {topic}")
            continue

        header = (
            f"Sumber: Wikipedia Bahasa Indonesia - {page.title}\n"
            f"URL: {page.fullurl}\n"
            f"Lisensi: CC BY-SA 4.0"
        )
        save_document(make_filename("wikipedia-id", page.title), header, page.text)
        time.sleep(1)


def fetch_openstax() -> None:
    print("\n=== OpenStax Astronomy 2e ===")

    for url in OPENSTAX_URLS:
        downloaded = trafilatura.fetch_url(url)

        if not downloaded:
            print(f"  GAGAL diunduh: {url}")
            continue

        text = trafilatura.extract(downloaded, include_comments=False)

        if not text or len(text.split()) < 200:
            print(f"  GAGAL diekstrak (kemungkinan halaman JavaScript): {url}")
            continue

        slug = url.rstrip("/").split("/")[-1]
        header = (
            f"Sumber: OpenStax Astronomy 2e\n"
            f"URL: {url}\n"
            f"Lisensi: CC BY 4.0"
        )
        save_document(f"openstax-{slug}.txt", header, text)
        time.sleep(2)


if __name__ == "__main__":
    fetch_wikipedia()
    fetch_openstax()
    print(f"\nSelesai. Cek folder: {OUTPUT_DIR}")