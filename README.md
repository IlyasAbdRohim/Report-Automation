# 📊 Notion Report Automation (OlshopERP)

Automasi pelaporan progress mingguan OlshopERP dari Notion **Raw Data Report** & linked sprint documents ke halaman eksekutif **Result Data Report**.

## 🚀 Fitur Utama
- **Ekstraksi Otomatis**: Membaca catatan mentah, sub-bullet kendala user, dan dokumen sprint mingguan publik.
- **Urutan Prioritas Baku**: Mengurutkan status *Done* berdasarkan skala kepentingan/urgensi (Finansial, Server Load, Integritas Order, Operasional).
- **Metrik Dinamis**: Menghitung persentase task selesai secara otomatis dari tabel metrik dokumen mingguan terbaru.
- **Bugs Krusial Aktif**: Menyajikan isu yang berstatus Open/RE-OPEN langsung dari sprint aktif tanpa penumpukan isu lama.
- **Standar Kerahasiaan & Aturan**: Mematuhi aturan penulisan dan privasi stakeholder sesuai [RULES.md](RULES.md).

## 🛠️ Instalasi & Setup

1. **Clone repository ini**:
   ```bash
   git clone <URL_REPOSITORY_ANDA>
   cd "Report Automation"
   ```

2. **Buat Virtual Environment & Install Dependencies**:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Konfigurasi Environment**:
   Salin `.env.example` menjadi `.env` lalu masukkan token dan ID halaman Notion Anda:
   ```env
   NOTION_TOKEN=ntn_xxxx...
   RAW_DATA_PAGE_ID=xxxx...
   RESULT_DATA_PAGE_ID=xxxx...
   ```

## ▶️ Cara Menjalankan

- **Opsi 1 (Satu Klik)**:
  Klik dua kali file `Jalankan_Report.bat`.

- **Opsi 2 (Terminal)**:
  ```bash
  .\.venv\Scripts\python.exe update_clevel_report.py
  ```
