# 📊 Laporan Progress On-Boarding & Perbaikan OlshopERP
**Tanggal**: 18 Agustus 2026  
**Sistem**: OlshopERP & Integrasi Operasional  
**Target Pembaca**: Manajemen & Ko Lukas  

---

## 📌 Ringkasan Eksekutif (Executive Summary)
Laporan status perbaikan dan pengembangan sistem OlshopERP per 18 Agustus 2026. Dari total **28 item** tindak lanjut:
- **✅ Selesai (Done & Ready)**: 14 Item (50%) — Fitur krusial seperti Auto VAT Store, PO/PR Choose Product, Bulk Import Gambar, dan Benchmark COGS sudah siap pakai.
- **⏳ Sedang Dikerjakan (In Progress)**: 10 Item (36%) — Termasuk modul pelacakan pesanan (Order Processing Trace), Colli V2, dan Rekonsiliasi Bank 2 Arah.
- **⚠️ Butuh Keputusan Atasan (Action Required)**: 1 Item — Alur pemilihan lokasi bahan baku pada modul Assembly.
- **❄️ Backlog / TBD**: 2 Item — Fitur Colli internal Garment & Adjustment selisih perakitan.
- **❌ Dibatalkan**: 1 Item — Perubahan nama supplier ke kode supplier di AP Inbound (dibatalkan sesuai kebutuhan operasional).

---

## ⚠️ BUTUH KEPUTUSAN ATASAN (High Priority Discussion)

### 🔴 Modul Assembly: Penentuan Lokasi Bahan Baku (Komponen)
- **Usulan Awal**: Lokasi komponen dikunci pada Level 20 (Gudang Bahan Baku).
- **Kendala User di Lapangan (Mba Tyas & Mba Shafira)**:
  Jika ada 1 saja komponen yang belum/lupa dipindah ke lokasi Level 20, tombol *Header BoM* terkunci dan perakitan tidak bisa diproses sama sekali.
- **Rekomendasi Tim IT**:
  Dibuat *adjustable by user* (bisa dipilih fleksibel saat input) agar operasional perakitan di gudang tidak terhenti macet.
- 👉 **Mohon konfirmasi/arahan dari Ko Lukas.**

---

## ✅ PERBAIKAN & FITUR YANG SELESAI (Siap Digunakan)

### 1. Penjualan & Pajak (Sales & Finance)
- **Auto Add PPN/VAT per Toko**: Perhitungan PPN transaksi otomatis membaca pengaturan dari Master Store masing-masing cabang/marketplace.
- **Extract Bundle (> Rp 0)**: Tombol *Extract Bundle* di All Sales Order kini berfungsi khusus untuk paket bundling yang nilainya di atas 0.
- **Approval Instant Settlement**: Validasi keamanan baru memastikan tanggal SI harus sama sebelum settlement disetujui.
- **Review Finance**: Seluruh transaksi harian (*All Transaction*) telah selesai direview oleh tim Finance.
- **Benchmark COGS**: Fitur override nilai benchmark COGS melalui file import telah selesai diterapkan.

### 2. Gudang & Inventori (Warehouse & Stock)
- **Stock Remapping**: Memperbaiki isu duplikasi data pada kolom *“Remapped To”*.
- **Transfer Internal**: Input jumlah transfer internal (group view) kini bisa langsung memilih beberapa *Stock ID* sekaligus.
- **Origin Gudang Assembly**: Field asal gudang perakitan kini mendukung Level 20 (yang level 19-nya terhubung ke WIP & Finish Goods).
- **Cetak Dokumen Perakitan**: Format printout dokumen global assembly sudah dilengkapi penomoran halaman rapi di kanan bawah.
- **Label Cetak Colli**: Tombol print Colli Dev telah disesuaikan dengan template desain Colli ID.
- **Filter Toko di Skip Wave**: Menambahkan pencarian berdasarkan nama toko (*Store Name*) pada filter lanjutan dan global search.

### 3. Master Produk & Pengadaan (Product & Procurement)
- **Bulk Import Gambar Produk**: User kini bisa mengunggah gambar hingga 1.000 SKU sekaligus via file import.
- **Penambahan Tipe Varian Berstok**: SKU varian yang sudah memiliki stok tetap bisa ditambah varian barunya tanpa merusak *Stock ID* dan jumlah stok existing.
- **Tombol 'Choose Product' di PO & PR**: Pembuatan PO tanpa PR dan PR kini dilengkapi tombol cepat pemilihan produk.

---

## ⏳ SEDANG DALAM PENGERJAAN AKTIF (In Progress)

### 1. Pelacakan & Operasional Gudang
- **[Menu Baru] Order Processing Trace**: Fitur monitoring status perjalanan 1 Sales Order dari Picking List (PL), Checking (CK), Packing (PK), hingga Delivery Order (DO) beserta kode transaksinya.
- **Konsep Colli V2**: Standardisasi Colli pada alur *Purchase Inbound*, *Transfer Internal*, dan hasil akhir barang jadi (*Assembly*).
- **Skip Wave Advanced Filter**: Pengembangan filter lanjutan untuk mempermudah pemilihan batch order.
- **Kerapian Urutan Printout**: Menyelaraskan urutan daftar cetak agar persis sama dengan urutan menu di layar sistem.

### 2. Keuangan & Akuntansi
- **Rekonsiliasi Bank 2 Arah (Cash/Bank Reconcile)**: Penyesuaian antarmuka agar finance bisa mencocokkan mutasi rekening dari sisi internal maupun rekening koran bank.
- **Nilai COGS Produk Bundle**: Logika pengakuan nilai COGS paket bundling yang dihitung otomatis dari penjumlahan komponen penyusunnya.

### 3. Master Data & Pesanan
- **Proteksi Detail Sales Order**: Menambahkan fitur tambah SKU serta mengunci proteksi agar baris pesanan tidak bisa dihapus sembarangan.
- **Sinkronisasi Gambar Server**: Proses penyalinan gambar produk dari server Meridian ke server Tyas.
- **Master Variant**: Fitur toggle default variant type dan otomatisasi produk tunggal ke varian untuk produk baru.

---

## ❄️ BACKLOG & RENCANA MENDATANG (Next MVP)
- **Merge Stock Jadi 1 Colli**: Menggabungkan beberapa stok di SKU dan rak yang sama menjadi 1 Colli (menunggu hasil pembahasan internal tim Garment).
- **Penyesuaian Selisih Perakitan (Stock Adjustment Qty)**: Format UI sudah disiapkan oleh Mas Ilyas, menunggu kebutuhan riil dari user lapangan saat implementasi.
