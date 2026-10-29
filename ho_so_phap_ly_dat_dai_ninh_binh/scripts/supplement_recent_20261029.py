"""Add the two visually reviewed October decisions discovered in a month-filtered search."""
import csv
import hashlib
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from lxml import html
from parse_sources import ROOT, write_csv

DATE = '2026-10-29'


def read(name):
    return list(csv.DictReader((ROOT / 'data' / name).open(encoding='utf-8-sig')))


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    rows = read('decisions_2026.csv')
    fields = list(rows[0])
    old_ids = {r['decision_id'] for r in rows}
    before = {r['decision_id']: r for r in rows}
    manual_path = ROOT / 'data/pdf_manual_reviews.json'
    manual = json.loads(manual_path.read_text(encoding='utf-8'))
    details_path = ROOT / 'data/decision_detail_reviews.json'
    details = json.loads(details_path.read_text(encoding='utf-8'))
    parts = read('decision_components.csv')
    supplements = []
    for number, area, index, slug in [('1737', '168.4', 1, '8'), ('1738', '190', 0, '9')]:
        page_path = f'documents/nguon_web/recent_20261029_xuanhong_{index}.html'
        tree = html.fromstring((ROOT / page_path).read_bytes())
        published = tree.xpath('//time/@datetime')[0]
        assert published.startswith('2026-10-02')
        pdf_url = parse_qs(urlsplit(tree.xpath('//iframe/@src')[0]).query)['url'][0]
        local = f'documents/quyet_dinh_2026/recent20261029_xuanhong_{number}.pdf'
        digest = hashlib.sha256((ROOT / local).read_bytes()).hexdigest()
        key = f'xaxuanhong|{number}/QĐ-UBND|2026-10-01'
        components = [dict(land_before='CLN', land_after='ONT', area_m2=area)]
        note = 'Bổ sung từ tìm kiếm giới hạn 29/09–29/10/2026; trang nguồn đăng 02/10/2026. Đã đọc ảnh số/ngày trang 1 và Điều 1 trang 2. Văn bản không nêu riêng tổng diện tích thửa; không dùng diện tích chuyển để thay thế tổng thửa.'
        row = {f: '' for f in fields}
        row.update(decision_id=key, locality='Xã Xuân Hồng', issuing_authority='UBND Xã Xuân Hồng',
                   decision_number=number + '/QĐ-UBND', issue_date='2026-10-01',
                   land_before='CLN', land_after='ONT', conversion_group='CLN->ONT', area_m2=area,
                   verification_status='official_pdf', pdf_identity_status='matched_number_and_date',
                   area_status='verified_pdf_identity', content_pdf_page='2',
                   source_page=f'https://xuanhong.ninhbinh.gov.vn/quyet-dinh-ve-viec-cho-phep-chuyen-muc-dich-su-dung-dat-{slug}/',
                   pdf_url=pdf_url, local_pdf=local, checked_on=DATE, notes=note,
                   parcel_area_m2='', initial_land_json='{}', post_land_json='{}',
                   residential_conversion_m2=area, components_json=json.dumps(components),
                   detail_status='visual_reviewed', detail_pdf_pages='1,2', detail_checked_on=DATE,
                   detail_notes_json=json.dumps([note], ensure_ascii=False), detail_flags_json='[]', term_after='Lâu dài')
        before[key] = row
        manual = [r for r in manual if r['record']['decision_id'] != key]
        manual.append(dict(record=row, sha256=digest, page_start=1, page_end=2,
                           method='visual_header_and_article_1_on_rendered_pdf_pages', reviewed_on=DATE))
        details[key] = dict(pages='1,2', fields={f: row[f] for f in ['parcel_area_m2', 'initial_land_json', 'post_land_json', 'residential_conversion_m2', 'components_json', 'area_m2', 'area_status', 'land_before', 'land_after', 'conversion_group', 'term_after']},
                            notes=[note], checked_on=DATE, source_pdf=local, sha256=digest)
        parts = [p for p in parts if p['decision_id'] != key]
        parts.append(dict(decision_id=key, component='1', **components[0], pdf_path=local,
                          pdf_pages='2', content_review='visual_reviewed', identity_status='matched_number_and_date', area_status='verified_pdf_identity'))
        supplements.append(dict(row, source_published_on=published[:10], source_html=page_path, sha256=digest))
    assert len({r['sha256'] for r in supplements}) == 2
    # No other existing decision is rewritten.
    write_csv(ROOT / 'data/decisions_2026.csv', list(before.values()), fields)
    write_csv(ROOT / 'data/decision_components.csv', parts, list(parts[0]))
    dump(manual_path, manual)
    dump(details_path, details)
    write_csv(ROOT / 'data/search_supplement_20261029.csv', supplements)
    coverage = read('coverage_129.csv')
    for row in coverage:
        if row['locality'] == 'Xã Xuân Hồng':
            row.update(pages_checked=str(max(int(row['pages_checked']), 2)), records_found=str(sum(r['locality'] == 'Xã Xuân Hồng' for r in before.values())),
                       status='found_public_records', checked_on=DATE,
                       notes='Tìm kiếm giới hạn một tháng; đọc hai bài đăng 02/10 và hai PDF 1737, 1738 ngày 01/10/2026. Chưa khẳng định duyệt hết chuyên mục/phân trang.')
    write_csv(ROOT / 'data/coverage_129.csv', coverage)
    scope_path = ROOT / 'data/decision_collection_scope.json'
    scope = json.loads(scope_path.read_text(encoding='utf-8'))
    scope.update(cutoff=DATE, latest_search_window=['2026-09-29', DATE],
                 note='Tập nguồn trước đây được bổ sung tìm kiếm giới hạn 29/09–29/10/2026 vào ngày 29/10. Mốc cập nhật mới không xác nhận đã rà toàn bộ cổng của 129 địa phương đến ngày này.')
    dump(scope_path, scope)
    dump(ROOT / 'data/search_audit_20261029.json', dict(checked_on=DATE, window_start='2026-09-29', window_end=DATE,
         base_query='site:ninhbinh.gov.vn chuyển mục đích', search_method='Bộ lọc 30 ngày và after/before; truy vấn thêm cụm cho phép, ngày tháng và loại bớt thủ tục/rừng. Kiểm tra lại ngày đăng trên HTML nguồn, không dùng ngày crawl làm ngày ban hành.',
         accepted_records=[r['decision_id'] for r in supplements], added=sum(r['decision_id'] not in old_ids for r in supplements),
         limitations='Kết quả tìm kiếm không bảo đảm đầy đủ. Nhiều kết quả là thủ tục, chuyển mục đích rừng, hoặc văn bản cũ được crawl lại; không nhập các kết quả này như quyết định chuyển sang đất ở.'))
    report = '''<!-- web: {"updatedOn":"2026-10-29","featured":true,"order":1,"icon":"folder"} -->
# Bổ sung hồ sơ từ tìm kiếm một tháng, ngày 29/10/2026

**Căn cứ:** Quyết định **1737/QĐ-UBND** và **1738/QĐ-UBND**, cùng ngày **01/10/2026** của UBND xã Xuân Hồng; Điều 1 ở trang 2 PDF. Hai bài nguồn đăng **02/10/2026**, nằm trong khoảng tìm **29/09–29/10/2026**.

| Quyết định | Hướng chuyển | Diện tích được phép chuyển | Tổng diện tích thửa |
| --- | --- | ---: | --- |
| [1737/QĐ-UBND](../documents/quyet_dinh_2026/recent20261029_xuanhong_1737.pdf#page=2) | CLN → ONT | 168,4 m² | Không nêu riêng |
| [1738/QĐ-UBND](../documents/quyet_dinh_2026/recent20261029_xuanhong_1738.pdf#page=2) | CLN → ONT | 190 m² | Không nêu riêng |
| **Tổng bổ sung** | | **358,4 m²** | |

Đã đối chiếu ảnh số/ngày trang 1, đọc Điều 1 trang 2 và kiểm tra toàn văn. Thời hạn đất ở: lâu dài; hình thức: giao đất có thu tiền sử dụng đất. Không suy tổng diện tích thửa từ diện tích chuyển hay từ số thửa/số tờ bản đồ. Không ghi thông tin tên, địa chỉ cư trú hay giấy tờ cá nhân trong bảng thống kê.

[Nguồn 1737](https://xuanhong.ninhbinh.gov.vn/quyet-dinh-ve-viec-cho-phep-chuyen-muc-dich-su-dung-dat-8/) · [Nguồn 1738](https://xuanhong.ninhbinh.gov.vn/quyet-dinh-ve-viec-cho-phep-chuyen-muc-dich-su-dung-dat-9/) · [Tải bảng dữ liệu](../data/search_supplement_20261029.csv).

Tìm bằng `site:ninhbinh.gov.vn chuyển mục đích` với bộ lọc một tháng và các truy vấn bổ sung. Chỉ bổ sung hai hồ sơ đã tải, đọc PDF và chống trùng bằng địa phương + số + ngày, kèm SHA256. Các kết quả thủ tục hành chính, chuyển mục đích rừng và văn bản cũ được lập chỉ mục lại không được tính thành quyết định mới. Đây là kết quả tìm thấy của đợt tra, không phải tổng ban hành toàn tỉnh trong tháng.
'''
    (ROOT / 'reports/search_supplement_20261029.md').write_text(report, encoding='utf-8')
    print(f'Added {sum(r["decision_id"] not in old_ids for r in supplements)}; total {len(before)}; residential conversion 358.4 m2; parcel totals unavailable.')


if __name__ == '__main__':
    main()
