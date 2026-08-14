"""Eksplorasi awal dataset SDSS sebelum melatih model.

Tujuannya memahami bentuk data, menemukan nilai rusak, dan
mengecek keseimbangan kelas. Belum ada machine learning di sini.
"""

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_FILE = BASE_DIR / "data" / "sdss" / "star_classification.csv"

BANDS = ["u", "g", "r", "i", "z"]


def main() -> None:
    if not CSV_FILE.exists():
        raise SystemExit(f"File tidak ditemukan: {CSV_FILE}")

    df = pd.read_csv(CSV_FILE)

    print(f"Jumlah baris  : {len(df):,}")
    print(f"Jumlah kolom  : {len(df.columns)}")
    print(f"\nNama kolom:\n{list(df.columns)}")

    # 1. Keseimbangan kelas
    print("\n" + "=" * 60)
    print("DISTRIBUSI KELAS")
    print("=" * 60)
    counts = df["class"].value_counts()
    for label, n in counts.items():
        pct = n / len(df) * 100
        bar = "#" * int(pct / 2)
        print(f"{label:<8} {n:>7,}  ({pct:5.1f}%)  {bar}")

    # 2. Nilai kosong
    print("\n" + "=" * 60)
    print("NILAI KOSONG (NaN)")
    print("=" * 60)
    missing = df.isnull().sum()
    total_missing = missing.sum()
    if total_missing == 0:
        print("Tidak ada nilai kosong.")
    else:
        print(missing[missing > 0])

    # 3. Nilai rusak pada kolom fotometri
    print("\n" + "=" * 60)
    print("NILAI RUSAK PADA KOLOM FOTOMETRI")
    print("=" * 60)
    print(f"{'Kolom':<8} {'Min':>12} {'Maks':>10} {'Rusak':>8}")
    print("-" * 42)

    broken_rows = pd.Series(False, index=df.index)
    for band in BANDS:
        is_broken = df[band] < 0
        broken_rows |= is_broken
        print(
            f"{band:<8} {df[band].min():>12.2f} {df[band].max():>10.2f} "
            f"{is_broken.sum():>8}"
        )

    print(f"\nTotal baris yang punya minimal 1 nilai rusak: {broken_rows.sum()}")

    # 4. Statistik setelah baris rusak dibuang
    clean = df[~broken_rows]
    print(f"Sisa baris bersih: {len(clean):,}")

    print("\n" + "=" * 60)
    print("RATA-RATA KECERAHAN PER KELAS (data bersih)")
    print("=" * 60)
    print(clean.groupby("class")[BANDS + ["redshift"]].mean().round(3))

    # 5. Contoh baris
    print("\n" + "=" * 60)
    print("CONTOH 5 BARIS PERTAMA (kolom penting saja)")
    print("=" * 60)
    print(clean[BANDS + ["redshift", "class"]].head().to_string())


if __name__ == "__main__":
    main()