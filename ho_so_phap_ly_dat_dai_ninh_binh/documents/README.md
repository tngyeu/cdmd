# Tài liệu nguồn

- `quy_hoach/`: quyết định, phụ lục phân bổ chỉ tiêu, bảng cấp tỉnh và lịch sử.
- `phap_luat/`: luật, nghị quyết, nghị định, văn bản tỉnh và ảnh trang gốc.
- `quyet_dinh_2026/`: quyết định chuyển mục đích được đính kèm trên cổng công khai; tải thành công chưa đồng nghĩa khớp định danh.
- `ngan_sach/`: nguồn bối cảnh ngân sách nếu có bản tải.
- `nguon_web/`: HTML công khai đã tải để truy nguyên và nhập dữ liệu.

Tra URL, thời điểm tải, SHA256 và lỗi qua `../data/download_log.jsonl`; tra nguồn pháp lý và mức xác minh qua `../data/legal_documents.csv`. Với quyết định cụ thể, đọc `../data/decisions_2026.csv`.

Giữ nguyên nội dung nguồn, kể cả tệp thiếu số/ngày hoặc các lỗi công bố; các điểm chưa khớp được ghi ở dữ liệu và báo cáo thay vì sửa bản gốc. PDF gốc có thể chứa thông tin cá nhân công khai; bảng nghiên cứu chỉ giữ trường cần thiết, không sao chép thông tin cá nhân vào báo cáo tổng hợp.
