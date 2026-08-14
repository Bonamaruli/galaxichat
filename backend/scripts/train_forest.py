"""Membandingkan Decision Tree dan Random Forest pada berbagai kedalaman.

Melatih skenario B (tanpa redshift) sebagai model utama,
dan skenario C (dengan redshift) sebagai pembanding.
"""

from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, recall_score

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "sdss" / "sdss_prepared.csv"

BANDS = ["u", "g", "r", "i", "z"]
COLORS = ["u_g", "g_r", "r_i", "i_z", "u_z"]
FEATURES_B = BANDS + COLORS
FEATURES_C = FEATURES_B + ["redshift"]

RANDOM_STATE = 42
DEPTHS = [3, 5, 10, 15, None]


def split(df: pd.DataFrame, features: list[str]):
    return train_test_split(
        df[features], df["class"],
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=df["class"],
    )


def report(model, X_train, X_test, y_train, y_test) -> tuple:
    model.fit(X_train, y_train)
    pred_train = model.predict(X_train)
    pred_test = model.predict(X_test)

    acc_train = accuracy_score(y_train, pred_train)
    acc_test = accuracy_score(y_test, pred_test)

    # Recall khusus kelas STAR, kelas paling bermasalah
    recall_star = recall_score(y_test, pred_test, labels=["STAR"], average="macro")

    return acc_train, acc_test, recall_star


def main() -> None:
    df = pd.read_csv(DATA_FILE)
    X_train, X_test, y_train, y_test = split(df, FEATURES_B)

    print("=" * 74)
    print("SKENARIO B (tanpa redshift) — pengaruh kedalaman")
    print("=" * 74)
    print(f"{'Model':<16} {'Depth':>6} {'Latih':>8} {'Uji':>8} {'Selisih':>9} {'Recall STAR':>12}")
    print("-" * 74)

    for depth in DEPTHS:
        tree = DecisionTreeClassifier(max_depth=depth, random_state=RANDOM_STATE)
        a_tr, a_te, r_star = report(tree, X_train, X_test, y_train, y_test)
        label = str(depth) if depth else "tanpa batas"
        print(
            f"{'Decision Tree':<16} {label:>6} {a_tr*100:>7.2f}% {a_te*100:>7.2f}% "
            f"{(a_tr-a_te)*100:>+8.2f}% {r_star*100:>11.2f}%"
        )

    print()
    for depth in DEPTHS:
        forest = RandomForestClassifier(
            n_estimators=100,
            max_depth=depth,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )
        a_tr, a_te, r_star = report(forest, X_train, X_test, y_train, y_test)
        label = str(depth) if depth else "tanpa batas"
        print(
            f"{'Random Forest':<16} {label:>6} {a_tr*100:>7.2f}% {a_te*100:>7.2f}% "
            f"{(a_tr-a_te)*100:>+8.2f}% {r_star*100:>11.2f}%"
        )

    # Pembanding: skenario C
    print("\n" + "=" * 74)
    print("SKENARIO C (dengan redshift) — pembanding")
    print("=" * 74)
    Xc_train, Xc_test, yc_train, yc_test = split(df, FEATURES_C)
    forest_c = RandomForestClassifier(
        n_estimators=100, max_depth=15, random_state=RANDOM_STATE, n_jobs=-1
    )
    a_tr, a_te, r_star = report(forest_c, Xc_train, Xc_test, yc_train, yc_test)
    print(f"Random Forest depth=15: uji {a_te*100:.2f}%, recall STAR {r_star*100:.2f}%")


if __name__ == "__main__":
    main()