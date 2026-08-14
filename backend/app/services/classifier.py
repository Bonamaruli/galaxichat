"""Modul klasifikasi objek langit berdasarkan data fotometri SDSS."""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_FILE = BASE_DIR / "data" / "models" / "sdss_classifier.joblib"

CLASS_LABELS = {
    "GALAXY": "Galaksi",
    "QSO": "Quasar",
    "STAR": "Bintang",
}

COLOR_PAIRS = [("u", "g"), ("g", "r"), ("r", "i"), ("i", "z")]


class SkyClassifier:
    """Menebak jenis objek langit dari lima nilai kecerahan fotometri."""

    def __init__(self) -> None:
        if not MODEL_FILE.exists():
            raise FileNotFoundError(
                f"Model tidak ditemukan: {MODEL_FILE}. "
                "Jalankan scripts/evaluate_sdss.py terlebih dahulu."
            )

        bundle = joblib.load(MODEL_FILE)
        self._model = bundle["model"]
        self._features = bundle["features"]
        self._classes = bundle["classes"]

    def _build_features(self, bands: dict) -> "pd.DataFrame":
        """Menghitung color index lalu menyusun fitur sesuai urutan saat pelatihan."""
        values = dict(bands)

        for first, second in COLOR_PAIRS:
            values[f"{first}_{second}"] = bands[first] - bands[second]
        values["u_z"] = bands["u"] - bands["z"]

        # Urutan dan nama kolom wajib sama persis dengan saat model dilatih.
        return pd.DataFrame([[values[name] for name in self._features]],
                            columns=self._features)

    def predict(self, u: float, g: float, r: float, i: float, z: float) -> dict:
        bands = {"u": u, "g": g, "r": r, "i": i, "z": z}

        for name, value in bands.items():
            if value <= 0 or value > 40:
                raise ValueError(
                    f"Nilai {name}={value} di luar rentang wajar (0-40). "
                    "Nilai -9999 menandakan pengukuran gagal."
                )

        X = self._build_features(bands)
        probabilities = self._model.predict_proba(X)[0]
        best_index = int(np.argmax(probabilities))
        predicted = self._classes[best_index]

        return {
            "predicted_class": predicted,
            "label": CLASS_LABELS.get(predicted, predicted),
            "confidence": round(float(probabilities[best_index]), 4),
            "probabilities": {
                CLASS_LABELS.get(cls, cls): round(float(p), 4)
                for cls, p in zip(self._classes, probabilities)
            },
            "color_index": {
                f"{a}-{b}": round(bands[a] - bands[b], 4) for a, b in COLOR_PAIRS
            },
        }


sky_classifier = SkyClassifier()