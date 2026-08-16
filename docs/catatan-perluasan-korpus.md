# Catatan Eksperimen — Perluasan Korpus Dokumen

**Proyek:** Galaxichat
**Tanggal:** 16 Agustus 2026

---

## Latar belakang

Evaluasi pada Tahap 3 mengidentifikasi satu kelemahan yang tidak dapat diatasi dengan penyetelan parameter: kategori `tidak_ada_di_dokumen` memperoleh skor **0%** pada **seluruh** konfigurasi yang diuji.

Eksperimen sebelumnya sudah mencoba:

- Mengubah nilai K (3, 5, 10) — tidak berpengaruh pada kategori ini
- Mengubah ukuran chunk (600, 800, 1000) — tidak berpengaruh
- Memperketat system prompt — mengurangi elaborasi halusinasi tetapi tidak menghilangkannya

Hipotesis yang disimpulkan saat itu: **akar masalahnya adalah cakupan korpus, bukan konfigurasi sistem.**

Eksperimen ini menguji hipotesis tersebut.

---

## Metode

Korpus diperluas dari **14 menjadi 30 dokumen**, dengan penambahan dikelompokkan menurut tiga tujuan:

**Menutup celah yang terbukti gagal di evaluasi:**
Paradoks Olbers, Aurora, Teleskop Luar Angkasa James Webb.

**Melengkapi topik yang dokumennya masih tipis:**
Nebula planet, Katai putih, Bintang neutron, Materi gelap, Energi gelap.

**Menambah topik yang wajar ditanyakan orang awam:**
Komet, Asteroid, Meteoroid, Gerhana matahari, Gerhana bulan, Satelit alami, Sabuk Kuiper, Teleskop, Astronomi, Alam semesta.

Seluruh pipeline dijalankan ulang: `fetch_docs` → `clean_docs` → `chunk_docs` → `ingest`. Konfigurasi tidak diubah sama sekali (chunk 800, overlap 150, K=5, ambang 0,45), sehingga satu-satunya variabel yang berubah adalah korpus.

Tiga pertanyaan uji diperbarui kategorinya karena jawabannya kini tersedia:

| No | Pertanyaan | Kategori lama | Kategori baru |
|---|---|---|---|
| 15 | Kenapa langit malam gelap | `tidak_ada_di_dokumen` | `ada_di_dokumen` |
| 16 | Penemuan terbaru James Webb | `tidak_ada_di_dokumen` | `ada_sebagian` |
| 17 | Proses terjadinya aurora | `ada_sebagian` | `ada_di_dokumen` |

Nomor 16 tetap `ada_sebagian` karena artikel yang tersedia membahas spesifikasi dan tujuan observasi teleskop, tetapi ditulis sebelum peluncuran sehingga tidak memuat penemuan terbarunya.

---

## Hasil

| Metrik | 14 dokumen | 30 dokumen | Perubahan |
|---|---|---|---|
| Total chunk | 949 | 1.480 | +56% |
| **Akurasi total** | **85,0%** | **95,0%** | **+10,0 poin** |
| Precision@1 | 85,7% | 81,2% | −4,5 poin |
| Recall@5 | 100% | 93,8% | −6,2 poin |
| Kategori sulit (tidak ada / sebagian) | 0/3 | 4/4 | +100% |
| Kategori di luar topik | 3/3 | 3/3 | tetap |

### Hipotesis terbukti

Ketiga pertanyaan yang sebelumnya gagal kini terjawab dengan benar. Skor kemiripan untuk pertanyaan aurora naik tajam dari **0,5971** menjadi **0,7508** — skor tertinggi di seluruh set pertanyaan uji — setelah tersedianya artikel khusus tentang topik tersebut.

Ini mengonfirmasi kesimpulan Tahap 3: **kualitas sistem RAG lebih ditentukan oleh cakupan dan kualitas korpus daripada oleh penyetelan parameter.**

### Trade-off yang teridentifikasi

Precision@1 dan recall@5 keduanya **menurun** meskipun akurasi total naik.

Penyebabnya dapat dijelaskan: dengan korpus 56% lebih besar, jumlah potongan yang bersaing untuk masuk peringkat teratas bertambah. Beberapa artikel baru memiliki cakupan topik yang tumpang tindih dengan artikel lama — misalnya "Astronomi" dan "Alam Semesta" sama-sama membahas bintang dan galaksi secara umum.

**Kasus yang terdampak:** pertanyaan nomor 6 ("Ada berapa banyak bintang di galaksi kita?"). Dokumen yang benar (Bima Sakti) sebelumnya berada di peringkat 5 dan masih lolos; setelah perluasan, dokumen tersebut terlempar keluar dari lima besar.

Analisis penyebabnya: pertanyaan mengandung kata "bintang" dan "galaksi" yang secara semantik kuat mengarah ke artikel berjudul sama, sementara frasa "galaksi kita" yang seharusnya menunjuk Bima Sakti memiliki bobot lebih lemah. Penambahan artikel bertopik umum memperkuat persaingan tersebut.

### Kesimpulan trade-off

Penurunan presisi merupakan harga yang layak dibayar. Kegagalan menjawab sepenuhnya (3 kasus pada korpus lama) jauh lebih merugikan pengguna daripada penurunan peringkat pada satu kasus, karena kegagalan menjawab berpotensi memicu halusinasi sebagaimana terdokumentasi pada Tahap 3.

Akurasi total yang naik 10 poin mencerminkan hal ini.

---

## Implikasi

1. **Perluasan korpus adalah intervensi paling berdampak** pada sistem RAG, dibandingkan penyetelan K, ukuran chunk, maupun prompt engineering.

2. **Perluasan tidak gratis.** Korpus yang lebih besar meningkatkan persaingan antar potongan, sehingga presisi peringkat teratas dapat menurun. Pemilihan dokumen sebaiknya mempertimbangkan tumpang tindih topik, bukan sekadar menambah jumlah.

3. **Metrik tunggal dapat menyesatkan.** Jika hanya melihat precision@1 atau recall@5, perluasan korpus ini akan tampak sebagai kemunduran. Akurasi total yang memperhitungkan kemampuan menolak dan kejujuran mengakui keterbatasan memberikan gambaran yang lebih tepat.

---

## Konfigurasi akhir sistem

| Komponen | Nilai |
|---|---|
| Dokumen sumber | 30 (Wikipedia ID + OpenStax) |
| Total chunk | 1.480 |
| Ukuran chunk | 800 karakter, overlap 150 |
| Top-K retrieval | 5 |
| Ambang kemiripan | 0,45 |
| Model embedding | BAAI/bge-m3, 1024 dimensi |
| Akurasi total | 95,0% (19/20) |