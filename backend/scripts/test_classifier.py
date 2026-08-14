"""Menguji modul classifier dengan sampel nyata dari dataset.

Mengambil beberapa contoh per kelas, plus kasus yang paling
membuat model ragu, lalu membandingkan tebakan dengan label asli.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import joblib
import pandas as pd

from app.services.classifier import sky_classifier

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "sdss" / "sdss_prepared.csv"
MODEL_FILE = BASE_DIR / "data" / "models" / "sdss_classifier.joblib"

BANDS = ["u", "g", "r", "i", "z"]
SAMPLES_PER_CLASS = 4


def show(title: str, rows: pd.DataFrame) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)
    print(f"{'Asli':<8} {'Tebakan':<10} {'Yakin':>7}  {'Status':<7} {'u-g':>7} {'g-r':>7}")
    print("-" * 78)

    correct = 0
    for _, row in rows.iterrows():
        result = sky_classifier.predict(**{b: float(row[b]) for b in BANDS})

        actual = row["class"]
        predicted = result["predicted_class"]
        is_right = actual == predicted
        correct += int(is_right)

        ci = result["color_index"]
        print(
            f"{actual:<8} {result['label']:<10} "
            f"{result['confidence'] * 100:>6.1f}%  "
            f"{'BENAR' if is_right else 'SALAH':<7} "
            f"{ci['u-g']:>7.3f} {ci['g-r']:>7.3f}"
        )

    print("-" * 78)
    print(f"Benar: {correct}/{len(rows)}")


def main() -> None:
    df = pd.read_csv(DATA_FILE)

    # 1. Sampel acak per kelas
    balanced = pd.concat([
        group.sample(SAMPLES_PER_CLASS, random_state=7)
        for _, group in df.groupby("class")
    ])
    show("SAMPEL ACAK DARI TIAP KELAS", balanced)

    # 2. Kasus yang paling membuat model ragu
    bundle = joblib.load(MODEL_FILE)
    probabilities = bundle["model"].predict_proba(df[bundle["features"]])
    df = df.assign(confidence=probabilities.max(axis=1))

    show("KASUS PALING MERAGUKAN (kepercayaan terendah)", df.nsmallest(6, "confidence"))

    # 3. Kasus yang paling meyakinkan
    show("KASUS PALING MEYAKINKAN", df.nlargest(3, "confidence"))

    # 4. Validasi nilai rusak
    print("\n" + "=" * 78)
    print("UJI VALIDASI NILAI RUSAK")
    print("=" * 78)
    try:
        sky_classifier.predict(u=-9999, g=22.0, r=20.0, i=19.0, z=18.0)
        print("GAGAL: nilai rusak seharusnya ditolak!")
    except ValueError as error:
        print(f"Ditolak dengan benar: {error}")


if __name__ == "__main__":
    main()