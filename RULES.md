# 📋 ATURAN & STANDAR APLIKASI AUTOMATION REPORT

> **PENTING BAGI SISTEM**: Dokumen ini adalah acuan aturan utama (Rules Engine). 
> Setiap kali script automasi dijalankan, sistem **WAJIB** membaca dokumen ini terlebih dahulu untuk memuat identitas pengguna dan menerapkan standar bahasa yang telah ditetapkan.

---

## 👥 1. Struktur Identitas & Stakeholder Perusahaan

### A. Pelapor Sistem (Author)
- **Nama**: Ilyas
- **Jabatan**: IT
- **Peran**: Penyusun laporan, pengembang sistem OlshopERP, dan eksekutor otomasi.

### B. Level Pimpinan / Manajemen (Executive)
- **Status Internal**: Ko Lukas
- **Peran**: Pengambil keputusan strategis dan pemberi arahan bisnis.
- ⚠️ **ATURAN KERAHASIAAN KHUSUS**: Pada dokumen publik / halaman **Result Data Report**, **JANGAN PERNAH** menyebutkan nama "Ko Lukas" maupun kata "CEO". Wajib selalu menggunakan sebutan netral: **"Manajemen"** atau **"Direksi"**.

### C. Tim Teknis / IT Reviewer
- **Nama**: Pak Yendy & Mba Yemima
- **Jabatan**: IT Specialist
- **Peran**: IT Developer, konsultan arsitektur sistem, dan koordinasi pengembangan IT.

### D. Tim Pengguna Lapangan (User / Operasional)
- **Nama**: Mba Mer, Mba Dila, Mba Dama, dan lainnya.
- **Jabatan / Status**: User (Tim Operasional / Bisnis)
- **Peran**: Pengguna sistem di lapangan yang memberikan masukan isu, kebutuhan fitur baru, dan kendala/stopper harian.

---

## 🎯 2. Aturan Input & Sumber Data (Data Ingestion Rules)

1. **Poin Butuh Keputusan (Need Discuss / Action Required)**:
   - **SUMBER EKSKLUSIF**: Poin keputusan **HANYA** boleh diambil dari apa yang diinputkan secara langsung oleh Ilyas di halaman **Raw Data Report** (khususnya pada bagian/section *`need discuss ko lukas`* atau item bertanda *`need discuss`*).
   - 🚫 **DILARANG KERAS**: Mengambil item keputusan/diskusi dari dokumen Notion lain (seperti dari tautan Weekly Report).
2. **Pemilahan Ketat Need Discuss vs Perlu Confirm User**:
   - Jika teks mengandung **`need discuss`** atau **`ko lukas`** → Masuk ke **Tabel 2: Menunggu Keputusan & Arahan Manajemen**.
   - Jika teks mengandung **`perlu confirm user`** (seperti isu Assembly) → **WAJIB** masuk ke **Tabel 3: Request & Kendala Tim Operasional (User)**, dan **TIDAK BOLEH** masuk ke Tabel 2. Mencegah duplikasi data.
3. **Penempatan & Penarikan Stopper Processing (User)**:
   - Isu pada header/bullet *Stopper Processing* diinputkan sebagai sub-bullet / nested children di Notion. Sistem **WAJIB membaca seluruh blok anak (has_children)** agar seluruh catatan kendala ditarik 100%.
   - Catatan ini ditaruh tersendiri sebagai **Catatan Khusus di bawah Tabel 3** dengan header baku: **`⚠️ Catatan Stopper Processing (User):`** lengkap dengan status `[In Progress]` atau `[Done]`.
4. **Summary Singkat sebagai Overall**:
   - Di awal laporan (sebelum tabel), wajib menyajikan **1 paragraf ringkas (Overall Summary)** yang mencakup gambaran umum performa sistem dan poin fokus minggu ini.
5. **Penanganan Multi-Dokumen Mingguan & Status Dinamis**:
   - Jika terdapat beberapa tautan dokumen mingguan pada section *"Progress yang dishare oleh tim IT selama 1 minggu"*, sistem **WAJIB mengambil dokumen mingguan TERAKHIR / TERBARU** sebagai acuan metrik sprint dan status bugs aktif.
   - **Metrik Dinamis**: Angka total task, persentase Done, Ready to Test, In Progress, dan Backlog **WAJIB diekstrak langsung dari tabel Metric dokumen terbaru**, bukan angka statis/hardcoded.
   - **Tabel 4 Dinamis (Bugs Krusial Open)**: Selalu diekstrak dinamis dari tabel *Outstanding / Section 5* dan *Ready to Test / Section 4* dokumen mingguan terbaru. Isu yang sudah beres di minggu baru otomatis hilang dari Tabel 4 dan berpindah ke Tabel 1 (Done), sehingga tidak ada isu kadaluarsa yang menumpuk.
6. **Section New Request User (Result Data Report)**:
   - Pada Tabel 3 (**New Request User & Kendala Tim Operasional**), **HANYA** tampilkan request user yang berstatus **SELAIN DONE** (seperti *In Progress*, *Pending*, *Perlu Confirm User*).
   - Item pada section *New Request User* yang berstatus **Done** **DILARANG** ditampilkan di Tabel 3 untuk mencegah redundansi, dan **HANYA** dimasukkan ke **Tabel 1A (Done Highlight)** sebagai poin perbaikan penting yang telah selesai.
   - Catatan kendala operasional (*Stopper Processing*) tetap dipisahkan tersendiri sebagai sub-catatan di bawah Tabel 3.

---

## 📊 3. Standar Format Tampilan & Urutan Tabel

1. **Format Berbasis Tabel Rapi**:
   - Seluruh data disajikan dalam tabel Notion bersih tanpa highlight / blok warna yang berlebihan.
2. **Bahasa Dekat dengan Definisi Asli & Integritas Nama Menu**:
   - Gunakan istilah teknis/lapangan yang persis dan natural (seperti nomor ETM, nama modul, alur wave/invoicing) agar pelapor (Ilyas) mudah menjelaskannya langsung.
   - ⚠️ **ATURAN INTEGRITAS NAMA MENU**: Ketika ada sebutan nama menu atau modul sistem (seperti **Instant Settlement**, **Purchase Report**, **All Sales Order**, dll.), **JANGAN PERNAH DIUBAH, DIUBAH-UBAH, ATAU DIPOTONG**. Wajib menggunakan nama menu asli secara utuh dan persis.
3. **Urutan Penyajian Tabel Baku**:
   - **Tabel 1**: ✅ Poin Penting Perbaikan Selesai (Done)
   - **Tabel 2**: 🛑 Menunggu Keputusan & Arahan Manajemen (Need Discuss / Decision)
   - **Tabel 3**: 👥 Request & Kendala Tim Operasional (User)
   - **Tabel 4**: 🚨 Bugs Krusial Masih Open & In Progress
4. **Status Baku Kolom**: `Done`, `Need Decision`, `Need Discuss`, `Kritis - Open`, `RE-OPEN`, `Pending`.
5. **Standar Urutan Prioritas Status Done (Tabel 1)**:
   - Tampilan tabel Done (Tabel 1A & 1B) **TIDAK menggunakan kolom status prioritas** agar tampilan tetap bersih dan natural, namun susunan barisnya **WAJIB diurutkan secara internal berdasarkan skala urgensi / perbaikan penting**, dimulai dari yang paling krusial:
     1. **Finansial & Stabilitas Core Server (Prioritas 1)**: Perbaikan selisih uang/laba, pencairan kas marketplace, pencegahan infinite loop pembebanan server, dan penutupan celah korupsi data transaksi utama.
     2. **Integritas Data & Unblock Alur Operasional (Prioritas 2)**: Pembersihan data sampah ribuan order, unblock alur produksi (Assembly), dan kalkulasi valuasi inventori.
     3. **Request User & Sanitasi Export (Prioritas 3)**: Pemenuhan request modul tim operasional (seperti info retur pembelian) dan sanitasi format data export.

---

## ⚙️ 4. Aturan Alur Kerja (Workflow Rules)
1. **Sumber Data**: Membaca blok mentah dari halaman **Raw Data Report**.
2. **Tujuan Data**: Menuliskan ringkasan eksekutif ke halaman **Result Data Report**.
3. **Pembersihan Otomatis**: Bersihkan blok lama di halaman Result sebelum menuliskan ringkasan baru agar tidak terjadi duplikasi data.
4. **Header & Footer**:
   - Header: `👤 Pelapor: Ilyas (IT)  |  🎯 Target: Manajemen  |  👥 Reviewer: Pak Yendy & Mba Yemima`
   - Keterangan Dasar Laporan: `ℹ️ Dasar Laporan: Disusun berdasarkan kebutuhan operasional & update perbaikan yang dishare oleh tim IT Development.`
   - Footer: `📋 Disusun oleh Ilyas (IT) via Python Automation pada [Waktu].` *(Tanpa menyebut nama Ko Lukas atau kata CEO)*.

