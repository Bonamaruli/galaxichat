# Galaxichat

Asisten astronomi berbahasa Indonesia yang menjawab dari dokumen terverifikasi, dilengkapi pengklasifikasi objek langit berbasis machine learning.

Dibangun sebagai proyek pembelajaran untuk memahami RAG (Retrieval-Augmented Generation) dan machine learning klasik secara menyeluruh — bukan sekadar merangkai library, tetapi mengukur, membandingkan, dan memahami setiap keputusan desainnya.

---

## Masalah yang diselesaikan

Chatbot berbasis LLM umumnya menjawab dari pengetahuan internal modelnya. Untuk topik edukasi seperti astronomi, ini bermasalah:

- **Jawaban tidak dapat diverifikasi.** Pengguna tidak tahu informasi itu berasal dari mana.
- **Model dapat mengarang** dengan sangat meyakinkan ketika tidak tahu jawabannya.
- **Pengetahuan tidak dapat diperbarui** tanpa melatih ulang model.

Galaxichat mengatasi ini dengan mengambil potongan dokumen yang relevan terlebih dahulu, lalu meminta LLM menjawab **hanya** berdasarkan potongan tersebut — lengkap dengan sitasi sumber yang dapat diklik.

---

## Fitur

**Chat berbasis RAG.** Setiap jawaban disertai dokumen sumber, nama bagian, dan skor kemiripan. Pertanyaan di luar topik ditolak sebelum memanggil LLM sehingga tidak memboroskan kuota API.

**Klasifikasi objek langit.** Menentukan apakah sebuah objek adalah bintang, galaksi, atau quasar berdasarkan lima nilai fotometri, kemudian menerjemahkan hasilnya menjadi penjelasan berbahasa manusia.

**Transparansi ketidakpastian.** Ketika model tidak yakin, sistem mengatakannya — bukan menyajikan tebakan lemah seolah pasti.

---

## Arsitektur

```
┌─────────────── PIPELINE OFFLINE (dijalankan manual) ───────────────┐
│                                                                    │
│  Wikipedia ID        data/raw        data/documents      949       │
│  + OpenStax     →    14 dokumen   →   69.000 kata     →  chunk  →  │
│                                                                    │
│    fetch_docs      clean_docs        chunk_docs         ingest     │
│                                                          ↓         │
└──────────────────────────────────────────────────────────────────┘
                                                      ChromaDB
                                                    (1024 dimensi)
                                                          ↑
┌─────────────── RUNTIME (saat pengguna bertanya) ────────┼─────────┐
│                                                          │         │
│  Pertanyaan  →  Retriever  →  RagService  →  Gemini  →  Jawaban   │
│                (cari top-5)   (susun konteks)          + sumber   │
│                                                                    │
│  Ambang 0,45: di bawah ini pertanyaan ditolak tanpa memanggil LLM │
└────────────────────────────────────────────────────────────────────┘
```

Keputusan arsitektur terpenting adalah **pemisahan pipeline offline dan runtime**. Seluruh proses berat — mengunduh, membersihkan, memotong, dan menghitung embedding — dijalankan manual dan hasilnya disimpan permanen. Backend hanya membaca hasil yang sudah jadi.

Dampaknya: backend menyala dalam hitungan detik, bukan menit.

---

## Teknologi

| Lapisan | Teknologi |
|---|---|
| Backend | Python 3.11, FastAPI, Uvicorn |
| Embedding | BAAI/bge-m3 (lokal, GPU) — 1024 dimensi |
| Vector database | ChromaDB (embedded, ruang cosine/HNSW) |
| LLM | Google Gemini 2.5 Flash via API |
| Machine learning | scikit-learn — Random Forest |
| Frontend | React 19, Vite, Tailwind CSS v4, React Router |

Embedding dijalankan lokal, LLM lewat API. Pembagian ini disengaja: model embedding cukup ringan untuk GPU 6 GB dan bebas kuota, sementara LLM berkualitas membutuhkan sumber daya yang tidak tersedia di perangkat pengembangan.

---

## Hasil pengukuran

### Sistem RAG

Diuji dengan 20 pertanyaan dalam empat kategori. Pertanyaan sengaja ditulis dengan kata-kata yang berbeda dari dokumen, untuk menguji pencarian berbasis makna.

| Metrik | Nilai |
|---|---|
| Recall@5 | 100% |
| Precision@1 | 85,7% |
| Penolakan pertanyaan di luar topik | 3/3 (100%) |
| Waktu pencarian | ~22 ms |

Konfigurasi terpilih: chunk 800 karakter, overlap 150, K=5, ambang kemiripan 0,45.

**Eksperimen nilai K:**

| K | Precision@1 | Recall@K |
|---|---|---|
| 3 | 85,7% | 92,9% |
| **5** | **85,7%** | **100%** |
| 10 | 85,7% | 100% |

K=3 kehilangan 7% recall; K=10 tidak menambah recall tetapi menggandakan panjang konteks yang dikirim ke LLM.

**Eksperimen ukuran chunk:**

| Chunk | Jumlah | Precision@1 | Recall@5 |
|---|---|---|---|
| 600 | 1212 | 92,9% | 92,9% |
| **800** | **949** | **85,7%** | **100%** |
| 1000 | 771 | 85,7% | 100% |

Chunk kecil menaikkan precision tetapi menurunkan recall — potongan pendek lebih fokus namun memecah informasi yang tersebar. Untuk RAG, recall lebih penting karena seluruh potongan teratas dikirim ke LLM.

### Klasifikasi objek langit

Dataset SDSS17, 100.000 objek. Dilatih dua skenario untuk menguji pengaruh kolom `redshift`.

| | Model B (fotometri saja) | Model C (+ redshift) |
|---|---|---|
| Akurasi | 88,50% | 97,91% |
| Recall STAR | 76,3% | 100,0% |
| Recall QSO | 81,2% | 93,2% |
| Data yang dibutuhkan | Fotometri | Fotometri + spektroskopi |

**Model B dipilih sebagai model utama meskipun akurasinya lebih rendah.**

Alasannya: `redshift` menyumbang 93% keputusan pada Model C, dan nilai tersebut hanya dapat diperoleh melalui spektroskopi — pengukuran yang jauh lebih mahal dan lambat. Model yang bergantung padanya tidak menjawab masalah aslinya, yaitu klasifikasi cepat dari data citra. Ini kasus *data leakage*: memakai informasi yang tidak akan tersedia saat sistem dipakai sungguhan.

Fitur yang dipakai Model B adalah lima nilai fotometri mentah ditambah lima *color index* hasil rekayasa fitur (u−g, g−r, r−i, i−z, u−z). Penambahan color index menaikkan akurasi dari 76,3% ke 83,3% pada Decision Tree — dua fitur teratas yang dipakai model adalah fitur turunan tersebut.

---

## Keterbatasan yang diketahui

Bagian ini disertakan karena mengetahui batas sistem sama pentingnya dengan mengetahui kemampuannya.

### Ambang kemiripan tunggal tidak dapat memisahkan "topik mirip" dari "ada jawaban"

Sebaran skor pada konfigurasi terpilih:

| Kelompok | Rentang skor tertinggi |
|---|---|
| Ada di dokumen | 0,6260 – 0,7345 |
| Tidak ada di dokumen | 0,5471 – 0,6258 |
| Di luar topik | 0,3549 – 0,4141 |

Kelompok "di luar topik" terpisah bersih dan ditolak dengan aman oleh ambang 0,45.

Namun kelompok "tidak ada di dokumen" bertumpang tindih dengan kelompok "ada di dokumen": skor tertinggi kelompok kedua adalah **0,6258**, sedangkan skor terendah kelompok pertama adalah **0,6260** — selisih **0,0002**. Secara matematis tidak ada nilai ambang tunggal yang dapat memisahkan keduanya.

### Pengetatan system prompt tidak sepenuhnya menahan halusinasi

Diuji pada pertanyaan "kenapa langit malam gelap padahal ada banyak bintang" (paradoks Olbers — tidak tersedia dalam korpus). LLM menyusun penjelasan sebab-akibat yang tidak dinyatakan dalam potongan mana pun.

Memperketat system prompt dengan larangan eksplisit mengurangi elaborasi tetapi tidak menghilangkan klaim utamanya, sekaligus memperburuk kualitas jawaban pada pertanyaan yang sebelumnya berhasil.

### Akar masalahnya adalah cakupan dokumen

Kategori "tidak ada di dokumen" tetap 0% pada **seluruh** konfigurasi yang diuji — mengubah K, ukuran chunk, maupun prompt tidak menyentuhnya sama sekali. Menambah dokumen yang relevan menyelesaikannya secara langsung.

Implikasinya: kualitas sistem RAG lebih ditentukan oleh cakupan dan kualitas korpus daripada oleh penyetelan parameter.

### Metrik recall@5 hanya mengukur dokumen, bukan potongan

Sistem dihitung berhasil apabila dokumen yang benar ditemukan, meskipun potongan spesifik yang memuat jawaban tidak masuk peringkat teratas. Pada satu kasus pengujian, jawaban yang dihasilkan kurang lengkap meski metriknya tercatat berhasil.

### Bintang dan galaksi sulit dibedakan dari fotometri

Kesalahan terbesar Model B adalah 647 bintang diklasifikasikan sebagai galaksi (15% dari seluruh bintang). Hal ini konsisten dengan sebaran color index keduanya yang bertumpang tindih, dan masuk akal secara fisika karena galaksi pada dasarnya adalah kumpulan bintang.

---

## Menjalankan proyek

### Prasyarat

- Python 3.11
- Node.js 18 atau lebih baru
- API key Google Gemini ([Google AI Studio](https://aistudio.google.com), gratis)
- GPU NVIDIA dengan CUDA (opsional — tanpa GPU, embedding tetap berjalan di CPU namun lebih lambat)

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
```

Salin `.env.example` menjadi `.env`, lalu isi API key:

```
GEMINI_API_KEY=isi_dengan_api_key_anda
GEMINI_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=BAAI/bge-m3
EMBEDDING_DEVICE=cuda          # ganti menjadi cpu bila tanpa GPU
CHROMA_COLLECTION=galaxichat_docs
```

Bangun basis pengetahuan (dijalankan sekali):

```bash
python scripts/fetch_docs.py     # unduh dokumen dari sumber terbuka
python scripts/clean_docs.py     # bersihkan sisa LaTeX dan bagian tak berguna
python scripts/chunk_docs.py     # potong menjadi chunk yang sadar struktur
python scripts/ingest.py         # hitung embedding, simpan ke ChromaDB
```

Latih pengklasifikasi:

```bash
# Unduh star_classification.csv dari Kaggle (Stellar Classification Dataset SDSS17)
# Simpan ke backend/data/sdss/

python scripts/prepare_sdss.py   # bersihkan data, buat fitur color index
python scripts/evaluate_sdss.py  # latih, evaluasi, simpan model
```

Jalankan server:

```bash
uvicorn app.main:app --reload
```

Dokumentasi API interaktif tersedia di `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
```

Buat berkas `.env`:

```
VITE_API_URL=http://localhost:8000
```

```bash
npm run dev
```

Aplikasi berjalan di `http://localhost:5173`.

---

## Struktur proyek

```
galaxichat/
├── backend/
│   ├── app/
│   │   ├── core/          konfigurasi terpusat, lapisan abstraksi LLM
│   │   ├── services/      retriever, RAG, classifier, explain
│   │   └── api/           endpoint chat dan classify
│   ├── data/              dokumen, vektor, model (tidak masuk Git)
│   └── scripts/           pipeline offline dan skrip evaluasi
├── frontend/
│   └── src/
│       ├── components/    navbar, layout, komponen chat
│       ├── pages/         Home, Chat, Klasifikasi
│       └── lib/           API client terpusat
└── docs/                  catatan eksperimen, diagram, gambar hasil
```

Isi folder `data/` sengaja tidak disertakan dalam Git karena seluruhnya dapat dibuat ulang dari skrip yang ada. Yang disimpan adalah resepnya, bukan hasilnya.

Satu pengecualian: `data/eval_questions.json` tetap disertakan karena ditulis manual dan berfungsi sebagai alat ukur — perbandingan antar konfigurasi hanya sah bila diuji dengan pertanyaan yang identik.

---

## Skrip evaluasi

```bash
python scripts/test_retrieval.py    # uji pencarian secara interaktif
python scripts/evaluate.py          # jalankan 20 pertanyaan uji, hitung akurasi
python scripts/test_classifier.py   # uji classifier dengan sampel dataset
python scripts/visualize_tree.py    # gambar pohon keputusan
```

`scripts/evaluate.py` sengaja tidak memanggil LLM. Alasannya, LLM dapat memberi jawaban berbeda untuk pertanyaan yang sama, sehingga hasilnya tidak dapat dipakai membandingkan konfigurasi. Metrik retrieval bersifat deterministik.

---

## Sumber data

| Sumber | Lisensi | Penggunaan |
|---|---|---|
| Wikipedia Bahasa Indonesia | CC BY-SA 4.0 | 12 artikel astronomi |
| OpenStax Astronomy 2e | CC BY 4.0 | 2 bagian pengantar |
| Stellar Classification Dataset SDSS17 (Kaggle) | CC0 | 100.000 objek langit |

---

## Catatan

Proyek ini dikerjakan sebagai persiapan Tugas Akhir. Fokusnya bukan pada jumlah fitur, melainkan pada pemahaman: setiap parameter diuji dan dibandingkan, setiap keputusan desain didasarkan pada data pengukuran, dan setiap keterbatasan didokumentasikan secara terbuka.

Catatan eksperimen lengkap tersedia di folder `docs/`.