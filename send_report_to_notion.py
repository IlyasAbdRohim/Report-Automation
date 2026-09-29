import os
import sys
import datetime
import pandas as pd
from dotenv import load_dotenv
from notion_client import Client

# Konfigurasi agar terminal Windows mendukung karakter UTF-8 / Emoji
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 1. Load kredensial dari file .env
load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN", "").strip()
PARENT_PAGE_ID = os.getenv("NOTION_PAGE_ID", "").strip()

def clean_page_id(page_id: str) -> str:
    """Membersihkan ID halaman jika user memasukkan full URL Notion"""
    page_id = page_id.split("?")[0].rstrip("/")
    if "/" in page_id:
        page_id = page_id.split("/")[-1]
    if "-" in page_id and len(page_id) > 32:
        page_id = page_id.split("-")[-1]
    return page_id

def generate_report():
    excel_path = "progress_olshoperp.xlsx"
    if not os.path.exists(excel_path):
        print(f"[ERROR] File '{excel_path}' tidak ditemukan!")
        return

    # 2. Baca data progress dari Excel
    df = pd.read_excel(excel_path)
    df.fillna("-", inplace=True)

    total_tasks = len(df)
    selesai_df = df[df["Status"].str.lower().str.contains("selesai|done|resolved", na=False)]
    progress_df = df[df["Status"].str.lower().str.contains("sedang|progress|on going", na=False)]
    pending_df = df[df["Status"].str.lower().str.contains("pending|tunda|rencana", na=False)]

    total_selesai = len(selesai_df)
    total_progress = len(progress_df)
    total_pending = len(pending_df)

    today_str = datetime.date.today().strftime("%d %B %Y")
    report_title = f"[Progress Report] Pembaruan & Perbaikan OlshopERP - {today_str}"

    print("=" * 60)
    print(f"📊 Menyiapkan: {report_title}")
    print(f"Total Isu/Fitur: {total_tasks} | Selesai: {total_selesai} | Sedang Dikerjakan: {total_progress} | Pending: {total_pending}")
    print("=" * 60)

    # Validasi Token & Page ID
    if not NOTION_TOKEN or "masukkan_token" in NOTION_TOKEN:
        print("\n[PERHATIAN] Token Notion belum diisi!")
        print("Buka file '.env' lalu masukkan NOTION_TOKEN dan NOTION_PAGE_ID Anda.")
        print("Berikut preview format laporan yang akan dikirim ke Notion:\n")
        tampilkan_preview_text(df, total_selesai, total_progress, total_pending, today_str)
        return

    page_id = clean_page_id(PARENT_PAGE_ID)
    notion = Client(auth=NOTION_TOKEN)

    # 3. Susun blok konten Notion dengan bahasa yang ramah & mudah dibaca atasan
    blocks = [
        # Callout Ringkasan Eksekutif
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
                                f"Ringkasan untuk Manajemen:\n"
                                f"Laporan per {today_str}. Dari total {total_tasks} isu/fitur yang masuk, "
                                f"sebanyak {total_selesai} perbaikan sudah berhasil diselesaikan (100% tuntas), "
                                f"{total_progress} modul sedang dalam tahap pengerjaan aktif, dan {total_pending} modul menunggu keputusan/konfirmasi lanjutan. "
                                f"Sistem OlshopERP saat ini beroperasi dengan stabil."
                            )
                        }
                    }
                ]
            }
        },
        # Divider
        {"object": "block", "type": "divider", "divider": {}},
        # Heading 1: Highlight Selesai
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "✅ Perbaikan yang Telah Selesai (Siap Digunakan)"}}]
            }
        }
    ]

    # Tambahkan item yang sudah selesai
    if total_selesai > 0:
        for _, row in selesai_df.iterrows():
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [
                        {"type": "text", "text": {"content": f"{row['Modul / Fitur']}: ", "link": None}, "annotations": {"bold": True}},
                        {"type": "text", "text": {"content": f"{row['Isu / Kendala']}. "}},
                        {"type": "text", "text": {"content": f"\n→ Solusi: {row['Progress & Solusi']} "}},
                        {"type": "text", "text": {"content": f"\n→ Dampak: {row['Dampak ke Bisnis']}", "link": None}, "annotations": {"italic": True, "color": "green"}}
                    ]
                }
            })
    else:
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": "Belum ada item yang selesai pada periode ini."}}]}
        })

    # Heading: Sedang Dikerjakan
    blocks.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": "⏳ Sedang Dalam Tahap Pengerjaan (In Progress)"}}]
        }
    })

    if total_progress > 0:
        for _, row in progress_df.iterrows():
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [
                        {"type": "text", "text": {"content": f"{row['Modul / Fitur']}: ", "link": None}, "annotations": {"bold": True}},
                        {"type": "text", "text": {"content": f"{row['Isu / Kendala']}. "}},
                        {"type": "text", "text": {"content": f"\n→ Update: {row['Progress & Solusi']} "}},
                        {"type": "text", "text": {"content": f"\n→ Target Manfaat: {row['Dampak ke Bisnis']}", "link": None}, "annotations": {"italic": True, "color": "blue"}}
                    ]
                }
            })
    else:
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": "Tidak ada modul yang sedang dalam pengerjaan."}}]}
        })

    # Heading: Pending / Butuh Koordinasi
    blocks.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": "⏸️ Rencana Selanjutnya / Menunggu Konfirmasi"}}]
        }
    })

    if total_pending > 0:
        for _, row in pending_df.iterrows():
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [
                        {"type": "text", "text": {"content": f"{row['Modul / Fitur']}: ", "link": None}, "annotations": {"bold": True}},
                        {"type": "text", "text": {"content": f"{row['Isu / Kendala']}. "}},
                        {"type": "text", "text": {"content": f"\n→ Catatan: {row['Progress & Solusi']} "}},
                        {"type": "text", "text": {"content": f"\n→ Rencana Dampak: {row['Dampak ke Bisnis']}", "link": None}, "annotations": {"italic": True, "color": "gray"}}
                    ]
                }
            })

    # Divider & Footer
    blocks.append({"object": "block", "type": "divider", "divider": {}})
    blocks.append({
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": f"🤖 Laporan ini dibuat secara otomatis oleh sistem Python pada {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."},
                    "annotations": {"italic": True, "color": "gray"}
                }
            ]
        }
    })

    # 4. Kirim ke Notion
    try:
        new_page = notion.pages.create(
            parent={"page_id": page_id},
            icon={"type": "emoji", "emoji": "🚀"},
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
        print("\n✅ BERHASIL! Halaman laporan baru telah dibuat di Notion:")
        print(f"🔗 URL: {new_page.get('url')}")
    except Exception as e:
        print(f"\n[ERROR] Gagal membuat halaman di Notion: {e}")
        print("Pastikan:")
        print("1. NOTION_TOKEN sudah benar.")
        print("2. Halaman induk Notion sudah di-invite/connect ke integrasi bot Anda.")

def tampilkan_preview_text(df, selesai, progress, pending, tgl):
    print(f"=== PREVIEW FORMAT LAPORAN UNTUK ATASAN ===")
    print(f"Judul: [Progress Report] Pembaruan & Perbaikan OlshopERP - {tgl}\n")
    print("📌 Ringkasan Eksekutif:")
    print(f"- Selesai Diperbaiki : {selesai} isu (100% siap pakai)")
    print(f"- Sedang Dikerjakan  : {progress} modul")
    print(f"- Menunggu Koordinasi: {pending} modul\n")
    print("Daftar Modul & Dampak ke Bisnis:")
    for _, r in df.iterrows():
        print(f"  • [{r['Status']}] {r['Modul / Fitur']}: {r['Isu / Kendala']}")
        print(f"    Solusi : {r['Progress & Solusi']}")
        print(f"    Manfaat: {r['Dampak ke Bisnis']}\n")

if __name__ == "__main__":
    generate_report()
