"""Extract narrowly matched article-1 data, with identity and area confidence separate."""
import collections
import csv
import hashlib
import json
import re
import sys
import logging
from decimal import Decimal
from pypdf import PdfReader
from parse_sources import ROOT, write_csv
from update_inventory import FIELDS
from manual_reviews import load_reviews, disjoint_reviewed_bundle

sys.stdout.reconfigure(encoding='utf-8')
logging.getLogger('pypdf').setLevel(logging.ERROR)

def main():
    rows=list(csv.DictReader((ROOT/'data/decisions_2026.csv').open(encoding='utf-8-sig')))
    downloaded={}
    for line in (ROOT/'data/download_log.jsonl').read_text(encoding='utf-8').splitlines():
        item=json.loads(line)
        if item.get('status')=='downloaded':downloaded[item['url']]=item
    digest_ids=collections.defaultdict(list)
    reviews=[]
    manual = load_reviews()
    for index,row in enumerate(rows):
        log=downloaded.get(row['pdf_url'])
        if not log:continue
        path=ROOT/log['path'];row['local_pdf']=log['path']
        digest_ids[hashlib.sha256(path.read_bytes()).hexdigest()].append(row['decision_id'])
        if row['decision_id'] in manual:
            row.update(manual[row['decision_id']]['record'])
            continue
        try:
            reader=PdfReader(path)
            pages=[page.extract_text() or '' for page in reader.pages]
            text=' '.join(' '.join(pages).split())
            header=' '.join(pages[0].split())[:650] if pages else ''
            front=' '.join(pages[0].split()).split('Căn cứ',1)[0] if pages else ''
            if re.search(r'CHỦ TỊCH\s+[ỦU]Ỷ?Y?\s*BAN NHÂN DÂN|CHỦ TỊCH\s+ỦY BAN NHÂN DÂN',front,re.I):
                row['issuing_authority']='Chủ tịch UBND '+row['locality']
            elif re.search(r'ỦY BAN NHÂN DÂN|UỶ BAN NHÂN DÂN',front,re.I):
                row['issuing_authority']='UBND '+row['locality']
            number=re.search(r'Số\s*:\s*(\d+)\s*/\s*Q[ĐDÐ]-UBND',header,re.I)
            date=re.search(r'ngày\s*(\d{1,2})\s*tháng\s*(\d{1,2})\s*năm\s*(2026)',header,re.I)
            number_ok=bool(number and int(number.group(1))==int(row['decision_number'].split('/')[0]))
            date_ok=bool(date and f'{date[3]}-{int(date[2]):02}-{int(date[1]):02}'==row['issue_date'])
            identity='matched_number_and_date' if number_ok and date_ok else ('number_or_date_conflict' if number or date else 'blank_or_image_header')
            row['pdf_identity_status']=identity
            if number_ok and date_ok:row['verification_status']='official_pdf'
            if len(text)<120:row['area_status']='scan_requires_ocr';continue
            article=re.search(r'Điều\s*1[.:](.*?)(?:Điều\s*2[.:]|$)',text,re.I)
            if not article:row['area_status']='article_not_parsed';continue
            section=article[1]
            if len(re.findall(r'\bsang\b', section, re.I))>1:
                row['area_status']='mixed_requires_component_review'
                row['conversion_group']='hon_hop_chua_tach'
                continue
            patterns=[
                r'chuyển mục đích sử dụng\s*(?:đất\s*)?(?:từ\s*)?([\d.,]+)\s*m\s*[²2]\s*(?:đất\s*)?(.{0,500}?)\s+sang\s+(?:mục đích\s*)?(.{0,110})',
                r'từ\s+([\d.,]+)\s*m\s*[²2]\s*đất\s*(.{0,500}?)\s+sang\s+(?:mục đích\s*)?(.{0,110})',
                r'chuyển mục đích sử dụng đất đối với\s*:\s*\+?\s*([\d.,]+)\s*m\s*[²2]\s*đất\s*(.{0,250}?)\s+sang\s*(.{0,110})',
            ]
            match=next((m for pattern in patterns if (m:=re.search(pattern,section,re.I))),None)
            if match:
                raw,before,after=match.groups()
            else:
                # Destination area is explicit; source land must be unique in the pre-conversion text.
                target=re.search(r'được chuyển mục đích sử dụng đất sang\s*(đất ở.*?(?:với diện tích)\s*([\d.,]+)\s*m\s*[²2])',section,re.I)
                if not target:row['area_status']='manual_review_needed';continue
                raw=target[2]; before=section[:target.start()]; after=target[1]
            codes=[('CLN',r'cây lâu năm|\bCLN\b'),('NTS',r'nuôi trồng th[uủ]y sản|\bNTS\b'),('LUA',r'trồng lúa|\bLUA\b|\bLUC\b'),('HNK',r'hằng năm|hàng năm|\bHNK\b')]
            old_codes=[code for code,pattern in codes if re.search(pattern,before,re.I)]
            new_code='ONT' if re.search(r'nông thôn|\bONT\b',after,re.I) else ('ODT' if re.search(r'đô thị|\bODT\b',after,re.I) else '')
            # A period-only numeric value may be a decimal or thousands separator: defer.
            if '.' in raw and ',' not in raw:row['area_status']='ambiguous_decimal_manual_review';continue
            area=Decimal(raw.replace('.','').replace(',','.'))
            if len(old_codes)!=1 or not new_code or not Decimal(0)<area<Decimal('10000000'):
                row['area_status']='classification_manual_review';continue
            row.update(land_before=old_codes[0],land_after=new_code,conversion_group=f'{old_codes[0]}->{new_code}',area_m2=str(area),area_status='verified_pdf_identity' if identity=='matched_number_and_date' else 'official_attachment_identity_pending')
            for i,t in enumerate(pages):
                if re.search(r'Điều\s*1[.:]',t):row['content_pdf_page']=str(i+1);break
            row['notes']='Loại đất/diện tích đọc từ Điều 1 của tệp đính kèm chính thức; '+('số/ngày khớp PDF.' if identity=='matched_number_and_date' else 'số/ngày nhận diện qua website; chưa khép định danh bản PDF.')
        except Exception as exc:
            row['area_status']='pdf_error'
            reviews.append(dict(decision_id=row['decision_id'],issue=str(exc)))
        if index%50==0:print('Reviewed',index,'/',len(rows),flush=True)
    duplicates=[dict(sha256=digest,decision_ids=';'.join(ids),status='same_pdf_requires_identity_review') for digest,ids in digest_ids.items() if len(ids)>1 and not disjoint_reviewed_bundle(ids, manual)]
    for duplicate in duplicates:
        ids=set(duplicate['decision_ids'].split(';'))
        for row in rows:
            if row['decision_id'] in ids:
                row['pdf_identity_status']='shared_pdf_conflict'
                row['verification_status']='official_metadata'
                row['area_status']='shared_pdf_excluded_from_verified_totals'
    write_csv(ROOT/'data/decisions_2026.csv',rows,FIELDS)
    write_csv(ROOT/'data/duplicate_pdf_review.csv',duplicates,['sha256','decision_ids','status'])
    print(json.dumps(dict(records=len(rows),pdfs=sum(bool(r['local_pdf']) for r in rows),verification=dict(collections.Counter(r['verification_status'] for r in rows)),area_status=dict(collections.Counter(r['area_status'] for r in rows)),shared_pdf_groups=len(duplicates)),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
