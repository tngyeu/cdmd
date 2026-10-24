"""Check source paths, snapshot integrity, decision totals and quota arithmetic."""
import collections
import csv
import json
import re
import subprocess
import shutil
from decimal import Decimal
from pathlib import Path
from urllib.parse import unquote, urlsplit
from lxml import html
from manual_reviews import load_reviews

ROOT = Path(__file__).resolve().parents[1]

def read(name):
    return list(csv.DictReader((ROOT/'data'/name).open(encoding='utf-8-sig')))

def main():
    decisions = read('decisions_2026.csv')
    manual = load_reviews()
    by_id = {row['decision_id']: row for row in decisions}
    for key, review in manual.items():
        assert all(by_id[key][field] == value for field, value in review['record'].items()), key
        assert not any(old in by_id for old in review.get('supersedes_decision_ids', [])), key
    coverage = read('coverage_129.csv')
    quotas = read('land_quotas.csv')
    legal = read('legal_documents.csv')
    legal_by_id = {r['document_id']: r for r in legal}
    assert len(legal_by_id) == len(legal), 'Duplicate legal document ID'
    assert all(r.get('summary') and r.get('practical_relevance') and r.get('summary_basis') for r in legal), 'Missing reviewed legal description'
    assert not any(r['title'] == 'Luật được viện dẫn trong chuỗi sửa đổi Luật Đất đai' for r in legal), 'Generic placeholder title'
    # Signed originals override the known incorrect catalogue dates.
    assert (legal_by_id['NB-NQ48-2025']['issued_date'], legal_by_id['NB-NQ48-2025']['effective_date']) == ('2025-12-09','2026-01-01')
    assert (legal_by_id['NB-NQ28-2026']['issued_date'], legal_by_id['NB-NQ28-2026']['effective_date']) == ('2026-04-29','2026-04-29')
    assert legal_by_id['NB-KL-QUYDAT-202605']['issued_date'] == '', 'Do not substitute meeting date for issue date'
    assert legal_by_id['CV6456']['issued_date'] == '', 'Unverified issue date'
    budget_by_metric = {r['metric']: r for r in read('budget_metrics.csv')}
    assert budget_by_metric['Dự toán HĐND: tổng thu tiền sử dụng đất']['status'] == 'official_pdf_visual_review'
    assert Decimal(budget_by_metric['Nguồn thu tiền sử dụng đất kế hoạch đầu tư công do tỉnh quản lý']['value_vnd_billion']) + Decimal(budget_by_metric['Nguồn thu tiền sử dụng đất kế hoạch đầu tư công do xã phường quản lý']['value_vnd_billion']) == Decimal(budget_by_metric['Nguồn thu tiền sử dụng đất trong kế hoạch đầu tư công trung hạn']['value_vnd_billion'])
    display = json.loads((ROOT/'data/display_data.json').read_text(encoding='utf-8'))
    keys = [(r['locality'], r['decision_number'], r['issue_date']) for r in decisions]
    assert len(keys) == len(set(keys)), 'Duplicate decision identity'
    assert len(coverage) == 129 and len({r['locality'] for r in coverage}) == 129
    known = {r['locality'] for r in coverage}
    assert all(r['locality'] in known for r in decisions)
    scope=json.loads((ROOT/'data/decision_collection_scope.json').read_text(encoding='utf-8'))
    assert all('2026-01-01' <= r['issue_date'] <= scope['cutoff'] for r in decisions)
    for table in (decisions, legal, quotas, read('land_reserves.csv'), read('land_quota_history.csv')):
        for row in table:
            for key in ('local_pdf', 'local_file', 'pdf_path'):
                value = row.get(key)
                if not value:
                    continue
                target = ROOT/unquote(urlsplit(value).path)
                assert target.is_file(), f'Missing {key}: {value}'
                if target.suffix.lower() == '.pdf':
                    with target.open('rb') as stream:
                        assert stream.read(5) == b'%PDF-', f'Invalid PDF: {target}'
    assert len({r['land_code'] for r in quotas}) == len(quotas)
    for r in quotas:
        delta = Decimal(r['target_ha']) - Decimal(r['baseline_ha'])
        assert delta == Decimal(r['change_ha']), r
        assert delta/5 == Decimal(r['average_2026_2030_ha']), r
    valid = [r for r in decisions if r['pdf_identity_status'] != 'shared_pdf_conflict']
    areas = [r for r in valid if r['area_status'] == 'verified_pdf_identity']
    assert all(r['verification_status'] == 'official_pdf' and r['land_before'] and r['land_after'] and Decimal(r['area_m2']) > 0 for r in areas)
    for r in decisions:
        if r['pdf_identity_status'] == 'shared_pdf_conflict':
            assert r['area_status'] != 'verified_pdf_identity'
    stats = display['stats']
    assert display['decisions'] == decisions
    assert display['coverage'] == coverage and display['legal'] == legal
    assert stats['records'] == len(decisions)
    assert stats['verified'] == len(valid)
    assert stats['pdf_verified'] + stats['metadata_verified'] == len(valid)
    assert stats['verified_area_records'] == len(areas)
    assert Decimal(stats['verified_area_m2']) == sum((Decimal(r['area_m2']) for r in areas), Decimal(0))
    assert sum(r['records'] for r in display['monthly']) == len(valid)
    assert sum(r['records'] for r in display['types']) == len(valid)
    assert sum(r['records'] for r in display['locality_summary']) == len(decisions)
    summary=display['locality_summary']
    assert len(summary)==129
    assert sum(r['known_area_records'] for r in summary)==len(areas)+sum(r['area_status']=='official_attachment_identity_pending' and bool(r['area_m2']) for r in valid)
    assert sum(Decimal(r['area_m2']) for r in summary)==Decimal(stats['verified_area_m2'])
    assert sum(Decimal(r['pending_area_m2']) for r in summary)==Decimal(stats['pending_area_m2'])
    assert read('locality_summary_2026.csv')==[{k:str(v) for k,v in r.items()} for r in summary]
    page = ROOT/'index.html'
    tree = html.fromstring(page.read_bytes())
    ids = tree.xpath('//@id')
    assert len(ids) == len(set(ids)), 'Duplicate HTML IDs'
    embedded = json.loads(tree.get_element_by_id('researchData').text)
    assert embedded == display, 'HTML snapshot out of date'
    for href in tree.xpath('//a/@href'):
        parts = urlsplit(href)
        if parts.scheme or parts.netloc:
            continue
        if parts.path:
            assert (ROOT/unquote(parts.path)).is_file(), f'Broken HTML link: {href}'
        elif parts.fragment:
            assert unquote(parts.fragment) in ids, f'Unknown section: {href}'
    for a in tree.xpath('//a[@href]'):
        href = a.get('href')
        if href.startswith(('https://','http://','documents/','reports/','data/')):
            assert a.get('target') == '_blank', href
            assert {'noopener','noreferrer'} <= set(a.get('rel','').split()), href
    province = json.loads((ROOT/'data/province_document_sources.json').read_text(encoding='utf-8'))
    for key, entry in province['documents'].items():
        row = next(r for r in legal if r['document_id'] == key)
        assert row['source_url'] == entry['updates']['source_url']
        assert urlsplit(row['source_url']).hostname == 'ninhbinh.gov.vn'
        assert (ROOT/entry['snapshot']).is_file()
    assert not tree.xpath('//script[@src] | //link[@rel="stylesheet"]'), 'Offline dependency'
    headings = [''.join(x.itertext()) for x in tree.xpath('//table[contains(@class,"decision-table")]/thead/tr/th')]
    assert len(headings) == 8 and 'Từ loại đất' in headings and 'Sang loại đất' in headings
    assert 'Chuyển / Tổng thửa(m²)' in headings
    for row in decisions:
        components=json.loads(row.get('components_json') or '[]')
        if components:
            assert sum(Decimal(c['area_m2']) for c in components)==Decimal(row['area_m2']), row['decision_id']
        if row.get('parcel_area_m2') and row.get('area_m2'):
            assert Decimal(row['area_m2'])<=Decimal(row['parcel_area_m2']), row['decision_id']
        if 'internal_area_conflict' in json.loads(row.get('detail_flags_json') or '[]'):
            assert row['area_status']=='source_internal_area_conflict', row['decision_id']
            assert row not in areas
    assert stats['parcel_area_records']==sum(bool(r.get('parcel_area_m2')) for r in decisions)
    assert stats['visual_reviewed']==sum(r.get('detail_status')=='visual_reviewed' for r in decisions)
    assert not re.search(r'Mở trang danh sách quyết định riêng', page.read_text(encoding='utf-8'))
    client = tree.xpath('//script[not(@type)]')[-1].text
    node = shutil.which('node') or str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')
    subprocess.run([node, '--check', '--input-type=commonjs'], input=client, text=True, encoding='utf-8', check=True)
    subprocess.run([node,str(ROOT/'scripts/validate_locality_summary.mjs')],check=True)
    print(json.dumps({'result': 'PASS', 'decisions': len(decisions), 'verified_pdf': stats['pdf_verified'], 'verified_area_m2': stats['verified_area_m2'], 'coverage_localities': len(coverage), 'legal_documents': len(legal), 'quota_rows': len(quotas), 'html_ids': len(ids), 'local_links': len(tree.xpath('//a/@href'))}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
