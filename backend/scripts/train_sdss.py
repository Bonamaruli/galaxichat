"""Melatih Decision Tree untuk klasifikasi objek langit.

Melatih tiga skenario untuk membandingkan pengaruh pilihan fitur,
terutama untuk menguji apakah redshift menyebabkan ketergantungan berlebih.
"""

from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "sdss" / "sdss_prepared.csv"

BANDS = ["u", "g", "r", "i", "z"]
COLORS = ["u_g", "g_r", "r_i", "i_z", "u_z"]

SCENARIOS = {
    "A. Fotometri mentah saja": BANDS,
    "B. Mentah + color index": BANDS + COLORS,
    "C. Semua + redshift": BANDS + COLORS + ["redshift"],
}

RANDOM_STATE = 42
MAX_DEPTH = 5


def run(name: str, features: list[str], df: pd.DataFrame) -> dict:
    X = df[features]
    y = df["class"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    model = DecisionTreeClassifier(
        max_depth=MAX_DEPTH,
        random_state=RANDOM_STATE,
    )
    model.fit(X_train, y_train)

    acc_train = accuracy_score(y_train, model.predict(X_train))
    acc_test = accuracy_score(y_test, model.predict(X_test))

    print("\n" + "=" * 68)
    print(name)
    print("=" * 68)
    print(f"Jumlah fitur   : {len(features)}")
    print(f"Akurasi latih  : {acc_train * 100:.2f}%")
    print(f"Akurasi uji    : {acc_test * 100:.2f}%")
    print(f"Selisih        : {(acc_train - acc_test) * 100:+.2f}%  (besar = overfitting)")

    print("\nLaporan per kelas (data uji):")
    print(classification_report(y_test, model.predict(X_test), digits=3))

    importance = (
        pd.Series(model.feature_importances_, index=features)
        .sort_values(ascending=False)
    )
    print("Kontribusi fitur (hanya yang > 0):")
    for feat, score in importance[importance > 0].items():
        bar = "#" * int(score * 50)
        print(f"  {feat:<10} {score:.4f}  {bar}")

    return {"name": name, "acc_test": acc_test, "model": model, "features": features}


def main() -> None:
    df = pd.read_csv(DATA_FILE)
    print(f"Total data: {len(df):,} baris")

    # Baseline: kalau model asal menebak kelas terbanyak
    majority = df["class"].value_counts(normalize=True).max()
    print(f"Baseline (selalu tebak kelas mayoritas): {majority * 100:.2f}%")

    results = [run(name, feats, df) for name, feats in SCENARIOS.items()]

    print("\n" + "=" * 68)
    print("RINGKASAN")
    print("=" * 68)
    for r in results:
        print(f"{r['name']:<32} {r['acc_test'] * 100:6.2f}%")


if __name__ == "__main__":
    main()