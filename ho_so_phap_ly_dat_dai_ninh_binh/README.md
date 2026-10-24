# Hồ sơ pháp lý đất đai Ninh Bình

> **Giao diện thống nhất hiện tại:** từ thư mục gốc workspace, chạy `npm run dev` và mở `http://localhost:8080/`. Eleventy nối phần thủ tục, hồ sơ pháp lý và chỉ tiêu vào một site. Nội dung dưới đây mô tả kho nguồn và công cụ nghiên cứu trước đây; các lệnh dựng HTML cũ được giữ để truy nguyên. Xem [hướng dẫn site hiện tại](../README.md) và [ghi nhận rà soát nội dung](reports/site_content_review_20261019.md).

Mốc nghiên cứu **19/10/2026**; khoảng thu thập quyết định **01/01–19/10/2026**. Trọng tâm phường Duy Tân và yêu cầu chuyển 106 m² CLN sang ODT. Mục tiêu là hiểu, tuân thủ pháp luật và chuẩn bị trao đổi có căn cứ, khách quan cả điểm thuận lợi, bất lợi và chưa đủ dữ liệu.

## Bản dự thảo và chỉ dẫn kế thừa

[Bộ dữ liệu văn bản bổ sung hoàn cảnh — 24/10/2026](drafts/bo_sung_hoan_canh_20261024/README.md) gồm [bản dự thảo hiện tại](drafts/bo_sung_hoan_canh_20261024/du_thao.md), yêu cầu về giọng văn và thứ tự, dữ kiện người dùng cung cấp, nguồn tham khảo và chỉ dẫn tiếp tục biên tập. Đây là bản làm việc đang được người dùng xem xét, chưa ghi nhận đã ký/gửi và chưa tích hợp lên website.

## Tra cứu

Mở **[index.html](index.html)** trực tiếp bằng trình duyệt. Thanh điều hướng có tổng quan, báo cáo Duy Tân, quyết định 2026, kho pháp luật, ngân sách, phạm vi nguồn còn thiếu và mục “07 · Hỏi–đáp trao đổi” với 22 tình huống, tìm kiếm không dấu, mở/thu gọn câu trả lời, ví dụ số liệu và liên kết căn cứ. Tìm kiếm hỗ trợ tiếng Việt không dấu. Giao diện và dữ liệu nằm trong HTML, không cần mạng để xem; tài liệu gốc nằm trong `documents/`, liên kết web cần Internet.

Danh sách quyết định nằm **ngay trong index**, có số/ngày, xã/phường, cơ quan ban hành, loại đất trước/sau, diện tích m², mức xác minh và liên kết trang/PDF. Có lọc địa phương, tháng, hướng chuyển, mức xác minh, tìm từ khóa, sắp xếp tăng/giảm tại tiêu đề cột và tải CSV theo bộ lọc. Hiển thị toàn bộ kết quả lọc, không phân trang; bấm riêng Số/ngày hoặc Chuyển/Tổng thửa để chọn cách sắp xếp, ô chưa rõ luôn ở cuối. Khi in, chỉ in báo cáo đang xem; bảng quyết định in các dòng đang hiển thị. CSV đầy đủ hoặc CSV bộ lọc dùng khi cần toàn bộ danh sách.

## Cấu trúc và nguồn

Giao diện dùng toàn chiều ngang, menu ở phía trên. Cột **Chuyển / Tổng thửa (m²)** tách diện tích đổi mục đích khỏi diện tích thửa; `?` nghĩa là chưa đọc được. Bộ lọc nội dung cho phép chọn có tổng thửa, đã đọc ảnh PDF, đã tách thành phần, nhiều hướng chuyển hoặc có điểm cần đối chiếu. Mở **Nội dung PDF / ghi chú** để xem cơ cấu trước/sau, giá ghi trong văn bản và liên kết đúng trang. Với quyết định hỗn hợp, bảng còn ghi riêng số m² sang đất ở.

Bảng **Thống kê quyết định theo xã/phường** mở sẵn trong trang Quyết định. Bảng dùng cùng bộ lọc của danh sách, đếm theo bản ghi quyết định, cộng m² được phép chuyển và tách m² sang đất ở, diện tích đã xác minh, diện tích chờ đối chiếu, số bản ghi chưa cộng được diện tích. Khi lọc một hướng chuyển, chỉ cộng thành phần khớp hướng đó; không lấy toàn bộ quyết định hỗn hợp. Có tìm tên, sắp xếp, dòng tổng, tùy chọn hiện nơi chưa có bản ghi và tải CSV thống kê theo bộ lọc. Bấm tên địa phương để xem quyết định. Bản ghi có diện tích mâu thuẫn/xung đột không được cộng; dấu “—” là chưa đủ số liệu, không phải tổng diện tích bằng 0.

- `data/locality_summary_2026.csv`: thống kê toàn tập theo đủ 129 đơn vị, có số bản ghi và mức độ đầy đủ diện tích. Phạm vi là tập công khai thu thập, chưa phải tổng chính thức toàn tỉnh.

- `data/decision_components.csv`: các thành phần diện tích trước/sau của từng quyết định; luôn đọc kèm trạng thái diện tích và định danh, không cộng các dòng có mâu thuẫn nguồn.
- `data/decision_detail_reviews.json`: phiếu đọc ảnh bổ sung, gắn đường dẫn PDF, SHA256 và trang; các phép tính, nội dung mâu thuẫn giữ chú thích.
- `reports/decision_reading_notes.md`: ví dụ cụ thể và điểm đáng chú ý đã đọc từ PDF, tích hợp trong mục Quyết định 2026 của HTML.

- `documents/`: bản tải từ nguồn, phân nhóm; tên tệp được chuẩn hóa, nội dung giữ nguyên. Tài liệu công khai có thể chứa dữ liệu cá nhân trong bản gốc; bảng tổng hợp không lưu tên, CCCD, địa chỉ cư trú hoặc số Giấy chứng nhận.
- `data/decisions_2026.csv`: một dòng theo khóa địa phương + số hiệu + ngày; có trạng thái định danh và trạng thái diện tích riêng.
- `data/legal_documents.csv`: chỉ mục văn bản, hiệu lực bắt đầu, quan hệ sửa đổi, chất lượng nguồn và giới hạn kiểm chứng.
- `data/legal_editorial.json`: mô tả đã rà soát, điểm cần đọc và căn cứ tóm tắt cho từng văn bản; bổ sung bản gốc Nghị quyết 48 ngày 09/12/2025, Nghị quyết 28 ngày 29/04/2026 và chỉ đạo hoàn thiện đề án quỹ đất. `scripts/enrich_legal_index.py` áp dụng vào CSV trước khi dựng trang. Bảng kho có nội dung quan trọng hiển thị trực tiếp, sắp xếp tại header và mặc định ngày ban hành mới nhất; ngày chưa rõ luôn cuối bảng. Nhóm Ngân sách/quỹ đất phân biệt tài liệu đã có với quyết định phê duyệt đề án còn thiếu.
- `data/land_quotas.csv`, `land_reserves.csv`, `land_quota_history.csv`: chỉ tiêu, dự trữ và so sánh lịch sử, tách riêng các ý nghĩa cột.
- `data/coverage_129.csv`: phạm vi trang đã truy cập của 129 đơn vị, không phải chứng nhận đã duyệt hết website.
- `data/duplicate_pdf_review.csv`: cùng PDF gắn với số hiệu khác cần làm rõ.
- `data/pdf_manual_reviews.json`: kết quả đọc trực quan/đối chiếu thủ công gắn SHA256; tách sáu quyết định trong PDF gộp theo phạm vi trang, giữ rõ mức chưa khép định danh.
- `reports/search_supplement_20261019.md`: nguồn, số hiệu và giới hạn của đợt bổ sung theo tìm kiếm ngày 19/10/2026.
- `data/download_log.jsonl`: thời điểm kiểm tra UTC+7, URL, kết quả/lỗi, đường dẫn và SHA256.
- `reports/`: báo cáo Markdown có dẫn nguồn; bản HTML được tạo từ các báo cáo và CSV.
- `scripts/`: công cụ nhập, kiểm chứng và dựng HTML. `tmp/`: danh sách URL công việc và tệp trung gian có thể dùng để tiếp tục kiểm tra.

Tập nguồn công khai tìm được chưa chứng minh tổng quyết định đã ban hành toàn tỉnh. Không tìm thấy bản ghi không có nghĩa chưa ban hành. Số lượng PDF tải được khác số PDF đã đối chiếu khớp số/ngày. Các tệp còn trống số/ngày, bản quét chưa đọc được, hướng chuyển hỗn hợp và diện tích chưa rõ có nhãn riêng; không quy dữ liệu thiếu về 0.

Mức “PDF: khớp số/ngày” chỉ xác nhận định danh; diện tích được cộng khi có `area_status=verified_pdf_identity`. Bản ghi `shared_pdf_conflict` bị loại khỏi tổng xác minh. Ngày hiệu lực bắt đầu trong chỉ mục không đồng nghĩa mọi điều khoản còn nguyên hiệu lực đến mốc nghiên cứu; đọc cột quan hệ và ghi chú.

## Cập nhật theo yêu cầu

Không có tác vụ chạy định kỳ. Rà soát nguồn và hiệu lực trước khi bổ sung kỳ mới. Các script đang cố định mốc 19/10/2026; muốn đổi mốc cần cập nhật mốc lọc, báo cáo, chỉ mục pháp luật và nhãn giao diện đồng bộ, không chỉ sửa ngày trên HTML.

Môi trường đã dùng: Python 3 với `lxml`, `pypdf`; Node.js với `marked`. `pypdfium2` dùng khi cần dựng ảnh trang PDF để đọc trực quan. Các bước tạo lại giao diện từ dữ liệu hiện có:

```powershell
python scripts/prepare_display.py
node scripts/build_html.mjs
python scripts/validate_repository.py
```

Sau khi sửa công cụ đọc dữ liệu, chạy `python -m unittest discover -s tests -v` trong thư mục này. Các kiểm tra bao gồm bản quét nhiều loại đất, giữ kết quả đọc thủ công và sửa ngày metadata mà không tạo bản ghi trùng.

Sau khi sửa mô tả văn bản, chạy `python scripts/enrich_legal_index.py` trước các bước trên. Không điền ngày hội nghị/ngày đăng thay ngày ban hành; các bản gốc Nghị quyết 48 và 28 có ngày khác metadata HĐND, đã ghi rõ trong chỉ mục.

`build_html.mjs` tìm `marked` theo cấu hình trong môi trường đã làm dự án; có thể chỉ định biến môi trường `MARKED_MODULE` bằng đường dẫn tuyệt đối tới `marked/lib/marked.esm.js` nếu dùng máy khác.

Quy trình bổ sung nguồn: chuẩn bị JSON gồm các công việc `{ "url": "https://...", "path": "documents/...pdf", "locality": "Xã ..." }`, chạy `python scripts/fetch_sources.py tmp/ten_jobs.json`. Script chỉ ghi trong module, lưu nhật ký và giữ phiên bản khác SHA256 thay vì ghi đè bản cũ. Sau đó chạy lần lượt:

```powershell
python scripts/update_inventory.py
python scripts/verify_pdf_content.py
python scripts/read_decision_details.py --enrich
python scripts/prepare_display.py
node scripts/build_html.mjs
python scripts/validate_repository.py
```

`update_inventory.py` có thể tạo thêm danh sách trang/PDF cần tải trong `tmp/`; xem URL, tải phần phù hợp rồi nhập lại. Việc đọc tự động chỉ là bước sàng lọc. Đối chiếu PDF gốc trước khi nâng mức xác minh; không để dữ liệu metadata yếu hơn ghi đè bản đã khớp PDF. Văn bản chỉ mới có nguồn thứ cấp cần giữ nhãn, không tự nâng thành bản gốc. Sau khi bổ sung văn bản pháp luật phải cập nhật cả chỉ mục và phân tích liên quan, không chỉ chạy lại trình dựng HTML.

Nguồn văn bản tỉnh ưu tiên [cổng chính tỉnh Ninh Bình](https://ninhbinh.gov.vn/Default.aspx?pageid=27172), dẫn đúng trang chi tiết khi đã khớp số/ngày/trích yếu. Các đối chiếu được lưu ở `data/province_document_sources.json`; chạy `scripts/province_sources.py` để cập nhật vào chỉ mục hiện có trước khi dựng lại dữ liệu hiển thị. Giữ nguồn xã/phường để đối chiếu hoặc khi chưa tìm được bản tỉnh. Nguồn cấp tỉnh không tự giải quyết việc đầu PDF còn trống số/ngày. Liên kết nguồn và tài liệu trong hai trang HTML mở ở tab mới; điều hướng giữa các mục hồ sơ giữ trong trang.

Các giới hạn và yêu cầu nguồn cụ thể nằm trong [báo cáo dữ liệu còn thiếu](reports/research_gaps.md); dữ kiện hồ sơ do người dùng cung cấp được phân biệt với chứng cứ cơ quan nhà nước trong [báo cáo Duy Tân](reports/duy_tan.md).

`read_decision_details.py --enrich` dùng bộ nhớ tạm theo SHA256 để đọc lớp chữ, chỉ lấy tổng thửa từ cụm từ nêu rõ phạm vi, tách hướng chuyển và đối chiếu số học. Phiếu đọc ảnh được áp dụng sau trích tự động; nếu PDF đổi SHA256 thì phải đọc lại. `source_internal_area_conflict` giữ số ở câu cho phép kèm các số mâu thuẫn, loại khỏi tổng diện tích xác minh và phần diện tích chờ định danh. “Đã đọc ảnh” và “đọc từ lớp chữ” có nhãn riêng; việc đọc nội dung không tự nâng mức xác minh số/ngày. Các ghi chú không xác định hiệu lực hay kết luận pháp lý về sai sót của văn bản.

## Trang phân tích chỉ tiêu ODT/ONT đến 2030

Mở [chi_tieu_dat_o_2030.html](chi_tieu_dat_o_2030.html) hoặc mục “08 · Chỉ tiêu ODT/ONT 2030”. Có mô hình quy đổi 50,26 ha, kịch bản theo năm, phân biệt số quyết định công khai với báo cáo hoạt động địa phương, và bảng 129 đơn vị với sắp xếp/lọc không phân trang. Các số là nội dung phụ lục công khai hoặc kịch bản có nhãn; không đồng nhất phần tăng với phần còn lại.

Nguồn và phép tính: `data/residential_activity_sources.json`, `data/residential_quota_analysis.json`, `data/residential_quotas_129.csv`, `data/residential_public_comparison.csv`; báo cáo: `reports/residential_quota_2030.md`. Tạo lại trang khi dữ liệu đầu vào thay đổi:

```powershell
python scripts/analyze_residential_quota.py
node scripts/build_quota_analysis.mjs
python scripts/validate_quota_analysis.py
node scripts/build_html.mjs
python scripts/validate_repository.py
```
