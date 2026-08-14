# Galaxichat — Checklist Progres per Sub-Tahap

**Diperbarui:** 8 Agustus 2026, malam
**Sisa waktu:** 22 hari (masuk kuliah 31 Agustus)
**Progres:** 2 dari 5 tahap wajib selesai

---

## ✅ TAHAP 0 — Persiapan (SELESAI)

- [x] **0.1** Python 3.11.9, Git 2.51, Node.js v24 terpasang
- [x] **0.2** Folder proyek di lokasi aman (tanpa spasi, di luar OneDrive)
- [x] **0.3** Struktur monorepo: backend / frontend / docs
- [x] **0.4** Virtual environment di `backend/venv`
- [x] **0.5** `.gitignore` untuk Python dan Node
- [x] **0.6** Git aktif + `.gitkeep` agar struktur folder terlacak

---

## ✅ TAHAP 1 — Fondasi Backend & LLM (SELESAI)

- [x] **1.1** Install FastAPI, uvicorn, python-dotenv, google-genai
- [x] **1.2** `requirements.txt` dibuat
- [x] **1.3** API key Gemini disimpan di `.env` (+ `.env.example`)
- [x] **1.4** Uji koneksi lewat `scripts/test_llm.py`
- [x] **1.5** `app/core/config.py` — konfigurasi terpusat
- [x] **1.6** `app/core/llm.py` — lapisan abstraksi LLM
- [x] **1.7** `app/api/chat.py` — endpoint `/api/chat`
- [x] **1.8** `app/main.py` — perakit aplikasi + `/health`
- [x] **1.9** Uji lewat `/docs`, eksperimen system prompt bajak laut

**Pemahaman:** system prompt vs user prompt, environment variable, separation of concerns, loose coupling, temperature.

---

## ✅ TAHAP 2 — Pipeline Data & Embedding (SELESAI)

- [x] **2.1** `scripts/fetch_docs.py` — unduh otomatis dari Wikipedia & web
- [x] **2.2** Pisahkan `data/raw/` (mentah) dan `data/documents/` (bersih)
- [x] **2.3** `scripts/clean_docs.py` — bersihkan sisa LaTeX & bagian tak berguna
- [x] **2.4** `scripts/chunk_docs.py` — pemotongan dasar (800 char, overlap 150)
- [x] **2.5** Perbaikan: chunking sadar struktur + konteks judul bagian
- [x] **2.6** Install sentence-transformers & chromadb
- [x] **2.7** Perbaiki PyTorch CPU → CUDA
- [x] **2.8** `scripts/ingest.py` — embedding + simpan ke ChromaDB
- [x] **2.9** Eksperimen batch size (8 / 16 / 32) + catat hasilnya
- [x] **2.10** Semua data dikeluarkan dari pelacakan Git

**Angka hasil:** 14 dokumen → 69.000 kata → 949 chunk → 949 vektor (1024 dimensi).
Model siap 12 detik, embedding 21 detik (45 chunk/detik), GPU RTX 4050.

**Pemahaman:** chunking & overlap, embedding, vector DB vs relasional, idempoten, pipeline offline vs online.

**Sisa PR:** tulis `docs/catatan-tahap-2.md` (jawaban pertanyaan uji nomor 2, 4, 5).

---

## ▶ TAHAP 3 — Retrieval & Perakitan RAG
**Perkiraan 3–4 hari**

### Bagian A — Pencarian (paling memuaskan, ringan)
- [ ] **3.1** `app/services/retriever.py` — muat model & koneksi ChromaDB
- [ ] **3.2** Ubah pertanyaan jadi vektor, cari chunk termirip
- [ ] **3.3** Skrip uji: ketik pertanyaan → lihat 5 chunk teratas + skor kemiripan
- [ ] **3.4** Uji pertanyaan yang tidak mengandung kata sama persis
- [ ] **3.5** Uji pertanyaan di luar topik (harus skornya rendah)

### Bagian B — Sambungkan ke LLM
- [ ] **3.6** Susun chunk hasil pencarian ke dalam prompt
- [ ] **3.7** Tulis ulang system prompt agar terikat dokumen
- [ ] **3.8** Endpoint `/api/chat` versi RAG
- [ ] **3.9** Tampilkan sumber jawaban (nama dokumen + URL)
- [ ] **3.10** Uji: apakah masih mengarang saat jawabannya tidak ada di dokumen?

### Bagian C — Evaluasi & Penyetelan
- [ ] **3.11** Buat 20 pertanyaan uji + jawaban seharusnya
- [ ] **3.12** Ukur berapa yang benar, catat angkanya
- [ ] **3.13** Eksperimen nilai K (3 vs 5 vs 10), bandingkan
- [ ] **3.14** Eksperimen ukuran chunk (600 vs 800 vs 1000)
- [ ] **3.15** Catat hasil terbaik + alasannya

**Konsep:** cosine similarity, top-K retrieval, prompt engineering RAG, halusinasi, evaluasi terukur.

---

## TAHAP 4 — Klasifikasi Objek Langit (SDSS)
**Perkiraan 4–5 hari**

### Bagian A — Data & Pemahaman
- [ ] **4.1** Unduh dataset SDSS (bintang / galaksi / quasar)
- [ ] **4.2** Eksplorasi: lihat isi, cek jumlah tiap kelas
- [ ] **4.3** Pahami arti kolom u, g, r, i, z (filter warna)
- [ ] **4.4** Feature engineering: buat color index (u−g, g−r, r−i, i−z)

### Bagian B — Model
- [ ] **4.5** Train/test split
- [ ] **4.6** Latih Decision Tree
- [ ] **4.7** **Gambar pohonnya**, baca aturan keputusannya
- [ ] **4.8** Latih Random Forest, bandingkan
- [ ] **4.9** Evaluasi: confusion matrix, precision, recall, F1
- [ ] **4.10** Simpan model terlatih (.joblib)

### Bagian C — Integrasi
- [ ] **4.11** `app/services/classifier.py`
- [ ] **4.12** Endpoint `/api/classify`
- [ ] **4.13** Sambungkan hasil klasifikasi ke penjelasan LLM

**Konsep:** supervised learning, feature engineering, overfitting, confusion matrix, class imbalance.

---

## TAHAP 5 — Frontend React & Portofolio
**Perkiraan 3–4 hari**

### Bagian A — Antarmuka
- [ ] **5.1** Buat proyek React + Vite di `frontend/`
- [ ] **5.2** Atasi CORS di backend
- [ ] **5.3** Komponen chat: input, daftar pesan, indikator loading
- [ ] **5.4** Tampilkan sumber jawaban di UI
- [ ] **5.5** Panel klasifikasi objek langit
- [ ] **5.6** Penanganan error yang ramah pengguna

### Bagian B — Portofolio
- [ ] **5.7** README: masalah → solusi → arsitektur → hasil → cara jalankan
- [ ] **5.8** Diagram arsitektur di `docs/`
- [ ] **5.9** Rekam demo singkat
- [ ] **5.10** Push ke GitHub
- [ ] **5.11** Tulis satu post LinkedIn tentang proses belajarnya

**Konsep:** CORS, JSON, state management, UX untuk loading & error.

---

## TAHAP 6 (OPSIONAL) — LoRA Fine-tuning
**Perkiraan 1–3 hari, atau ditunda ke semester 5**

- [ ] **6.1** Susun dataset instruksi (100–300 pasangan tanya-jawab)
- [ ] **6.2** Pahami format instruction-tuning
- [ ] **6.3** Latih model kecil (1–3B) dengan QLoRA
- [ ] **6.4** Bandingkan dengan RAG: akurasi, biaya, kemudahan update
- [ ] **6.5** Tulis kesimpulan → jadi bahan proposal TA

---

## Ringkasan progres

| Tahap | Sub-tahap | Status |
|---|---|---|
| 0 — Persiapan | 6/6 | Selesai |
| 1 — Backend & LLM | 9/9 | Selesai |
| 2 — Pipeline & Embedding | 10/10 | Selesai |
| 3 — Retrieval & RAG | 0/15 | Berikutnya |
| 4 — Klasifikasi SDSS | 0/13 | Belum |
| 5 — Frontend & Portofolio | 0/11 | Belum |
| 6 — Fine-tuning (opsional) | 0/5 | Belum |

**Total wajib: 25 dari 64 sub-tahap selesai (39%)**

Perkiraan selesai: sekitar 24–26 Agustus, menyisakan ~5 hari untuk Tahap 6 atau penyempurnaan.

---

## Yang boleh dikorbankan kalau tertinggal

Urutan prioritas untuk dilepas: **Tahap 6** dulu → kedalaman **5.3–5.6** (UI seadanya asal jalan) → eksperimen **3.13–3.14**.

**Jangan pernah lepas:** 3.1–3.10 dan 4.1–4.10. Itu inti yang paling sering ditanya penguji.

Ukuran keberhasilan sebenarnya bukan semua kotak tercentang, tapi: **bisakah kamu menjelaskan cara kerja sistemmu ke teman sampai dia paham?**
