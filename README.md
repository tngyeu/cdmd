# Sổ tay đất đai Ninh Bình

Một site thống nhất dùng **Eleventy 3 + Vanilla JavaScript**, kết nối nghiên cứu thủ tục, hồ sơ Duy Tân, kho pháp lý, quyết định công khai, chỉ tiêu đất ở và 22 tình huống hỏi đáp. Chạy trong workspace, không cần dịch vụ bên ngoài hoặc cơ sở dữ liệu.

## Chạy trên máy

**Cách nhanh trên Windows:** nhấp đúp `run.bat` ở thư mục gốc. File tự vào đúng thư mục dự án, cài phụ thuộc nếu chưa có, khởi động server và mở trình duyệt khi site sẵn sàng. Giữ cửa sổ lệnh đang mở trong lúc sử dụng; nhấn Ctrl+C để dừng. Nếu cổng 8080 đang được dùng, file mở đúng cổng thay thế do Eleventy chọn.

Yêu cầu Node.js 20 trở lên. Các phụ thuộc đã được cài; trên máy mới chạy `npm install` trước.

```powershell
npm run dev
```

Mở **http://localhost:8080/**. Nếu máy hoặc trình duyệt phân giải localhost không phù hợp, dùng **http://127.0.0.1:8080/**. Dừng bằng Ctrl+C. Khi sửa nội dung/template, Eleventy tự dựng lại và tải lại trang.

```powershell
npm run build  # tạo bản tĩnh trong _site/
npm run check  # kiểm tra dữ liệu, liên kết, anchor và tài nguyên sau build
npm test       # build rồi chạy toàn bộ kiểm tra trên
```

Không mở trực tiếp `_site/index.html` bằng file:// vì site dùng đường dẫn từ gốc và tải mục lục tìm kiếm qua HTTP. Dùng `npm run dev` để đọc đầy đủ. Sau khi cài phụ thuộc, site và tài liệu trong kho có thể dùng không cần Internet; chỉ liên kết nguồn bên ngoài cần mạng.

## Các lối vào

| Đường dẫn | Nội dung |
| --- | --- |
| `/` | Trang bắt đầu theo nhu cầu, hồ sơ đang theo dõi và chuyên đề |
| `/thu-tuc/` | Đường đi 8 công đoạn; biểu mẫu; nghiên cứu chuyên sâu có mục lục |
| `/ho-so-duy-tan/` | Dữ kiện hồ sơ 106 m², nhóm thông tin cần xác nhận và bản Word đã soạn |
| `/ho-so-duy-tan/chuan-bi-phan-hoi/` | Chọn 11 lý do, nhập nguyên văn phản hồi, ghép dự thảo; sửa, lưu tại trình duyệt, sao chép sang Word, tải TXT hoặc in |
| `/ho-so-duy-tan/muc-san-sang/` | Kiểm kê dữ liệu, đánh giá mức sẵn sàng, bản đồ nguồn từng nhánh và chứng cứ E01–E08; quy trình tiếp nhận phản hồi |
| `/ho-so-duy-tan/hieu-luc-han-muc-50/` | Hiệu lực và sửa đổi căn cứ trọng tâm; QĐ 193, hạn mức, chuyển một phần 50 m², chính sách tính tiền một lần và chuỗi QĐ 194 → 86 |
| `/ho-so-duy-tan/bo-sung-50m2/` | Bản bổ sung 50 m² soạn sẵn ngày 22/10; chỉnh trực tiếp, sao chép sang Word, tải TXT hoặc in riêng văn bản; câu hỏi tiếp và nguồn đối chiếu |
| `/ho-so-duy-tan/de-nghi-so-huong-dan/` | Bản đề nghị Sở hướng dẫn khi phường vẫn không đồng ý 50 m² hoặc chưa rõ căn cứ; chỉnh, sao chép, tải TXT, in; bảng đối chiếu và danh mục chứng cứ |
| `/ho-so-duy-tan/sau-phan-hoi-so/` | Tám kịch bản sau phản hồi của Sở, bản hỏi tiếp có thể chỉnh/sao chép/tải/in; tuyến khiếu nại, khởi kiện, mốc thời gian và nguồn hiện hành đã lưu |
| `/ho-so-duy-tan/de-nghi-tinh-kiem-tra/` | Bản đề nghị Chủ tịch UBND tỉnh Ninh Bình kiểm tra việc áp dụng căn cứ đối với 50 m²; chỉnh/sao chép/tải/in, đoạn theo từng phản hồi, bảng đối chiếu và nguồn về thẩm quyền |
| `/ho-so-duy-tan/sau-chuyen-don-tinh/` | Tám kịch bản sau chuyển đơn, bản phản hồi gửi Chủ tịch tỉnh, bảng đối chiếu nhiệm vụ với kết quả; phân biệt kiến nghị và xác minh/giải quyết khiếu nại |
| `/ho-so-duy-tan/kich-ban-phan-hoi/` | Toàn bộ kịch bản, căn cứ, dữ liệu đã có, chứng cứ cần bổ sung và giới hạn |
| `/phap-ly/` | 52 văn bản; ưu tiên mới nhất, lọc năm và 7 chủ đề; phiếu riêng có vai trò, quan hệ sửa đổi và nguồn |
| `/ho-so-duy-tan/bao-ve-ho-so/` | Giải trình nhu cầu vị trí 106 m², căn cứ phản hồi và yêu cầu thông tin; cập nhật 20/10/2026 |
| `/ho-so-duy-tan/doc-nhanh/` | Tóm tắt hai phút: kết luận, ví dụ diện tích lớn, nguồn thu và câu dùng khi trao đổi |
| `/ho-so-duy-tan/tinh-huong/` | 13 tình huống và cách phản hồi; ba lý do chính, số liệu, chứng cứ Anhome và đoạn giải trình |
| `/ho-so-duy-tan/doi-dap/` | Tám lượt đối đáp với cán bộ khó tính; mức chắc của lập luận và thứ tự bổ sung bằng chứng |
| `/ho-so-duy-tan/tai-chinh/` | Công văn 7713 về đất ở có sẵn khi tính tiền; điều kiện và hệ quả chính sách một lần khi chọn 50/106 m² |
| `/phap-ly/ra-soat/` | Những điểm nội dung và cách dẫn nguồn đã rà soát khi tổ chức lại |
| `/quyet-dinh/` | 446 bản ghi; lọc, sắp xếp, chi tiết PDF, CSV và thống kê theo địa phương |
| `/quyet-dinh/ra-soat-ban-quet/` | 14 quyết định đã đọc ảnh ngày 21/10: thêm 8 bản ghi, 1.604,3 m² và sửa ngày Quang Hưng 1058 |
| `/chi-tieu/` | Mô hình 50,26 ha; so sánh và bảng ODT/ONT của 129 đơn vị |
| `/hoi-dap/` | 22 tình huống; tìm không dấu, mở/thu gọn và liên kết từng câu |
| `/nguon-va-gioi-han/` | Giới hạn kiểm chứng và dữ liệu cần bổ sung |

Tìm toàn site bằng Ctrl+K. Bộ lọc ghi trong URL để lưu hoặc chia sẻ đường dẫn cục bộ. Bảng hiển thị toàn bộ kết quả lọc; dùng vùng cuộn cho bảng dài. CSV xuất đúng bộ lọc. Nút in chỉ in trang đang xem và các dòng bảng đang hiển thị; câu hỏi đang thu gọn giữ trạng thái thu gọn.

Web là nơi đọc và tra cứu chính; Markdown trong `reports/` là nguồn nội dung. Trang chủ có mục **Mới bổ sung**, nối tới bài đầy đủ, bảng đối chiếu và tài liệu gốc. Tìm kiếm Ctrl+K đọc cả nội dung bài phân tích. Để đưa một bài vào mục mới, thêm ghi chú JSON `<!-- web: { "updatedOn": "2026-10-21", "featured": true, "order": 1, "icon": "book", "summary": "Tóm tắt ngắn và giới hạn cần nhớ." } -->` ngay sau tiêu đề Markdown; giao diện lấy tóm tắt và ngày từ đó, không chép lại kết luận vào template.

## Cấu trúc mã nguồn

- `eleventy.config.js`: cấu hình Eleventy và ánh xạ tài liệu gốc.
- `src/`: Nunjucks templates, layout chung và CSS/Vanilla JS.
- `lib/content.mjs`: đọc Markdown/CSV/JSON, phân chủ đề, nối liên kết nguồn và tạo mục lục.
- `lib/decision-math.mjs`: tìm không dấu, lọc/sắp xếp, thống kê diện tích và mô hình chỉ tiêu; dùng chung cho kiểm tra và trình duyệt.
- `tests/`: kiểm tra các quy tắc diện tích, đối chiếu tổng theo 129 địa phương và kịch bản.
- `scripts/check-site.mjs`: kiểm tra trang sinh ra, liên kết nội bộ, anchor, tài nguyên và mục lục tìm kiếm.
- `_site/`: đầu ra được tạo lại, không sửa trực tiếp và không đưa vào Git.

## Nguồn và cập nhật

**Sau khi tỉnh chuyển đơn, ngày 22/10:** nguồn `reports/sau_chuyen_don_tinh_20261022.md` → `/ho-so-duy-tan/sau-chuyen-don-tinh/`. Tám nhánh T01–T08, bản phản hồi chỉnh/sao chép/tải/in và bảng công việc được giao — kết quả — điểm còn vướng. Bổ sung Thông tư 05/2021/TT-TTCP từ Chính phủ; kiểm tra ảnh Điều 6(1), 20, 29, 30(2) ở trang 3, 9, 11–12, chỉ dùng nội dung cấp tỉnh. Nguồn, SHA-256 và giới hạn kiểm tra hiệu lực tại `data/forwarded_petition_sources_20261022.json`. Đọc lại Điều 29, 38–42 Luật Khiếu nại; phân biệt báo cáo xác minh với quyết định giải quyết. Không mặc định chuyển đơn nghĩa là tỉnh thống nhất, không suy giữ nguyên kết quả là sai, không dùng mẫu kiến nghị thay thủ tục khiếu nại/khởi kiện. Chưa có phiếu chuyển/kết quả thật; chưa tính thời hạn. Nội dung tiếp tục lấy từ Markdown và dùng chung `preparedDraft`.

**Đề nghị Chủ tịch tỉnh kiểm tra, ngày 22/10:** nguồn `reports/de_nghi_tinh_kiem_tra_50m2_20261022.md` → `/ho-so-duy-tan/de-nghi-tinh-kiem-tra/`. Dự thảo đầy đủ có ba nhóm việc: kiểm tra căn cứ/dữ liệu, đánh giá 50 m² và nhu cầu/vị trí, giao đầu mối phối hợp và làm rõ kết quả. Có hướng ghi nhận nếu tỉnh giao lại Sở/phường rà soát. Bổ sung Luật 72/2025/QH15 từ nguồn Chính phủ, đối chiếu khoản 4 và 15 Điều 17 tại ảnh PDF trang 20–21; provenance tại `data/province_petition_sources_20261022.json`. Dùng chung `preparedDraft`; chỉ nội dung giữa hai marker được sao chép/tải/in. Chưa có phản hồi thực tế, không tự xác định sai phạm, không tự chuyển thành đơn khiếu nại lần hai hoặc coi kiến nghị làm dừng thời hiệu. Chưa xác minh kênh nhận và thời hạn riêng của đề nghị kiểm tra; kiểm tra tại ngày gửi.

**Sau phản hồi của Sở, ngày 22/10:** nguồn `reports/sau_phan_hoi_so_20261022.md` → `/ho-so-duy-tan/sau-phan-hoi-so/`. Tám nhánh P01–P08, bản đề nghị làm rõ, đoạn kiến nghị tỉnh kiểm tra và hướng xác định đúng thủ tục. Bổ sung ba PDF hợp nhất về khiếu nại/tố tụng; nguồn và SHA-256 tại `data/escalation_sources_20261022.json`. Luật Khiếu nại đã gồm sửa đổi hiệu lực 01/07/2026, thời hạn thụ lý đủ điều kiện là 07 ngày làm việc. Không coi thư hướng dẫn Sở là quyết định giải quyết khiếu nại, không coi gửi thư là dừng thời hiệu, không mặc định Sở là cấp khiếu nại lần hai của Chủ tịch phường. Chưa có phản hồi thật nên chưa chọn người bị khiếu nại/kiện hoặc tính ngày cuối. Trang dùng chung `preparedDraft`, toàn bộ nội dung tiếp tục lấy từ Markdown; không thay 11 kịch bản cấp phường.

**Bản đề nghị Sở hướng dẫn ngày 22/10:** nguồn `reports/de_nghi_so_huong_dan_50m2_20261022.md` → `/ho-so-duy-tan/de-nghi-so-huong-dan/`, dùng khi phường vẫn không đồng ý 50 m² hoặc căn cứ/cách áp dụng chưa rõ. Bản đầy đủ, hai cách trình bày theo phản hồi, bảng đối chiếu và danh mục chứng cứ cùng nằm trong Markdown. Dùng chung giao diện `preparedDraft`; metadata `draftFilename` đặt tên TXT riêng. Chỉ đoạn nằm giữa hai marker được sao chép/tải/in; phần hướng dẫn không đi vào bản gửi. Cần điền phản hồi và chứng cứ thực nhận, chưa coi đề nghị hướng dẫn là khiếu nại hoặc tự xác định Sở là cấp giải quyết tiếp theo.

**Bản bổ sung 50 m² ngày 22/10:** nguồn là `reports/du_thao_bo_sung_50m2_20261022.md` trong module hồ sơ. Phần giữa `<!-- prepared-draft:start -->` và `<!-- prepared-draft:end -->` là nguyên văn bản được nạp vào ô chỉnh sửa; chỉ phần này được sao chép, tải TXT và in. Hướng dẫn/câu hỏi tiếp/nguồn nằm ngoài bản gửi. Metadata `preparedDraft: true` bật giao diện trong `src/bao-cao.njk`; nội dung pháp lý không chép riêng vào JavaScript. Chỉnh trên trình duyệt không ghi ngược vào Markdown và không tự lưu qua lần mở khác; cần tải TXT để giữ phần sửa. Dùng sau khi điền văn bản thực nhận, chưa suy hồ sơ 106 m² đã được điều chỉnh hoặc phường đã bác 50 m².

**Căn cứ trọng tâm đã rà tiếp ngày 21/10:** đọc `reports/hieu_luc_han_muc_50m2_20261021.md` và `data/legal_validity_review_20261021.json` trong module hồ sơ. Đã khớp hình bản ký 193/43/64, sửa lỗi lớp chữ bỏ sót; thêm 192, 194, 86 và nguồn Công báo. Điều 6 NĐ 50 quy định chính sách một lần, lịch sử tính từ 01/08/2024; không hứa giữ lại hạn mức nếu chuyển 50 m² trước. Phạm vi rà gồm 200 trích yếu Công báo (127 năm 2026), không phải toàn văn tất cả. Khi có phản hồi thực tế, vẫn tra văn bản mới và quy định chuyển tiếp đúng thời điểm.

**Khi tiếp tục xử lý phản hồi của phường:** đọc trước `ho_so_phap_ly_dat_dai_ninh_binh/reports/muc_san_sang_phan_hoi_20261021.md`. Có bảng nguồn theo 11 nhánh, mức kiểm chứng, danh mục chứng cứ còn thiếu và quy trình phân tích đầu vào mới. Giữ kịch bản xấu nhất cùng phương án 50 m²; không coi hồ sơ 106 m² đã tự được điều chỉnh. Khi có văn bản mới, lưu bản gốc đủ trang và ngày nhận, đối chiếu câu hỏi đã gửi, kiểm tra hiệu lực theo nội dung thực tế rồi mới ghép dự thảo. Không dùng số lượng tài liệu làm mức chắc pháp lý.

Rà soát ngày 21/10 đã đối chiếu lại khoản 3 Điều 11 NQ 254 tại ảnh trang 13 và hai giải đáp chính thức của Bộ: chuyển một phần thửa đất không bắt buộc tách thửa; vẫn phải đáp ứng điều kiện chuyển mục đích. Đã sửa nhận định quá dè dặt ở kịch bản 50 m² và bổ sung nguồn S09/Q07. Biên bản dữ liệu nằm tại `data/response_readiness_audit_20261021.json` trong module hồ sơ. Tạo kiểm kê theo ngày rà soát bằng `node scripts/audit-response-readiness.mjs YYYY-MM-DD`; kiểm tra đường dẫn/SHA-256 không thay việc thẩm định hiệu lực hoặc đủ điều kiện.

Ưu tiên người dùng xác nhận ngày 21/10/2026: chuẩn bị dữ liệu và các kịch bản để nhanh chóng trả lời khi Chủ tịch phường có văn bản. Tập trung vào từng lý do thực tế, không chỉ tăng số lượng nghiên cứu. Nguồn nội dung là `reports/bo_phan_hoi_van_ban.md`; các mục `## S01…S11` và sáu mục con được `lib/reply-content.mjs` đọc cho giao diện. Sửa lập luận tại Markdown rồi build; không chép nội dung kịch bản vào JavaScript. Dự thảo không tự suy lời nói miệng thành lý do chính thức, không tự ghi đã đính kèm tài liệu, không dùng mốc giao đơn thay ngày tiếp nhận hợp lệ và không tự biến kiến nghị thành khiếu nại. Nội dung nhập xử lý tại trình duyệt; chỉ lưu localStorage khi người dùng bấm lưu, không ghi lại vào nguồn Markdown. Lưu trữ gắn với đúng địa chỉ/cổng web; bản TXT có thể giữ riêng.

Bổ sung cùng ngày: người dùng xác nhận nhu cầu chỉ cần 50 m² ở vị trí phù hợp và đặc biệt yêu cầu giữ kịch bản trưởng phòng/chủ tịch nhất quyết không đồng ý. Nguồn `reports/duy_tan_tu_choi_50m2.md` → `/ho-so-duy-tan/van-khong-dong-y/` có câu hỏi và câu hỏi tiếp, đoạn đưa vào đơn, bảng ghi nhận và khung đề nghị Sở. S09 trong bộ ghép dự thảo thể hiện sẵn sàng điều chỉnh còn 50 m²; S11 dùng khi vẫn không đồng ý. Chưa có sơ đồ 50 m², chưa tự sửa hồ sơ 106 m². Không suy thiếu câu trả lời thành cố ý bỏ qua; phân biệt kiến nghị chuyên môn với tuyến khiếu nại theo quy định hiện hành.

Mỗi kịch bản có thể thêm mục tùy chọn `### Tiêu đề trong văn bản` để dự thảo dùng tiêu đề phù hợp khi gửi cơ quan. S09/S11 dùng tiêu đề trung tính; nhãn “nhất quyết không đồng ý” chỉ giúp nhận diện tình huống trên giao diện. Sáu mục nội dung bắt buộc vẫn giữ nguyên.

Theo yêu cầu người dùng ngày 20/10/2026, trình bày kết quả nghiên cứu theo hai mức: phần đọc nhanh khoảng hai phút ở trước, gồm kết luận chính, 3–5 điểm đáng nhớ và cách dùng khi trao đổi/viết đơn; phần điều khoản, tài liệu gốc và kiểm chứng chi tiết ở sau hoặc qua liên kết. Giữ giới hạn làm thay đổi kết luận ngay cạnh nhận định tương ứng; tránh bắt người đọc đi qua toàn bộ báo cáo dài mới biết điều gì có ích cho hồ sơ.

Ngày 20/10, đã đối chiếu một phần hồ sơ Anhome theo quyền đọc người dùng cung cấp. Ba PDF nguồn được lưu nguyên vẹn kèm SHA-256 tại `documents/ho_so_duy_tan/anhome/` trong module hồ sơ. Người dùng xác nhận hoàn cảnh chăm sóc bà cố, chú ở lâu dài, con gái đang ở với ông bà ngoại và cho phép sử dụng để giải trình; quy mô nhà là hai tầng chính, tầng 3/mái có một phần công năng. Bản vẽ kiến trúc chưa xác định ranh CLN 106 m². Giữ riêng xác nhận người dùng, nội dung bản vẽ và suy luận; xem báo cáo tình huống mới. Không thay dữ liệu thiết kế tại Anhome.

Các tài liệu nguồn vẫn nằm trong `nghien_cuu_quy_trinh/` và `ho_so_phap_ly_dat_dai_ninh_binh/`. Site dựng trực tiếp từ báo cáo Markdown, CSV và JSON hiện có. Không phải sao chép nội dung báo cáo sang template khi sửa bài.

Giữ nguyên bản PDF/Word nguồn. Build sao chép chúng vào `_site/tai-lieu/`; CSV/JSON được đưa vào `_site/du-lieu/`. Nguồn khoảng 656 MB nên lần build đầu có thể lâu hơn lần xem trước. Dev dùng passthrough để phục vụ tài liệu trực tiếp, không sao chép lại toàn kho mỗi lần sửa giao diện.

Sau khi bổ sung quyết định, chạy công cụ kiểm chứng/chuẩn bị dữ liệu trong [hướng dẫn dữ liệu](ho_so_phap_ly_dat_dai_ninh_binh/README.md) để đồng bộ `decisions_2026.csv`, `display_data.json` và thống kê đã rà soát. Sau đó chạy `npm test`. Các script HTML cũ được giữ để truy nguyên; giao diện thống nhất hiện được dựng bằng Eleventy ở thư mục gốc.

Đợt thu thập nền đến **19/10/2026**, bổ sung riêng Mỹ Lộc đến 20/10 và đọc sâu một số bản quét, hướng dẫn tài chính ngày 21/10; chưa cập nhật toàn bộ địa phương đến ngày 21/10. Dev/build không tự kéo nguồn mới. Việc tổ chức lại không tự nâng mức xác minh của nguồn, không xác nhận toàn bộ chuỗi sửa đổi hiện hành và không kết luận hồ sơ được chấp thuận. Dữ kiện người dùng cung cấp luôn được ghi riêng. Xem [phạm vi rà soát mới](ho_so_phap_ly_dat_dai_ninh_binh/reports/scan_review_20261021.md).

Các HTML trước đây được giữ trong thư mục nguồn. Trong bản site, ba URL HTML cũ chuyển sang đường dẫn tương ứng trong sổ tay, kể cả các mục điều hướng cũ của trang hồ sơ pháp lý.
