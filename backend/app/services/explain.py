"""Menerjemahkan hasil klasifikasi menjadi penjelasan berbahasa manusia."""

from app.core.llm import llm_client
from app.services.classifier import sky_classifier

EXPLAIN_SYSTEM_PROMPT = """Kamu adalah Galaxichat, asisten astronomi berbahasa Indonesia.

Tugasmu menjelaskan hasil klasifikasi objek langit kepada orang awam.

ATURAN:
1. Jangan mengubah atau meragukan hasil klasifikasi. Hasil itu berasal dari model machine learning, bukan dari kamu.
2. Jelaskan secara singkat apa itu objek yang terklasifikasi tersebut.
3. Kaitkan penjelasanmu dengan nilai indeks warna yang diberikan. Indeks warna adalah selisih kecerahan antar filter; nilai kecil berarti cahaya merata di seluruh spektrum (sumber sangat panas), nilai besar berarti objek jauh lebih redup di ultraviolet (didominasi cahaya kemerahan).
4. Sebutkan tingkat keyakinan model. Jika keyakinan di bawah 70 persen, katakan terus terang bahwa hasil ini kurang pasti dan sebutkan kelas alternatif yang mungkin.
5. Jawab maksimal 4 kalimat, dengan bahasa yang mudah dipahami.
6. Jangan menyebut istilah teknis seperti "model", "fitur", atau "probabilitas" secara berlebihan.
7. Jika nilai indeks warna TIDAK mendukung kelas yang diprediksi, katakan itu apa adanya. Jangan mengarang penjelasan yang seolah-olah mendukung. Sebagai acuan: Quasar biasanya punya indeks warna kecil (di bawah 0,7) karena cahayanya merata dan kuat di ultraviolet. Galaksi punya indeks warna besar (di atas 1,3) karena didominasi bintang tua kemerahan. Bintang berada di antara keduanya."""


class ExplainService:
    def explain(self, u: float, g: float, r: float, i: float, z: float) -> dict:
        result = sky_classifier.predict(u=u, g=g, r=r, i=i, z=z)

        colors = ", ".join(f"{k} = {v}" for k, v in result["color_index"].items())
        probs = ", ".join(f"{k} {v * 100:.1f}%" for k, v in result["probabilities"].items())

        user_message = (
            f"HASIL KLASIFIKASI:\n"
            f"Jenis objek: {result['label']}\n"
            f"Keyakinan: {result['confidence'] * 100:.1f}%\n"
            f"Rincian kemungkinan: {probs}\n"
            f"Indeks warna: {colors}\n\n"
            f"Jelaskan hasil ini kepada pengguna awam."
        )

        explanation = llm_client.generate(
            user_message=user_message,
            system_prompt=EXPLAIN_SYSTEM_PROMPT,
        )

        return {**result, "explanation": explanation}


explain_service = ExplainService()