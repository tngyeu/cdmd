"""Record the visual source review of Phu Long 231 and provincial letter 5061."""
import hashlib
import json
from pathlib import Path

from parse_sources import ROOT, write_csv
from enrich_legal_index import apply_legal_editorial


def read_json(relative):
    return json.loads((ROOT / relative).read_text(encoding='utf-8'))


def save_json(relative, value):
    (ROOT / relative).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


editorial = read_json('data/legal_editorial.json')
phulong = {
    'verification_status': 'official_pdf',
    'relevant_articles': 'Phần căn cứ, đoạn mục tiêu ngân sách và mục 1–4; PDF trang 1',
    'current_status': 'Thông báo tiếp tục tiếp nhận từ 01/08/2026 tại Phú Long; chưa rà mọi văn bản tiếp theo',
    'relationship': 'Triển khai Công văn tỉnh 5061/UBND-VP5 về thu tiền sử dụng đất; viện dẫn chỉ tiêu theo 1702 tại thời điểm tháng 7. Chỉ tiêu hiện đối chiếu theo 3279 từ 30/08/2026.',
    'notes': 'Đã đọc ảnh toàn trang: số 231/TB-UBND, ngày 29/07/2026, chữ ký/dấu và tên Phó Chủ tịch Đinh Mạnh Cường. Lớp chữ trích xuất bỏ sót số/ngày được điền; sửa ghi chú cũ rằng PDF trống. Metadata người ký Đặng Xuân Tuấn khác bản ký, ưu tiên bản ký. URL người dùng gửi trùng SHA256 với phulong_notice_375.pdf. Công văn 5061 đã có bản gốc độc lập trên cổng tỉnh.',
    'summary': 'Để phù hợp chỉ tiêu và bảo đảm nguồn thu ngân sách xã 6 tháng cuối năm, tiếp tục nhận, giải quyết hồ sơ chuyển đất nông nghiệp sang đất ở từ 01/08/2026; giao tiếp nhận, thẩm định và thông tin cho người dân.',
    'practical_relevance': 'Dẫn chứng trực tiếp về địa phương tổ chức giải quyết hồ sơ chuyển mục đích để thực hiện mục tiêu thu. Dùng hỏi Duy Tân về kế hoạch triển khai 5061 và vướng mắc cụ thể; chưa có chứng cứ phường chưa triển khai hoặc phải áp dụng cùng lịch Phú Long.',
    'summary_basis': 'Đọc ảnh trang 1, phần dẫn 1702/5061, mục tiêu nguồn thu và mục 1–4; đã khớp số/ngày trên ảnh, chữ ký/dấu, lưu ý sai khác người ký trên metadata.'
}
editorial['documents']['NB-PL-231-2026'].update(phulong)

verified_decisions = {
    'NB1702': {
        'verification_status': 'official_pdf',
        'effective_date': '2026-05-12',
        'notes': 'Đã đọc ảnh cả 2 trang từ cổng tỉnh: số 1702/QĐ-UBND, ngày 12/05/2026, chữ ký/dấu Nguyễn Anh Chức. Điều 2 hiệu lực từ ngày ký. Lớp chữ bỏ sót số/ngày; sửa ghi chú cũ rằng đầu PDF trống. Quyết định đã hết hiệu lực từ 30/08/2026 theo Điều 3 Quyết định 3279; phụ lục Duy Tân trong bộ 1702 chưa đối chiếu.',
        'summary_basis': 'Ảnh trang 1–2 của bản ký; trích yếu cổng tỉnh; Điều 3 trang 4 bản ký 3279. Phần Duy Tân trong phụ lục 1702 chưa đối chiếu.'
    },
    'NB-3279-2026': {
        'verification_status': 'official_pdf',
        'effective_date': '2026-08-30',
        'notes': 'Đã đọc ảnh trang 1, 3–4: số 3279/QĐ-UBND, ngày 30/08/2026, chữ ký/dấu Nguyễn Anh Chức; Điều 3 hiệu lực từ ngày ký và cho 162/1702 hết hiệu lực. Sửa ghi chú cũ rằng đầu quyết định trống do lớp chữ bỏ sót số/ngày. Phụ lục 129 đơn vị công bố cùng trang tỉnh, trùng SHA256 bộ đã lưu; riêng dòng dẫn số/ngày ở phụ lục 121 trang 241 vẫn trống.',
        'summary_basis': 'Điều 1–3; ảnh quyết định trang 1, 3–4; biểu toàn tỉnh; phụ lục 121 trang 241–242. Đã khớp số/ngày trên ảnh quyết định; dòng dẫn phụ lục còn trống.'
    }
}
for document_id, updates in verified_decisions.items():
    editorial['documents'][document_id].update(updates)

letter = {
    'document_id': 'NB-CV5061-2026',
    'number': '5061/UBND-VP5',
    'group': 'Ngân sách/quỹ đất',
    'title': 'Tập trung chỉ đạo thực hiện công tác thu tiền sử dụng đất năm 2026',
    'issuer': 'UBND tỉnh Ninh Bình',
    'issued_date': '2026-07-18',
    'effective_date': '',
    'current_status': 'Chỉ đạo công tác thu năm 2026; chưa rà mọi văn bản triển khai hoặc điều chỉnh tiếp theo',
    'verification_status': 'official_pdf',
    'document_class': 'chi_dao_hanh_chinh',
    'relevant_articles': 'Đoạn tình hình thu và mục 1–3; PDF trang 1–2',
    'relationship': 'Được Thông báo 231/TB-UBND ngày 29/07/2026 của Phú Long viện dẫn khi tổ chức tiếp tục nhận hồ sơ chuyển mục đích; đọc cùng Đề án 08 và phân bổ chỉ tiêu hiện tại theo 3279.',
    'source_url': 'https://ninhbinh.gov.vn/?pageid=27160&p_steering=47617',
    'local_file': 'documents/phap_luat/province_5061_original.pdf',
    'checked_on': '2026-10-19',
    'notes': 'Bản ký 2 trang ghi số 5061/UBND-VP5, ngày 18/07/2026; trang 2 có chữ ký/dấu Nguyễn Anh Chức. Metadata cổng tỉnh ghi ngày ban hành/hiệu lực 20/07/2026; ưu tiên ngày 18/07 trên bản ký, chưa gán ngày hiệu lực riêng. Mục 1 nhấn mạnh nguồn đấu giá đất nhỏ lẻ xen kẹp và đất đã đầu tư hạ tầng, không trực tiếp yêu cầu chấp thuận mọi hồ sơ chuyển mục đích. Biểu giao thu được viện dẫn không có trong tệp 2 trang; chưa có số riêng Duy Tân.',
    'summary': 'Giao Chủ tịch UBND các xã/phường tập trung thu tiền sử dụng đất, nhất là đấu giá, chịu trách nhiệm về kết quả; giao Sở Tài chính và Sở Nông nghiệp và Môi trường theo dõi, đôn đốc. Thu tiền sử dụng đất đến 14/07/2026 là 8.474,279 tỷ đồng, đạt 19,99% dự toán HĐND.',
    'practical_relevance': 'Xác nhận chỉ đạo thu ở cấp tỉnh áp dụng cho xã/phường. Đọc cùng bản ký Phú Long 231 để chứng minh một địa phương đã triển khai bằng tiếp nhận, thẩm định hồ sơ chuyển mục đích đủ điều kiện; từ đó hỏi kế hoạch và vướng mắc cụ thể tại Duy Tân.',
    'summary_basis': 'Đọc ảnh cả 2 trang, số/ngày tại trang 1, chữ ký/dấu trang 2, đoạn tình hình và mục 1–3; đối chiếu Thông báo 231.'
}
editorial['new_documents'] = [row for row in editorial['new_documents'] if row['document_id'] != letter['document_id']]
editorial['new_documents'].append(letter)
save_json('data/legal_editorial.json', editorial)

import csv
rows = list(csv.DictReader((ROOT / 'data/legal_documents.csv').open(encoding='utf-8-sig')))
rows = apply_legal_editorial(rows)
write_csv(ROOT / 'data/legal_documents.csv', rows)

province = read_json('data/province_document_sources.json')
for document_id, updates in verified_decisions.items():
    province['documents'][document_id]['updates'].update(updates)
province['documents'][letter['document_id']] = {
    'number': letter['number'],
    'snapshot': 'documents/nguon_web/province_document_5061.html',
    'attachment_urls': ['https://storage-vnportal.vnpt.vn/nbh-ubnd/2925/Năm 2026/Văn bản/80. giao chỉ tiêu thu ngân sách cac px 19.pdf'],
    'updates': {key: letter[key] for key in ['source_url', 'local_file', 'checked_on', 'issued_date', 'verification_status', 'notes']}
}
save_json('data/province_document_sources.json', province)

# Refresh only the legal payload; preserve reports and decision calculations.
display = read_json('data/display_data.json')
display['legal'] = rows
save_json('data/display_data.json', display)

review = {
    'checked_on': '2026-10-19',
    'documents': [],
    'duy_tan_check': {
        'queries': json.loads((ROOT / 'tmp/jobs_duytan_budget_check.json').read_text(encoding='utf-8')),
        'result': 'Hai truy vấn văn bản điều hành theo 5061 và chuyển mục đích hiển thị không tìm thấy văn bản. Hai truy vấn mục tin không cho thấy thông báo tương ứng. Chưa đủ kết luận chưa ban hành hoặc chưa triển khai.',
        'coverage': 'Phạm vi các trang tìm kiếm đã lưu, không phải toàn bộ hồ sơ quản lý của phường.'
    },
    'assessment': 'Chuỗi chứng cứ: phân bổ chỉ tiêu tại thời điểm tháng 7 theo 1702; nhiệm vụ thu chung theo 5061; Phú Long triển khai nhận, thẩm định chuyển mục đích theo 231. Phân bổ hiện đối chiếu theo 3279 từ 30/08/2026.',
    'source_conflicts': {
        'NB-CV5061-2026': 'Ngày trên bản ký 18/07/2026, metadata cổng tỉnh 20/07/2026; dùng ngày trên bản ký.',
        'NB-PL-231-2026': 'Người ký trên bản ký Đinh Mạnh Cường, metadata Đặng Xuân Tuấn; dùng bản ký.',
        'text_extraction': 'Lớp chữ bỏ sót số/ngày ở 231, 1702 và 3279; đã sửa nhận định trống sau khi đọc ảnh. Dòng dẫn phụ lục 121 của 3279 vẫn trống số/ngày.'
    },
    'missing': ['Biểu giao thu kèm 5061', 'Kế hoạch triển khai và số theo dõi chính thức tại Duy Tân']
}
for document_id, relative, pages in [
    ('NB-PL-231-2026', 'documents/phap_luat/phulong_notice_375.pdf', [1]),
    ('NB-CV5061-2026', letter['local_file'], [1, 2]),
    ('NB1702', 'documents/phap_luat/province_1702_original.pdf', [1, 2]),
    ('NB-3279-2026', 'documents/quy_hoach/3279_2026_quyet_dinh.pdf', [1, 3, 4]),
    ('NB-3279-2026-PL121', 'documents/quy_hoach/3279_2026_phu_luc_129.pdf', [241])
]:
    review['documents'].append({'document_id': document_id, 'local_file': relative, 'sha256': hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(), 'visual_pages': pages})
save_json('data/budget_implementation_review_20261019.json', review)
print(f'Updated legal index: {len(rows)} records; visual reviews and source conflicts recorded.')
