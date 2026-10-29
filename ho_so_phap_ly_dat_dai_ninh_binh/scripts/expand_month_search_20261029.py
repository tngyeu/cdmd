"""Apply source-bound readings after direct Google/Bing browser review."""
import csv
import hashlib
import json
import sys
from decimal import Decimal
from pathlib import Path
from supplement_recent_20261029 import ROOT, read, dump, write_csv
from parse_sources import slug

DATE = '2026-10-29'
sys.stdout.reconfigure(encoding='utf-8')
# number, date, locality, file stem, components. All checked on rendered pages.
READINGS = [
 ('1971','2026-10-16','Xã Đồng Thái','google_month_dongthai529_0',[('HNK','ONT','200')]),
 ('1977','2026-10-16','Xã Đồng Thái','google_month_dongthai534_0',[('CLN','ONT','100')]),
 ('2121','2026-10-19','Xã Giao Hòa','google_month_giaohoa_0',[('CLN','ONT','80')]),
 ('2136','2026-10-20','Xã Giao Hòa','google_month_giaohoa_1',[('NTS','ONT','60')]),
 ('422','2026-10-26','Xã Khánh Hội','google_month_khanhhoi422_0',[('CLN','ONT','157.4')]),
 ('4428','2026-10-23','Phường Nam Định','google_month_namdinh200438_0',[('NTS','DAT_O','192.4')]),
 ('2925','2026-10-23','Phường Nam Hoa Lư','google_month_namhoalu2925_0',[('HNK','ODT','83.2')]),
 ('2204','2026-10-09','Xã Yên Mô','google_month_yenmo1647_0',[('CLN','ONT','77.3'),('NTS','ONT','125.5')]),
 ('1023','2026-07-09','Xã Yên Từ','google_month_yentu795_0',[('NTS','ONT','491')]),
 ('421','2026-10-26','Xã Khánh Hội','google_related_google_related_1192_0',[('NTS','ONT','209.9')]),
 ('423','2026-10-26','Xã Khánh Hội','google_related_google_related_1194_0',[('CLN','ONT','157.4')]),
 ('424','2026-10-26','Xã Khánh Hội','google_related_google_related_1195_0',[('CLN','ONT','152')]),
 ('425','2026-10-26','Xã Khánh Hội','google_related_google_related_1196_0',[('NTS','ONT','130')]),
 ('426','2026-10-26','Xã Khánh Hội','google_related_google_related_1197_0',[('CLN','ONT','120.2')]),
 ('2734','2026-10-12','Phường Nam Hoa Lư','google_related_google_related_1483_0',[('CLN','ODT','167.4')]),
 ('2687','2026-10-06','Phường Nam Hoa Lư','google_related_google_related_1502_0',[('HNK','ODT','91.7')]),
 ('3192','2026-10-13','Phường Tây Hoa Lư','supplement_link_phuongtayhoalu_0',[('NTS','ODT','100')]),
]


def main():
 rows=read('decisions_2026.csv');fields=list(rows[0]);by_id={r['decision_id']:r for r in rows}
 audit_path=ROOT/'data/search_expanded_20261029.json'
 previous=json.loads(audit_path.read_text(encoding='utf-8')) if audit_path.exists() else {}
 previous_actions={r['decision_id']:r['import_action'] for r in previous.get('records',[])}
 baseline=previous.get('baseline_records',len(rows));manual_path=ROOT/'data/pdf_manual_reviews.json';manual=json.loads(manual_path.read_text(encoding='utf-8'))
 detail_path=ROOT/'data/decision_detail_reviews.json';details=json.loads(detail_path.read_text(encoding='utf-8'))
 parts=read('decision_components.csv');result=[]
 logs=[json.loads(x) for x in (ROOT/'data/download_log.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
 downloads={j['path']:j for j in logs if j.get('status')=='downloaded'}
 basejobs=json.loads((ROOT/'tmp/jobs_google_month.json').read_text(encoding='utf-8'))
 basejobs+=json.loads((ROOT/'tmp/jobs_related_month.json').read_text(encoding='utf-8'))
 basejobs+=json.loads((ROOT/'tmp/jobs_google_month_pdfs.json').read_text(encoding='utf-8'))
 pdfjobs=json.loads((ROOT/'tmp/jobs_related_pdf_month.json').read_text(encoding='utf-8'))
 for n,d,loc,stem,cs in READINGS:
  number=n+'/QĐ-UBND';key=f'{slug(loc)}|{number}|{d}';prior=next((r for r in rows if r['locality']==loc and r['decision_number']==number),None)
  local=f'documents/quyet_dinh_2026/{stem}.pdf';pdf=ROOT/local;assert pdf.is_file()
  if stem.startswith('google_related_'):
   j=next(j for j in pdfjobs if j['path']==local);source=j['source_page'];source_html=j['source_html']
  elif stem=='supplement_link_phuongtayhoalu_0':source=prior['source_page'];source_html='documents/nguon_web/google_month_tayhoalu475.html'
  else:
   base=stem.rsplit('_',1)[0];j=next(j for j in basejobs if Path(j['path']).stem==base);source=j['url'];source_html=j['path']
  url=downloads[local]['url'] if local in downloads else prior['pdf_url']
  digest=hashlib.sha256(pdf.read_bytes()).hexdigest();components=[dict(land_before=a,land_after=b,area_m2=c) for a,b,c in cs]
  area=str(sum((Decimal(c) for _,_,c in cs),Decimal(0)));page='1' if loc=='Xã Giao Hòa' else '2'
  note='Đã đọc ảnh số/ngày trang 1 và Điều 1 của PDF. Chỉ cộng phần được phép chuyển sang đất ở; chưa thấy tổng diện tích thửa riêng, để trống.'
  if loc=='Phường Tây Hoa Lư':note+=' Trang nguồn ghi 16/10/2026; PDF lưu từ đợt trước ghi 13/10/2026, dùng ngày PDF. Liên kết tải hiện trả 404; giữ bản lưu, không coi ngày cổng là ngày ký.'
  if loc=='Phường Nam Định':note+=' Điều 1 chỉ ghi đất ở; giữ mã DAT_O, không tự suy mã ODT.'
  if loc=='Xã Yên Từ':note+=' Quyết định tháng 7 đã có trong dữ liệu; chỉ nâng xác minh, không tính thành quyết định mới trong tháng gần đây.'
  row=dict(prior) if prior else {f:'' for f in fields}
  row.update(decision_id=key,locality=loc,issuing_authority='UBND '+loc,decision_number=number,issue_date=d,land_before='+'.join(c[0] for c in cs),land_after=cs[0][1],conversion_group='hon_hop_da_tach' if len(cs)>1 else cs[0][0]+'->'+cs[0][1],area_m2=area,residential_conversion_m2=area,
   verification_status='official_pdf',pdf_identity_status='matched_number_and_date',area_status='verified_pdf_identity',content_pdf_page=page,source_page=source,pdf_url=url,local_pdf=local,checked_on=DATE,notes=note,
   parcel_area_m2='',initial_land_json='{}',post_land_json='{}',components_json=json.dumps(components),detail_status='visual_reviewed',detail_pdf_pages='1,2',detail_checked_on=DATE,detail_notes_json=json.dumps([note],ensure_ascii=False),detail_flags_json='[]')
  supersedes=next((m.get('supersedes_decision_ids',[]) for m in manual if m['record']['decision_id']==key),[])
  if prior and prior['decision_id']!=key:
   supersedes=[prior['decision_id']];by_id.pop(prior['decision_id']);details.pop(prior['decision_id'],None)
  by_id[key]=row
  manual=[m for m in manual if m['record']['decision_id'] not in [key]+supersedes]
  review=dict(record=row,sha256=digest,page_start=1,page_end=2,method='visual_header_and_article_1_on_rendered_pdf_pages',reviewed_on=DATE)
  if supersedes:review['supersedes_decision_ids']=supersedes
  manual.append(review)
  details[key]=dict(pages='1,2',fields={f:row[f] for f in ['area_m2','area_status','parcel_area_m2','initial_land_json','post_land_json','residential_conversion_m2','components_json','land_before','land_after','conversion_group']},notes=[note],checked_on=DATE,source_pdf=local,sha256=digest)
  parts=[p for p in parts if p['decision_id'] not in [key]+supersedes]
  for i,c in enumerate(components,1):parts.append(dict(decision_id=key,component=i,**c,pdf_path=local,pdf_pages=page,content_review='visual_reviewed',identity_status='matched_number_and_date',area_status='verified_pdf_identity'))
  result.append(dict(row,sha256=digest,source_html=source_html,import_action=previous_actions.get(key,'review_existing' if prior else 'new_record')))
 assert len({r['sha256'] for r in result})==17
 write_csv(ROOT/'data/decisions_2026.csv',list(by_id.values()),fields);write_csv(ROOT/'data/decision_components.csv',parts,list(parts[0]));dump(manual_path,manual);dump(detail_path,details)
 write_csv(ROOT/'data/search_expanded_20261029.csv',result)
 new=[r for r in result if r['import_action']=='new_record'];total=sum((Decimal(r['area_m2']) for r in new),Decimal(0))
 audit=dict(checked_on=DATE,baseline_records=baseline,final_records=len(by_id),new_records=len(new),new_residential_area_m2=str(total),reviewed_existing=len(result)-len(new),google_pages=10,bing_note='Đã mở liên kết Bing; bộ lọc thực tế hiển thị Past year. Không dùng nhãn ngày tương đối trên công cụ tìm kiếm để suy ngày ký.',
  excluded=[dict(local_pdf='documents/quyet_dinh_2026/google_month_yenmac.pdf',number='1736/QĐ-UBND',issue_date='2026-10-05',reason='Điều 1 giao 180 m² đất; không phải quyết định cho phép chuyển mục đích.')],records=result)
 dump(ROOT/'data/search_expanded_20261029.json',audit)
 coverage=read('coverage_129.csv')
 for r in coverage:
  if r['locality'] in {x['locality'] for x in result}:
   r.update(records_found=str(sum(x['locality']==r['locality'] for x in by_id.values())),status='found_public_records',checked_on=DATE,notes=r['notes']+' Rà trực tiếp Google/Bing 29/10/2026, đọc bổ sung PDF; phạm vi chi tiết trong search_expanded_20261029.json.')
   r['pages_checked']=str(max(1,int(r['pages_checked'])))
 write_csv(ROOT/'data/coverage_129.csv',coverage)
 lines=['<!-- web: {"updatedOn":"2026-10-29","featured":true,"order":1,"icon":"folder"} -->','# Rà mở rộng Google và Bing ngày 29/10/2026','',
  '**Căn cứ:** bản PDF các quyết định trong bảng dưới; đã đối chiếu ảnh số/ngày trang 1 và Điều 1. Duyệt trực tiếp 10 trang Google với bộ lọc một tháng, mở thêm liên kết Bing và các văn bản liên quan trên cổng địa phương. Lượt tìm trước chỉ bổ sung hai bản Xuân Hồng và đã bỏ sót nhiều đầu mối.','',
  f'**Lượt rà mở rộng: thêm {len(new)} quyết định, {str(total).replace(".",",")} m² chuyển sang đất ở; đọc lại 3 quyết định đã có. Tổng dữ liệu: {len(by_id)} bản ghi.** Không có tổng diện tích thửa riêng đủ căn cứ trong các bản vừa đọc; giữ trống trường này.','',
  '| Địa phương | Quyết định | Ngày PDF | Sang đất ở (m²) | Hướng chuyển | Kết quả |','| --- | --- | --- | ---: | --- | --- |']
 for r in result:
  lines.append(f'| {r["locality"]} | [{r["decision_number"]}](../{r["local_pdf"]}#page={r["content_pdf_page"]}) | {r["issue_date"]} | {r["area_m2"].replace(".",",")} | {r["conversion_group"]} | '+('Mới' if r['import_action']=='new_record' else 'Đã có, đọc đối chiếu')+' |')
 lines+=['','**Những điểm cần phân biệt:** Tây Hoa Lư 3192 ghi ngày 13/10 trên PDF lưu, khác 16/10 ở trang nguồn; sửa theo PDF và giữ sai khác. Liên kết tải hiện trả 404 nhưng bản lưu cũ còn đọc được. Yên Từ 1023 ngày 09/07 đã có trong dữ liệu, chỉ nâng mức xác minh, không tính thành quyết định mới tháng 10. Nam Hoa Lư 2687 đã có, không đếm lại. Yên Mạc 1736 ngày 05/10 là giao đất 180 m², loại khỏi tập chuyển mục đích.','',
  '**Diện tích:** Yên Mô 2204 gồm 77,3 m² CLN + 125,5 m² NTS = 202,8 m²; không cộng lặp tổng và thành phần. Nam Định 4428 chỉ ghi “đất ở” trong Điều 1, giữ mã DAT_O.','',
  '[Tải bảng đầy đủ, đường dẫn nguồn và SHA256](../data/search_expanded_20261029.csv). Tất cả PDF và nguồn ngoài mở tab mới. Kết quả tìm kiếm không bảo đảm bao quát mọi quyết định; các bài tin có từ khóa trong thanh bên không được coi là quyết định chuyển mục đích.']
 (ROOT/'reports/search_expanded_20261029.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 print(json.dumps({k:v for k,v in audit.items() if k not in ['records','excluded']},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
