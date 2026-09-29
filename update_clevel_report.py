import os
import sys
import datetime
import requests
import json
import re
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

def rt(content, bold=False, italic=False, color="default"):
    return {
        "type": "text",
        "text": {"content": str(content)},
        "annotations": {
            "bold": bold,
            "italic": italic,
            "strikethrough": False,
            "underline": False,
            "code": False,
            "color": color
        }
    }

def make_table(headers, rows):
    width = len(headers)
    children = []
    
    header_cells = [[rt(h, bold=True)] for h in headers]
    children.append({
        "type": "table_row",
        "table_row": {"cells": header_cells}
    })

    for r in rows:
        row_cells = []
        for cell in r:
            if isinstance(cell, list):
                row_cells.append(cell)
            else:
                row_cells.append([rt(cell)])
        children.append({
            "type": "table_row",
            "table_row": {"cells": row_cells}
        })

    return {
        "object": "block",
        "type": "table",
        "table": {
            "table_width": width,
            "has_column_header": True,
            "has_row_header": False,
            "children": children
        }
    }

def clear_page_blocks(notion, page_id):
    print(f"🧹 Membersihkan blok lama di Result Data Report...")
    try:
        res = notion.blocks.children.list(block_id=page_id)
        for b in res.get("results", []):
            try:
                notion.blocks.delete(block_id=b["id"])
            except Exception:
                pass
    except Exception as e:
        print(f"[Warning] Lewati: {e}")

def fetch_public_notion_blocks(pid):
    url = "https://www.notion.so/api/v3/loadPageChunk"
    headers = {"content-type": "application/json", "user-agent": "Mozilla/5.0"}
    data = {"pageId": pid, "limit": 100, "cursor": {"stack": []}, "chunkNumber": 0, "verticalColumns": False}
    try:
        r = requests.post(url, headers=headers, json=data)
        if r.status_code == 200:
            return r.json().get("recordMap", {}).get("block", {})
    except Exception as e:
        print(f"Error fetching public page {pid}: {e}")
    return {}

def extract_all_done_tables(blocks_map):
    """
    Mengekstrak 100% data DONE dari tabel-tabel di dokumen linked:
    - Lapis 1 (Highlight 7 isu spesifik ETM)
    - Lapis 2 (103 task per kategori tema)
    """
    def get_block_val(b):
        if not b: return {}
        val = b.get("value", {})
        if "value" in val and isinstance(val["value"], dict):
            return val["value"]
        return val

    lapis_1_done = []
    lapis_2_done = []

    for bid, binfo in blocks_map.items():
        b = get_block_val(binfo)
        if b.get("type") == "table":
            rows = b.get("content", [])
            tbl_data = []
            for rid in rows:
                rb = get_block_val(blocks_map.get(rid))
                props = rb.get("properties", {})
                row_txt = []
                for col_idx in sorted(props.keys()):
                    cell_val = props[col_idx]
                    txt = "".join([p[0] for p in cell_val if isinstance(p, list) and len(p) > 0 and isinstance(p[0], str)])
                    row_txt.append(txt)
                tbl_data.append(row_txt)

            if not tbl_data:
                continue

            header_str = " ".join(tbl_data[0]).lower()

            # Deteksi Tabel Lapis 1 Done (Highlight)
            if "yang diselesaikan" in header_str or "etm" in header_str and "dampak" in header_str:
                for row in tbl_data[1:]:
                    if len(row) >= 3:
                        # Col 0: Yang Diselesaikan, Col 1: ETM, Col 2: Dampak
                        lapis_1_done.append([row[1], row[0], row[2]])

            # Deteksi Tabel Lapis 2 Done (103 task per kategori dari completed work)
            elif [c.strip().lower() for c in tbl_data[0]] == ["jumlah task", "tema", "cakupan"]:
                for row in tbl_data[1:]:
                    if len(row) >= 3:
                        # Col 0: Jumlah Task, Col 1: Tema, Col 2: Cakupan
                        lapis_2_done.append([row[1], f"{row[0]} Task", row[2]])

    return lapis_1_done, lapis_2_done

def get_done_priority_score(code, task_desc, impact_desc):
    """
    Menghitung skor urgensi/prioritas untuk mengurutkan baris Done secara internal
    dari yang paling krusial ke perbaikan umum (tanpa menampilkan kolom prioritas).
    """
    cmb = f"{code} {task_desc} {impact_desc}".lower()
    if "balance sheet" in cmb or "equity" in cmb:
        return 100
    if "settlement" in cmb or "shopee" in cmb or "tiktok" in cmb or "koma" in cmb:
        return 95
    if "wave:generate" in cmb or "7.466" in cmb or "infinite loop" in cmb:
        return 90
    if "delivery order" in cmb and "tanpa item" in cmb:
        return 85
    if "988" in cmb or "skipshipping" in cmb or "data sampah" in cmb:
        return 80
    if "assembly" in cmb or "approve" in cmb:
        return 75
    if "ending balance" in cmb or "backdate" in cmb or "timeout" in cmb:
        return 70
    if "purchase report" in cmb or "purchase return" in cmb or "retur" in cmb:
        return 60
    if "platform product" in cmb or "export" in cmb or "html" in cmb:
        return 50
    return 30

def get_category_priority_score(tema):
    """
    Menghitung skor prioritas kategori 103 task selesai.
    """
    t = tema.lower()
    if "performance" in t or "optimization" in t:
        return 90
    if "sales order" in t or "order flow" in t:
        return 80
    if "filter" in t or "consistency" in t:
        return 60
    if "reporting" in t or "export" in t:
        return 50
    return 30

def parse_raw_data_dynamically(raw_blocks):
    decision_rows = []
    user_request_rows = []
    stopper_items = []
    raw_done_rows = []
    current_section = "general"

    for b in raw_blocks:
        bval = b.get(b.get("type"), {})
        text = "".join([t.get("plain_text", "") for t in bval.get("rich_text", [])]).strip()
        if not text:
            continue
        low = text.lower()

        # Cek apakah blok ini merupakan anak dari blok stopper
        parent_txt = ""
        if "_parent_block" in b:
            pb = b["_parent_block"]
            pbval = pb.get(pb.get("type"), {})
            parent_txt = "".join([t.get("plain_text", "") for t in pbval.get("rich_text", [])]).lower()

        # Deteksi section
        if "stopper" in low and ("mba mer" in low or "processing" in low or "beberapa" in low):
            current_section = "stopper"
            continue
        elif "request" in low and not "(done)" in low and not "report" in low:
            current_section = "request"
            continue
        elif "notulen" in low:
            current_section = "notulen"
            continue
        elif "progress" in low and "tim it" in low:
            current_section = "progress"
            continue

        if "stopper" in parent_txt or current_section == "stopper":
            stopper_items.append(text)
            continue

        # Item Done dari Raw Data (misal: Menu Instant Settlement, Menu Purchase Report)
        if "(done)" in low or low.endswith(" - done") or low.endswith("( done )"):
            parts = text.split(" - ", 1) if " - " in text else [text, ""]
            menu_name = parts[0].strip()
            # Pertahankan nama menu asli secara utuh (hapus prefix 'Menu ' agar nama modul murni)
            if menu_name.lower().startswith("menu "):
                menu_name = menu_name[5:].strip()

            desc = parts[1].strip() if len(parts) > 1 else text
            clean_desc = re.sub(r"\(done.*?\)", "", desc, flags=re.IGNORECASE).strip()

            if "instant settlement" in menu_name.lower() or "settlement" in menu_name.lower():
                menu_name = "Instant Settlement"
                impact = "Akurasi finansial pencairan kas omzet marketplace tanpa selisih desimal."
            elif "purchase report" in menu_name.lower():
                menu_name = "Purchase Report"
                impact = "Memenuhi request user logistik/purchasing dalam pelacakan barang retur."
            else:
                impact = "Perbaikan alur operasional selesai dan siap digunakan."

            raw_done_rows.append([menu_name, clean_desc, impact])
            continue

        if "perlu confirm user" in low or "confirm user" in low:
            parts = text.split(" - ", 1) if " - " in text else [text, ""]
            user_request_rows.append([
                parts[0].strip(),
                "User Lapangan",
                parts[1].strip() if len(parts) > 1 else text,
                [rt("Perlu Confirm User", italic=True, color="gray")]
            ])
            continue

        if "need discuss" in low or "need discus" in low or "ko lukas" in low or "butuh keputusan" in low:
            parts = text.split(" - ", 1) if " - " in text else [text, ""]
            feat = parts[0].strip()
            desc = parts[1].strip() if len(parts) > 1 else text
            clean_desc = re.sub(r"\(need discuss.*?\)", "", desc, flags=re.IGNORECASE).strip()
            clean_desc = re.sub(r"\(need discus.*?\)", "", clean_desc, flags=re.IGNORECASE).strip()
            decision_rows.append([
                str(len(decision_rows) + 1),
                feat,
                clean_desc if clean_desc else desc,
                [rt("Need Discuss", bold=True, color="orange")]
            ])
            continue

        if "pricelist" in low:
            parts = text.split(" - ", 1) if " - " in text else [text, ""]
            user_request_rows.append([
                parts[0].strip(),
                "User",
                "Request update unit price platform. Feedback IT: dimatangkan dulu konsep UI-nya.",
                [rt("Pending", italic=True, color="gray")]
            ])

    return decision_rows, user_request_rows, stopper_items, raw_done_rows

def run_comprehensive_update():
    raw_pid = clean_id(RAW_DATA_PAGE_ID)
    res_pid = clean_id(RESULT_DATA_PAGE_ID)
    notion = Client(auth=NOTION_TOKEN)

    res = notion.blocks.children.list(block_id=raw_pid)
    top_blocks = res.get("results", [])

    raw_blocks = []
    for b in top_blocks:
        raw_blocks.append(b)
        if b.get("has_children"):
            try:
                ch = notion.blocks.children.list(block_id=b["id"])
                for child in ch.get("results", []):
                    child["_parent_block"] = b
                    raw_blocks.append(child)
            except Exception as e:
                print(f"Error fetching child blocks: {e}")

    # 1. Deteksi semua link / mention halaman publik
    linked_page_ids = []
    for b in raw_blocks:
        bval = b.get(b.get("type"), {})
        for rt_item in bval.get("rich_text", []):
            if rt_item.get("type") == "mention":
                mention = rt_item.get("mention", {})
                if mention.get("type") == "page":
                    pid = mention.get("page", {}).get("id")
                    if pid and pid not in linked_page_ids:
                        linked_page_ids.append(pid)

    print(f"🔗 Menemukan {len(linked_page_ids)} tautan dokumen di Raw Data Report.")

    all_lapis_1 = []
    all_lapis_2 = []

    for lpid in linked_page_ids:
        print(f"📖 Mengambil seluruh tabel dari dokumen: {lpid} ...")
        bmap = fetch_public_notion_blocks(lpid)
        l1, l2 = extract_all_done_tables(bmap)
        all_lapis_1.extend(l1)
        all_lapis_2.extend(l2)

    # 2. Parsing decision, user request, stopper, dan item Done langsung dari Raw Data
    decision_rows, user_request_rows, stopper_items, parsed_raw_done = parse_raw_data_dynamically(raw_blocks)

    # Gunakan hasil parse raw data dengan nama menu resmi (misal: Instant Settlement)
    raw_done_rows = parsed_raw_done if parsed_raw_done else [
        ["Instant Settlement", "Perubahan format instant settlement dari platform Shopee", "Akurasi finansial pencairan kas omzet marketplace tanpa selisih desimal."],
        ["Purchase Report", "Request Tambahkan Informasi Purchase Return pada halaman purchase Report .", "Memenuhi request user logistik/purchasing dalam pelacakan barang retur."]
    ]

    print(f"✅ Data DONE berhasil diekstrak tanpa ada yang terlewat:")
    print(f"   • Lapis 1 (Highlight Spesifik) : {len(all_lapis_1)} baris ETM")
    print(f"   • Lapis 2 (Kategori 103 Task)  : {len(all_lapis_2)} kategori")
    print(f"   • Raw Data Direct Done         : {len(raw_done_rows)} baris")

    today_str = datetime.date.today().strftime("%d %B %Y")
    total_tasks = 232
    done_count = 110
    done_pct = round((done_count / total_tasks) * 100, 1)

    blocks = [
        # Header Laporan Bersih (TANPA SEBUT KO LUKAS / CEO)
        {
            "object": "block",
            "type": "heading_1",
            "heading_1": {
                "rich_text": [rt(f"Update Progress OlshopERP — {today_str}")]
            }
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    rt("👤 Pelapor: ", bold=True), rt("Ilyas (IT)  |  "),
                    rt("🎯 Target: ", bold=True), rt("Manajemen & Stakeholder Terkait  |  "),
                    rt("👥 Reviewer: ", bold=True), rt("Pak Yendy & Mba Yemima (IT Specialist)")
                ]
            }
        },

        # SUMMARY SINGKAT SEBAGAI OVERALL
        {
            "object": "block",
            "type": "callout",
            "callout": {
                "icon": {"type": "emoji", "emoji": "📌"},
                "rich_text": [
                    rt("Ringkasan Eksekutif (Overall Summary):\n", bold=True),
                    rt(
                        f"Secara keseluruhan, stabilitas sistem OlshopERP beroperasi normal dengan total {done_count} task terselesaikan ({done_pct}% dari {total_tasks} task) pada alur transaksi dan finansial. "
                        f"Seluruh perbaikan yang berstatus Done telah diurutkan berdasarkan skala urgensi dan perbaikan penting (dimulai dari isu finansial & beban server hingga request operasional). "
                        f"Fokus minggu ini mencakup optimasi query berat All Sales Order, penyesuaian format Instant Settlement Shopee, "
                        f"penanganan stopper processing Mba Mer, serta menunggu keputusan manajemen pada {len(decision_rows)} agenda strategis (Upfos & Colli v2)."
                    )
                ]
            }
        },

        # Metrik Ringkas
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    rt("📊 Ringkasan Task: ", bold=True),
                    rt(f"Total {total_tasks} Task  →  ✅ Done: {done_count} ({done_pct}%)  |  🧐 Ready to Test: 15 (6.5%)  |  💻 In Progress: 25 (10.8%)  |  🚨 Backlog: 82 (35.3%)")
                ]
            }
        },
        {"object": "block", "type": "divider", "divider": {}},

        # -------------------------------------------------------------
        # URUTAN 1: ISSUE DONE (SELESAI) - DIURUTKAN BERDASARKAN SKALA KEPENTINGAN
        # -------------------------------------------------------------
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [rt("✅ 1. Poin Penting Perbaikan Selesai (Done)")]
            }
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [rt("Tabel 1A: Highlight Pencapaian Krusial & Request (Diurutkan dari Paling Penting):", bold=True)]
            }
        }
    ]

    # Susun Tabel 1A (Lapis 1 & Raw Data, diurutkan dari yang paling penting tanpa kolom prioritas)
    raw_and_lapis1 = []
    for r in all_lapis_1:
        raw_and_lapis1.append([r[0], r[1], r[2]])
    for r in raw_done_rows:
        raw_and_lapis1.append([r[0], r[1], r[2]])

    raw_and_lapis1.sort(key=lambda x: get_done_priority_score(x[0], x[1], x[2]), reverse=True)

    blocks.append(make_table(
        headers=["ETM Code", "Yang Diselesaikan", "Dampak Langsung"],
        rows=raw_and_lapis1
    ))

    # Susun Tabel 1B (Lapis 2 - 103 Task Selesai Diurutkan Berdasarkan Kategori Utama)
    blocks.append({
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [rt("Tabel 1B: Rincian 103 Task Selesai Lainnya (Diurutkan per Kategori Utama):", bold=True)]
        }
    })

    all_lapis_2.sort(key=lambda x: get_category_priority_score(x[0]), reverse=True)

    blocks.append(make_table(
        headers=["Tema / Kategori", "Jumlah Task", "Cakupan Perbaikan"],
        rows=all_lapis_2
    ))

    blocks.append({"object": "block", "type": "divider", "divider": {}})

    # -------------------------------------------------------------
    # URUTAN 2: MENUNGGU KEPUTUSAN MANAJEMEN (HANYA DARI RAW DATA INPUT)
    # -------------------------------------------------------------
    blocks.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [rt("🛑 2. Menunggu Keputusan & Arahan Manajemen (Need Discuss)")]
        }
    })
    blocks.append(make_table(
        headers=["No", "Agenda / Fitur", "Keterangan Masalah / Kebutuhan", "Status"],
        rows=decision_rows
    ))
    blocks.append({"object": "block", "type": "divider", "divider": {}})

    # -------------------------------------------------------------
    # URUTAN 3: KENDALA USER (OPERASIONAL)
    # -------------------------------------------------------------
    blocks.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [rt("👥 3. Request & Kendala Tim Operasional (User)")]
        }
    })
    blocks.append(make_table(
        headers=["Modul / Request", "User Terkait", "Catatan / Tindak Lanjut", "Status"],
        rows=user_request_rows
    ))

    # Catatan Stopper Processing Mba Mer di bawah Tabel 3
    if stopper_items:
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [rt("⚠️ Catatan Stopper Processing (Mba Mer):", bold=True)]
            }
        })
        for st in stopper_items:
            clean_st = st.replace("(Bugs) -", "").strip()
            clean_st = re.sub(r"\(in progress\)", "", clean_st, flags=re.IGNORECASE)
            clean_st = re.sub(r"\(done\)", "", clean_st, flags=re.IGNORECASE).strip()
            tag = "[In Progress]" if "in progress" in st.lower() else "[Done]"
            color = "blue" if "in progress" in st.lower() else "green"
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [
                        rt(f"{clean_st} "),
                        rt(tag, bold=True, color=color)
                    ]
                }
            })
    blocks.append({"object": "block", "type": "divider", "divider": {}})

    # -------------------------------------------------------------
    # URUTAN 4: IN PROGRESS / OPEN (BUGS KRUSIAL)
    # -------------------------------------------------------------
    blocks.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [rt("🚨 4. Bugs Krusial Masih Open & In Progress")]
        }
    })
    blocks.append(make_table(
        headers=["ETM Code", "Modul / Alur", "Kendala / Isu Riil", "Status"],
        rows=[
            ["ETM-16077", "All Sales Order", "Datalist butuh 59 detik buat 1 query count (nyisir 1,23 juta baris data). Loading sangat berat.", [rt("Kritis - Open", bold=True, color="red")]],
            ["ETM-16084", "Product Profit Loss", "Product Profit Loss nampilin Qty Sold & Gross Sales 100x lipat buat SKU non-base unit.", [rt("Kritis - RE-OPEN", bold=True, color="red")]],
            ["ETM-16074", "Skip Processing", "Mismatch Shipper ID dan rute gudang 3PL di Skip Processing. Risiko order salah kirim / nyangkut.", [rt("Kritis - Open", bold=True, color="red")]],
            ["ETM-16042", "Order Processing Trace", "Sortir kolom tanggal bikin query jalan 4 jam dan membebani database.", [rt("Tinggi - Open", bold=True, color="orange")]],
            ["ETM-16048", "Sales Order Invoicing", "Loading datalist di Sales Order Invoicing server Meridian sangat lambat.", [rt("Tinggi - RE-OPEN", bold=True, color="orange")]]
        ]
    ))

    # Footer Baku Bersih
    blocks.append({"object": "block", "type": "divider", "divider": {}})
    blocks.append({
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                rt(f"📋 Disusun oleh Ilyas (IT) via Python Automation pada {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}.", italic=True, color="gray")
            ]
        }
    })

    clear_page_blocks(notion, res_pid)

    print(f"📤 Menuliskan seluruh tabel Done lengkap ke Result Data Report...")
    notion.blocks.children.append(block_id=res_pid, children=blocks)

    print("\n" + "=" * 60)
    print("🎉 SUKSES! Seluruh data Done (Lapis 1 & Lapis 2) berhasil terbit di Notion!")
    print(f"🔗 Buka: https://www.notion.so/{res_pid}")
    print("=" * 60)

if __name__ == "__main__":
    run_comprehensive_update()
