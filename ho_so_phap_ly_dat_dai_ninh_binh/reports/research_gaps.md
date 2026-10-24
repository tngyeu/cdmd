# Phạm vi hoàn thành và dữ liệu cần tiếp tục xác minh

**Rà soát mức sẵn sàng ngày 21/10/2026:** đã có [bảng đánh giá, bản đồ căn cứ theo 11 lý do và danh mục chứng cứ E01–E08](muc_san_sang_phan_hoi_20261021.md). Kho có 52 mục pháp lý và 446 quyết định; độ rộng khá tốt, chứng cứ riêng của thửa đất còn thiếu. Đã sửa điểm trước còn để ngỏ về chuyển 50 m²: khoản 3 Điều 11 NQ 254 có quy định không bắt buộc tách thửa khi chuyển một phần. Xem [kịch bản đã cập nhật](duy_tan_tu_choi_50m2.md).

**Đợt rà hiệu lực trọng tâm:** [hạn mức và phương án 50 m²](hieu_luc_han_muc_50m2_20261021.md). Đã khớp hình bản ký QĐ 193, 43, 64, sửa ghi chú cũ về thiếu số/ngày; bổ sung QĐ 192 và chuỗi QĐ 194 → 86. Đã làm rõ chính sách tính tiền một lần, mốc lịch sử 01/08/2024 và hệ quả nếu chuyển 50 m² trước, 56 m² sau. Rà 200 trích yếu Công báo, trong đó 127 văn bản năm 2026; chưa coi đó là chứng nhận không thiếu sửa đổi.

## 1. Kho đã hình thành

**Bổ sung ngày 21/10/2026:** danh mục hiện có 446 bản ghi sau khi thêm 7 quyết định trong tệp ghép và 1 bản Quang Hưng; đã đọc ảnh 14 quyết định với 1.604,3 m² chuyển sang đất ở. [Chi tiết kiểm tra](scan_review_20261021.md). Kho pháp lý có thêm Công văn 7713 của Bộ Tài chính về cách tính tiền, nhưng vẫn cần nguồn gốc đất và lịch sử hưởng chính sách của gia đình để áp dụng. [Phân tích tài chính](tai_chinh_dat_o_co_san.md).

Thủ tục, hồ sơ Duy Tân, pháp lý, quyết định và chỉ tiêu đã được kết nối trong một site Eleventy, chạy bằng `npm run dev`. Các báo cáo, CSV, tài liệu tải về và nhật ký URL/SHA256 được giữ làm nguồn. Danh mục 129 đơn vị lấy từ phụ lục chính thức; URL cổng được thử và đối chiếu liên kết thực tế, không coi tên miền suy ra là bằng chứng website đã được kiểm tra đầy đủ. Có 127 đơn vị có trang đã kiểm tra trong dữ liệu nguồn; 129 là số đơn vị trong danh mục.

Quyết định 3279 và phụ lục 121 đã được đọc, có số liệu 2025/2030, bình quân số học và bảng dự trữ riêng. Đã bổ sung sửa đổi bảng giá theo Nghị quyết 33/2026 có hiệu lực 10/09/2026. Thông tin hồ sơ 655/106 m² được tách khỏi số liệu nguồn chính thức.

## 2. Những việc chưa thể coi là đã hoàn tất

- **Chưa chứng minh thu thập được tất cả quyết định tỉnh đã ban hành.** Kết quả là tập văn bản công khai tìm được trong các trang đã lưu; có cổng hiển thị qua biểu mẫu động, có URL PDF lỗi, có tiêu đề hoặc phụ lục không đủ thông tin.
- **Chưa có dữ liệu thực hiện đầy đủ tại Duy Tân.** Mức tăng ODT 50,26 ha và định hướng tại Đề án 08 là các yếu tố thuận lợi để xem xét hồ sơ phù hợp. Chưa có chứng cứ phường đã hết chỉ tiêu; khoảng trống về số thực hiện không tự chứng minh thiếu chỉ tiêu. Cần đối chiếu khi cơ quan viện dẫn lý do này.
- **Đã khớp bản ký Quyết định 3279 qua ảnh trang 1 và 4.** Phụ lục 121 được đăng cùng trang tỉnh nhưng dòng dẫn số/ngày của phụ lục còn trống; ghi riêng tình trạng phụ lục, bỏ nhận định cũ rằng đầu quyết định trống.
- **Chưa hoàn thiện chuỗi sửa đổi của mọi văn bản.** Các dòng chỉ mục chưa có bản gốc hoặc mới nhận diện qua viện dẫn được giữ nhãn tương ứng.
- **Chưa kiểm tra giấy tờ thửa đất và phiếu hẹn.** Chưa kết luận đủ điều kiện, quá hạn, mức tiền hay vi phạm.
- **Đã có toàn văn Đề án 08 và số dự kiến thu 1.465,8 tỷ đồng tại trang 4.** Còn thiếu các biểu chi tiết được viện dẫn, số giao riêng Duy Tân và bảng tách riêng tiền chuyển mục đích. Xem [Đề án 08/ĐA-UBND ngày 29/07/2026](https://ninhbinh.gov.vn/?pageid=27160&p_steering=47854).

## 3. Cách hiểu mức xác minh

| Nhãn trong HTML | Ý nghĩa |
| --- | --- |
| PDF: khớp số/ngày | Đọc được số và ngày từ PDF chính thức khớp metadata; nội dung diện tích có trạng thái riêng |
| Metadata chính thức | Số/ngày/trích yếu đọc từ cổng chính thức; bản PDF có thể thiếu, ảnh quét hoặc chưa khép định danh |
| Xung đột PDF | Cùng SHA256 được dùng cho các số hiệu khác nhau; giữ mọi nguồn, loại khỏi tổng xác minh để chờ làm rõ |
| Diện tích xác minh | Có loại đất, số m² và định danh PDF khớp; cộng vào tổng diện tích xác minh |
| Nội dung tệp kèm, chờ định danh | Đọc được m²/loại đất trong tệp gắn với trang chính thức, còn thiếu khép số/ngày; không cộng vào tổng diện tích xác minh |
| Chưa tìm thấy trong phạm vi đã tra | Không có bản ghi phù hợp trong trang được lưu; không phải kết luận chưa ban hành |

Tải được PDF không tự nâng mức xác minh. Các bản quét chưa đọc được và quyết định có nhiều hướng chuyển đất được chuyển sang hàng chờ đọc thủ công; không cộng nhầm diện tích cả thửa hoặc chỉ lấy một phần của quyết định hỗn hợp.

## 4. Cập nhật theo yêu cầu

Nhật ký lưu ngày giờ kiểm tra theo UTC+7, URL ban đầu/cuối, lỗi tải, SHA256 và đường dẫn. Script tải giữ phiên bản mới khi nội dung đổi, không ghi đè tệp cũ khác SHA256. Script nhập hợp nhất theo địa phương + số hiệu + ngày ban hành; bản đã được xác minh từ PDF không bị hạ xuống khi nhập lại metadata.

Các yêu cầu truy cập lỗi được giữ nguyên trong nhật ký. Việc kiểm tra tên miền gốc hoặc trang danh mục không được đánh dấu là đã bao phủ toàn bộ nguồn. Bảng `coverage_129.csv` ghi số trang đã tra cho từng địa phương; phần nguồn thiếu cần tiếp tục qua công khai văn bản, đầu mối quản lý hoặc bản cung cấp hợp lệ.

Đây là bộ nghiên cứu khách quan để hiểu và tuân thủ pháp luật, chuẩn bị câu hỏi có căn cứ; không nhằm gây sức ép hoặc suy đoán động cơ cán bộ. Các cập nhật cần ưu tiên đóng những khoảng trống làm thay đổi kết luận, thay vì chỉ tăng số lượng tệp.

## 5. Đợt bổ sung từ tìm kiếm ngày 19/10/2026

Đã đối chiếu truy vấn `site:ninhbinh.gov.vn chuyển mục đích` và các biến thể với kho hiện có; bổ sung 19 bản ghi, đưa danh mục từ 380 lên 399 bản ghi tại 27 địa phương. Xem [chi tiết nguồn và 19 bản bổ sung](../reports/search_supplement_20261019.md). Bảy quyết định Nam Hoa Lư đã đọc trực quan bản quét; sáu quyết định trong một PDF gộp được phân biệt theo các phạm vi trang không chồng nhau.

Đã sửa nhận diện tiêu đề rút gọn và chữ tiếng Việt ở dạng Unicode tổ hợp. Tìm kiếm chỉ là đầu mối: không dùng số kết quả Google làm số quyết định, không nhập văn bản ngoài khoảng ngày nghiên cứu hoặc cộng trang thủ tục/rừng vào tập quyết định đất đai. Thông báo Phú Long 201 chưa tải được PDF; bản 231 đã đọc ảnh, khớp số/ngày và có chữ ký/dấu, chỉ còn sai khác tên người ký trên metadata. Đã bổ sung bản ký Công văn 5061 từ cổng tỉnh, còn thiếu biểu giao thu kèm theo và kế hoạch triển khai Duy Tân. Chưa tìm được thông báo tiếp nhận tương ứng hoặc quyết định Duy Tân phù hợp trong nguồn đã tra; chưa đủ kết luận phường chưa triển khai.

## 6. Bổ sung riêng Mỹ Lộc đến 20/10/2026

Đã đọc đủ 10 trang theo từ khóa “chuyển mục đích” trên tab người dùng tìm kiếm. 94 dòng có 1 dòng lặp; 93 trang văn bản riêng gồm 40 năm 2026 và 53 năm 2025. Tải được 87 PDF, gồm đủ 40 bản năm 2026. Sáu tệp năm 2025 trả lỗi 403; hai trang ghi 1868/1869 nhưng ảnh PDF ghi 1968/1969 được đánh dấu riêng. Xem [danh mục và bộ tệp tải](../reports/myloc_download_20261020.md).

Bảng chung năm 2026 có 438 bản ghi sau khi nhập thêm 39 và cập nhật bản Mỹ Lộc đã có. Đã đối chiếu số/ngày và Điều 1 của đủ 40 PDF Mỹ Lộc năm 2026, cộng **6.196 m² sang ODT (0,6196 ha)** vào số liệu đã xác minh. Xem [bảng theo tháng và từng quyết định](../reports/myloc_area_2026.md). Mốc 20/10 là cập nhật riêng Mỹ Lộc; các đợt tra địa phương khác và báo cáo pháp lý trước đó vẫn giữ ngày kiểm tra cụ thể, chưa phải đã rà lại toàn tỉnh đến ngày 20/10.
