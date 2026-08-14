# Galaxichat — Rencana & Checklist Proyek

**Chatbot pengetahuan alam semesta berbasis RAG + klasifikasi objek langit**

**Periode:** 8 – 30 Agustus 2026 | **Masuk kuliah:** 31 Agustus
**Lokasi proyek:** `C:\Projects\galaxichat`

---

## Prinsip kerja

1. **Satu tahap tidak ditinggalkan sebelum bisa dijelaskan.** Tiap tahap punya "pertanyaan uji". Belum bisa menjawab pakai kalimat sendiri = belum boleh lanjut.
2. **Paham dulu, baru ngoding.** Kode ditulis untuk memenuhi tujuan, bukan disalin lalu dicari alasannya.
3. **Ukur, jangan menebak.** Kalau lambat, catat berapa detik dan di bagian mana.
4. **Commit tiap selesai sub-langkah.** Mesin waktu hanya berguna kalau titik simpannya rajin dibuat.

---

## Arsitektur sistem

```
galaxichat/
├── backend/              <- Python 3.11 + FastAPI
│   ├── venv/             <- lingkungan Python terisolasi
│   ├── app/
│   │   ├── core/         <- konfigurasi, koneksi LLM
│   │   ├── services/     <- modul RAG, modul klasifikasi
│   │   └── api/          <- endpoint yang diakses frontend
│   ├── data/
│   │   ├── documents/    <- dokumen sumber astronomi
│   │   └── vectordb/     <- database vektor (tidak masuk Git)
│   ├── scripts/          <- program sekali jalan (ingest, training)
│   └── tests/
├── frontend/             <- React + Vite
├── docs/                 <- catatan, diagram, laporan
└── .gitignore
```

**Tiga modul utama:**

| Modul | Fungsi | Teknologi |
|---|---|---|
| RAG | Menjawab pertanyaan astronomi berdasarkan dokumen | Embedding lokal + ChromaDB + LLM via API |
| Klasifikasi objek langit | Menebak bintang / galaksi / quasar dari data fotometri | Decision Tree → Random Forest (scikit-learn) |
| Antarmuka | Tampilan pengguna | React |

**Pembagian beban perangkat keras:**
- LLM → API (Gemini). Model besar tanpa membebani laptop.
- Embedding → lokal di GPU RTX 4050. Gratis, cepat, data tidak keluar.
- Klasifikasi → CPU. Ringan, latihan hitungan detik.

---

# ✅ TAHAP 0 — Persiapan (SELESAI)

- [x] Python 3.11.9 terpasang
- [x] Git 2.51 terpasang
- [x] Node.js v24 (LTS) terpasang
- [x] Folder proyek di `C:\Projects\galaxichat` (tanpa spasi, di luar OneDrive)
- [x] Struktur monorepo backend/frontend/docs
- [x] Virtual environment di `backend/venv`
- [x] `.gitignore` mencakup Python dan Node
- [x] Repository Git aktif, commit pertama tersimpan
- [x] File `.gitkeep` agar struktur folder terlacak

**Yang sudah kamu pahami di tahap ini:**
- Fungsi virtual environment dan kenapa tiap proyek butuh sendiri
- PATH dan kenapa `python` bisa "tidak dikenali"
- Kenapa API key tidak boleh masuk Git
- Git melacak file, bukan folder — karena itu ada `.gitkeep`
- Kenapa spasi pada path dan sinkronisasi cloud berbahaya untuk proyek kode

---

# ▶ TAHAP 1 — Fondasi Backend & Koneksi LLM
**Target: 3 hari**

### Yang dikerjakan
- [ ] Install library dasar (FastAPI, uvicorn, python-dotenv)
- [ ] Buat `requirements.txt`
- [ ] Ambil API key Gemini dari Google AI Studio
- [ ] Simpan key di `.env`, buat juga `.env.example`
- [ ] Buat file konfigurasi terpusat di `app/core/config.py`
- [ ] Buat lapisan abstraksi LLM di `app/core/llm.py`
- [ ] Buat endpoint `/chat` sederhana
- [ ] Uji lewat dokumentasi otomatis di `/docs`
- [ ] Commit

### Kenapa belum ada RAG di sini
Disengaja. Kita pastikan jalur paling dasar (pertanyaan → LLM → jawaban) benar-benar jalan sebelum menambah kerumitan. Kalau nanti error, kamu tahu penyebabnya ada di bagian baru, bukan fondasi. Ini prinsip debugging: kurangi jumlah kemungkinan penyebab.

### Konsep yang dipelajari
- Arsitektur client-server & REST API
- Environment variable dan keamanan kredensial
- *Separation of concerns* dan *loose coupling*
- System prompt vs user prompt, temperature

### Pertanyaan uji
- Apa bedanya system prompt dan user prompt?
- Kenapa API key tidak boleh ditulis langsung di kode?
- Kalau Gemini kena limit besok, file mana saja yang harus diubah?
- Apa gunanya `requirements.txt`?

---

# TAHAP 2 — Ingestion Pipeline
**Target: 4 hari**

### Yang dikerjakan
- [ ] Kumpulkan dokumen astronomi (NASA, ESA, ensiklopedia, jurnal terbuka)
- [ ] Buat `scripts/ingest.py` — dijalankan **manual, sekali saja**
- [ ] Baca dokumen dan bersihkan teksnya
- [ ] Potong jadi chunk, atur ukuran dan overlap
- [ ] Muat model embedding lokal
- [ ] Simpan vektor permanen ke ChromaDB
- [ ] Ukur: berapa detik backend nyala sekarang
- [ ] Commit

### Kenapa ini krusial
**Inilah tahap yang menyelesaikan masalah startup lambat pada proyek lamamu.**

Mengubah ratusan halaman jadi vektor itu berat. Kalau dilakukan setiap backend dinyalakan, kamu membayar ongkos yang sama berulang untuk hasil yang persis sama — seperti menyalin ulang seluruh buku catatan tiap mau ujian padahal isinya tidak berubah.

Maka dipisah: `ingest.py` yang berat dijalankan manual saat ada dokumen baru. Backend hanya membuka hasil yang tersimpan.

**Soal chunking:** dokumen dipotong karena LLM punya batas teks sekali baca, dan pencarian jadi lebih presisi. Terlalu besar → jawaban melebar. Terlalu kecil → konteks hilang, kalimat terpotong di tengah makna. Ukurannya diuji, bukan ditebak.

**Soal embedding:** proses mengubah kalimat jadi deretan angka yang mewakili maknanya. Kalimat bermakna mirip menghasilkan angka yang berdekatan. Ini yang memungkinkan pencarian berdasarkan **makna**, bukan kecocokan kata. Contoh: "kenapa langit malam gelap" bisa menemukan dokumen tentang "paradoks Olbers" walau tidak ada satu kata pun yang sama.

### Konsep yang dipelajari
- Chunking dan chunk overlap
- Embedding & ruang vektor
- Vector database vs database relasional
- Pemisahan proses offline (berat) dan online (ringan)

### Pertanyaan uji
- Jelaskan embedding tanpa istilah teknis
- Kenapa dokumen dipotong-potong?
- Kenapa embedding tidak boleh dijalankan tiap backend nyala?
- Apa bedanya ChromaDB dengan MySQL?

---

# TAHAP 3 — Retrieval & Perakitan RAG
**Target: 4 hari**

### Yang dikerjakan
- [ ] Ubah pertanyaan pengguna jadi vektor
- [ ] Cari chunk termirip dari database
- [ ] Susun chunk hasil pencarian ke dalam prompt
- [ ] Tampilkan sumber jawaban (dokumen mana yang dipakai)
- [ ] Buat 20 pertanyaan uji + jawaban seharusnya
- [ ] Ukur berapa yang benar, catat hasilnya
- [ ] Eksperimen: ubah ukuran chunk dan nilai K, bandingkan
- [ ] Commit

### Kenapa ini jantungnya
Kualitas pencarian **lebih menentukan** daripada ukuran LLM. Kalau chunk yang diambil salah, model sebesar apa pun menjawab ngawur. Sampah masuk, sampah keluar.

Menampilkan sumber bukan hiasan — jawaban yang tidak bisa dilacak asalnya tidak layak dipercaya, dan fitur ini membuktikan sistemmu tidak mengarang.

Pengujian terukur inilah yang membedakan proyek ilmiah dari proyek asal jalan. Angkanya masuk ke laporan TA.

### Konsep yang dipelajari
- Cosine similarity
- Top-K retrieval dan pengaruh nilai K
- Prompt engineering untuk RAG
- Halusinasi dan cara menekannya
- Evaluasi terukur

### Pertanyaan uji
- Bagaimana komputer tahu dokumen mana yang relevan?
- Apa efek K terlalu besar / terlalu kecil?
- Kenapa RAG mengurangi halusinasi?
- Apa kelemahan RAG?

---

# TAHAP 4 — Klasifikasi Objek Langit (SDSS)
**Target: 5 hari**

### Yang dikerjakan
- [ ] Unduh dataset SDSS (bintang / galaksi / quasar)
- [ ] Eksplorasi data: lihat isinya, cek keseimbangan kelas
- [ ] Feature engineering: buat *color index* (u−g, g−r, r−i, i−z)
- [ ] Train/test split
- [ ] Latih Decision Tree, **gambar pohonnya**, baca aturannya
- [ ] Naik ke Random Forest, bandingkan
- [ ] Evaluasi: confusion matrix, precision, recall, F1
- [ ] Simpan model terlatih
- [ ] Sambungkan ke backend sebagai endpoint
- [ ] Commit

### Kenapa SDSS, bukan citra galaksi
Klasifikasi citra membutuhkan CNN, dan pada CNN **komputer yang menemukan sendiri cirinya** — tersembunyi di jutaan angka, tidak bisa kamu jelaskan. Itu kotak hitam, dan bertentangan dengan tujuan utama kita.

SDSS bekerja pada data tabel: angka kecerahan objek pada lima filter warna (u, g, r, i, z). Datanya bisa dilihat langsung dengan mata, dan Decision Tree-nya bisa **digambar dan dibaca**: "kalau selisih warna di bawah sekian, maka galaksi."

Yang paling berharga: cirinya punya **makna fisika**. *Color index* menunjukkan objek lebih terang di ultraviolet atau di merah — bintang panas cenderung biru, bintang tua cenderung merah, quasar punya pola khas karena cahayanya dari materi yang jatuh ke lubang hitam. Saat ditanya "kenapa pakai fitur ini?", jawabanmu astrofisika, bukan "karena akurasinya naik".

Bonus: latihannya hitungan detik di CPU, jadi kamu bisa bereksperimen puluhan kali sehari. Pengulangan cepat itulah yang membangun intuisi.

### Konsep yang dipelajari
- Supervised learning & klasifikasi
- Feature engineering berbasis domain
- Train/test split, overfitting
- Confusion matrix, precision, recall, F1
- Class imbalance

### Pertanyaan uji
- Kenapa selisih warna lebih informatif daripada kecerahan mentah?
- Apa itu overfitting dan bagaimana mendeteksinya?
- Kenapa akurasi 95% belum tentu berarti model bagus?
- Kenapa Random Forest biasanya lebih akurat daripada satu Decision Tree?

---

# TAHAP 5 — Frontend React & Portofolio
**Target: 4 hari**

### Yang dikerjakan
- [ ] Buat proyek React dengan Vite di folder `frontend/`
- [ ] Bangun antarmuka chat
- [ ] Hubungkan ke backend (atasi CORS)
- [ ] Tampilkan sumber jawaban di UI
- [ ] Halaman/panel untuk klasifikasi objek langit
- [ ] Tulis README (masalah → solusi → arsitektur → hasil → cara menjalankan)
- [ ] Rekam demo singkat
- [ ] Tulis satu post LinkedIn tentang proses belajarnya
- [ ] Commit & push ke GitHub

### Kenapa frontend baru sekarang
Kalau tampilan dibuat duluan, kamu mendesain untuk data yang belum ada bentuknya, lalu mengulang saat bentuknya berubah. Bangun mesinnya dulu, baru bodinya.

**Soal README:** rekruter melihat GitHub rata-rata di bawah semenit. README yang menjelaskan *masalah apa yang kamu pecahkan* jauh lebih berkesan daripada daftar fitur.

**Soal LinkedIn:** post proses belajar lebih dihargai daripada post pencapaian, karena menunjukkan cara berpikir. Satu tulisan jujur soal "kenapa saya memilih RAG dibanding fine-tuning" lebih bernilai daripada sepuluh sertifikat webinar.

### Konsep yang dipelajari
- Komunikasi frontend-backend, JSON, CORS
- State management dasar di React
- Penanganan loading dan error dari sisi pengguna

---

# TAHAP 6 (OPSIONAL) — LoRA Fine-tuning
**Target: 1–3 hari, atau ditunda ke semester 5**

### Yang dikerjakan
- [ ] Susun dataset instruksi kecil (100–300 pasangan tanya-jawab astronomi)
- [ ] Latih model kecil (1–3B) dengan QLoRA di RTX 4050
- [ ] Bandingkan hasilnya dengan RAG: akurasi, biaya, kemudahan update
- [ ] Tulis kesimpulan perbandingannya

### Posisinya dalam rencana
Bukan pengganti RAG — RAG sudah menjawab masalah utama. Ini untuk **pengalaman langsung**, supaya kalau ditanya "kenapa tidak fine-tuning saja?", jawabanmu berdasarkan percobaan sendiri.

Ini juga **jembatan menuju TA**: topik "perbandingan RAG dan fine-tuning" menuntut sistem RAG yang jalan sebagai pembanding — yang berarti kerja liburan ini jadi setengah TA yang sudah selesai duluan.

Kerjakan hanya kalau Tahap 1–5 sudah beres. Jangan korbankan fondasi demi yang terdengar keren.

---

## Kalau tertinggal

Urutan yang boleh dikorbankan: **Tahap 6 dulu**, lalu kedalaman Tahap 5 (UI seadanya asal jalan), lalu eksperimen tambahan di Tahap 4.

**Jangan pernah korbankan Tahap 2 dan 3.** Itu inti pemahamanmu, dan itu yang paling sering ditanya penguji.

Tertinggal 2–3 hari itu normal, bukan kegagalan. Istirahat juga bagian dari rencana — konsep baru butuh waktu mengendap, dan memaksa 12 jam sehari selama 3 minggu membuat pemahaman dangkal.

**Ukuran keberhasilan sebenarnya:** kalau akhir Agustus kamu bisa menjelaskan cara kerja sistemmu ke teman sampai dia paham, rencana ini berhasil — sekalipun ada fitur yang belum selesai.
