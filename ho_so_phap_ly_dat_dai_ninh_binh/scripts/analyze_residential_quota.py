"""Derive residential-quota comparisons without treating missing data as zero."""
import csv
import datetime as dt
from decimal import Decimal as D
import hashlib
import json
import math
import re
import statistics
import sys
from parse_sources import ROOT, write_csv

sys.stdout.reconfigure(encoding='utf-8')

SCOPE = json.loads((ROOT/'data/decision_collection_scope.json').read_text(encoding='utf-8'))
CUTOFF = dt.date.fromisoformat(SCOPE['cutoff'])
PDF = 'documents/quy_hoach/3279_2026_phu_luc_129.pdf'


def read(name):
    return list(csv.DictReader((ROOT / 'data' / name).open(encoding='utf-8-sig')))


def number(value):
    return D(value.replace('.', '').replace(',', '.'))


def vn(value, places=2):
    return f'{value:,.{places}f}'.replace(',', '_').replace('.', ',').replace('_', '.')


def write_report(data):
    h = data['households']
    rows = data['observed_comparisons']
    gain = data['gain_m2']
    mean = 150
    threshold = gain/mean/60/h['households']*1000
    east = next(r for r in rows if r['locality']=='Phường Đông A')
    ratio = threshold/east['cases_per_1000_households_month']
    lines = ['# Chỉ tiêu ODT Duy Tân: sức chứa và số hồ sơ thực tế công bố', '',
        '## 1. Căn cứ văn bản', '',
        '**Quyết định 3279/QĐ-UBND ngày 30/08/2026 của UBND tỉnh Ninh Bình**, theo [trang công bố của tỉnh](https://ninhbinh.gov.vn/?pageid=27160&p_steering=48598). Điều 1 và Phụ lục 121, trang 241 ghi ODT Duy Tân: 269,76 ha hiện trạng 2025, 320,02 ha chỉ tiêu 2030, chênh lệch tăng ròng 50,26 ha. ONT bằng 0 tại cả hai mốc. [Phụ lục Duy Tân](../documents/quy_hoach/3279_2026_phu_luc_129.pdf#page=241).', '',
        '[Điều 2 khoản 4](../documents/quy_hoach/3279_2026_quyet_dinh.pdf#page=3) yêu cầu chuyển mục đích phù hợp chỉ tiêu được phân bổ và báo cáo kết quả thực hiện. Mức tăng ròng chưa phải số còn lại để giải quyết cho hộ. Bảng dự trữ ODT 100 ha ở trang 242 là bảng riêng, không tự cộng/trừ cơ học vào 50,26 ha.', '',
        'Đã đọc ảnh số 3279, ngày 30/08/2026 tại trang 1 và chữ ký/dấu tại trang 4 của quyết định; lớp chữ đã bỏ sót số/ngày. Riêng dòng dẫn số/ngày trên phụ lục 121 còn trống. Bộ quyết định, biểu tổng tỉnh và phụ lục 129 đơn vị được công bố cùng trang tỉnh, trùng SHA-256 với bộ đã lưu từ nguồn địa phương.', '',
        'Theo Điều 3 tệp công khai, 162/QĐ-UBND ngày 19/01/2026 và 1702/QĐ-UBND ngày 12/05/2026 hết hiệu lực khi quyết định này có hiệu lực; phần định hướng sử dụng đất trong 568/1543 thực hiện theo quyết định này. Không suy thành toàn bộ 568/1543 hết hiệu lực. [Điều 3, trang 4](../documents/quy_hoach/3279_2026_quyet_dinh.pdf#page=4).', '',
        '## 2. Tính ngược: 50,26 ha tương đương bao nhiêu trường hợp?', '',
        f'**Mẫu số dân cư Duy Tân:** {vn(h["households"],0)} hộ, {vn(h["population"],0)} người, theo [bài công bố 04/06/2026]({h["source_url"]}). Không coi tổng số hộ là số có nhu cầu; không suy số hộ từ dân số.', '',
        'Công thức: 502.600 m² / diện tích chuyển mỗi trường hợp, lấy phần nguyên. Quy đổi thành hộ chỉ khi mỗi hộ có một lần chuyển; chưa xác nhận các quyết định/báo cáo đều tương ứng các hộ riêng biệt.', '',
        '| Phần chuyển/trường hợp | Số trường hợp tương đương | So với số hộ Duy Tân | Bình quân/năm nếu chia 5 |', '| ---: | ---: | ---: | ---: |']
    for r in h['capacity_scenarios']:
        lines.append(f'| {r["mean_m2"]} m² | {vn(r["household_capacity"],0)} | {vn(r["share_of_baseline_percent"])}% | ≈ {vn(gain/r["mean_m2"]/5,0)} |')
    lines += ['', f'150 m² là mốc quy đổi làm tròn, gần bình quân {vn(data["sample"]["ward_mean_m2"])} m² của {data["sample"]["ward_n"]} quyết định ở phường đọc được diện tích; mẫu chọn lọc, chưa đại diện riêng Duy Tân. 106 m² là phần chuyển người dùng cung cấp; 200 m² là mốc so độ nhạy của phép chia.', '',
        '## 3. Ghép số hộ, dân số và hồ sơ của đúng địa phương', '',
        '| Địa phương | Quy mô dân cư được công bố | Hồ sơ thực tế trong kỳ | Hồ sơ/1.000 hộ trong kỳ | Bình quân/tháng/1.000 hộ |', '| --- | --- | --- | ---: | ---: |']
    for r in rows:
        g=r['demographics']
        lines.append(f'| {r["locality"]} | [{vn(g["households"],0)} hộ; {vn(g["population"],0)} người]({g["source_url"]}) | [{r["count"]} — {r["period"]}]({r["source_url"]}); {r["unit"]} | {vn(r["cases_per_1000_households_period"])} | {vn(r["cases_per_1000_households_month"])} |')
    lines += ['', 'Tỷ lệ trong kỳ = số hồ sơ / số hộ công bố × 1.000. Bình quân tháng chia tiếp cho số tháng của kỳ. Đây là tỷ lệ **hồ sơ so với quy mô hộ**, không phải tỷ lệ các hộ duy nhất có nhu cầu, không phải dự báo số hồ sơ năm hay mức trung bình toàn tỉnh.', '',
        'Nguồn có đơn vị khác nhau: Đông A là tiếp nhận/giải quyết, Khánh Thiện là trường hợp được cho phép, Hiển Khánh là hồ sơ đã giải quyết. Chưa có diện tích hoặc xác nhận tất cả đều sang đất ở. Không cộng 15, 82, 16 thành một tổng chung; không cộng lẫn quyết định đã tải với báo cáo tổng hợp.', '']
    for r in rows:
        g=r['demographics']
        lines += [f'- **{r["locality"]}:** {g["source_period_label"]}. {g["caveat"]} [Bản quy mô dân cư đã lưu](../{g["local_file"]}'+(f'#page={g["pdf_page"]}' if g.get('pdf_page') else '')+f'). Nguồn hồ sơ: {r["meaning"]} [Bản đã lưu](../{r["local_file"]}'+(f'#page={r["pdf_page"]}' if r.get('pdf_page') else '')+').']
    lines += ['', '## 4. Nhận định tương đối từ dữ liệu ghi nhận', '',
        f'**Đông A là đối chiếu cùng loại phường, có quy mô gần Duy Tân:** 9.406 hộ so với 8.934 hộ Duy Tân; số ghi nhận 15 hồ sơ trong tháng báo cáo tương đương {vn(east["cases_per_1000_households_month"],2)} hồ sơ/1.000 hộ/tháng.', '',
        f'**Mốc dùng hết 50,26 ha** ở mức 150 m²/trường hợp trong cả 5 năm 2026–2030 tương đương khoảng {vn(gain/150/5,0)} trường hợp/năm, {vn(gain/150/60,0)}/tháng, hay {vn(threshold,2)}/1.000 hộ/tháng của Duy Tân. Sau khi tính đến quy mô hộ, cao khoảng {vn(ratio,1)} lần nhịp tháng được Đông A công bố.', '',
        'Vì vậy, **50,26 ha có sức chứa quy đổi khá lớn so với nhịp ghi nhận Đông A trong tháng đó**. Khánh Thiện có nhịp ghi nhận cao hơn Đông A khi chia theo tháng/1.000 hộ; Hiển Khánh thấp hơn. Đây là so sánh trong ba nguồn và các kỳ khác nhau, chưa đủ gọi một địa phương cao/thấp so với toàn tỉnh hoặc đánh giá nhu cầu thực.', '',
        '## 5. Điều cần xác nhận trước khi nói còn hay hết chỉ tiêu', '',
        'Cần số đã thực hiện, phần đã phân bổ cho dự án và phần còn có thể giải quyết cho hộ của chính Duy Tân, cùng diện tích chuyển thực tế. Nguồn dân cư và kỳ hồ sơ không hoàn toàn cùng thời điểm, nhất là Khánh Thiện dùng quy mô công bố 2025 cho báo cáo quý I/2026. Chưa có tổng hồ sơ Duy Tân theo kỳ nên chưa chốt thực tế đang dư hay thiếu.', '',
        '> “Theo phụ lục, mức tăng 50,26 ha tương đương vài nghìn trường hợp nhỏ. Xin cho biết phần đã dùng, đã phân bổ dự án và phần còn cho hộ; nếu thiếu, xin nêu số liệu và căn cứ áp dụng cho hồ sơ của em.”', '',
        '[JSON phép tính](../data/residential_quota_analysis.json) · [Nguồn dân cư đối chiếu](../data/residential_locality_demographics.json) · [Bảng ODT/ONT 129 đơn vị](../data/residential_quotas_129.csv)']
    (ROOT/'reports/residential_quota_2030.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


def main():
    text = (ROOT / 'tmp/3279_2026_phu_luc_129.txt').read_text(encoding='utf-8')
    matches = list(re.finditer(r'--- PDF PAGE (\d+) ---\s+PHỤ LỤC (\d+)\.\s*PHÂN BỔ CHỈ TIÊU SỬ DỤNG ĐẤT ĐẾN NĂM 2030\s+([^\n]+)', text))
    directory = {int(row['appendix']): row for row in read('localities.csv')}
    assert len(matches) == len(directory) == 129
    quotas, flat = [], []
    for i, match in enumerate(matches):
        appendix, page = int(match[2]), int(match[1])
        locality = directory[appendix]['locality']
        section = text[match.end():matches[i+1].start() if i+1 < len(matches) else len(text)].split('* Ghi chú:', 1)[0]
        row = dict(locality=locality, kind='Phường' if locality.startswith('Phường ') else 'Xã', appendix=appendix, pdf_page=page)
        for code in ('ODT', 'ONT'):
            found = re.findall(r'\b' + code + r'\s+([\d.,]+)\s+([\d.,]+)\s*$', section, re.M)
            assert len(found) <= 1, (locality, code)
            if found:
                baseline, target = map(number, found[0])
                value = dict(baseline_ha=float(baseline), target_ha=float(target), change_ha=float(target-baseline), status='official_attachment_identity_pending')
            else:
                # Chất Bình has a blank ODT row: retain unknown, never infer zero.
                assert locality == 'Xã Chất Bình' and code == 'ODT', (locality, code)
                value = dict(baseline_ha=None, target_ha=None, change_ha=None, status='blank_in_source')
            row[code] = value
            flat.append(dict(locality=locality, land_code=code, **value, source_pdf=PDF, pdf_page=page))
        quotas.append(row)
    duy = next(row for row in quotas if row['locality'] == 'Phường Duy Tân')
    assert duy['ODT'] == dict(baseline_ha=269.76, target_ha=320.02, change_ha=50.26, status='official_attachment_identity_pending')
    assert duy['ONT']['baseline_ha'] == duy['ONT']['target_ha'] == 0
    gain = D('50.26') * 10000
    decisions = read('decisions_2026.csv')
    assert all(r['issue_date'] <= CUTOFF.isoformat() for r in decisions)
    valid = [r for r in decisions if r['pdf_identity_status'] != 'shared_pdf_conflict']
    days = (CUTOFF - dt.date(2026, 1, 1)).days + 1
    comparison = []
    for name in sorted({r['locality'] for r in decisions}):
        all_rows = [r for r in decisions if r['locality'] == name]
        rows = [r for r in valid if r['locality'] == name]
        sizes = [r for r in rows if r.get('residential_conversion_m2') and r['area_status'] not in ('source_internal_area_conflict', 'shared_pdf_excluded_from_verified_totals')]
        verified = [r for r in sizes if r['area_status'] == 'verified_pdf_identity']
        comparison.append(dict(locality=name, kind='Phường' if name.startswith('Phường ') else 'Xã', records=len(all_rows), nonconflict_records=len(rows), conflicts=len(all_rows)-len(rows), content_area_records=len(sizes), residential_content_area_m2=float(sum((D(r['residential_conversion_m2']) for r in sizes), D(0))) if sizes else None, verified_area_records=len(verified), verified_residential_area_m2=float(sum((D(r['residential_conversion_m2']) for r in verified), D(0))) if verified else None, annualized_public_record_rate=len(rows)*365/days, first_date=min(r['issue_date'] for r in rows), last_date=max(r['issue_date'] for r in rows), source_pages=sorted({r['source_page'] for r in rows})))
    sizes = [D(r['residential_conversion_m2']) for r in valid if r.get('residential_conversion_m2') and r['area_status'] not in ('source_internal_area_conflict', 'shared_pdf_excluded_from_verified_totals')]
    ward_sizes = [D(r['residential_conversion_m2']) for r in valid if r['locality'].startswith('Phường ') and r.get('residential_conversion_m2') and r['area_status'] not in ('source_internal_area_conflict', 'shared_pdf_excluded_from_verified_totals')]
    scenarios = [dict(mean_m2=size, total_cases=math.floor(gain/D(size)), annual_capacity=float(gain/D(size)/5)) for size in (80, 100, 106, 120, 150, 200, 300)]
    sources = json.loads((ROOT/'data/residential_activity_sources.json').read_text(encoding='utf-8'))
    data = dict(cutoff=CUTOFF.isoformat(), elapsed_days=days, source_pdf=PDF, source_pdf_sha256=hashlib.sha256((ROOT/PDF).read_bytes()).hexdigest(), duy_tan=duy, gain_m2=int(gain), baseline_growth_percent=float(D('50.26')/D('269.76')*100), square_side_m=math.sqrt(float(gain)), rectangle_100_100_m_count=float(gain/10000), scenarios=scenarios, sample=dict(n=len(sizes), mean_m2=float(statistics.mean(sizes)), median_m2=float(statistics.median(sizes)), ward_n=len(ward_sizes), ward_mean_m2=float(statistics.mean(ward_sizes)), ward_median_m2=float(statistics.median(ward_sizes)), status='content_from_selected_public_decisions_not_representative'), quotas=quotas, public_decisions=comparison, activity_sources=sources, limitations=['50,26 ha là tăng ròng ODT 2025–2030, chưa phải phần còn lại hay quỹ riêng cho hộ.', 'Duy Tân không có thêm 50 ha ONT; ONT trong phụ lục là 0 → 0.', 'Một quyết định, một hồ sơ và một hộ không luôn là cùng một đơn vị.', 'Ngoại suy nhịp báo cáo không phải dự báo được cơ quan phê duyệt.'])
    data['collection_note']=SCOPE.get('note','')
    data['targeted_review_note']=SCOPE.get('targeted_review_note','')
    households = json.loads((ROOT/'data/duy_tan_households.json').read_text(encoding='utf-8'))
    total = households['households']
    households['source_sha256'] = hashlib.sha256((ROOT/households['local_file']).read_bytes()).hexdigest()
    households['capacity_scenarios'] = [dict(mean_m2=size,household_capacity=math.floor(gain/size),share_of_baseline_percent=float(D(math.floor(gain/size))/total*100),all_households_area_ha=float(D(total)*size/10000)) for size in (106,150,200)]
    data['households'] = households
    demographic_rows = json.loads((ROOT/'data/residential_locality_demographics.json').read_text(encoding='utf-8'))
    demographics = {r['locality']:r for r in demographic_rows}
    comparisons = []
    for source in sources:
        g = dict(demographics[source['locality']])
        g['source_sha256'] = hashlib.sha256((ROOT/g['local_file']).read_bytes()).hexdigest()
        period_rate = source['count']/g['households']*1000
        comparisons.append(dict(**source,demographics=g,cases_per_1000_households_period=period_rate,cases_per_1000_households_month=period_rate/source['period_months']))
    data['observed_comparisons'] = comparisons
    data['input_sha256'] = {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ('data/decisions_2026.csv', 'data/decision_collection_scope.json', 'data/residential_activity_sources.json', 'data/duy_tan_households.json', 'data/residential_locality_demographics.json', 'tmp/3279_2026_phu_luc_129.txt')}
    (ROOT/'data/residential_quota_analysis.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    write_csv(ROOT/'data/residential_quotas_129.csv', flat)
    write_csv(ROOT/'data/residential_public_comparison.csv', [{k:v for k,v in r.items() if k!='source_pages'} for r in comparison])
    write_report(data)
    wards = sorted((r for r in quotas if r['kind']=='Phường'), key=lambda r:r['ODT']['change_ha'], reverse=True)
    rank = next(i+1 for i,r in enumerate(wards) if r['locality']=='Phường Duy Tân')
    print(json.dumps(dict(result='PASS', quota_localities=len(quotas), ward_count=len(wards), duy_tan_odt_growth_rank=rank, top_ward=wards[0], sample=data['sample'], public_ward_max=max(r['records'] for r in comparison if r['kind']=='Phường')),ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
