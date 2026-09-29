import os
import sys
import datetime
from dotenv import load_dotenv
from notion_client import Client

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN", "").strip()
PARENT_PAGE_ID = os.getenv("NOTION_PAGE_ID", "").strip()

# Target Parent Page (Raw Data Report): 3e775a94c477800b9141ff5c51b40d10
DEFAULT_PARENT_ID = "3e775a94c477800b9141ff5c51b40d10"

def clean_page_id(page_id: str) -> str:
    if not page_id:
        return DEFAULT_PARENT_ID
    page_id = page_id.split("?")[0].rstrip("/")
    if "/" in page_id:
        page_id = page_id.split("/")[-1]
    if "-" in page_id and len(page_id) > 32:
        page_id = page_id.split("-")[-1]
    return page_id

def create_report_page():
    if not NOTION_TOKEN or "masukkan_token" in NOTION_TOKEN:
        print("\n[PERHATIAN] NOTION_TOKEN belum diisi di file .env!")
        print("Silakan masukkan token integrasi Notion Anda pada file 'c:\\Report Automation\\.env'")
        print("Panduan pembuatan token ada di chat.")
        return

    page_id = clean_page_id(PARENT_PAGE_ID)
    notion = Client(auth=NOTION_TOKEN)

    today_str = datetime.date.today().strftime("%d %B %Y")
    report_title = f"📊 [Executive Report] Update Progress On-Boarding OlshopERP ({today_str})"

    print(f"Menghubungkan ke Notion untuk membuat halaman: {report_title} ...")

    blocks = [
        # Callout Executive Summary
        {
            "object": "block",
            "type": "callout",
            "callout": {
                "icon": {"type": "emoji", "emoji": "📌"},
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": (
                                "Ringkasan Eksekutif untuk Manajemen & Ko Lukas:\n"
                                "Evaluasi berkala progress On-Boarding dan perbaikan sistem OlshopERP. "
                                "Dari total 28 item: 14 item (50%) telah tuntas dan siap pakai, "
                                "10 item (36%) sedang dalam pengerjaan aktif, dan terdapat 1 item prioritas tinggi "
                                "yang memerlukan arahan/keputusan dari manajemen."
                            )
                        }
                    }
                ]
            }
        },
        {"object": "block", "type": "divider", "divider": {}},
        
        # Section 1: Butuh Keputusan Atasan
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "⚠️ BUTUH KEPUTUSAN ATASAN (High Priority)"}}]
            }
        },
        {
            "object": "block",
            "type": "callout",
            "callout": {
                "icon": {"type": "emoji", "emoji": "🔴"},
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": "Modul Assembly (Lokasi Pengambilan Bahan Baku Level 20)\n", "link": None},
                        "annotations": {"bold": True}
                    },
                    {
                        "type": "text",
                        "text": {
                            "content": (
                                "• Kondisi: Sebelumnya disarankan mengunci lokasi ke Level 20 (Bahan Baku).\n"
                                "• Kendala Lapangan (Mba Tyas & Mba Shafira): Jika ada 1 saja komponen yang belum dipindah ke rak bahan baku, Header BoM terkunci dan proses perakitan terhenti total.\n"
                                "• Rekomendasi IT: Dibuat adjustable/fleksibel oleh user saat input agar operasional tidak macet.\n"
                                "👉 Mohon arahan & konfirmasi Ko Lukas."
                            )
                        }
                    }
                ]
            }
        },
        {"object": "block", "type": "divider", "divider": {}},

        # Section 2: Selesai
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "✅ PERBAIKAN SELESAI (Siap Digunakan - 14 Item)"}}]
            }
        },
        {
            "object": "block",
            "type": "heading_3",
            "heading_3": {
                "rich_text": [{"type": "text", "text": {"content": "1. Penjualan, Toko & Pajak"}}]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Auto Add PPN/VAT per Toko: ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Perhitungan PPN otomatis membaca setting masing-masing Master Store."}}
                ]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Extract Bundle: ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Fitur extract bundle di All Sales Order kini aktif khusus paket dengan nilai > 0."}}
                ]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Approval Instant Settlement: ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Validasi tanggal SI harus sama sebelum settlement disetujui."}}
                ]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Review Finance (All Transaction): ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Pengecekan transaksi harian selesai dilakukan oleh tim Finance."}}
                ]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Benchmark COGS: ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Fitur override nilai benchmark COGS lewat menu import sudah aktif."}}
                ]
            }
        },

        {
            "object": "block",
            "type": "heading_3",
            "heading_3": {
                "rich_text": [{"type": "text", "text": {"content": "2. Gudang & Inventori"}}]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Stock Remapping: ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Perbaikan bug duplikasi pada kolom 'Remapped To'."}}
                ]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Transfer Internal: ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Input qty group view sekarang mendukung multiple Stock ID sekaligus."}}
                ]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Gudang Asal Assembly: ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Mendukung WH Level 20 yang level 19-nya sudah di-setting WIP & Finish Goods."}}
                ]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Printout Dokumen Assembly: ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Penambahan penomoran halaman di pojok kanan bawah hasil cetak."}}
                ]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Pencarian Skip Wave: ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Pencarian filter by Store Name pada advanced filter & global search."}}
                ]
            }
        },

        {
            "object": "block",
            "type": "heading_3",
            "heading_3": {
                "rich_text": [{"type": "text", "text": {"content": "3. Master Produk & Pengadaan"}}]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Bulk Import Gambar Produk: ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Upload gambar produk massal hingga 1.000 SKU via file import."}}
                ]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Penambahan Varian Berstok: ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "SKU varian yang sudah berstok kini aman ditambah varian baru tanpa mengubah nilai & Stock ID existing."}}
                ]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Tombol 'Choose Product' di PO & PR: ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Pemilihan produk cepat pada PO (tipe without PR) dan dokumen PR."}}
                ]
            }
        },

        {"object": "block", "type": "divider", "divider": {}},

        # Section 3: Sedang Dikerjakan
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "⏳ SEDANG DIKERJAKAN (In Progress - 10 Item)"}}]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "[Menu Baru] Order Processing Trace: ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Pelacakan alur pesanan dari PL, CK, PK, hingga DO lengkap dengan kode transaksi terkait."}}
                ]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Standarisasi Colli V2: ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Penerapan konsep Colli V2 pada Purchase Inbound, Transfer Internal, dan Output Finish Goods Assembly."}}
                ]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Rekonsiliasi Bank 2 Arah: ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Penyesuaian UI Cash/Bank Reconcile agar dapat diproses dari sisi internal maupun mutasi bank."}}
                ]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "COGS Bundle: ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Perhitungan nilai benchmark COGS bundle berdasarkan total akumulasi komponennya."}}
                ]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Proteksi & Tambah SKU Sales Order: ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Dapat menambah SKU di detail pesanan serta validasi pencegahan hapus baris."}}
                ]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Skip Wave Advanced Filter: ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Pengembangan filter lanjutan pada menu Skip Wave Process."}}
                ]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Sinkronisasi Server Gambar: ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Proses duplikasi gambar produk dari server Meridian ke server Tyas."}}
                ]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Master Variant & Auto Single to Variant: ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Toggle default variant type dan otomatisasi produk baru."}}
                ]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Keseragaman Urutan Cetak: ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Menyesuaikan urutan list pada print out dengan antarmuka menu."}}
                ]
            }
        },

        {"object": "block", "type": "divider", "divider": {}},

        # Section 4: Backlog & Cancelled
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "❄️ BACKLOG & PEMBAHASAN MENDATANG"}}]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Merge Stock 1 Colli: ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Menggabungkan stok di SKU & rak yang sama menjadi 1 Colli (TBD internal tim Garment)."}}
                ]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Adjustment Selisih Perakitan: ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Format UI sudah dibuatkan oleh Mas Ilyas, menunggu kebutuhan riil operasional saat go-live."}}
                ]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Pembatalan (Cancelled): ", "link": None}, "annotations": {"bold": True, "color": "red"}},
                    {"type": "text", "text": {"content": "Perubahan field supplier name ke supplier code di AP Inbound dibatalkan sesuai evaluasi."}}
                ]
            }
        }
    ]

    try:
        new_page = notion.pages.create(
            parent={"page_id": page_id},
            icon={"type": "emoji", "emoji": "📊"},
            properties={
                "title": [
                    {
                        "text": {
                            "content": report_title
                        }
                    }
                ]
            },
            children=blocks
        )
        print("\n" + "=" * 60)
        print("🎉 BERHASIL! Halaman laporan baru telah dibuat di akun Notion Anda!")
        print(f"🔗 Link Halaman: {new_page.get('url')}")
        print("=" * 60)
    except Exception as e:
        print(f"\n[ERROR] Gagal membuat halaman: {e}")
        print("Pastikan token integrasi Notion Anda sudah ditambahkan ke halaman tersebut melalui menu '... -> Connections'.")

if __name__ == "__main__":
    create_report_page()
