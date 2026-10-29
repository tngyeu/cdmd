# WordCraft MCP trên Windows

Thiết lập và kiểm tra ngày 29/10/2026. Chưa soạn văn bản chính thức.

## Bản cài và cấu hình

- Desktop: `C:\Program Files\WordCraft\wordcraft.exe`
- CLI: `C:\Program Files\WordCraft\wordcraft-cli.exe`, phiên bản 0.11.0.
- Cấu hình Codex: `C:\Users\thuan\.codex\config.toml`, server toàn cục `wordcraft`, enabled.
- Đã đăng ký bằng `codex mcp add wordcraft -- "C:\Program Files\WordCraft\wordcraft-cli.exe" mcp --connect 127.0.0.1:7981`.
- Desktop đã được chạy bằng `wordcraft.exe --control 7981` và giữ mở để quan sát tài liệu thử nghiệm.

Cấu hình tương đương:

```toml
[mcp_servers.wordcraft]
command = 'C:\Program Files\WordCraft\wordcraft-cli.exe'
args = ["mcp", "--connect", "127.0.0.1:7981"]
```

Tài liệu chính thức: https://github.com/storytold/wordcraft/blob/main/docs/mcp.md

Cấu hình Codex MCP: https://developers.openai.com/codex/mcp/

## Kết quả kiểm tra thực tế

Đã bắt tay JSON-RPC MCP initialize, nhận danh sách công cụ từ tools/list và gọi tools/call tới Desktop, không chỉ kiểm tra cấu hình.

Các công cụ đã chạy: new_document, list_commands, execute, batch, type_text, select_text, inspect_document, get_text, save_document và render_page.

- Tạo tài liệu trắng, nhập 3 đoạn tiếng Việt có dấu và ký hiệu m².
- Đặt A4 dọc, lề trái 3 cm, các lề còn lại khoảng 2 cm.
- Times New Roman 13 pt; tiêu đề đậm 15 pt, căn giữa; nội dung căn đều, giãn dòng 1.15, cách đoạn 6 pt; đoạn cuối nghiêng.
- Lưu DOCX và PDF, mở lại DOCX rồi đọc nội dung và thuộc tính định dạng.
- Sửa một câu trong đoạn giữa, lưu DOCX/PDF sang tên mới, mở lại để xác nhận.
- Đối chiếu inspect_document: các đoạn không sửa cùng định dạng được giữ nguyên; định dạng đoạn giữa và thiết lập trang được giữ nguyên.
- SHA256 của DOCX gốc không đổi sau thử nghiệm: `2E79E5C3974A29AF9145568268BA6A966F9074352B249A9738785131EF1CE5CC`.
- render_page xuất PNG thành công; đã xem trang thử nghiệm.

Tệp thử và nhật ký nằm trong `D:\Workspace\CĐMĐ\tmp\wordcraft_mcp_setup_20261029`:

- Kiem_tra_MCP_goc.docx và Kiem_tra_MCP_goc.pdf.
- Kiem_tra_MCP_da_sua.docx và Kiem_tra_MCP_da_sua.pdf.
- tools.json: schema công cụ thực tế của bản cài.
- log_discovery.json, log_discover_commands.json, log_create_test.json, log_edit_test.json: yêu cầu/phản hồi MCP.
- mcp_probe.py: trình khách MCP stdio để chẩn đoán khi danh sách công cụ của chat chưa nạp server.
- verify_results.py và verification.json: kiểm chứng nội dung, định dạng, XML DOCX và PDF.

## Sử dụng lần sau

1. Mở WordCraft với `--control 7981`; có thể chạy `Mo_WordCraft_MCP.ps1` trong thư mục này. Script chỉ kiểm tra cổng và khởi chạy chương trình, không thao tác GUI.
2. Sau khi thêm server lần đầu, nếu chat chưa có công cụ `wordcraft`, nạp lại kết nối MCP hoặc mở chat mới; nếu vẫn thiếu, khởi động lại Codex. Chưa kiểm chứng việc tự nạp nóng trong chat hiện tại.
3. Gọi inspect_document để xác nhận Desktop đang kết nối và xem nội dung hiện tại trước khi tạo/mở tài liệu khác.
4. Dùng list_commands lấy đúng tên lệnh và tham số, rồi execute/batch/type_text. Dùng select_text để sửa cục bộ.
5. Đọc lại bằng get_text và inspect_document, xem render_page; lưu bằng save_document sang tên mới và mở lại để kiểm tra.

Ví dụ yêu cầu: “Dùng WordCraft Desktop MCP, tạo tài liệu theo nội dung sau; lưu bản mới trong D:\Workspace\CĐMĐ, kiểm tra nội dung và bố cục trước khi giao.”

## Nguyên tắc và giới hạn

- Không dùng chuột, bàn phím giả lập, tọa độ hoặc automation giao diện, kể cả MCP click/key, để soạn thảo. Chức năng thiếu MCP phải báo lại.
- Không ghi đè file hiện có khi chưa được yêu cầu. Tài liệu hiện tại có thể đang có thay đổi chưa lưu: phải kiểm tra trước.
- Sandbox của phiên hiện tại chặn socket loopback (os error 10013). Trình khách chẩn đoán chỉ kết nối được khi thực thi với quyền phù hợp bên ngoài sandbox; không sửa firewall hay cài đặt bảo mật.
- Cấu hình server đã lưu toàn cục, nhưng công cụ native chưa xuất hiện trong danh sách công cụ của chat đang chạy. Các phép thử dùng MCP stdio thực tế qua CLI, gọi chính công cụ của WordCraft.
- Tài liệu GitHub main có chức năng mới hơn bản 0.11.0 đang cài (ví dụ tools/list bản cài không có list_documents hoặc tham số doc). Phải dựa trên tools/list và list_commands thực tế, không suy đoán theo tài liệu mới.
- Bảo toàn định dạng mới được kiểm chứng trên tài liệu ngắn có 3 đoạn. Bảng phức tạp, hình, trường, footnote và các tài liệu Word khác cần kiểm tra riêng.
- Desktop MCP không hỗ trợ automation-read-root/write-root như headless; không phối hợp các cờ này với --connect.
- Không cài phiên bản mới, không bật tự khởi động Windows, không soạn đơn chính thức trong lần thiết lập này.
