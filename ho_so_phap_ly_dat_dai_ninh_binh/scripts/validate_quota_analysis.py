"""Validate the independent quota page, source snapshots and scenario arithmetic."""
import csv
from decimal import Decimal as D
import hashlib
import json
import math
import re
import shutil
import subprocess
from urllib.parse import unquote, urlsplit
from lxml import html
from parse_sources import ROOT


def main():
    d = json.loads((ROOT/'data/residential_quota_analysis.json').read_text(encoding='utf-8'))
    assert hashlib.sha256((ROOT/d['source_pdf']).read_bytes()).hexdigest() == d['source_pdf_sha256']
    for name, digest in d['input_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, f'Rebuild analysis: {name}'
    assert len(d['quotas']) == len({r['locality'] for r in d['quotas']}) == 129
    flat = list(csv.DictReader((ROOT/'data/residential_quotas_129.csv').open(encoding='utf-8-sig')))
    assert len(flat) == 258
    for row in d['quotas']:
        for code in ('ODT','ONT'):
            q = row[code]
            if q['change_ha'] is None:
                assert row['locality'] == 'Xã Chất Bình' and code == 'ODT'
                assert q['baseline_ha'] is q['target_ha'] is None
            else:
                assert round(q['target_ha']-q['baseline_ha'],2) == q['change_ha']
    assert d['gain_m2'] == 502600
    assert d['duy_tan']['ONT']['change_ha'] == 0
    wards = sorted([r for r in d['quotas'] if r['kind']=='Phường'],key=lambda r:r['ODT']['change_ha'],reverse=True)
    assert len(wards) == 31 and wards[0]['locality'] == 'Phường Đông A'
    assert wards[28]['locality'] == 'Phường Duy Tân'
    for row in d['scenarios']:
        assert row['total_cases'] == math.floor(D(502600)/D(row['mean_m2']))
        assert abs(row['annual_capacity']-502600/row['mean_m2']/5) < 1e-7
    assert 'demand' not in d and 'shares' not in d
    assert len(d['observed_comparisons']) == 3
    decisions=list(csv.DictReader((ROOT/'data/decisions_2026.csv').open(encoding='utf-8-sig')))
    assert {r['locality'] for r in d['public_decisions']} == {r['locality'] for r in decisions}
    for row in d['public_decisions']:
        assert row['records']==sum(r['locality']==row['locality'] for r in decisions), row['locality']
    assert d['cutoff']==json.loads((ROOT/'data/decision_collection_scope.json').read_text(encoding='utf-8'))['cutoff']
    assert sorted(s['annualized_count'] for s in d['activity_sources']) == [32,180,328]
    page = ROOT/'chi_tieu_dat_o_2030.html'
    tree = html.fromstring(page.read_bytes())
    ids = tree.xpath('//@id')
    assert len(ids) == len(set(ids))
    assert json.loads(tree.get_element_by_id('quotaData').text) == d
    assert not tree.xpath('//script[@src] | //link[@rel="stylesheet"]')
    for href in tree.xpath('//a/@href'):
        parts = urlsplit(href)
        if parts.scheme or parts.netloc: continue
        if parts.path: assert (ROOT/unquote(parts.path)).is_file(), href
        elif parts.fragment: assert unquote(parts.fragment) in ids, href
    for a in tree.xpath('//a[@href]'):
        href = a.get('href')
        if href.startswith(('https://','http://','documents/','reports/','data/')):
            assert a.get('target') == '_blank', href
            assert {'noopener','noreferrer'} <= set(a.get('rel','').split()), href
    client = tree.xpath('//script[not(@type)]')[-1].text
    subprocess.run([shutil.which('node'),'--check','--input-type=commonjs'],input=client,text=True,encoding='utf-8',check=True)
    report = (ROOT/'reports/residential_quota_2030.md').read_text(encoding='utf-8')
    assert len(re.findall(r'^## ',report,re.M)) == 5
    assert report.index('## 1. Căn cứ văn bản') < report.index('## 2. Tính ngược:') < report.index('## 3. Ghép số hộ')
    assert tree.xpath('//div[@id="briefContent"]/section/@id') == ['legal-basis','analysis','method']
    legal = tree.get_element_by_id('legal-basis').text_content()
    for phrase in ('3279/QĐ-UBND', '30/08/2026', 'UBND tỉnh Ninh Bình', 'Điều 1', 'Điều 2 khoản 4', 'Phụ lục 121', 'Đã đọc số/ngày và chữ ký/dấu của quyết định', 'riêng dòng dẫn số/ngày trên phụ lục còn trống'):
        assert phrase in legal, phrase
    h = d['households']
    assert h['households'] == 8934 and h['population'] == 27849
    assert h['published_date'] == '2026-06-04' and h['statistical_reference_date'] is None
    assert hashlib.sha256((ROOT/h['local_file']).read_bytes()).hexdigest() == h['source_sha256']
    snapshot = html.fromstring((ROOT/h['local_file']).read_bytes())
    assert '8.934 hộ gia đình' in snapshot.text_content()
    article = next(json.loads(el.text) for el in snapshot.xpath('//script[@type="application/ld+json"]') if json.loads(el.text).get('@type') == 'NewsArticle')
    assert article['datePublished'].startswith(h['published_date'])
    for row in h['capacity_scenarios']:
        assert row['household_capacity'] == 502600 // row['mean_m2']
        assert abs(row['share_of_baseline_percent']-row['household_capacity']/8934*100) < 1e-9
    assert 'demand_scenarios' not in h and 'annual_scenarios' not in h
    assert 'quotaArea' in ids and 'householdDemandShare' not in ids
    assert '8.934' in tree.get_element_by_id('analysis').text_content()
    assert len(tree.xpath('//details[contains(@class,"extra")]')) == 3
    assert not tree.xpath('//details[contains(@class,"extra") and @open]')
    brief = json.loads((ROOT/'data/residential_quota_brief.json').read_text(encoding='utf-8'))
    assert brief['full_ha'] == 50.26 and 'household_rows' not in brief
    assert [r['mean_m2'] for r in brief['capacity_rows']] == [106,150,200]
    expected_populations = {'Phường Đông A':(9406,31980),'Xã Khánh Thiện':(6616,24281),'Xã Hiển Khánh':(8786,30210)}
    for row in brief['benchmark_rows']:
        g = row['demographics']
        assert (g['households'],g['population']) == expected_populations[row['locality']]
        assert hashlib.sha256((ROOT/g['local_file']).read_bytes()).hexdigest() == g['source_sha256']
        assert abs(row['cases_per_1000_households_period'] - row['count']/g['households']*1000) < 1e-10
        assert abs(row['cases_per_1000_households_month'] - row['count']/g['households']/row['period_months']*1000) < 1e-10
        assert g['published_date'] is None or g['published_date'] <= d['cutoff']
    dong_a = next(r for r in brief['benchmark_rows'] if r['locality']=='Phường Đông A')
    assert dong_a['count'] == 15 and dong_a['period_months'] == 1
    assert round(dong_a['cases_per_1000_households_month'],2) == 1.59
    assert round(brief['monthly_capacity_per_1000_households'],2) == 6.25
    assert round(dong_a['capacity_to_observed_rate'],1) == 3.9
    projection=brief['projection']
    assert projection['period_start']=='2026-01-01' and projection['period_end']=='2030-12-31'
    assert projection['source_count']==82 and projection['source_period_months']==3
    assert projection['annual_cases']==328 and projection['period_cases']==1640
    assert D(str(projection['area_ha']))==D(1640)*150/10000==D('24.6')
    assert projection['province_rank_confirmed'] is False
    extra=tree.get_element_by_id('higherPace').text_content()
    for phrase in ('01/01/2026','1.640','24,6 ha','chưa có thống kê đủ','toàn tỉnh'):
        assert phrase in extra,phrase
    brief_text=(ROOT/'reports/residential_quota_brief.md').read_text(encoding='utf-8')
    assert '25%' not in brief_text and '10%' not in brief_text
    print(json.dumps(dict(result='PASS',localities=129,quota_rows=258,ward_rank=29,scenario_total_150m2=3350,scenario_annual_150m2=670.1333333333333,activity_sources=3),ensure_ascii=True))


if __name__ == '__main__':
    main()
