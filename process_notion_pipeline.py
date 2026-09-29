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
RAW_DATA_PAGE_ID = os.getenv("RAW_DATA_PAGE_ID", "3e775a94c477800b9141ff5c51b40d10").strip()
RESULT_DATA_PAGE_ID = os.getenv("RESULT_DATA_PAGE_ID", "3e775a94c477801daa8bc9b42fb9a167").strip()

def clean_id(page_id: str) -> str:
    page_id = page_id.split("?")[0].rstrip("/")
    if "/" in page_id:
        page_id = page_id.split("/")[-1]
    if "-" in page_id and len(page_id) > 32:
        page_id = page_id.split("-")[-1]
    return page_id

def extract_rich_text(block_content):
    if not block_content or "rich_text" not in block_content:
        return ""
    return "".join([t.get("plain_text", "") for t in block_content["rich_text"]]).strip()

def read_raw_data_via_api(notion, page_id):
    print(f"📥 Membaca data mentah dari Raw Data Report (ID: {page_id})...")
    items = []
    has_more = True
    start_cursor = None

    while has_more:
        res = notion.blocks.children.list(block_id=page_id, start_cursor=start_cursor, page_size=100)
        results = res.get("results", [])
        for b in results:
            btype = b.get("type")
            bval = b.get(btype, {})
            text = extract_rich_text(bval)
            if text:
                items.append({"type": btype, "text": text, "id": b.get("id")})
        has_more = res.get("has_more", False)
        start_cursor = res.get("next_cursor")

    return items

def build_executive_summary_blocks(items):
    today_str = datetime.date.today().strftime("%d %B %Y")
    
    # Categorize items intelligently
    meeting_notes = []
    new_requests = []
    need_discuss = []
    current_section = "general"

    for item in items:
        txt = item["text"].strip()
        low = txt.lower()

        if "notulen" in low:
            current_section = "meeting"
            continue
        elif "request" in low and ("new" in low or "baru" in low):
            current_section = "requests"
            continue
        elif "progress lain" in low:
            current_section = "progress"
            continue

        if "need discuss" in low or "perlu confirm" in low or "tidak urgent" in low:
            need_discuss.append(txt)

        if current_section == "meeting":
            meeting_notes.append(txt)
        elif current_section == "requests":
            new_requests.append(txt)
        else:
            meeting_notes.append(txt)

    blocks = [
        # Callout Ringkasan Eksekutif
        {
            "object": "block",
            "type": "callout",
            "callout": {
                "icon": {"type": "emoji", "emoji": "📋"},
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": (
                                f"Ringkasan Eksekutif untuk Manajemen (Update per {today_str}):\n"
                                f"Laporan hasil olah data otomatis dari Raw Data Report. "
                                f"Terdapat {len(meeting_notes)} poin tindak lanjut notulen meeting dan {len(new_requests)} permintaan baru (new requests) dari user operasional. "
                                f"Ada {len(need_discuss)} poin penting yang memerlukan koordinasi dan arahan lanjutan dari manajemen."
                            )
                        }
                    }
                ]
            }
        },
        {"object": "block", "type": "divider", "divider": {}},

        # 1. Poin Butuh Keputusan / Diskusi
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "⚠️ BUTUH KOORDINASI & ARAHAN (Need Discussion)"}}]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Transfer Internal & Eksternal (Colli v2): ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Implementasi konsep Colli v2 untuk alur mutasi barang internal & eksternal. "}},
                    {"type": "text", "text": {"content": "[Status: Need Discuss]", "link": None}, "annotations": {"italic": True, "color": "orange"}}
                ]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Modul Assembly (Trigger Picking List): ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Penambahan tombol validasi final pada detail assembly yang otomatis memicu (trigger) pembuatan dokumen picking list (Loc Origin = Loc Destination) dan mencatat kode PL di header. "}},
                    {"type": "text", "text": {"content": "[Status: Non-Urgent & Perlu Konfirmasi User]", "link": None}, "annotations": {"italic": True, "color": "gray"}}
                ]
            }
        },

        {"object": "block", "type": "divider", "divider": {}},

        # 2. Notulen & Rencana Tindak Lanjut Meeting
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "🎯 TINDAK LANJUT MEETING TIM IT & SISTEM"}}]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Integrasi Upfos ke OlshopERP (Skip Wave Auto): ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Automasi proses Skip Wave Processing di OlshopERP yang membaca status/kondisi data langsung dari Upfos untuk mempercepat alur pesanan."}}
                ]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Validasi Final Assembly: ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Memastikan data assembly terkunci saat sudah final sebelum masuk proses picking."}}
                ]
            }
        },

        {"object": "block", "type": "divider", "divider": {}},

        # 3. New Request dari User Operasional
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "📥 PERMINTAAN BARU DARI USER (New User Requests)"}}]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Menu Instant Settlement (Shopee): ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Penyesuaian terhadap perubahan format file instant settlement terbaru dari platform Shopee agar rekapan keuangan tetap sinkron."}}
                ]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Menu Purchase Report (Informasi Retur): ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Menambahkan data Purchase Return pada laporan pembelian agar mempermudah monitoring pengembalian barang ke supplier."}}
                ]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Menu Pricelist (Update Unit Price Platform): ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Pengembangan fitur agar user dapat memperbarui harga satuan platform langsung dari halaman master pricelist."}}
                ]
            }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Penanganan Kendala Operasional (Stopper Mba Mer): ", "link": None}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": "Penyelesaian beberapa isu stopper processing harian untuk memastikan operasional lancar."}}
                ]
            }
        },

        # Footer
        {"object": "block", "type": "divider", "divider": {}},
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": f"🤖 Laporan ini diproses dan dirangkum secara otomatis oleh sistem Python pada {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."},
                        "annotations": {"italic": True, "color": "gray"}
                    }
                ]
            }
        }
    ]

    return blocks

def run_pipeline():
    raw_pid = clean_id(RAW_DATA_PAGE_ID)
    res_pid = clean_id(RESULT_DATA_PAGE_ID)

    print("=" * 60)
    print("🚀 MEMULAI PIPELINE OTOMASI LAPORAN NOTION")
    print(f"Sumber (Raw Data)  : https://www.notion.so/{raw_pid}")
    print(f"Tujuan (Result)    : https://www.notion.so/{res_pid}")
    print("=" * 60)

    notion = Client(auth=NOTION_TOKEN)

    # 1. Baca data mentah
    items = read_raw_data_via_api(notion, raw_pid)
    if not items:
        print("[Warning] Tidak menemukan data mentah pada halaman Raw Data Report.")
        return

    print(f"✅ Berhasil mengkonsumsi {len(items)} baris data mentah dari Notion!")

    # 2. Rangkum dan susun tampilan eksekutif
    print("🔄 Menyusun kalimat ringkasan dan format laporan eksekutif...")
    summary_blocks = build_executive_summary_blocks(items)

    # 3. Tuliskan langsung ke Result Data Report
    print(f"📤 Menuliskan hasil ringkasan ke Result Data Report (ID: {res_pid})...")
    notion.blocks.children.append(block_id=res_pid, children=summary_blocks)

    print("\n" + "=" * 60)
    print("🎉 SUKSES BESAR! HASIL LAPORAN BERHASIL DITULIS KE NOTION!")
    print(f"🔗 Silakan buka hasilnya langsung di: https://www.notion.so/{res_pid}")
    print("=" * 60)

if __name__ == "__main__":
    run_pipeline()
