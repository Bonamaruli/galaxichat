"""Menggambar pohon keputusan agar logikanya bisa dibaca manusia.

Menghasilkan dua keluaran: gambar PNG dan aturan dalam bentuk teks.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # tanpa jendela GUI

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree, export_text

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "sdss" / "sdss_prepared.csv"
OUTPUT_DIR = BASE_DIR / "data" / "sdss"

BANDS = ["u", "g", "r", "i", "z"]
COLORS = ["u_g", "g_r", "r_i", "i_z", "u_z"]
FEATURES = BANDS + COLORS          # skenario B

RANDOM_STATE = 42
VIZ_DEPTH = 3                      # dangkal, agar gambarnya terbaca


def main() -> None:
    df = pd.read_csv(DATA_FILE)

    X_train, _, y_train, _ = train_test_split(
        df[FEATURES], df["class"],
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=df["class"],
    )

    model = DecisionTreeClassifier(max_depth=VIZ_DEPTH, random_state=RANDOM_STATE)
    model.fit(X_train, y_train)

    # 1. Aturan dalam bentuk teks
    rules = export_text(model, feature_names=FEATURES, decimals=3)
    print("=" * 70)
    print(f"ATURAN POHON KEPUTUSAN (kedalaman {VIZ_DEPTH})")
    print("=" * 70)
    print(rules)

    (OUTPUT_DIR / "tree_rules.txt").write_text(rules, encoding="utf-8")

    # 2. Gambar
    fig, ax = plt.subplots(figsize=(24, 12))
    plot_tree(
        model,
        feature_names=FEATURES,
        class_names=model.classes_,
        filled=True,
        rounded=True,
        fontsize=9,
        impurity=False,
        proportion=True,
        ax=ax,
    )
    ax.set_title(
        f"Decision Tree Klasifikasi Objek Langit (kedalaman {VIZ_DEPTH})",
        fontsize=16,
    )
    fig.tight_layout()

    png_path = OUTPUT_DIR / "decision_tree.png"
    fig.savefig(png_path, dpi=110, bbox_inches="tight")
    plt.close(fig)

    print(f"\nGambar tersimpan : {png_path}")
    print(f"Aturan tersimpan : {OUTPUT_DIR / 'tree_rules.txt'}")


if __name__ == "__main__":
    main()