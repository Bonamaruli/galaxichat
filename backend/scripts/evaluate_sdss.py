"""Evaluasi mendalam model klasifikasi dan penyimpanan model final.

Melatih model utama (skenario B) dan pembanding (skenario C),
menampilkan confusion matrix, lalu menyimpan keduanya.
"""

from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "sdss" / "sdss_prepared.csv"
MODEL_DIR = BASE_DIR / "data" / "models"
OUTPUT_DIR = BASE_DIR / "data" / "sdss"

BANDS = ["u", "g", "r", "i", "z"]
COLORS = ["u_g", "g_r", "r_i", "i_z", "u_z"]
FEATURES_B = BANDS + COLORS
FEATURES_C = FEATURES_B + ["redshift"]

RANDOM_STATE = 42
MAX_DEPTH = 15


def train_and_evaluate(name: str, features: list[str], df: pd.DataFrame):
    X_train, X_test, y_train, y_test = train_test_split(
        df[features], df["class"],
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=df["class"],
    )

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=MAX_DEPTH,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    pred = model.predict(X_test)

    print("\n" + "=" * 70)
    print(name)
    print("=" * 70)
    print(f"Akurasi uji: {accuracy_score(y_test, pred) * 100:.2f}%\n")
    print(classification_report(y_test, pred, digits=3))

    labels = list(model.classes_)
    cm = confusion_matrix(y_test, pred, labels=labels)

    print("CONFUSION MATRIX (baris = sebenarnya, kolom = tebakan)")
    print(f"{'':<10}" + "".join(f"{l:>9}" for l in labels))
    for i, actual in enumerate(labels):
        row = "".join(f"{cm[i][j]:>9,}" for j in range(len(labels)))
        print(f"{actual:<10}{row}")

    # Kesalahan terbesar
    print("\nKesalahan terbesar:")
    errors = []
    for i, actual in enumerate(labels):
        for j, predicted in enumerate(labels):
            if i != j and cm[i][j] > 0:
                pct = cm[i][j] / cm[i].sum() * 100
                errors.append((cm[i][j], pct, actual, predicted))
    for count, pct, actual, predicted in sorted(errors, reverse=True)[:3]:
        print(f"  {actual} ditebak {predicted}: {count:,} kasus ({pct:.1f}% dari {actual})")

    return model, cm, labels


def plot_confusion(cm, labels, title: str, filename: str) -> None:
    cm_pct = cm / cm.sum(axis=1, keepdims=True) * 100

    fig, ax = plt.subplots(figsize=(7, 5.5))
    sns.heatmap(
        cm_pct, annot=True, fmt=".1f", cmap="Blues",
        xticklabels=labels, yticklabels=labels,
        cbar_kws={"label": "% dari kelas sebenarnya"}, ax=ax,
    )
    ax.set_xlabel("Tebakan model")
    ax.set_ylabel("Kelas sebenarnya")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / filename, dpi=120)
    plt.close(fig)


def main() -> None:
    df = pd.read_csv(DATA_FILE)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    model_b, cm_b, labels = train_and_evaluate(
        "MODEL UTAMA — Skenario B (fotometri saja)", FEATURES_B, df
    )
    plot_confusion(cm_b, labels, "Model B — fotometri saja", "confusion_b.png")

    model_c, cm_c, _ = train_and_evaluate(
        "PEMBANDING — Skenario C (dengan redshift)", FEATURES_C, df
    )
    plot_confusion(cm_c, labels, "Model C — dengan redshift", "confusion_c.png")

    # Simpan model beserta daftar fiturnya
    joblib.dump(
        {"model": model_b, "features": FEATURES_B, "classes": list(model_b.classes_)},
        MODEL_DIR / "sdss_classifier.joblib",
    )
    joblib.dump(
        {"model": model_c, "features": FEATURES_C, "classes": list(model_c.classes_)},
        MODEL_DIR / "sdss_classifier_redshift.joblib",
    )

    size = (MODEL_DIR / "sdss_classifier.joblib").stat().st_size / 1024 / 1024
    print(f"\nModel utama tersimpan ({size:.1f} MB): {MODEL_DIR / 'sdss_classifier.joblib'}")
    print(f"Gambar confusion matrix: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()