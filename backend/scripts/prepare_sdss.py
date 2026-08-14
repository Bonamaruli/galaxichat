"""Membersihkan dataset SDSS dan membuat fitur color index.

Hasilnya disimpan sebagai CSV siap latih, agar proses ini
tidak perlu diulang setiap kali melatih model.
"""

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_FILE = BASE_DIR / "data" / "sdss" / "star_classification.csv"
OUTPUT_FILE = BASE_DIR / "data" / "sdss" / "sdss_prepared.csv"

BANDS = ["u", "g", "r", "i", "z"]

# Pasangan filter yang bersebelahan dalam spektrum.
COLOR_PAIRS = [("u", "g"), ("g", "r"), ("r", "i"), ("i", "z")]


def main() -> None:
    df = pd.read_csv(RAW_FILE)
    print(f"Baris awal: {len(df):,}")

    # 1. Buang baris dengan nilai fotometri rusak (-9999)
    valid = (df[BANDS] > 0).all(axis=1)
    df = df[valid].copy()
    print(f"Setelah buang nilai rusak: {len(df):,}")

    # 2. Buat fitur color index
    for first, second in COLOR_PAIRS:
        df[f"{first}_{second}"] = df[first] - df[second]

    # 3. Selisih ujung ke ujung: rentang warna total
    df["u_z"] = df["u"] - df["z"]

    color_features = [f"{a}_{b}" for a, b in COLOR_PAIRS] + ["u_z"]

    # 4. Simpan hanya kolom yang dipakai
    keep = BANDS + color_features + ["redshift", "class"]
    df = df[keep]

    df.to_csv(OUTPUT_FILE, index=False)

    print(f"\nFitur color index yang dibuat: {color_features}")
    print(f"Total kolom fitur: {len(BANDS) + len(color_features)} (+ redshift)")

    print("\n" + "=" * 66)
    print("RATA-RATA COLOR INDEX PER KELAS")
    print("=" * 66)
    print(df.groupby("class")[color_features].mean().round(3))

    print("\n" + "=" * 66)
    print("SIMPANGAN BAKU (makin kecil = makin konsisten dalam satu kelas)")
    print("=" * 66)
    print(df.groupby("class")[color_features].std().round(3))

    print(f"\nTersimpan: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()