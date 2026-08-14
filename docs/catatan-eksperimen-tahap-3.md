# Catatan Eksperimen Tahap 3 — Retrieval & RAG

**Proyek:** Galaxichat
**Tanggal:** 9 Agustus 2026
**Perangkat:** RTX 4050 Laptop (6 GB VRAM), CUDA 12.6

---

## Konfigurasi dasar

| Komponen | Nilai |
|---|---|
| Model embedding | BAAI/bge-m3 (lokal, GPU) |
| Dimensi vektor | 1024 |
| Vector database | ChromaDB, ruang cosine (HNSW) |
| LLM | Gemini 2.5 Flash via API |
| Temperature | 0.3 |
| Sumber dokumen | 14 dokumen (12 Wikipedia ID + 2 OpenStax) |
| Total kata | ~69.000 |

---

## Set pertanyaan uji

20 pertanyaan dalam 4 kategori:

| Kategori | Jumlah | Yang diuji |
|---|---|---|
| `ada_di_dokumen` | 14 | Apakah dokumen yang benar ditemukan |
| `tidak_ada_di_dokumen` | 2 | Apakah sistem jujur mengaku tidak tahu |
| `ada_sebagian` | 1 | Apakah sistem menjawab sebagian dengan jujur |
| `di_luar_topik` | 3 | Apakah ditolak sebelum memanggil LLM |

Pertanyaan sengaja ditulis dengan kata-kata yang **berbeda dari dokumen**, untuk menguji pencarian berbasis makna, bukan kecocokan kata.

Contoh: dokumen memakai istilah "rotasi sinkron", pertanyaan uji berbunyi "kenapa kita selalu melihat wajah Bulan yang itu-itu saja".

---

## Eksperimen 1 — Nilai K (jumlah chunk yang diambil)

Konfigurasi chunk tetap: 800 karakter, overlap 150.

| K | Precision@1 | Recall@K | Catatan |
|---|---|---|---|
| 3 | 85,7% | 92,9% | Soal no. 6 terpotong (dokumen benar ada di peringkat 5) |
| **5** | **85,7%** | **100%** | **Optimal** |
| 10 | 85,7% | 100% | Tidak ada perbaikan, konteks 2x lebih panjang |

**Temuan:**

1. **Precision@1 tidak dipengaruhi K sama sekali.** Masuk akal — peringkat pertama ditentukan kedekatan vektor, bukan berapa banyak hasil yang diminta.
2. **K=3 kehilangan 7% recall.** Terlalu sempit untuk dokumen dengan topik yang saling tumpang tindih.
3. **K=10 tidak menambah recall** tapi menggandakan panjang konteks yang dikirim ke LLM — memboroskan kuota API, memperlambat jawaban, dan berisiko *context dilution* (potongan lemah mengalihkan perhatian model dari potongan yang benar).

**Keputusan: K = 5.**

---

## Eksperimen 2 — Ukuran chunk

Konfigurasi K tetap: 5.

| Chunk | Overlap | Jumlah chunk | Rata-rata | Precision@1 | Recall@5 | Konteks ke LLM* |
|---|---|---|---|---|---|---|
| 600 | 100 | 1212 | 445 char | **92,9%** | 92,9% | ~2.225 char |
| **800** | **150** | **949** | **565 char** | **85,7%** | **100%** | **~2.825 char** |
| 1000 | 200 | 771 | 687 char | 85,7% | 100% | ~3.435 char |

\* rata-rata ukuran chunk × K=5

**Temuan:**

1. **Chunk kecil menaikkan precision@1 tapi menurunkan recall@5.** Potongan pendek lebih fokus sehingga lebih presisi mencocokkan pertanyaan spesifik (soal no. 5 jadi tepat di peringkat 1), tetapi memuat lebih sedikit konteks sehingga informasi yang tersebar jadi terpecah (soal no. 6 terlempar keluar 5 besar sepenuhnya).

2. **Untuk RAG, recall@5 lebih penting daripada precision@1**, karena kelima potongan sama-sama dikirim ke LLM. Potongan benar di peringkat 3 sama bergunanya dengan di peringkat 1; yang fatal adalah kalau tidak masuk sama sekali.

3. **Chunk 800 dan 1000 identik pada kedua metrik**, tetapi chunk 800 mengirim ~20% lebih sedikit teks ke LLM. Lebih hemat tanpa kehilangan akurasi.

4. **Chunk kecil memperburuk kasus "jawaban tidak tersedia".** Skor soal aurora naik dari 0,5971 (chunk 800) ke 0,6195 (chunk 600) — potongan pendek membuat pertanyaan yang jawabannya tidak lengkap justru terlihat lebih meyakinkan bagi sistem.

**Keputusan: chunk 800 karakter, overlap 150.**

---

## Keterbatasan sistem yang teridentifikasi

### Ambang skor tunggal tidak dapat memisahkan "topik mirip" dari "ada jawaban"

Sebaran skor pada konfigurasi terpilih (chunk 800, K=5):

| Kelompok | Rentang skor tertinggi |
|---|---|
| Ada di dokumen (14 soal) | 0,6260 – 0,7345 |
| Tidak ada di dokumen (3 soal) | 0,5471 – 0,6258 |
| Di luar topik (3 soal) | 0,3549 – 0,4141 |

Kelompok "di luar topik" terpisah bersih — ambang 0,45 menolaknya dengan aman, 3/3 benar, tanpa memanggil LLM sama sekali (menghemat kuota API).

Namun kelompok "tidak ada di dokumen" **tumpang tindih** dengan kelompok "ada di dokumen":

- Skor tertinggi kelompok "tidak ada": **0,6258** (pertanyaan langit malam)
- Skor terendah kelompok "ada": **0,6260** (pertanyaan pasang surut)
- **Selisih: 0,0002**

Secara matematis tidak ada nilai ambang tunggal yang dapat memisahkan keduanya. Menaikkan ambang ke 0,626 akan menolak pertanyaan yang jawabannya jelas tersedia.

### Pengetatan system prompt tidak sepenuhnya menahan halusinasi

Diuji dua versi system prompt pada kasus "kenapa langit malam gelap" (paradoks Olbers — tidak ada di dokumen):

**Versi 1 (dasar):** LLM menjawab bahwa langit gelap karena debu antarbintang menghalangi cahaya, lengkap dengan analogi kabut asap. Jawaban ini **salah secara ilmiah** dan tidak dinyatakan dalam potongan mana pun — LLM menyusun sendiri hubungan sebab-akibatnya.

**Versi 2 (diperketat):** ditambahkan larangan eksplisit menyusun hubungan sebab-akibat yang tidak dinyatakan konteks, serta penegasan bahwa konteks yang hanya "menyerempet" dihitung sebagai tidak ada jawaban.

**Hasil:** halusinasi utama **tetap bertahan** (klaim debu menghalangi cahaya), hanya elaborasinya berkurang. Sementara itu muncul efek samping: jawaban untuk pertanyaan yang berhasil (nasib Matahari) menjadi lebih defensif dan susunannya memburuk — dibuka dengan penyangkalan ("tidak akan meledak sebagai supernova") alih-alih menjawab pertanyaan.

**Kesimpulan:** prompt engineering bukan pengaman yang dapat diandalkan sepenuhnya, dan pengetatan memiliki biaya pada kualitas jawaban yang lain. Versi 1 dipertahankan.

### Akar masalah sebenarnya: cakupan dokumen

Halusinasi terjadi karena topik yang ditanyakan memang tidak ada di korpus. Menambahkan dokumen yang relevan menyelesaikan masalah ini secara langsung, sementara mengubah K, ukuran chunk, ataupun prompt tidak menyentuhnya sama sekali (kategori "tidak ada di dokumen" tetap 0% pada **seluruh** konfigurasi yang diuji).

**Implikasi: kualitas sistem RAG lebih ditentukan oleh cakupan dan kualitas dokumen daripada oleh penyetelan parameter.**

### Keterbatasan metrik

Metrik `recall@5` hanya mengukur apakah **dokumen** yang benar ditemukan, bukan apakah **potongan spesifik** yang memuat jawaban ikut terambil.

Contoh: pada soal no. 11 (metode deteksi eksoplanet), dokumen yang benar ditemukan, tetapi potongan yang memuat daftar lengkap keempat metode (astrometri, kecepatan radial, pulsar waktu, transit) tidak masuk 5 besar. Sistem dihitung berhasil, padahal jawaban yang dihasilkan kemungkinan kurang lengkap.

---

## Hasil akhir konfigurasi terpilih

**Chunk 800 / overlap 150 / K=5 / ambang 0,45**

| Metrik | Nilai |
|---|---|
| Precision@1 | 85,7% |
| Recall@5 | 100% |
| Kategori di luar topik | 3/3 (100%) |
| Kategori tidak ada di dokumen | 0/2 (0%) |
| **Akurasi total** | **85% (17/20)** |

Kinerja pipeline:

| Proses | Waktu |
|---|---|
| Memuat model embedding | ~11–13 detik (sekali, saat backend start) |
| Embedding 949 chunk | ~21 detik (~45 chunk/detik) |
| Pencarian per pertanyaan | ~22 ms |

Catatan: proses embedding dijalankan terpisah lewat `scripts/ingest.py`, bukan saat backend dinyalakan. Pemisahan ini menghilangkan masalah startup lambat yang terjadi pada proyek sebelumnya.

---

## Rencana perbaikan berikutnya

1. Menambah cakupan dokumen untuk topik yang sering ditanyakan tetapi belum tersedia (paradoks Olbers, aurora, instrumen astronomi modern).
2. Menguji pendekatan penyaringan selain ambang tunggal.
3. Mengukur kualitas jawaban akhir (bukan hanya retrieval) dengan penilaian manual pada 20 pertanyaan yang sama.
