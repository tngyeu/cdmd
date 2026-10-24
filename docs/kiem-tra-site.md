# Ghi nhận kiểm tra site

Ngày thực hiện: **19/10/2026**. Nội dung nguồn giữ mốc nghiên cứu cùng ngày.

## Bổ sung Mỹ Lộc ngày 20/10/2026

Đã dùng tab người dùng tìm kiếm, đọc đủ 10 trang và mở từng văn bản trong tab riêng. 94 dòng có 1 dòng trùng 3416/QĐ-UBND; còn 93 trang nguồn, gồm 40 năm 2026 và 53 năm 2025. Tải đủ 40 PDF năm 2026 và 47 PDF năm 2025. Sáu tệp cũ trả 403 ở cả liên kết động và URL gốc; thử nút postback không nhận được tệp. Đã trả tab nguồn về trang 1, giữ nguyên từ khóa.

87 tệp PDF đều đọc được, tổng 268 trang, SHA256 khác nhau. ZIP có đủ 87 PDF, qua kiểm tra CRC; chỉ mục HTML có 93 dòng, bộ lọc năm/trạng thái, tiêu đề số/ngày để sắp xếp và liên kết PDF mở tab mới. Đã kiểm tra mọi tệp/liên kết cục bộ của chỉ mục; sáu tệp lỗi không có liên kết giả tới tệp trong kho. Hai sai khác 1868/1869 trên cổng so với 1968/1969 trên ảnh PDF được ghi riêng.

Bảng năm 2026 sau bổ sung có 438 bản ghi, Mỹ Lộc 40 bản; diện tích mới chưa cộng khi chưa đọc nội dung. Build thành công, 9 bài kiểm tra đạt; xác nhận 70 trang, 2.625 liên kết nội bộ và mục lục 523 mục. Mốc 20/10 chỉ bổ sung Mỹ Lộc, chưa rà lại các địa phương khác đến cùng ngày. Các mục bên dưới ghi lại các lượt kiểm tra trước đó.

## Kiểm tra bằng lệnh

Lượt cập nhật sau khi bổ sung Đề án 08 và Công văn 5061: build Eleventy thành công; `npm run check` xác nhận 9 bài kiểm tra và liên kết đầu ra.

- Build tạo 69 trang HTML và một mục lục tìm kiếm 483 mục; có phiếu Đề án 08 và Công văn 5061 trong tìm kiếm toàn site.
- 2.558 liên kết nội bộ, anchor và tài nguyên trong các trang đã được kiểm tra tồn tại.
- Chỉ mục pháp lý có 48 văn bản, gồm bổ sung ngày 20/10/2026: Nghị định 309, Luật Tiếp cận thông tin 01/2026 và Nghị định 337; kiểm tra sắp xếp ngày hai chiều, ngày chưa rõ luôn cuối, mốc 12 tháng và truy cập văn bản cũ.
- Thống kê của đủ 129 địa phương khớp các trường chính trong `locality_summary_2026.csv`.
- Diện tích xung đột không đi vào tổng; quyết định hỗn hợp chỉ cộng thành phần khớp hướng lọc.
- Ô số chưa rõ nằm cuối khi sắp xếp cả hai chiều.
- Mô hình 50,26 ha khớp các mốc 150 m² → 3.350 và 106 m² → 4.741 trường hợp.

## Lượt kiểm tra trình duyệt trước khi đổi danh mục pháp lý

Các kết quả dưới đây thuộc giao diện trước đợt đổi sang bảng theo ngày. Chúng không xác nhận trực quan bố cục pháp lý mới. Công cụ trình duyệt bị chặn bởi chính sách trong lượt cập nhật này; không thử đường truy cập khác để vượt hạn chế. Giao diện mới được kiểm tra qua template, mô hình lọc/sắp xếp và đầu ra build.

- Trang bắt đầu và menu chung; các trang thủ tục, pháp lý, quyết định, chỉ tiêu và hỏi đáp.
- Lọc pháp lý theo nhóm thủ tục ra 5 văn bản; kết hợp từ khóa `64/2026` ra một văn bản và mở được phiếu nguồn.
- Tìm toàn site với `han muc` ra các kết quả liên quan không cần dấu.
- Lọc `CLN → ODT` ra 8 quyết định; sắp xếp diện tích ra 50, 60, 110, 127, 208, 230, 300, 308 m².
- Thống kê cùng bộ lọc có 1.393 m² đọc được: 230 m² đã xác minh và 1.163 m² chờ khớp định danh.
- CSV thực tế tải được, chứa tiêu đề cột và đúng các bản ghi đang lọc.
- Lọc Duy Tân không có bản ghi hiện thông báo và dấu “—” ở diện tích chưa có dữ liệu.
- Mô hình chọn 106 m² cập nhật thành 4.741 trường hợp; bảng chỉ tiêu tìm `duy tan` ra đúng 269,76 → 320,02 ha.
- Hỏi đáp tìm `het chi tieu` ra một tình huống; đường dẫn `#cau-18` mở đúng câu hỏi.
- URL HTML cũ với `#legal` chuyển đến `/phap-ly/`.
- Bố cục điện thoại 390 × 844 và kích thước trung gian 820 × 1180: menu hoạt động, nội dung không gây tràn ngang toàn trang; các bảng cuộn trong vùng riêng.

## Kiểm tra bổ sung: Công văn 5061 và Phú Long 231

Đã đọc ảnh bản ký 5061 (2 trang), Thông báo 231 (1 trang), Quyết định 1702 (2 trang), Quyết định 3279 (trang 1, 3–4) và phụ lục 121 (trang 241). Lưu URL, SHA256, sai khác metadata và phạm vi tra cứu Duy Tân tại `data/budget_implementation_review_20261019.json` trong kho hồ sơ.

Sau build, Edge kiểm tra trang ngân sách ở 1365 px và 390 px: phần căn cứ đứng trước phân tích; tiêu đề hiển thị đúng dấu &; bài và mục lục nằm trong màn hình, bảng cuộn riêng. Cả 28 liên kết nguồn/tài liệu của bài mở tab mới. PDF 5061 trả đúng tệp; liên kết hỏi–đáp số 9 mở đúng mục, phiếu 5061 ghi ngày 18/07/2026; không có lỗi JavaScript. Đã xem ảnh chụp cả hai kích thước. Script kiểm tra dùng server cục bộ tạm thời và đã đóng sau khi chạy.

## Giới hạn kiểm tra nguồn ngoài

Kiểm tra liên kết nội bộ xác nhận tệp và anchor; không xác nhận mọi website bên ngoài vẫn truy cập được. Việc rà soát nội dung dựa trên kho nghiên cứu hiện có, chưa là một đợt kiểm chứng mới toàn bộ hiệu lực pháp luật. Các giới hạn đó được ghi trong site và [báo cáo rà soát](../ho_so_phap_ly_dat_dai_ninh_binh/reports/site_content_review_20261019.md).

## File khởi động Windows

Đã chạy `run.bat --no-open` và runner Node để kiểm tra khởi động; Eleventy chọn cổng 8081 khi 8080 đang được sử dụng. Runner đọc thông báo sẵn sàng từ stdout/stderr, nhận đúng URL thực tế và in đường dẫn 127.0.0.1. Đã dừng server kiểm thử do phiên này tạo. Chưa kiểm tra trực tiếp thao tác tự mở trình duyệt; lần chạy kiểm thử dùng cờ `--no-open`.

## Nội dung Đề án 08

Đã đọc lớp chữ toàn văn 11 trang và ảnh trang 1–4, 9–11 của PDF từ cổng tỉnh; giữ URL, SHA-256 và giới hạn về các biểu chưa có. Phân tích tích cực về chủ trương được ghi là nhận định từ nguồn, tách khỏi quyết định cho thửa đất cụ thể. Đã bỏ ví dụ giả định chỉ tiêu Duy Tân gần cạn vì chưa có dữ liệu hỗ trợ.
# Thống kê diện tích Mỹ Lộc, 20/10/2026

- Đã đọc ảnh số/ngày trang 1 và Điều 1 trang 2 của đủ 40 PDF năm 2026: 6.196 m² được phép chuyển sang ODT, tương đương 0,6196 ha; bình quân 154,9 m²/quyết định.
- 43 thành phần diện tích trong 40 quyết định. Quyết định 3438: 74,8 + 215 = 289,8 m²; 3418: 65,4 + 320 = 385,4 m². Các tổng theo tháng, CSV chi tiết, bảng thành phần và bảng chung khớp 6.196 m²; 40 SHA256 riêng được đối chiếu với PDF gốc.
- Đã thêm báo cáo `/quyet-dinh/my-loc/dien-tich/`, CSV 40 dòng và cột diện tích có nút sắp xếp trong danh mục ngoại tuyến; các văn bản tiếp tục mở tab mới. Bộ ZIP giữ 87 PDF và bổ sung bảng diện tích.
- `npm run build` thành công; `npm run check`: 9/9 kiểm tra đạt, 71 trang và 2.689 liên kết nội bộ/neo/tài nguyên hợp lệ. Các số liệu khác không bị đưa vào tổng Mỹ Lộc.
- Chưa kiểm tra thao tác sắp xếp bằng trình duyệt: công cụ trình duyệt từ chối giao thức `file:` theo chính sách URL. Không thử vòng qua hạn chế này. Kiểm tra dữ liệu và quá trình dựng trang ở trên đã hoàn thành.

