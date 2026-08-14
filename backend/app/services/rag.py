"""Merangkai pencarian dokumen dengan LLM menjadi satu alur jawaban."""

from app.core.llm import llm_client
from app.services.retriever import Retriever

TOP_K = 5
MIN_SIMILARITY = 0.45

GREETING_WORDS = {
    "halo", "hai", "hi", "hello", "hey", "woi", "woy",
    "pagi", "siang", "sore", "malam",
    "assalamualaikum", "salam", "permisi",
    "test", "tes", "coba", "ping",
}

GREETING_REPLY = (
    "Halo! Saya Galaxichat, asisten untuk pertanyaan seputar astronomi "
    "dan alam semesta. Coba tanyakan tentang tata surya, bintang, galaksi, "
    "lubang hitam, atau topik luar angkasa lainnya."
)

OUT_OF_SCOPE_REPLY = (
    "Maaf, pertanyaan itu sepertinya di luar topik astronomi yang saya kuasai. "
    "Coba tanyakan tentang tata surya, bintang, galaksi, lubang hitam, "
    "atau topik alam semesta lainnya."
)

RAG_SYSTEM_PROMPT = """Kamu adalah Galaxichat, asisten yang menjelaskan astronomi dan alam semesta dalam bahasa Indonesia.

ATURAN YANG WAJIB KAMU PATUHI:
1. Jawab HANYA berdasarkan KONTEKS yang diberikan di bawah. Jangan menggunakan pengetahuanmu sendiri di luar konteks tersebut.
2. Jika konteks tidak memuat jawaban atas pertanyaan, katakan dengan jujur: "Maaf, informasi itu tidak ada dalam dokumen yang saya miliki." Jangan mengarang, jangan menebak, dan jangan melengkapi dari pengetahuan umummu.
3. Jangan menyebutkan kata "konteks" atau "dokumen yang diberikan" dalam jawabanmu. Jawab secara alami.
4. Jawab dengan ringkas, jelas, dan mudah dipahami orang awam.
5. Jika konteks hanya menjawab sebagian, jawab bagian yang ada dan katakan bagian mana yang tidak tersedia."""


class RagService:
    """Alur lengkap: cari potongan relevan, susun prompt, minta jawaban ke LLM."""

    def __init__(self) -> None:
        self._retriever = Retriever()

    def _build_context(self, chunks: list[dict]) -> str:
        """Menyusun potongan dokumen menjadi satu blok teks bernomor."""
        blocks = []
        for index, chunk in enumerate(chunks, start=1):
            source = chunk["metadata"]["source"]
            blocks.append(f"[Dokumen {index} - {source}]\n{chunk['text']}")
        return "\n\n".join(blocks)

    def _collect_sources(self, chunks: list[dict]) -> list[dict]:
        """Mengumpulkan sumber unik agar tidak tampil berulang."""
        seen = set()
        sources = []
        for chunk in chunks:
            meta = chunk["metadata"]
            key = meta["source"]
            if key in seen:
                continue
            seen.add(key)
            sources.append({
                "source": meta["source"],
                "url": meta.get("url", ""),
                "heading": meta.get("heading", ""),
                "similarity": chunk["similarity"],
            })
        return sources

    def _is_greeting(self, question: str) -> bool:
        """Mendeteksi sapaan singkat agar tidak diperlakukan sebagai pertanyaan."""
        words = [w.strip(".,!?") for w in question.lower().split()]

        # Hanya dianggap sapaan jika pesannya pendek DAN seluruh katanya sapaan.
        if not words or len(words) > 3:
            return False

        return all(word in GREETING_WORDS for word in words)

    def answer(self, question: str) -> dict:
        # Sapaan ditangani lebih dulu agar tidak memanggil pencarian maupun LLM.
        if self._is_greeting(question):
            return {
                "answer": GREETING_REPLY,
                "sources": [],
                "chunks_used": 0,
                "top_similarity": 0.0,
            }

        chunks = self._retriever.search(question, top_k=TOP_K)

        # Saring potongan yang terlalu jauh maknanya dari pertanyaan.
        relevant = [c for c in chunks if c["similarity"] >= MIN_SIMILARITY]

        if not relevant:
            return {
                "answer": OUT_OF_SCOPE_REPLY,
                "sources": [],
                "chunks_used": 0,
                "top_similarity": chunks[0]["similarity"] if chunks else 0.0,
            }

        context = self._build_context(relevant)
        user_message = (
            f"KONTEKS:\n{context}\n\n"
            f"PERTANYAAN: {question}\n\n"
            f"Jawab pertanyaan di atas berdasarkan konteks yang diberikan."
        )

        answer = llm_client.generate(
            user_message=user_message,
            system_prompt=RAG_SYSTEM_PROMPT,
        )

        return {
            "answer": answer,
            "sources": self._collect_sources(relevant),
            "chunks_used": len(relevant),
            "top_similarity": relevant[0]["similarity"],
        }


rag_service = RagService()