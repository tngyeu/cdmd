"""Build report aggregates from CSV; missing values never become verified zeros."""
import collections
import csv
import json
from decimal import Decimal
from parse_sources import ROOT, write_csv

def read(name):
    return list(csv.DictReader((ROOT/'data'/name).open(encoding='utf-8-sig')))

def summarize_localities(decisions, coverage):
    rows=[]
    for name in sorted({r['locality'] for r in coverage}):
        part=[r for r in decisions if r['locality']==name]
        valid=[r for r in part if r['pdf_identity_status']!='shared_pdf_conflict']
        strong=[r for r in valid if r['area_status']=='verified_pdf_identity' and r['area_m2']]
        pending=[r for r in valid if r['area_status']=='official_attachment_identity_pending' and r['area_m2']]
        known=strong+pending
        bad=[r for r in part if r['pdf_identity_status']=='shared_pdf_conflict' or r['area_status']=='source_internal_area_conflict']
        amount=lambda items:sum((Decimal(r['area_m2']) for r in items),Decimal(0))
        home=lambda r:Decimal(r.get('residential_conversion_m2') or (r['area_m2'] if r['land_after'] in ('ONT','ODT','DAT_O') else '0'))
        rows.append(dict(locality=name,records=len(part),pdf=sum(r['verification_status']=='official_pdf' for r in valid),metadata=sum(r['verification_status']!='official_pdf' for r in valid),conflicts=len(part)-len(valid),area_m2=str(amount(strong)),known_area_records=len(known),known_area_m2=str(amount(known)),residential_area_m2=str(sum((home(r) for r in known),Decimal(0))),pending_area_m2=str(amount(pending)),missing_area_records=len(part)-len(known),excluded_area_records=len(bad),unread_area_records=len(part)-len(known)-len(bad),coverage_note='Có bản ghi trong tập thu thập' if part else 'Chưa tìm thấy trong phạm vi đã tra; không đồng nghĩa chưa ban hành'))
    return rows

def main():
    decisions=read('decisions_2026.csv')
    coverage=read('coverage_129.csv')
    scope_path=ROOT/'data/decision_collection_scope.json'
    scope=json.loads(scope_path.read_text(encoding='utf-8')) if scope_path.exists() else {'cutoff':'2026-10-19'}
    cutoff=scope['cutoff']
    cutoff_label='/'.join(reversed(cutoff.split('-')))
    eligible=[r for r in decisions if r['pdf_identity_status']!='shared_pdf_conflict']
    strong=[r for r in eligible if r['verification_status']=='official_pdf']
    areas=[r for r in eligible if r['area_status']=='verified_pdf_identity']
    weakareas=[r for r in eligible if r['area_status']=='official_attachment_identity_pending']
    total=sum((Decimal(r['area_m2']) for r in areas),Decimal(0))
    stats=dict(records=len(decisions),verified=len(eligible),pdf_verified=len(strong),metadata_verified=len(eligible)-len(strong),conflicts=len(decisions)-len(eligible),downloaded_pdfs=sum(bool(r['local_pdf']) for r in decisions),localities=len({r['locality'] for r in eligible}),coverage_checked=sum(int(r['pages_checked'])>0 for r in coverage),verified_area_records=len(areas),verified_area_m2=str(total),pending_area_records=len(weakareas),pending_area_m2=str(sum((Decimal(r['area_m2']) for r in weakareas),Decimal(0))),cutoff='2026-10-19')
    stats.update(parcel_area_records=sum(bool(r.get('parcel_area_m2')) for r in decisions),visual_reviewed=sum(r.get('detail_status')=='visual_reviewed' for r in decisions),component_decisions=sum(bool(json.loads(r.get('components_json') or '[]')) for r in decisions),detail_issue_records=sum(bool(json.loads(r.get('detail_flags_json') or '[]')) for r in decisions))
    stats['verified_residential_conversion_m2']=str(sum((Decimal(r.get('residential_conversion_m2') or (r['area_m2'] if r['land_after'] in ('ONT','ODT') else '0')) for r in areas),Decimal(0)))
    stats['cutoff']=cutoff
    locality_rows=summarize_localities(decisions,coverage)
    write_csv(ROOT/'data/locality_summary_2026.csv',locality_rows)
    monthly=[dict(month=f'2026-{n:02}',records=sum(r['issue_date'][:7]==f'2026-{n:02}' for r in eligible)) for n in range(1,11)]
    types=[]
    for group in sorted({r['conversion_group'] for r in eligible}):
        part=[r for r in eligible if r['conversion_group']==group]
        types.append(dict(group=group,records=len(part),pdf=sum(r['verification_status']=='official_pdf' for r in part),area_m2=str(sum((Decimal(r['area_m2']) for r in part if r['area_status']=='verified_pdf_identity'),Decimal(0)))))
    data=dict(stats=stats,decisions=decisions,coverage=coverage,legal=read('legal_documents.csv'),quotas=read('land_quotas.csv'),reserves=read('land_reserves.csv'),history=read('land_quota_history.csv'),budget=read('budget_metrics.csv'),locality_summary=locality_rows,monthly=monthly,types=types)
    (ROOT/'data/display_data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    lines=['# Quyết định chuyển mục đích công khai năm 2026','',f'Phạm vi ngày ban hành: 01/01–19/10/2026. Đã ghi nhận **{len(decisions)} bản ghi** tại **{stats["localities"]} địa phương**; **{stats["verified"]}** bản ghi được tính trong tổng xác minh theo số/ngày, gồm **{stats["pdf_verified"]} PDF khớp số/ngày** và **{stats["metadata_verified"]} metadata chính thức**. **{stats["conflicts"]}** bản ghi xung đột do cùng PDF được tách khỏi tổng xác minh.','',f'Đây là **tổng của tập nguồn công khai tìm được**, không phải tổng quyết định đã ban hành toàn tỉnh. Đã truy cập danh mục/trang liên quan của {stats["coverage_checked"]}/129 đơn vị; việc có trang được truy cập không chứng minh đã duyệt hết mọi chuyên mục, phân trang hay nguồn đính kèm. Cổng tỉnh có hạn chế truy cập; tìm kiếm website không bảo đảm chỉ mục đầy đủ.','',f'Tổng diện tích đã khép định danh và phân loại được: **{total:,.2f} m²**, từ {len(areas)} quyết định. {len(weakareas)} tệp có diện tích đọc được nhưng chưa khép định danh, được trình bày riêng và không cộng vào tổng này. Diện tích chưa đọc/không xác minh được không quy về 0.','', '## Theo địa phương','', '| Địa phương | Bản ghi quyết định | Tổng chuyển đọc được (m²) | Trong đó sang đất ở (m²) | Đã xác minh (m²) | Chờ đối chiếu số/ngày (m²) | Chưa cộng diện tích (bản ghi) |','| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    lines[2]=lines[2].replace('01/01–19/10/2026','01/01–'+cutoff_label)
    if scope.get('note'):lines[4:4]=[scope['note'],'']
    if scope.get('targeted_review_note'):lines[6:6]=[scope['targeted_review_note'],'']
    for r in locality_rows:
        values=[r[k] if r['known_area_records'] else 'Chưa có số liệu đủ điều kiện cộng' for k in ['known_area_m2','residential_area_m2','area_m2','pending_area_m2']]
        lines.append(f'| {r["locality"]} | {r["records"]} | '+ ' | '.join(values)+f' | {r["missing_area_records"]} |')
    lines+=['','Tổng đọc được gồm diện tích đã xác minh và diện tích còn chờ đối chiếu số/ngày. Chỉ cộng diện tích được phép chuyển; không cộng tổng thửa. Bản ghi thiếu diện tích, xung đột PDF hoặc mâu thuẫn số học không được cộng. Bản ghi chưa tìm thấy không chứng minh địa phương chưa ban hành quyết định.']
    lines+=['','## Theo tháng','', '| Tháng | Bản ghi trong tổng xác minh |','| --- | ---: |']
    lines += [f'| {r["month"]} | {r["records"]} |' for r in monthly]
    lines+=['','Tháng 10 mới tính đến ngày 19/10. Các cột phản ánh ngày ban hành đọc được trên nguồn; không dùng để suy tỷ lệ giải quyết hồ sơ toàn tỉnh.','','## Theo hướng chuyển đất','', '| Hướng chuyển | Bản ghi phân loại được | PDF khớp | Diện tích xác minh (m²) |','| --- | ---: | ---: | ---: |']
    for r in types:lines.append(f'| {r["group"]} | {r["records"]} | {r["pdf"]} | {r["area_m2"] if Decimal(r["area_m2"]) else "Chưa xác định"} |')
    lines+=['','Loại đất/diện tích có mức xác minh riêng với số/ngày. Nhóm `chua_xac_dinh` và `hon_hop_chua_tach` không được suy thành CLN → đất ở. Một quyết định có nhiều hướng chuyển cần bảng thành phần trước khi tính diện tích theo loại.','','## Riêng Duy Tân','','Chưa tìm được quyết định cho phép chuyển mục đích phù hợp trong các nguồn đã truy cập của Duy Tân. Điều này **không chứng minh chưa ban hành hoặc chưa giải quyết hồ sơ nào**. Chưa có tổng diện tích thực hiện chính thức để đối chiếu chỉ tiêu. Cần sổ theo dõi/báo cáo của phường và cơ quan quản lý đất đai.','','## Đối chiếu kết quả sơ bộ 141 quyết định / 13 địa phương','','Con số 141 do người dùng cung cấp chỉ được dùng làm đầu mối tra cứu; không cộng 141 vào dữ liệu mới. Không có danh sách 141 số hiệu ban đầu để đối chiếu từng dòng nên chưa xác nhận được bản ghi nào trong tập sơ bộ trùng với tập hiện tại. Đã tìm thêm các địa phương ngoài danh sách khởi đầu.','','## Chống trùng và nguồn chứng minh','','Nhập theo khóa địa phương + số hiệu + ngày ban hành; bảng desktop/mobile trên cùng trang không được tính hai lần. So sánh SHA256 của PDF để phát hiện cùng tệp dùng cho số khác nhau. Hai bản ghi Phú Long 420 và 421 ngày 23/04/2026 dùng cùng PDF còn trống số: chưa đủ căn cứ quyết định đây là một quyết định hay hai trang đính nhầm tệp, vì vậy giữ nguồn và loại cả hai khỏi tổng xác minh.','', 'Mỗi dòng CSV có URL nguồn, URL PDF nếu tìm thấy, đường dẫn bản tải khi có, ngày kiểm tra và trạng thái. Dữ liệu tổng hợp không có cột tên, địa chỉ cư trú, CCCD hoặc số Giấy chứng nhận. URL gốc có thể chứa tên trong tên tệp, được giữ để truy nguyên đúng tài liệu.','','## Phạm vi 129 xã/phường','', '| Địa phương | Trang đã tra | Bản ghi tìm được | Trạng thái |','| --- | ---: | ---: | --- |']
    for r in coverage:lines.append(f'| {r["locality"]} | {r["pages_checked"]} | {r["records_found"]} | {r["status"]} |')
    lines += ['', '## Bổ sung theo tìm kiếm ngày 19/10/2026', '', 'Đợt tra cứu theo truy vấn người dùng gợi ý bổ sung 19 bản ghi (380 → 399), trong đó 7 PDF khớp số/ngày với 706,8 m². Xem [nguồn, danh sách bổ sung và giới hạn](../reports/search_supplement_20261019.md). PDF gộp Nam Hoa Lư được phân biệt theo các phạm vi trang đã đọc trực quan, không coi là xung đột chỉ vì chung SHA256.']
    lines=[line.replace('Tháng 10 mới tính đến ngày 19/10.',f'Tháng 10 mới tính đến ngày {cutoff_label[:5]}.') for line in lines]
    if (ROOT/'data/myloc_download_inventory.json').exists():
        lines+=['','## Bổ sung Mỹ Lộc ngày 20/10/2026','','Đã đọc 10 trang kết quả qua trình duyệt, mở từng văn bản trong tab mới. 94 dòng có 1 dòng trùng; còn 93 trang nguồn: 40 năm 2026 và 53 năm 2025. Đã tải đủ 40 PDF năm 2026, nhập thêm 39 bản ghi và cập nhật bản 5179 đã có. 47 PDF năm 2025 lưu riêng, 6 tệp cũ trả lỗi 403. [Danh mục, nguồn và bộ PDF](../reports/myloc_download_20261020.md).']
        if (ROOT/'data/myloc_area_review_20261020.json').exists():
            lines+=['','Đã đối chiếu ảnh số/ngày và Điều 1 của đủ 40 PDF Mỹ Lộc năm 2026: **6.196 m² sang ODT (0,6196 ha)**, bình quân **154,9 m²/quyết định**. Diện tích này đã được đưa vào tổng xác minh ở trên; diện tích năm 2025 chưa thống kê. [Xem bảng 40 quyết định và cách cộng](../reports/myloc_area_2026.md).']
        else:
            lines+=['','Chưa đọc ảnh định danh và diện tích của đủ 40 PDF; chưa cộng diện tích mới.']
    if (ROOT/'data/scan_review_20261021.json').exists():
        review=json.loads((ROOT/'data/scan_review_20261021.json').read_text(encoding='utf-8'))
        lines+=['','## Đọc bổ sung bản quét ngày 21/10/2026','',f'Đã đọc ảnh {review["reviewed_records"]} quyết định, thêm {review["added_records"]} bản ghi so với tập {review["baseline_records"]}; diện tích xác minh thêm {review["additional_verified_area_m2"].replace(".",",")} m² chuyển sang đất ở. Bản Quang Hưng 1058 dùng ngày 28/09/2026 trên bản ký; ngày 19/10/2026 của metadata trùng ngày sao y. [Bảng từng quyết định, phạm vi trang và giới hạn](scan_review_20261021.md).']
    (ROOT/'reports/decisions_2026.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(stats,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
