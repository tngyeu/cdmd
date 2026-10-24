"""Record the 40 source-bound visual reviews of Mỹ Lộc's 2026 ODT grants.

The annotations below were checked against rendered page 1 (identity) and
page 2 (Article 1), not inferred from the first area in extracted text.
"""
import collections
import csv
import hashlib
import json
import logging
import sys
from decimal import Decimal

from manual_reviews import load_reviews
from parse_sources import ROOT, write_csv

logging.getLogger('pypdf').setLevel(logging.ERROR)
DATE = '2026-10-20'
# Preserve the source's LNK/TSN codes in 5305 rather than silently recoding them.
ANNOTATIONS = {
    '5305': [('LNK', '113'), ('TSN', '47')],
    '5306': [('CLN', '68')], '5179': [('CLN', '55')],
    '4932': [('NTS', '100')], '4933': [('CLN', '200')],
    '4931': [('NTS', '95')], '4864': [('CLN', '70')],
    '4865': [('NTS', '210')], '4809': [('NTS', '242.5')],
    '4652': [('NTS', '130')], '4577': [('CLN', '80')],
    '4410': [('NTS', '160')], '4385': [('CLN', '116')],
    '4351': [('NTS', '180')], '4162': [('NTS', '407')],
    '4109': [('CLN', '88')], '4068': [('CLN', '80')],
    '3414': [('NTS', '150')], '3415': [('CLN', '70')],
    '3416': [('CLN', '120')],
    '3418': [('CLN', '65.4'), ('NTS', '320')],
    '3438': [('CLN', '74.8'), ('NTS', '215')],
    '2315': [('NTS', '115')], '2254': [('HNK', '132')],
    '2255': [('CLN', '90')], '2256': [('NTS', '160')],
    '2257': [('CLN', '118.3')], '2260': [('CLN', '113')],
    '2090': [('NTS', '120')], '2089': [('NTS', '120')],
    '2091': [('CLN', '125')], '2092': [('CLN', '290')],
    '2000': [('NTS', '168')], '1706': [('CLN', '80')],
    '1707': [('NTS', '225')], '1708': [('CLN', '368')],
    '1709': [('NTS', '100')], '1594': [('CLN', '145')],
    '1595': [('CLN', '150')], '1556': [('CLN', '120')],
}


def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def read_csv(name):
    return list(csv.DictReader((ROOT / 'data' / name).open(encoding='utf-8-sig')))


def vi(value):
    formatted = format(Decimal(value), ',f')
    if '.' in formatted:
        formatted = formatted.rstrip('0').rstrip('.')
    return formatted.replace(',', '_').replace('.', ',').replace('_', '.')


def main():
    extracted = json.loads((ROOT / 'tmp/pdfs/myloc_area_2026/texts.json').read_text(encoding='utf-8'))
    assert len(extracted) == len(ANNOTATIONS) == 40
    records = read_csv('decisions_2026.csv')
    by_id = {r['decision_id']: r for r in records}
    manual_path = ROOT / 'data/pdf_manual_reviews.json'
    manual = json.loads(manual_path.read_text(encoding='utf-8'))
    details_path = ROOT / 'data/decision_detail_reviews.json'
    details = json.loads(details_path.read_text(encoding='utf-8'))
    reviewed, new_manual, new_components = [], [], []
    for doc in extracted:
        number = doc['source_number'].split('/')[0]
        parts = ANNOTATIONS[number]
        pdf = ROOT / doc['local_pdf']
        assert hashlib.sha256(pdf.read_bytes()).hexdigest() == doc['sha256']
        assert doc['article_pages'] == [2]
        key = f"phuongmyloc|{doc['source_number']}|{doc['issue_date']}"
        row = by_id[key]
        assert row['local_pdf'] == doc['local_pdf']
        components = [dict(land_before=code, land_after='ODT', area_m2=area) for code, area in parts]
        total = sum((Decimal(a) for _, a in parts), Decimal(0))
        note = 'Đã đối chiếu ảnh trang 1 (số/ngày) và Điều 1 trang 2: diện tích được phép chuyển sang ODT; không lấy tổng diện tích thửa.'
        if number == '5305':
            note += ' Hai phần 113 m² LNK + 47 m² TSN = 160 m²; giữ nguyên ký hiệu nguồn.'
        elif number == '3418':
            note += ' Tổng 385,4 m² gồm 65,4 m² CLN + 320 m² NTS; chỉ cộng tổng một lần.'
        elif number == '3438':
            note += ' Hai phần 74,8 m² CLN + 215 m² NTS = 289,8 m², đều chuyển sang ODT.'
        elif number == '3416':
            note += ' Dòng nguồn lặp giữa hai trang tìm kiếm, chỉ tính quyết định này một lần.'
        row.update(land_before='+'.join(c for c, _ in parts), land_after='ODT',
                   conversion_group='hon_hop_da_tach' if len(parts) > 1 else parts[0][0] + '->ODT',
                   area_m2=str(total), residential_conversion_m2=str(total),
                   verification_status='official_pdf', pdf_identity_status='matched_number_and_date',
                   area_status='verified_pdf_identity', content_pdf_page='2', checked_on=DATE,
                   notes=note, parcel_area_m2='', initial_land_json='{}', post_land_json='{}',
                   components_json=json.dumps(components, ensure_ascii=False),
                   detail_notes_json=json.dumps([note], ensure_ascii=False),
                   detail_status='visual_reviewed', detail_pdf_pages='1,2', detail_checked_on=DATE,
                   detail_flags_json='[]', term_after='Lâu dài')
        reviewed.append(dict(decision_id=key, decision_number=doc['source_number'], issue_date=doc['issue_date'],
                             land_after='ODT', residential_area_m2=str(total), components=components,
                             source_page=doc['source_page'], local_pdf=doc['local_pdf'],
                             sha256=doc['sha256'], identity_pdf_page=1, content_pdf_page=2,
                             reviewed_on=DATE, note=note))
        new_manual.append(dict(record=dict(row), sha256=doc['sha256'], page_start=1, page_end=2,
                               method='visual_header_and_article_1_on_rendered_pdf_pages', reviewed_on=DATE))
        detail_fields = ['parcel_area_m2', 'initial_land_json', 'post_land_json', 'residential_conversion_m2',
                         'components_json', 'area_m2', 'area_status', 'land_before', 'land_after',
                         'conversion_group', 'term_after', 'detail_flags_json']
        details[key] = dict(pages='1,2', fields={f: row[f] for f in detail_fields}, notes=[note],
                            checked_on=DATE, source_pdf=doc['local_pdf'], sha256=doc['sha256'])
        for i, component in enumerate(components, 1):
            new_components.append(dict(decision_id=key, component=i, **component,
                                       pdf_path=doc['local_pdf'], pdf_pages='2', content_review='visual_reviewed',
                                       identity_status='matched_number_and_date', area_status='verified_pdf_identity'))
    reviewed.sort(key=lambda r: (r['issue_date'], int(r['decision_number'].split('/')[0])))
    total = sum((Decimal(r['residential_area_m2']) for r in reviewed), Decimal(0))
    assert total == Decimal('6196.0')
    assert len({r['sha256'] for r in reviewed}) == 40
    months = collections.defaultdict(list)
    for row in reviewed:
        months[row['issue_date'][:7]].append(Decimal(row['residential_area_m2']))
    monthly = [dict(month=m, decisions=len(values), area_m2=str(sum(values, Decimal(0)))) for m, values in sorted(months.items())]
    summary = dict(reviewed_on=DATE, decisions=40, residential_area_m2=str(total),
                   residential_area_ha=str(total / 10000), mean_m2=str(total / 40),
                   first_date=reviewed[0]['issue_date'], last_date=reviewed[-1]['issue_date'],
                   land_after='ODT', method='Đọc ảnh trang 1 và Điều 1 trang 2 của từng PDF; cộng các phần được phép chuyển sang đất ở.',
                   monthly=monthly)
    dump(ROOT / 'data/myloc_area_review_20261020.json', dict(summary, records=reviewed))
    area_rows = []
    for row in reviewed:
        area_rows.append({**{k: row[k] for k in ['decision_number', 'issue_date', 'land_after', 'residential_area_m2']},
                          'components': ' + '.join(f"{c['area_m2']} {c['land_before']}" for c in row['components']),
                          **{k: row[k] for k in ['content_pdf_page', 'local_pdf', 'source_page', 'sha256', 'reviewed_on', 'note']}})
    write_csv(ROOT / 'data/myloc_residential_area_2026.csv', area_rows)
    write_csv(ROOT / 'data/decisions_2026.csv', records, list(records[0]))
    keys = {r['decision_id'] for r in reviewed}
    dump(manual_path, [r for r in manual if r['record']['decision_id'] not in keys] + new_manual)
    dump(details_path, details)
    prior_components = read_csv('decision_components.csv')
    write_csv(ROOT / 'data/decision_components.csv', [r for r in prior_components if r['decision_id'] not in keys] + new_components, list(prior_components[0]))
    bound_reviews = load_reviews()
    assert all(k in bound_reviews for k in keys)

    lines = ['# Mỹ Lộc: diện tích chuyển sang đất ở trong 40 quyết định năm 2026', '',
             '**Căn cứ thống kê:** Điều 1 của 40 quyết định cho phép chuyển mục đích do UBND phường Mỹ Lộc ban hành từ **14/05 đến 20/10/2026**, tải từ cổng văn bản của phường. Đã đối chiếu số/ngày ở trang 1 và phần cho phép chuyển ở trang 2 của từng PDF.', '',
             '**Tổng được phép chuyển sang đất ở đô thị (ODT): 6.196 m² = 0,6196 ha.** Bình quân **154,9 m²/quyết định**.', '',
             '| Tháng ban hành | Số quyết định | Chuyển sang ODT (m²) |', '| --- | ---: | ---: |']
    for m in monthly:
        lines.append(f"| {m['month'][5:]}/2026 | {m['decisions']} | {vi(m['area_m2'])} |")
    lines += ['| **Tổng** | **40** | **6.196** |', '',
              'Con số này là **diện tích đã được cho phép trong tập 40 văn bản công khai**, chưa xác nhận đã nộp tiền hay hoàn thành chuyển mục đích. Không suy 40 quyết định thành 40 hộ duy nhất; cũng không khẳng định đây là toàn bộ quyết định của phường từ 01/01/2026.', '',
              '**Điểm cần cộng đủ:** Quyết định 3438/QĐ-UBND ngày 13/08/2026 có 74,8 m² CLN + 215 m² NTS, tổng **289,8 m²**. Quyết định 3418 có tổng 385,4 m² gồm hai phần, không cộng lặp. Quyết định 3416 xuất hiện hai lần trên cổng nhưng chỉ tính một.', '',
              '[Mở danh mục có cột diện tích và sắp xếp](../documents/quyet_dinh_myloc_20261020/index.html?year=2026) · [Tải bảng 40 dòng CSV](../data/myloc_residential_area_2026.csv)', '',
              '<details><summary>Đối chiếu từng quyết định và PDF gốc</summary>', '',
              '| Quyết định | Ngày ban hành | Sang ODT (m²) | Các phần diện tích trước chuyển |', '| --- | --- | ---: | --- |']
    for row in reviewed:
        parts = ' + '.join(f"{vi(c['area_m2'])} {c['land_before']}" for c in row['components'])
        lines.append(f"| [{row['decision_number']}](../{row['local_pdf']}#page=2) | {'/'.join(reversed(row['issue_date'].split('-')))} | {vi(row['residential_area_m2'])} | {parts} |")
    lines += ['', '</details>', '', 'Mỗi dòng CSV giữ đường dẫn PDF, trang Điều 1, URL cổng và SHA256 để truy nguyên. Ký hiệu LNK/TSN trong Quyết định 5305 được giữ nguyên theo bản gốc.']
    (ROOT / 'reports/myloc_area_2026.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
