"""Read downloaded decision texts; cache page text for repeatable source review."""
import csv
import hashlib
import json
import logging
import re
import unicodedata
import sys
from decimal import Decimal
from pathlib import Path
from pypdf import PdfReader
from parse_sources import ROOT, write_csv

logging.getLogger('pypdf').setLevel(logging.ERROR)
CACHE=ROOT/'tmp/decision_text_cache.json'
DETAIL_FIELDS=['parcel_area_m2','initial_land_json','post_land_json','residential_conversion_m2','components_json','detail_notes_json','detail_status','detail_pdf_pages','land_price_vnd_m2','term_after','detail_checked_on','detail_flags_json']
LAND=r'(?:dat\s+(?:trong\s+cay\s+(?:lau\s+nam|hang\s+nam\s+khac)|nuoi\s+trong\s+thuy\s+san|o\s+(?:tai\s+)?(?:nong\s+(?:\d+\s+)?thon|do\s+thi)|trong\s+lua))'
AREA=r'([\d.,]+)\s*m\s*[²2]'

def canon(s):
    s=''.join(c for c in unicodedata.normalize('NFD',s) if not unicodedata.combining(c)).lower().replace('đ','d')
    return re.sub(r'\bd\s+at\b','dat',s)

def amount(s):
    if ',' in s:return Decimal(s.replace('.','').replace(',','.'))
    if '.' in s and len(s.rsplit('.',1)[1])==3:raise ValueError('Ambiguous thousands/decimal')
    return Decimal(s)

def land_code(s):
    if 'lau nam' in s:return 'CLN'
    if 'thuy san' in s:return 'NTS'
    if 'hang nam' in s:return 'HNK'
    if 'trong lua' in s:return 'LUA'
    if re.search(r'nong\s+(?:\d+\s+)?thon',s):return 'ONT'
    if 'do thi' in s:return 'ODT'
    return ''

def named_areas(s):
    results=[]
    for m in re.finditer(AREA+r'\s*('+LAND+r')',s):
        try:results.append((land_code(m[2]),amount(m[1]),m.start(),m.end()))
        except ValueError:pass
    for m in re.finditer('('+LAND+r')(?:\s*\([^)]{1,40}\))?\s*:?\s*'+AREA,s):
        if any(m.start()<end and m.end()>start for _,_,start,end in results):continue
        try:results.append((land_code(m[1]),amount(m[2]),m.start(),m.end()))
        except ValueError:pass
    return sorted(results,key=lambda x:x[2])

def group_areas(values):
    result={}
    for code,n,*_ in values:result[code]=str(Decimal(result.get(code,'0'))+n)
    return result

def parse_components(grant, before_context, row):
    result=[]
    for clause in re.split(r';|\+|\bva dien tich\b',grant):
        if ' sang ' not in clause:continue
        left,right=clause.split(' sang ',1)
        src=named_areas(left);dst=named_areas(right)
        if not src and row.get('land_before') in ('CLN','NTS','HNK','LUA'):
            # Existing source classification can be used only for the explicit destination-only template.
            m=re.search(r'voi dien tich\s*'+AREA,right)
            if m and len({land_code(x[0]) for x in re.finditer(LAND,right)})==1:
                try:src=[(row['land_before'],amount(m[1]),0,0)]
                except ValueError:pass
        if not src:continue
        src_total=sum((n for _,n,*_ in src),Decimal(0))
        if not dst:
            kinds={land_code(m[0]) for m in re.finditer(LAND,right)}
            if len(kinds)==1:dst=[(kinds.pop(),src_total,0,0)]
        if not dst:continue
        dst_total=sum((n for _,n,*_ in dst),Decimal(0))
        if src_total != dst_total:continue
        if len({x[0] for x in dst})==1:
            result.extend(dict(land_before=c,land_after=dst[0][0],area_m2=str(n)) for c,n,*_ in src)
        elif len({x[0] for x in src})==1:
            result.extend(dict(land_before=src[0][0],land_after=c,area_m2=str(n)) for c,n,*_ in dst)
    # Merge repeated components without losing their total.
    combined={}
    for r in result:
        key=(r['land_before'],r['land_after'])
        combined[key]=combined.get(key,Decimal(0))+Decimal(r['area_m2'])
    return [dict(land_before=a,land_after=b,area_m2=str(n)) for (a,b),n in combined.items()]

def apply_scanned_review(row, prior, reviewed=None):
    """Apply image evidence after the caller has checked the PDF hash and pages."""
    row['detail_status']='visual_reviewed';row['detail_checked_on']=prior['reviewed_on']
    row['detail_pdf_pages']=','.join(str(i) for i in range(prior['page_start'],prior['page_end']+1))
    notes=['Kế thừa phiếu đọc ảnh PDF đã xác minh SHA256 và phạm vi trang của riêng quyết định.' if reviewed else 'Kế thừa phiếu đọc ảnh PDF đã xác minh SHA256 và phạm vi trang của riêng quyết định; chưa bổ sung được tổng thửa.']
    # A combined code does not identify the area of each source/destination.
    single=all(row.get(k) and not re.search(r'[;+]',row[k]) for k in ('land_before','land_after'))
    components=[dict(land_before=row['land_before'],land_after=row['land_after'],area_m2=row['area_m2'])] if single and row.get('area_m2') else []
    row['components_json']=json.dumps(components,ensure_ascii=False)
    row['residential_conversion_m2']=row['area_m2'] if row['land_after'] in ('ONT','ODT') else ''
    if reviewed:
        row.update(reviewed.get('fields',{}));notes.extend(reviewed.get('notes',[]))
        row['detail_pdf_pages']=reviewed['pages']
        row['detail_checked_on']=reviewed.get('checked_on',prior['reviewed_on'])
        components=json.loads(row.get('components_json') or '[]')
    if components:
        if any(not c[k] or re.search(r'[;+]',c[k]) for c in components for k in ('land_before','land_after')):
            raise ValueError('Unsplit land types in scanned review: '+row['decision_id'])
        total=sum((Decimal(c['area_m2']) for c in components),Decimal(0))
        if any(Decimal(c['area_m2'])<=0 for c in components) or total!=Decimal(row['area_m2']):
            raise ValueError('Scanned components disagree with reviewed area: '+row['decision_id'])
        if row.get('parcel_area_m2') and total>Decimal(row['parcel_area_m2']):
            raise ValueError('Scanned conversion exceeds parcel area: '+row['decision_id'])
        row['residential_conversion_m2']=str(sum((Decimal(c['area_m2']) for c in components if c['land_after'] in ('ONT','ODT','DAT_O')),Decimal(0)))
        row['land_before']=';'.join(dict.fromkeys(c['land_before'] for c in components))
        row['land_after']=';'.join(dict.fromkeys(c['land_after'] for c in components))
        row['conversion_group']=components[0]['land_before']+'->'+components[0]['land_after'] if len(components)==1 else 'hon_hop_da_tach'
    elif not single:
        notes.append('Chưa có diện tích riêng của từng hướng chuyển; chưa tạo thành phần từ mã đất gộp.')
    if reviewed and not row.get('parcel_area_m2'):
        notes.append('Chưa đọc được tổng diện tích thửa; không lấy diện tích chuyển làm tổng thửa.')
    if row.get('land_price_vnd_m2'):
        notes.append('Giá đồng/m² là số ghi trong quyết định, chưa phải tổng tiền sử dụng đất phải nộp; không nhân thẳng để suy nghĩa vụ tài chính.')
    row['detail_notes_json']=json.dumps(list(dict.fromkeys(notes)),ensure_ascii=False)
    return components


def enrich():
    from update_inventory import FIELDS
    from manual_reviews import load_reviews
    rows=load_texts();review_path=ROOT/'data/decision_detail_reviews.json'
    reviews=json.loads(review_path.read_text(encoding='utf-8')) if review_path.exists() else {}
    prior_reviews=load_reviews()
    by_id={r['decision_id']:r for r in rows}
    for key,review in reviews.items():
        target=ROOT/by_id[key]['local_pdf']
        assert review['source_pdf']==by_id[key]['local_pdf']
        assert hashlib.sha256(target.read_bytes()).hexdigest()==review['sha256'], 'Reviewed PDF has changed: '+key
    for row in rows:
        for key in DETAIL_FIELDS:row.setdefault(key,'')
        article=row.get('_article','');a=canon(article)
        if not a:
            if row['decision_id'] in prior_reviews:
                apply_scanned_review(row,prior_reviews[row['decision_id']],reviews.get(row['decision_id']))
            else:row['detail_status']=('scan_requires_review' if len(row.get('_text',''))<120 else 'content_requires_review') if row['local_pdf'] else 'no_pdf'
            continue
        pages=[str(i+1) for i,p in enumerate(row['_pages']) if re.search(r'Điều\s*1[.:]',p)]
        if pages:
            first=int(pages[0])-1
            last=next((i for i in range(first,len(row['_pages'])) if re.search(r'Điều\s*2[.:]',row['_pages'][i])),first)
            pages=[str(i+1) for i in range(first,last+1)]
        row['detail_pdf_pages']=','.join(pages)
        row['detail_status']='text_extracted';row['detail_checked_on']='2026-10-19'
        # Only explicit whole-parcel phrases provide a denominator; no area from cadastral IDs.
        matches=list(re.finditer(r'(?:dien tich thua dat\s*:?|tong dien tich(?:\s+sau khi chuyen muc dich su dung)?\s*:?)\s*'+AREA,a))
        if matches:
            vals=set()
            for m in matches:
                try:vals.add(amount(m[1]))
                except ValueError:pass
            if len(vals)==1:row['parcel_area_m2']=str(vals.pop())
        grant_m=re.search(r'(?:duoc\s+(?:phep\s+)?chuyen muc dich su dung)',a)
        before=a[:grant_m.start()] if grant_m else ''
        if before:row['initial_land_json']=json.dumps(group_areas(named_areas(before)),ensure_ascii=False)
        after_m=re.search(r'sau khi chuyen muc dich[,\s]',a)
        if after_m:
            after=a[after_m.end():];after=re.split(r'phuong thuc|gia dat|vi tri thua dat',after)[0]
            row['post_land_json']=json.dumps(group_areas(named_areas(after)),ensure_ascii=False)
        grant=a[grant_m.end():] if grant_m else ''
        grant=re.split(r'vi tri|hinh thuc|sau khi chuyen|thoi han su dung dat sau|gia dat',grant)[0]
        components=parse_components(grant,before,row)
        notes=[]
        if components:
            row['components_json']=json.dumps(components,ensure_ascii=False)
            total=sum((Decimal(c['area_m2']) for c in components),Decimal(0))
            # Refuse totals larger than the explicitly stated parcel.
            if row['parcel_area_m2'] and total>Decimal(row['parcel_area_m2']):
                components=[];row['components_json']='[]';notes.append('Các số diện tích chưa khớp tổng thửa; cần đọc lại, chưa cộng vào tổng.')
            else:
                row['area_m2']=str(total)
                row['land_before']=';'.join(dict.fromkeys(c['land_before'] for c in components))
                row['land_after']=';'.join(dict.fromkeys(c['land_after'] for c in components))
                row['conversion_group']=components[0]['land_before']+'->'+components[0]['land_after'] if len(components)==1 else 'hon_hop_da_tach'
                row['residential_conversion_m2']=str(sum((Decimal(c['area_m2']) for c in components if c['land_after'] in ('ODT','ONT','DAT_O')),Decimal(0)))
                row['area_status']='verified_pdf_identity' if row['pdf_identity_status']=='matched_number_and_date' else 'official_attachment_identity_pending'
        price=re.search(r'gia dat.{0,100}?:\s*([\d.,]+)\s*(?:dong|d)/?\s*(?:1\s*)?m',a)
        if price:
            try:row['land_price_vnd_m2']=str(Decimal(price[1].replace('.','').replace(',','.')))
            except ValueError:pass
        if re.search(r'lau dai',a) and (row['land_after'] in ('ODT','ONT','DAT_O') or row.get('residential_conversion_m2')):
            row['term_after']='Đất ở: lâu dài (theo nội dung tệp)'
        if row['decision_id'] in reviews:
            reviewed=reviews[row['decision_id']]
            row.update(reviewed.get('fields',{}));notes.extend(reviewed.get('notes',[]))
            row['detail_status']='visual_reviewed';row['detail_pdf_pages']=reviewed['pages']
            row['detail_checked_on']=reviewed.get('checked_on',row['detail_checked_on'])
            components=json.loads(row.get('components_json') or '[]')
        if components:
            total=sum((Decimal(c['area_m2']) for c in components),Decimal(0))
            residential=sum((Decimal(c['area_m2']) for c in components if c['land_after'] in ('ODT','ONT','DAT_O')),Decimal(0))
            row['area_m2']=str(total);row['residential_conversion_m2']=str(residential)
            row['land_before']=';'.join(dict.fromkeys(c['land_before'] for c in components));row['land_after']=';'.join(dict.fromkeys(c['land_after'] for c in components))
            row['conversion_group']=components[0]['land_before']+'->'+components[0]['land_after'] if len(components)==1 else 'hon_hop_da_tach'
            row['area_status']='verified_pdf_identity' if row['pdf_identity_status']=='matched_number_and_date' else 'official_attachment_identity_pending'
            if residential!=total:notes.append(f'Có hướng chuyển không thành đất ở: chỉ {residential} m² trong {total} m² chuyển mục đích là sang đất ở.')
        if row['pdf_identity_status']=='shared_pdf_conflict':
            row['area_status']='shared_pdf_excluded_from_verified_totals';notes.append('PDF đang được gắn cho nhiều số quyết định; chỉ xem nội dung tham khảo, chưa quy diện tích cho số nào.')
        initial=json.loads(row['initial_land_json'] or '{}');post=json.loads(row['post_land_json'] or '{}')
        flags=json.loads(row.get('detail_flags_json') or '[]')
        if row['parcel_area_m2']:
            for label,parts in [('trước chuyển',initial),('sau chuyển',post)]:
                subtotal=sum((Decimal(v) for v in parts.values()),Decimal(0))
                if parts and subtotal!=Decimal(row['parcel_area_m2']):
                    flags.append('internal_area_conflict');notes.append(f'Cơ cấu {label} cộng được {subtotal} m², khác tổng thửa {row["parcel_area_m2"]} m² ghi trong tệp. Chưa tự sửa số liệu.')
        repeated=re.search(r'(?:gom|bao gom)\s*'+AREA+r'\s*chuyen muc dich',a)
        if repeated and row.get('residential_conversion_m2'):
            try:
                if amount(repeated[1])!=Decimal(row['residential_conversion_m2']):
                    flags.append('internal_area_conflict');notes.append(f'Điều 1 nêu diện tích cho chuyển {row["residential_conversion_m2"]} m² nhưng phần cơ cấu sau chuyển ghi {repeated[1]} m² chuyển mục đích. Giữ cả hai thông tin để kiểm tra bản ký.')
            except ValueError:pass
        if 'internal_area_conflict' in flags:row['area_status']='source_internal_area_conflict'
        row['detail_flags_json']=json.dumps(list(dict.fromkeys(flags)),ensure_ascii=False)
        old_home=sum((Decimal(v) for k,v in initial.items() if k in ('ONT','ODT')),Decimal(0))
        if old_home:notes.append(f'Thửa đã có {old_home} m² đất ở trước chuyển; không đồng nhất với diện tích được chuyển thêm.')
        if row['land_price_vnd_m2']:notes.append('Giá đồng/m² là số ghi trong quyết định, chưa phải tổng tiền sử dụng đất phải nộp; không nhân thẳng để suy nghĩa vụ tài chính.')
        if row['parcel_area_m2'] and row.get('area_m2'):
            if Decimal(row['area_m2'])<Decimal(row['parcel_area_m2']):notes.append('Quyết định chỉ chuyển một phần thửa; phần còn lại không tự trở thành đất ở.')
        if not row['parcel_area_m2']:notes.append('Chưa đọc được tổng diện tích thửa từ nội dung đã trích; không lấy diện tích chuyển làm tổng thửa.')
        row['detail_notes_json']=json.dumps(list(dict.fromkeys(notes)),ensure_ascii=False)
    # Reviewed record fields are authoritative, including source-code spelling and
    # notes. Regeneration must not replace them with parser guesses or boilerplate.
    components_all=[]
    for row in rows:
        if row['decision_id'] in prior_reviews:
            row.update(prior_reviews[row['decision_id']]['record'])
        for i,c in enumerate(json.loads(row.get('components_json') or '[]')):
            components_all.append(dict(decision_id=row['decision_id'],component=i+1,**c,pdf_path=row['local_pdf'],pdf_pages=row['detail_pdf_pages'],content_review=row['detail_status'],identity_status=row['pdf_identity_status'],area_status=row['area_status']))
    clean=[{k:r.get(k,'') for k in FIELDS} for r in rows]
    write_csv(ROOT/'data/decisions_2026.csv',clean,FIELDS)
    write_csv(ROOT/'data/decision_components.csv',components_all,['decision_id','component','land_before','land_after','area_m2','pdf_path','pdf_pages','content_review','identity_status','area_status'])
    from collections import Counter
    print(json.dumps(dict(details=dict(Counter(r['detail_status'] for r in rows)),explicit_parcel_area=sum(bool(r['parcel_area_m2']) for r in rows),component_decisions=sum(bool(r['components_json'] and r['components_json']!='[]') for r in rows),components=len(components_all)),ensure_ascii=False,indent=2))

def load_texts():
    cache=json.loads(CACHE.read_text(encoding='utf-8')) if CACHE.exists() else {}
    rows=list(csv.DictReader((ROOT/'data/decisions_2026.csv').open(encoding='utf-8-sig')))
    for i,r in enumerate(rows):
        if not r['local_pdf']:continue
        p=ROOT/r['local_pdf']; digest=hashlib.sha256(p.read_bytes()).hexdigest()
        if digest not in cache:
            cache[digest]={'pages':[x.extract_text() or '' for x in PdfReader(p).pages]}
        r['_pages']=cache[digest]['pages']
        r['_text']=' '.join(' '.join(r['_pages']).split())
        match=re.search(r'Điều\s*1[.:](.*?)(?:Điều\s*2[.:]|$)',r['_text'],re.I)
        r['_article']=match[1] if match else ''
    CACHE.write_text(json.dumps(cache,ensure_ascii=False),encoding='utf-8')
    return rows

if __name__=='__main__':
    if '--enrich' in sys.argv:
        enrich()
        raise SystemExit()
    rows=load_texts()
    selected=[]
    # Show source evidence around area terms; avoid reproducing recipient names.
    for r in rows:
        a=r.get('_article','')
        if not a:continue
        hits=list(re.finditer(r'(?:tổng diện tích|diện tích (?:cả |toàn bộ )?thửa|trên (?:tổng )?diện tích|thửa đất (?:có )?diện tích|diện tích được chuyển|chuyển mục đích sử dụng)',a,re.I))
        if hits:
            selected.append(dict(id=r['decision_id'],path=r['local_pdf'],status=r['area_status'],evidence=[a[max(0,m.start()-30):m.start()+500] for m in hits[:3]]))
    (ROOT/'tmp/decision_detail_candidates.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Cached',sum(bool(r.get('_text')) for r in rows),'PDF texts;',len(selected),'detail candidates')
