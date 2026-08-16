# Catatan Eksperimen Tahap 6 — LoRA Fine-tuning

**Proyek:** Galaxichat
**Tanggal:** 16 Agustus 2026
**Perangkat:** RTX 4050 Laptop (6 GB VRAM), CUDA 12.6

---

## Tujuan eksperimen

Eksperimen ini **bukan** dimaksudkan untuk menggantikan sistem RAG yang sudah dibangun, melainkan untuk memperoleh pengalaman langsung dengan fine-tuning sehingga perbandingan antara kedua pendekatan dapat didasarkan pada hasil percobaan sendiri, bukan pada kutipan literatur.

Pertanyaan yang ingin dijawab: **apakah fine-tuning pada skala data yang realistis untuk proyek tingkat sarjana dapat menanamkan pengetahuan domain ke dalam model bahasa kecil?**

---

## Metode

### Penyiapan dataset instruksi

Dataset dihasilkan secara sintetis dari 949 chunk dokumen astronomi yang sudah tersedia dari Tahap 2. Sebuah LLM diminta membuat dua pasangan pertanyaan-jawaban dari setiap potongan dokumen, dengan instruksi bahwa jawaban harus sepenuhnya berdasarkan potongan tersebut.

**Kendala kuota dan pergantian penyedia.**

Generasi awal memakai Gemini 2.5 Flash, tetapi terhenti pada 42 pasangan karena batas tier gratis sebesar 20 permintaan per hari. Dengan laju tersebut, pengumpulan 300 pasangan akan memerlukan sekitar tujuh hari.

Penyedia dialihkan ke Groq (Llama 3.3 70B), yang tier gratisnya jauh lebih longgar. Pengumpulan selesai dalam beberapa menit dengan total 301 pasangan.

**Catatan arsitektur:** pergantian penyedia hanya memerlukan perubahan pada `app/core/config.py` dan `app/core/llm.py`. Modul RAG, endpoint, dan seluruh logika aplikasi tidak disentuh sama sekali. Ini memvalidasi keputusan membangun lapisan abstraksi LLM pada Tahap 1.

Perlu dicatat bahwa chatbot utama tetap memakai Gemini; Groq hanya dipakai untuk pembuatan dataset, agar hasil evaluasi RAG pada Tahap 3 tetap berlaku.

### Penyaringan dataset

Pemeriksaan manual menunjukkan kualitas keluaran Groq lebih rendah daripada Gemini. Sebagian jawaban hanya satu kalimat pendek, sebagian pertanyaan menyalin kalimat dokumen, dan beberapa keluar dari topik astronomi.

Contoh pasangan yang bermasalah:

> Pertanyaan: "Di mana pengikut Aryabhata sangat banyak?"
> Jawaban: "Pengikut Aryabhata sangat banyak di India Selatan."

Pertanyaan tersebut hanya membalik kalimat jawaban, jawabannya hanya 49 karakter, dan topiknya sejarah, bukan astronomi.

Disusun penyaring dengan empat kriteria: panjang jawaban minimum, jumlah kalimat minimum, panjang pertanyaan minimum, dan rasio tumpang tindih kata antara pertanyaan dan jawaban (untuk mendeteksi pertanyaan yang sekadar membalik jawaban).

**Hasil dua tingkat penyaringan:**

| Kriteria | Ketat | Longgar |
|---|---|---|
| Panjang jawaban minimum | 120 karakter | 80 karakter |
| Jumlah kalimat minimum | 2 | 1 |
| Rasio tumpang tindih maksimum | 0,75 | 0,85 |
| **Pasangan tersisa** | **59 (19,6%)** | **232 (77,1%)** |

Penyaringan ketat menyisakan terlalu sedikit data untuk pelatihan, sehingga dipakai versi longgar. Namun selisih antara keduanya menunjukkan bahwa mayoritas data berada di zona abu-abu — memenuhi syarat minimum tetapi tidak sebaik yang diminta instruksi.

### Konfigurasi pelatihan

| Parameter | Nilai |
|---|---|
| Model dasar | Qwen2.5-1.5B-Instruct |
| Kuantisasi | 4-bit NF4 (QLoRA), compute dtype bfloat16 |
| LoRA rank | 16 |
| LoRA alpha | 32 |
| LoRA dropout | 0,05 |
| Target modules | q, k, v, o, gate, up, down projection |
| Epoch | 3 |
| Batch size | 1 (gradient accumulation 8) |
| Learning rate | 2e-4 |
| Max sequence length | 512 |
| Optimizer | paged_adamw_8bit |

**Alasan pemilihan model 1,5B:** dengan VRAM 6 GB yang sebagian sudah terpakai proses lain, model 7B tidak akan muat bahkan dengan kuantisasi 4-bit. Model 1,5B menyisakan ruang yang cukup untuk memori kerja selama pelatihan.

**Kendala teknis yang ditemui:** pelatihan awal gagal dengan `NotImplementedError: _amp_foreach_non_finite_check_and_unscale_cuda not implemented for BFloat16`. Penyebabnya adalah pencampuran tipe data — konfigurasi memakai `fp16=True` sementara model internalnya bekerja dengan bfloat16. Diperbaiki dengan menyeragamkan seluruh jalur ke bfloat16, yang juga lebih tepat untuk pelatihan karena rentang nilainya lebih lebar dan tidak memerlukan gradient scaler.

---

## Hasil pelatihan

| Metrik | Nilai |
|---|---|
| Parameter model total | 907.081.216 |
| Parameter dilatih | 18.464.768 (**2,04%**) |
| Waktu pelatihan | 6,5 menit (87 langkah, 3 epoch) |
| Loss rata-rata | 1,236 |
| Loss akhir | 0,895 |
| Mean token accuracy | 0,81 |
| Ukuran adapter | 37 MB (model dasar: 3,09 GB) |

Loss menurun secara konsisten, menandakan model memang mempelajari pola dari data latih. Adapter yang dihasilkan hanya **1,2% dari ukuran model dasar** — inilah keunggulan praktis LoRA: sepuluh varian domain hanya memerlukan sepuluh adapter kecil dan satu model dasar bersama.

---

## Evaluasi kualitatif

Lima pertanyaan diajukan ke model yang sama dengan adapter dinonaktifkan (sebelum) dan diaktifkan (sesudah).

### Pertanyaan 1 — "Tata Surya dibagi menjadi berapa daerah?"

**Sebelum:** menjawab tujuh daerah berupa Kepulauan Sumatera, Kalimantan, Sulawesi, dan seterusnya. Model salah memahami "Tata Surya" sebagai pembagian wilayah geografis Indonesia.

**Sesudah:** menjawab delapan daerah berupa "Angkasa Utara, Angkasa Selatan, Tata Surya Lintas, Tata Surya Besar" — istilah yang tidak dikenal dalam astronomi.

**Jawaban benar** (tiga daerah: bagian dalam, bagian luar, dan wilayah melampaui Neptunus) **terdapat dalam data latih**, tetapi tidak diserap model.

### Pertanyaan 2 — "Apa yang membuat cahaya tidak bisa lepas dari lubang hitam?"

**Sebelum:** menjelaskan lewat "kepadatan jaringan magnetik" dan "isolasi oleh atmosfer matahari" — keduanya keliru.

**Sesudah:** menjelaskan lewat "momentum sudut yang sama dengan momentum sudut di sekitar pusat gravitasi" — lebih ringkas, tetapi tetap keliru. Konsep yang benar adalah cakrawala peristiwa.

### Pertanyaan 3 — "Bagaimana bintang terbentuk?"

**Sebelum:** menyebut fusi helium dan hidrogen menjadi oksigen (salah).

**Sesudah:** menyebut bintang terbentuk dari "lubang hitam atau benda kerak sabun" (salah dan tidak bermakna).

### Pertanyaan 4 — "Kenapa langit malam gelap padahal ada banyak bintang?"

Topik ini (paradoks Olbers) tidak tersedia dalam korpus dokumen maupun data latih.

**Sesudah:** menjawab "tidak ada cahaya yang masuk ke atmosfer Bumi" — dikarang, disampaikan dengan nada seyakin jawaban lainnya, tanpa indikasi ketidakpastian apa pun.

### Pertanyaan 5 — "Bagaimana cara memasak rendang padang?"

Pertanyaan sengaja diajukan di luar domain astronomi.

**Sesudah:** tetap menjawab dengan resep yang keliru (menyebut kacang merah dan telur sebagai bahan rendang). Model tidak memiliki mekanisme untuk menolak pertanyaan di luar cakupannya.

---

## Analisis

### Fine-tuning mengubah gaya, bukan pengetahuan

Perubahan yang jelas terlihat pada seluruh pertanyaan adalah **format jawaban**: dari paragraf panjang bertele-tele menjadi ringkas satu sampai dua kalimat, sesuai pola data latih.

Namun tidak satu pun jawaban menjadi lebih akurat secara faktual. Pada Pertanyaan 1 dan 3, jawaban yang benar tersedia dalam data latih tetapi tetap tidak muncul.

Ini konsisten dengan pemahaman umum tentang mekanisme fine-tuning: 232 contoh yang dibaca tiga kali cukup untuk membentuk pola respons, tetapi jauh dari cukup untuk menanamkan pengetahuan faktual ke dalam bobot model.

### Tidak ada mekanisme penolakan

Perbedaan paling tajam dengan sistem RAG terlihat pada Pertanyaan 4 dan 5.

Sistem RAG menolak pertanyaan resep rendang dengan `chunks_used = 0` karena skor kemiripan tertingginya hanya 0,3549 — di bawah ambang 0,45 — sehingga LLM tidak dipanggil sama sekali.

Model hasil fine-tuning tidak memiliki lapisan penyaring semacam itu. Setiap masukan menghasilkan keluaran, dan tidak ada sinyal apa pun yang menunjukkan bahwa model sedang mengarang.

### Perbandingan langsung

| Pertanyaan | RAG (Gemini + 949 chunk) | Fine-tuned (Qwen 1.5B + 232 pasangan) |
|---|---|---|
| Tata Surya | Tiga daerah, dengan sitasi Wikipedia | "Angkasa Utara, Tata Surya Lintas" — dikarang |
| Lubang hitam | Cakrawala peristiwa, dengan sitasi | "Momentum sudut" — keliru |
| Langit malam gelap | Bermasalah, tetapi terdeteksi lewat skor 0,6258 | Dikarang tanpa indikasi apa pun |
| Resep rendang | Ditolak sebelum memanggil LLM | Dijawab dengan resep yang salah |
| Verifikasi sumber | Tersedia (nama dokumen + URL + skor) | Tidak tersedia |
| Pembaruan pengetahuan | Tambah dokumen, jalankan ingest | Latih ulang seluruh model |

---

## Kesimpulan

Untuk domain yang menuntut akurasi faktual dan sumber yang dapat diverifikasi, **RAG unggul secara meyakinkan** dibanding fine-tuning pada skala data yang realistis untuk proyek tingkat sarjana.

Fine-tuning berhasil mengubah gaya penyampaian tetapi gagal menanamkan pengetahuan — model tetap mengarang, bahkan untuk pertanyaan yang jawabannya terdapat dalam data latihnya sendiri.

Temuan ini konsisten dengan prinsip yang berlaku umum: fine-tuning tepat digunakan ketika masalahnya adalah *"model tahu tetapi cara menjawabnya tidak sesuai"*, sedangkan RAG tepat ketika masalahnya adalah *"model tidak tahu fakta yang dibutuhkan"*. Kasus chatbot astronomi ini termasuk kategori kedua.

### Keterbatasan eksperimen

Beberapa hal yang membatasi generalisasi temuan ini:

1. **Skala data sangat kecil.** 232 pasangan jauh di bawah skala yang lazim untuk instruction tuning (umumnya ribuan hingga puluhan ribu). Hasil yang berbeda mungkin diperoleh dengan data lebih besar.

2. **Model dasar sangat kecil.** Qwen2.5-1.5B dipilih karena keterbatasan VRAM 6 GB. Model yang lebih besar memiliki kapasitas menyerap pengetahuan yang lebih baik.

3. **Data dihasilkan dua model berbeda.** 42 pasangan dari Gemini, 259 dari Groq, dengan kualitas yang tidak seragam.

4. **Data bersifat sintetis.** Model yang dilatih dari keluaran LLM lain pada dasarnya mempelajari gaya model tersebut, dan tidak akan melampaui kualitas sumbernya.

5. **Evaluasi bersifat kualitatif.** Hanya lima pertanyaan yang diuji, tanpa metrik terukur seperti yang dilakukan pada evaluasi RAG di Tahap 3.

### Arah pengembangan lanjutan

Temuan ini membuka kemungkinan topik penelitian yang lebih terstruktur: **perbandingan terukur antara RAG dan fine-tuning untuk chatbot domain spesifik berbahasa Indonesia**, dengan set pertanyaan uji yang sama dan metrik yang setara untuk kedua pendekatan.

Sistem RAG yang sudah terevaluasi pada Tahap 3 (recall@5 100%, precision@1 85,7%) dapat berfungsi sebagai pembanding, sehingga sebagian besar infrastruktur penelitian sudah tersedia.

---

## Berkas terkait

| Berkas | Keterangan |
|---|---|
| `scripts/build_instruction_dataset.py` | Generasi dataset sintetis, mendukung eksekusi bertahap |
| `scripts/filter_dataset.py` | Penyaringan kualitas dataset |
| `scripts/train_lora.py` | Pelatihan adapter LoRA |
| `scripts/test_lora.py` | Perbandingan sebelum dan sesudah fine-tuning |
| `data/instruction_dataset_clean.jsonl` | 232 pasangan hasil penyaringan |
| `data/models/lora-astronomi/` | Adapter hasil pelatihan (37 MB) |