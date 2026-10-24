"""Add sources checked for the Duy Tan dossier; preserve unrelated records."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

entries = [
    {
        "document_id": "ND309",
        "number": "309/2026/NĐ-CP",
        "title": "Sửa đổi Nghị định 118 về cơ chế một cửa sau Nghị định 367",
        "issuer": "Chính phủ",
        "issued_date": "2026-08-05",
        "effective_date": "2026-08-05",
        "relevant_articles": "Điều 8 khoản 1–3; Điều 16",
        "relationship": "Sửa Nghị định 118/2025 đã được sửa bởi Nghị định 367/2025.",
        "source_url": "https://vanban.chinhphu.vn/?docid=219100&orggroupid=2&pageid=27160",
        "local_file": "documents/phap_luat/nd309_2026.pdf",
        "summary": "Sửa quy định tiếp nhận và xử lý hồ sơ một cửa. Điều 8 cập nhật hướng dẫn hồ sơ trực tuyến, tiếp nhận qua ki-ốt, mã hồ sơ và mốc tính thời gian.",
        "practical_relevance": "Khoản 3 Điều 8: hồ sơ được tiếp nhận có mã trên giấy tiếp nhận/hẹn trả; không đồng nhất việc Chủ tịch nhận đơn kiến nghị với tiếp nhận hợp lệ hồ sơ chuyển mục đích.",
        "summary_basis": "Điều 8 trang 4; hiệu lực Điều 16 trang 6 và bản ký trang 7 đã đọc trực quan.",
    },
    {
        "document_id": "LTC01-2026",
        "number": "01/2026/QH16",
        "title": "Luật Tiếp cận thông tin",
        "issuer": "Quốc hội",
        "issued_date": "2026-04-23",
        "effective_date": "2026-09-01",
        "relevant_articles": "Điều 15–17; 23–27; 30–31",
        "relationship": "Thay Luật 104/2016/QH13 từ 01/09/2026, có chuyển tiếp tại Điều 31; Nghị định 337 quy định chi tiết.",
        "source_url": "https://chinhphu.vn/?classid=1&docid=218098&orggroupid=1&pageid=27160",
        "local_file": "documents/phap_luat/luat_tiep_can_thong_tin_01_2026.pdf",
        "summary": "Quy định công khai thông tin và cung cấp theo yêu cầu, quyền tiếp cận, giới hạn thông tin và trách nhiệm của cơ quan, đơn vị.",
        "practical_relevance": "Có thể dùng để yêu cầu văn bản tiêu chí ưu tiên, quy hoạch và báo cáo chỉ tiêu hiện có liên quan hồ sơ; kiểm tra thông tin đã công khai, giới hạn tiếp cận và cơ quan chịu trách nhiệm.",
        "summary_basis": "Đối chiếu ảnh trang 7–9, 13–16: phạm vi, cung cấp theo yêu cầu, từ chối, hiệu lực và chuyển tiếp.",
    },
    {
        "document_id": "ND337",
        "number": "337/2026/NĐ-CP",
        "title": "Quy định chi tiết và biện pháp thi hành Luật Tiếp cận thông tin",
        "issuer": "Chính phủ",
        "issued_date": "2026-08-26",
        "effective_date": "2026-09-01",
        "relevant_articles": "Điều 8 khoản 2; Điều 9; Điều 10; Điều 15; Mẫu 01a",
        "relationship": "Hướng dẫn Luật 01/2026/QH16; thay Nghị định 13/2018/NĐ-CP.",
        "source_url": "https://vanban.chinhphu.vn/?classid=1&docid=219284&orggroupid=2&pageid=27160",
        "local_file": "documents/phap_luat/nd337_2026.pdf",
        "summary": "Quy định tổ chức cung cấp thông tin, xử lý yêu cầu, biểu mẫu và việc tách phần được tiếp cận trong tài liệu có nội dung bị hạn chế.",
        "practical_relevance": "Cá nhân dùng Mẫu 01a. Thông tin đơn giản có sẵn: tối đa 3 ngày làm việc; phức tạp cần tập hợp/ý kiến: 12 ngày; gia hạn tối đa 12 ngày và phải thông báo trước khi hết hạn.",
        "summary_basis": "Điều 8–10 trang 7–8; Điều 15 trang 10; Mẫu 01a trang 13–14 đã đối chiếu bản gốc.",
    },
]

csv_path = ROOT / "data/legal_documents.csv"
with csv_path.open(encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)
    fields = reader.fieldnames
    rows = list(reader)
by_id = {row["document_id"]: row for row in rows}

editorial_path = ROOT / "data/legal_editorial.json"
editorial = json.loads(editorial_path.read_text(encoding="utf-8-sig"))

for entry in entries:
    record = {field: "" for field in fields}
    record.update(
        group="Pháp luật chung",
        current_status="Đã kiểm tra điều khoản liên quan ngày 20/10/2026; không xác nhận đã rà toàn bộ sửa đổi",
        verification_status="official_pdf",
        document_class="quy_dinh_bat_buoc",
        checked_on="2026-10-20",
        notes="Nguồn tải chính thức có URL và SHA-256 trong download_log.jsonl. Phạm vi áp dụng cho hồ sơ được nêu trong chuyên đề bảo vệ hồ sơ Duy Tân.",
    )
    record.update(entry)
    if entry["document_id"] in by_id:
        by_id[entry["document_id"]].update(record)
    else:
        rows.append(record)
    editorial["documents"][entry["document_id"]] = {
        field: record[field]
        for field in ("summary", "practical_relevance", "summary_basis")
    }

nd118 = by_id["ND118"]
nd118.update(
    relationship="Sửa đổi bởi Nghị định 367/2025 và 309/2026; đã đọc phần liên quan tiếp nhận, mã hồ sơ và thời gian.",
    checked_on="2026-10-20",
    practical_relevance="Đối chiếu hướng dẫn hồ sơ, theo dõi tiến độ và trả kết quả; đọc cùng sửa đổi 367/2025 và 309/2026, nhất là Điều 17.",
    summary_basis="Điều 16–19 bản gốc; khoản 3 Điều 17 đọc theo khoản 3 Điều 8 Nghị định 309/2026.",
)
editorial["documents"]["ND118"].update({
    field: nd118[field]
    for field in ("relationship", "checked_on", "practical_relevance", "summary_basis")
})

with csv_path.open("w", encoding="utf-8-sig", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
editorial_path.write_text(
    json.dumps(editorial, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

# Refresh only the legal snapshot; do not regenerate unrelated decision reports.
display_path = ROOT / "data/display_data.json"
display = json.loads(display_path.read_text(encoding="utf-8-sig"))
display["legal"] = rows
display_path.write_text(
    json.dumps(display, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({"legal_documents": len(rows), "added_or_updated": [e["document_id"] for e in entries]}, ensure_ascii=False))
