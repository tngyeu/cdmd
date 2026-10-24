"""Build an auditable download catalog from the 10 browser-observed result pages."""
import collections
import csv
import hashlib
import html
import json
import logging
import shutil
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
import zipfile

from pypdf import PdfReader
from parse_sources import ROOT, write_csv

logging.getLogger('pypdf').setLevel(logging.ERROR)
sys.stdout.reconfigure(encoding='utf-8')
DATE = '2026-10-20'
FOLDER = ROOT / 'documents/quyet_dinh_myloc_20261020'
MANIFEST = json.loads((ROOT / 'data/myloc_browser_manifest_20261020.json').read_text(encoding='utf-8'))
FIELDS = ['source_number', 'pdf_number_reviewed', 'issue_date', 'year', 'list_page', 'source_page', 'pdf_url', 'direct_asset_url', 'local_pdf', 'download_status', 'pdf_pages', 'bytes', 'sha256', 'residential_area_m2', 'area_pdf_page', 'review_note']
AREA_PATH = ROOT / 'data/myloc_area_review_20261020.json'
AREA_REVIEW = json.loads(AREA_PATH.read_text(encoding='utf-8')) if AREA_PATH.exists() else None


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def inventory():
    result = []
    areas = {r['local_pdf']: r for r in AREA_REVIEW['records']} if AREA_REVIEW else {}
    for number, issued, page, steering, prefix, filename, title_match in MANIFEST['items']:
        original = MANIFEST['handler_urls'].get(steering, MANIFEST['prefixes'][prefix] + filename)
        direct = parse_qs(urlsplit(original).query).get('Url', [original])[0]
        relative = f'{issued[:4]}/myloc_{number}_{issued}.pdf'
        target = FOLDER / relative
        row = dict(source_number=number + '/QĐ-UBND', pdf_number_reviewed='', issue_date=issued, year=issued[:4], list_page=page,
                   source_page=f'https://myloc.ninhbinh.gov.vn/?pageid=35106&p_steering={steering}', pdf_url=original,
                   direct_asset_url=direct, local_pdf='', download_status='unavailable_http_403', pdf_pages='', bytes='', sha256='',
                   residential_area_m2='', area_pdf_page='', review_note='Cổng và tệp gốc trả HTTP 403; chưa có PDF, không coi tải thành công.')
        if target.exists():
            raw = target.read_bytes()
            assert raw.startswith(b'%PDF'), target
            reader = PdfReader(target)
            row.update(local_pdf=target.relative_to(ROOT).as_posix(), download_status='downloaded_identity_unreviewed',
                       pdf_pages=len(reader.pages), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                       review_note='Đã tải và kiểm tra tệp PDF đọc được; số/ngày lấy từ cổng, chưa đọc ảnh định danh toàn bộ tệp.')
        if steering == '200182':
            row.update(pdf_number_reviewed='5305/QĐ-UBND', download_status='header_visually_matched',
                       review_note='Đã đọc ảnh trang 1: số 5305/QĐ-UBND, ngày 20/10/2026 khớp cổng. Chưa xác minh diện tích từ toàn văn.')
        if steering in ('187552', '187553'):
            actual = '1968' if steering == '187552' else '1969'
            row.update(pdf_number_reviewed=actual + '/QĐ-UBND', download_status='metadata_pdf_number_conflict',
                       review_note=f'Ảnh trang 1 ghi {actual}/QĐ-UBND ngày 22/10/2025; cổng ghi {number}/QĐ-UBND. Giữ cả hai thông tin, không tự coi là hai quyết định.')
        if row['local_pdf'] in areas:
            area = areas[row['local_pdf']]
            assert row['sha256'] == area['sha256']
            assert row['source_number'] == area['decision_number'] and issued == area['issue_date']
            row.update(pdf_number_reviewed=area['decision_number'], download_status='area_visually_reviewed',
                       residential_area_m2=area['residential_area_m2'], area_pdf_page=area['content_pdf_page'],
                       review_note=area['note'])
        result.append(row)
    assert len(result) == 93
    assert len({r['source_page'] for r in result}) == 93
    return result


def merge_2026(rows):
    scope_path = ROOT / 'data/decision_collection_scope.json'
    prior_scope = json.loads(scope_path.read_text(encoding='utf-8')) if scope_path.exists() else {}
    target = ROOT / 'data/decisions_2026.csv'
    prior = list(csv.DictReader(target.open(encoding='utf-8-sig')))
    fields = list(prior[0])
    by_id = {r['decision_id']: r for r in prior}
    added = 0
    for doc in rows:
        if doc['year'] != '2026':
            continue
        key = f"phuongmyloc|{doc['source_number']}|{doc['issue_date']}"
        if key not in by_id:
            by_id[key] = {field: '' for field in fields}
            by_id[key].update(decision_id=key, locality='Phường Mỹ Lộc', issuing_authority='UBND Phường Mỹ Lộc',
                              decision_number=doc['source_number'], issue_date=doc['issue_date'], conversion_group='chua_xac_dinh',
                              verification_status='official_metadata', pdf_identity_status='downloaded_requires_identity_review',
                              initial_land_json='{}', post_land_json='{}', components_json='[]', detail_notes_json='[]', detail_flags_json='[]')
            added += 1
        row = by_id[key]
        row.update(source_page=doc['source_page'], pdf_url=doc['pdf_url'], local_pdf=doc['local_pdf'], checked_on=DATE)
        if row['verification_status'] != 'official_pdf':
            row['notes'] = 'Bổ sung qua 10 trang tìm kiếm Mỹ Lộc ngày 20/10/2026. PDF đã tải; số/ngày theo cổng, chưa đọc ảnh định danh và diện tích. Một quyết định chưa đồng nghĩa một hộ duy nhất.'
            row['detail_status'] = 'downloaded_requires_review'
        if doc['download_status'] == 'header_visually_matched':
            row.update(verification_status='official_pdf', pdf_identity_status='matched_number_and_date',
                       notes=doc['review_note'], detail_status='identity_header_reviewed', detail_pdf_pages='1', detail_checked_on=DATE)
    write_csv(target, list(by_id.values()), fields)
    coverage_path = ROOT / 'data/coverage_129.csv'
    coverage = list(csv.DictReader(coverage_path.open(encoding='utf-8-sig')))
    for row in coverage:
        if row['locality'] == 'Phường Mỹ Lộc':
            row.update(pages_checked='103', records_found='40', status='found_public_records', checked_on=DATE,
                       notes='Đã đọc 10 trang kết quả và 93 trang chi tiết. 94 dòng có 1 dòng lặp; 40 trang năm 2026, 53 trang năm 2025. Tải đủ 40 PDF năm 2026; dữ liệu 2025 và 6 tệp lỗi 403 giữ trong chỉ mục riêng.')
    write_csv(coverage_path, coverage)
    dump(ROOT / 'data/decision_collection_scope.json', {
        'cutoff': DATE,
        'note': 'Tập ban đầu đến 19/10/2026 được bổ sung riêng Mỹ Lộc đến 20/10/2026; chưa cập nhật lại toàn bộ địa phương đến ngày 20/10.',
        'myloc_added_records': added or prior_scope.get('myloc_added_records', 0),
        'myloc_2026_records': 40
    })
    return added or prior_scope.get('myloc_added_records', 0), len(by_id)


def make_catalog(rows, summary):
    FOLDER.mkdir(parents=True, exist_ok=True)
    write_csv(FOLDER / 'danh_muc.csv', rows, FIELDS)
    if AREA_REVIEW:
        shutil.copyfile(ROOT / 'data/myloc_residential_area_2026.csv', FOLDER / 'dien_tich_2026.csv')
    write_csv(ROOT / 'data/myloc_documents_20261020.csv', rows, FIELDS)
    labels = {'downloaded_identity_unreviewed': 'Đã tải PDF', 'header_visually_matched': 'Số/ngày đã đọc ảnh',
              'area_visually_reviewed': 'Đã đối chiếu diện tích ODT',
              'metadata_pdf_number_conflict': 'Số cổng khác PDF', 'unavailable_http_403': 'Chưa tải được · HTTP 403'}
    table = []
    for row in rows:
        file = Path(row['local_pdf']).relative_to(FOLDER.relative_to(ROOT)).as_posix() if row['local_pdf'] else ''
        pdf = f'<a href="{html.escape(file)}" target="_blank" rel="noopener">Mở PDF</a>' if file else '<span class="missing">Tệp nguồn lỗi 403</span>'
        reviewed = f'<small>PDF: {html.escape(row["pdf_number_reviewed"])}</small>' if row['download_status'] == 'metadata_pdf_number_conflict' else ''
        area = row['residential_area_m2']
        area_display = area.replace('.', ',') if area else 'Chưa thống kê'
        table.append(f'<tr data-year="{row["year"]}" data-number="{row["source_number"].split("/")[0]}" data-date="{row["issue_date"]}" data-area="{area}" data-loaded="{bool(file)}"><td>{html.escape(row["source_number"])}{reviewed}</td><td>{row["issue_date"]}</td><td>{area_display}</td><td>{labels[row["download_status"]]}</td><td>{pdf} · <a href="{html.escape(row["source_page"])}" target="_blank" rel="noopener">Nguồn phường</a><small>{html.escape(row["review_note"])}</small></td></tr>')
    page = '''<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Quyết định chuyển mục đích · Mỹ Lộc</title><style>
    *{box-sizing:border-box}body{margin:0;background:#f5f7f2;color:#213e33;font:15px/1.65 'Segoe UI',Arial,sans-serif}main{max-width:1140px;margin:auto;padding:34px 20px}h1{font-size:30px;line-height:1.3}h2{font-size:19px}a{color:#215e4b}p{max-width:850px}.note,section{background:#fff;border:1px solid #dbe3d5;border-radius:10px;padding:20px;margin:20px 0}.stats{display:flex;flex-wrap:wrap;gap:16px}.stats div{flex:1;min-width:140px;background:#edf3e6;padding:14px;border-radius:8px}.stats b{font-size:29px;display:block}.controls{display:flex;flex-wrap:wrap;gap:12px;margin:20px 0}input,select,button{font:inherit;padding:8px 11px;border:1px solid #cad6c4;border-radius:5px;background:#fff;color:inherit}.scroll{overflow:auto;max-height:72vh;border:1px solid #dbe3d5;border-radius:7px}table{border-collapse:collapse;width:100%;min-width:680px;background:white;font-size:14px}th,td{padding:12px;vertical-align:top;border-bottom:1px solid #e4eadf;text-align:left}th{position:sticky;top:0;background:#eaf1e2}th button{border:0;background:none;padding:0;font-weight:650;cursor:pointer}small{display:block;color:#637467;font-size:12px;max-width:530px}.missing{color:#956126}tr[hidden]{display:none}footer{margin:22px 0;font-size:13px;color:#667565}@media(max-width:600px){main{padding:20px 14px}h1{font-size:25px}.note,section{padding:15px}}
    </style><main><p>Mỹ Lộc · Tra cứu và tải ngày 20/10/2026</p><h1>94 kết quả tìm kiếm có bao nhiêu văn bản?</h1><p>Nguồn: <a href="https://myloc.ninhbinh.gov.vn/?&amp;sid=2415&amp;pageid=35113" target="_blank" rel="noopener">cổng văn bản phường Mỹ Lộc</a>, từ khóa “chuyển mục đích”, tìm trong toàn bộ. Đã đọc đủ 10 trang, mở từng văn bản ở tab mới.</p>
    <div class="stats"><div><b>94</b>dòng kết quả</div><div><b>93</b>trang văn bản riêng</div><div><b>87</b>PDF đã tải</div><div><b>6</b>tệp nguồn lỗi 403</div></div>
    <div class="note"><strong>Tách theo năm:</strong> 40 văn bản năm 2026, đã tải đủ 40 PDF; 53 văn bản năm 2025, tải được 47. Văn bản 3416/QĐ-UBND lặp ở trang 2 và 3, chỉ tính một lần. Số văn bản chưa xác định số hộ dân duy nhất.<p><strong>Hai sai khác cần giữ:</strong> cổng ghi 1868 và 1869 ngày 22/10/2025, ảnh PDF ghi 1968 và 1969. Đã đối chiếu số/ngày và Điều 1 của đủ 40 PDF năm 2026: tổng chuyển sang đất ở đô thị (ODT) <strong>6.196 m² = 0,6196 ha</strong>, bình quân 154,9 m²/quyết định. Diện tích năm 2025 chưa thống kê.</p></div>
    <p><a href="dien_tich_2026.csv" download>Tải bảng diện tích 40 quyết định năm 2026</a> · <a href="danh_muc.csv" download>Tải danh mục CSV</a> · <a href="../myloc_quyet_dinh_20261020.zip" download>Tải trọn bộ PDF và danh mục</a></p>
    <section><h2>Danh mục đầy đủ · không phân trang</h2><div class="controls"><input id="query" type="search" placeholder="Tìm số quyết định…" aria-label="Tìm số quyết định"><select id="year" aria-label="Năm"><option value="">Cả 2025 và 2026</option value="2026">Năm 2026</option><option value="2025">Năm 2025</option></select><select id="loaded" aria-label="Trạng thái tải"><option value="">Mọi trạng thái</option><option value="True">Đã tải</option><option value="False">Chưa tải được</option></select></div><p id="count" role="status">93 văn bản</p><div class="scroll"><table><thead><tr><th><button data-sort="number">Số quyết định ↕</button></th><th><button data-sort="date">Ngày ban hành ↕</button></th><th><button data-sort="area">Sang ODT (m²) ↕</button></th><th>Tình trạng</th><th>Tệp và nguồn</th></tr></thead><tbody>''' + '\n'.join(table) + '''</tbody></table></div></section>
    <footer>Sáu tệp cũ không tải được: 1523, 1376, 1116, 1115, 1111, 1110/QĐ-UBND năm 2025. Tên tệp lưu theo số trên cổng; sai khác với số trong PDF được ghi riêng. Các liên kết văn bản mở ở tab mới.</footer></main><script>
    const rows=[...document.querySelectorAll('tbody tr')],q=document.querySelector('#query'),y=document.querySelector('#year'),l=document.querySelector('#loaded');y.value=new URLSearchParams(location.search).get('year')||'';let sort={key:'date',asc:false};function render(){const body=document.querySelector('tbody');rows.sort((a,b)=>{if(sort.key==='area'&&(!a.dataset.area||!b.dataset.area))return Number(!a.dataset.area)-Number(!b.dataset.area)||Number(a.dataset.number)-Number(b.dataset.number);let c=sort.key==='number'?Number(a.dataset.number)-Number(b.dataset.number):sort.key==='area'?Number(a.dataset.area)-Number(b.dataset.area):a.dataset.date.localeCompare(b.dataset.date);return (sort.asc?c:-c)||Number(a.dataset.number)-Number(b.dataset.number)});let count=0;for(const row of rows){row.hidden=!!((q.value&&!row.textContent.toLowerCase().includes(q.value.toLowerCase()))||(y.value&&row.dataset.year!==y.value)||(l.value&&row.dataset.loaded!==l.value));if(!row.hidden)count++;body.append(row)}document.querySelector('#count').textContent=count+' / '+rows.length+' văn bản · Bấm tiêu đề số, ngày hoặc diện tích để sắp xếp';for(const button of document.querySelectorAll('[data-sort]'))button.closest('th').setAttribute('aria-sort',sort.key===button.dataset.sort?(sort.asc?'ascending':'descending'):'none')};for(const input of [q,y,l])input.addEventListener('input',render);for(const button of document.querySelectorAll('[data-sort]'))button.addEventListener('click',()=>{const key=button.dataset.sort;sort={key,asc:sort.key===key?!sort.asc:true};render()});render();</script></html>'''
    (FOLDER / 'index.html').write_text(page, encoding='utf-8')
    readme = f'''# Quyết định chuyển mục đích sử dụng đất Mỹ Lộc

Tra cứu ngày 20/10/2026 tại {MANIFEST['source_url']}, từ khóa “chuyển mục đích”, tìm toàn bộ.

- 94 dòng qua 10 trang; 3416/QĐ-UBND lặp giữa trang 2 và 3; còn 93 trang văn bản riêng.
- 2026: 40 trang, tải đủ 40 PDF, từ 14/05 đến 20/10/2026.
- 2025: 53 trang, tải được 47 PDF, từ 25/08 đến 31/12/2025.
- 87 PDF đọc được, {summary['pdf_pages']} trang, SHA256 khác nhau. Đã đọc ảnh định danh và Điều 1 của 40 PDF năm 2026: 6.196 m² sang ODT, tương đương 0,6196 ha; bình quân 154,9 m²/quyết định. Năm 2025 chưa thống kê diện tích.
- Sáu tệp trả 403 ở liên kết FileEntry và URL gốc: 1523, 1376, 1116, 1115, 1111, 1110/QĐ-UBND năm 2025. Nút tải postback của cổng cũng chưa trả tệp khi thử; không ghi là tải thành công.
- Cổng ghi 1868/1869 nhưng ảnh PDF ghi 1968/1969 ngày 22/10/2025. Giữ số nguồn trong tên lưu và ghi số PDF trong danh mục.

Mở index.html để lọc năm, trạng thái và sắp xếp số/ngày/diện tích; các văn bản mở tab mới. danh_muc.csv có URL gốc, đường dẫn tệp, SHA256 và trạng thái từng dòng. dien_tich_2026.csv có 40 dòng, nguồn PDF và diện tích ODT. Quyết định 3438 gồm 74,8 + 215 = 289,8 m²; 3418 gồm 65,4 + 320 = 385,4 m². Không suy số văn bản thành số hộ duy nhất.
'''
    (FOLDER / 'README.md').write_text(readme, encoding='utf-8')
    dump(FOLDER / 'inventory.json', dict(summary, records=rows))


def make_report(summary):
    text = '''# Mỹ Lộc: kết quả tải quyết định ngày 20/10/2026

**Nguồn:** [cổng văn bản Mỹ Lộc](https://myloc.ninhbinh.gov.vn/?&sid=2415&pageid=35113), từ khóa “chuyển mục đích”, tìm toàn bộ. Đã mở văn bản trong tab mới và đọc đủ 10 trang.

| Phạm vi | Trang văn bản riêng | PDF tải được |
| --- | ---: | ---: |
| Năm 2026, 14/05–20/10 | 40 | 40 |
| Năm 2025, 25/08–31/12 | 53 | 47 |
| Tổng | 93 | 87 |

**94 kết quả không phải 94 hộ:** 3416/QĐ-UBND lặp ở trang 2 và 3. Có 93 trang nguồn riêng và 87 tệp PDF khác SHA256; chưa xác nhận số hộ duy nhất. Cổng ghi 1868/1869 nhưng ảnh PDF ghi 1968/1969 ngày 22/10/2025; giữ rõ sai khác.

**Còn thiếu 6 PDF năm 2025:** 1523, 1376, 1116, 1115, 1111 và 1110/QĐ-UBND. Cả liên kết tải động và tệp gốc trả 403; thử nút postback chưa nhận được tệp. Các trang nguồn đã được lưu.

[Mở danh mục đầy đủ: lọc năm, sắp xếp và mở từng PDF](../documents/quyet_dinh_myloc_20261020/index.html) · [Tải trọn bộ 87 PDF](../documents/myloc_quyet_dinh_20261020.zip) · [Danh mục CSV](../data/myloc_documents_20261020.csv)

40 bản ghi năm 2026 được nhập vào bảng quyết định chung, thay cho một bản ghi Mỹ Lộc trước đây; không nhập 53 bản năm 2025 vào bảng năm 2026. **Đã đối chiếu ảnh số/ngày và Điều 1 của đủ 40 PDF năm 2026: tổng được phép chuyển sang ODT là 6.196 m² (0,6196 ha), bình quân 154,9 m²/quyết định.** [Xem thống kê theo tháng và từng quyết định](../reports/myloc_area_2026.md). Năm 2025 chưa thống kê diện tích. Đợt bổ sung riêng Mỹ Lộc đến 20/10 không xác nhận đã cập nhật lại toàn tỉnh đến ngày đó.
'''
    (ROOT / 'reports/myloc_download_20261020.md').write_text(text, encoding='utf-8')


if __name__ == '__main__':
    rows = inventory()
    downloaded = [row for row in rows if row['local_pdf']]
    assert len(downloaded) == 87
    assert len({row['sha256'] for row in downloaded}) == 87
    summary = dict(checked_on=DATE, reported_total=94, unique_source_pages=93, downloaded_pdfs=len(downloaded), missing_pdfs=6,
                   pdf_pages=sum(row['pdf_pages'] for row in downloaded), pdf_bytes=sum(row['bytes'] for row in downloaded),
                   years=dict(collections.Counter(row['year'] for row in rows)), source_url=MANIFEST['source_url'])
    if AREA_REVIEW:
        summary.update(reviewed_2026_decisions=AREA_REVIEW['decisions'], residential_area_2026_m2=AREA_REVIEW['residential_area_m2'], residential_area_2026_ha=AREA_REVIEW['residential_area_ha'])
    make_catalog(rows, summary)
    added, total = merge_2026(rows)
    summary.update(added_2026=added, total_2026=total)
    dump(ROOT / 'data/myloc_download_inventory.json', dict(summary, records=rows))
    make_report(summary)
    archive = ROOT / 'documents/myloc_quyet_dinh_20261020.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=3) as out:
        for file in sorted(FOLDER.rglob('*')):
            if file.is_file():
                out.write(file, Path('my_loc_20261020') / file.relative_to(FOLDER))
    with zipfile.ZipFile(archive) as check:
        assert check.testzip() is None
        assert len([name for name in check.namelist() if name.endswith('.pdf')]) == 87
    print(json.dumps(dict(summary, archive=str(archive), archive_bytes=archive.stat().st_size), ensure_ascii=False, indent=2))
