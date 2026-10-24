"""Rebuild public decision inventory from downloaded official pages, preserving reviews."""
import collections
import csv
import json
import re
import sys
from urllib.parse import urlsplit, parse_qs
from lxml import html as lhtml
from parse_sources import ROOT, clean, links, slug, parse_decisions, write_csv, decision_title_matches
from manual_reviews import load_reviews, apply_manual_reviews

sys.stdout.reconfigure(encoding='utf-8')
FIELDS=['decision_id','locality','issuing_authority','decision_number','issue_date','land_before','land_after','conversion_group','area_m2','verification_status','source_page','pdf_url','local_pdf','checked_on','notes','pdf_identity_status','area_status','content_pdf_page']
FIELDS += ['parcel_area_m2','initial_land_json','post_land_json','residential_conversion_m2','components_json','detail_notes_json','detail_status','detail_pdf_pages','land_price_vnd_m2','term_after','detail_checked_on']
FIELDS += ['detail_flags_json']
RANK={'candidate':0,'official_metadata':1,'official_pdf':2}

def read_csv(path):
    return list(csv.DictReader(path.open(encoding='utf-8-sig'))) if path.exists() else []

def detail_record(text, job):
    tree=lhtml.fromstring(text)
    metadata={}
    for row in tree.xpath('//tr'):
        cells=row.xpath('./th|./td')
        if len(cells)==2:
            metadata[clean(lhtml.tostring(cells[0],encoding='unicode'))]=clean(lhtml.tostring(cells[1],encoding='unicode'))
    title=metadata.get('Trích yếu','')
    if not title:
        title=' '.join(tree.xpath('//h1//text()'))
    if not decision_title_matches(title):return None
    if re.search(r'thu hồi|đính chính|hủy|điều chỉnh|thủ tục|hồ sơ',title,re.I):return None
    number=next((metadata[k] for k in ('Số ký hiệu văn bản','Số ký hiệu','Số hiệu','Ký hiệu') if metadata.get(k)), '')
    date=metadata.get('Ngày ban hành','')
    mock=f'<table><tr><td>{number}</td><td>Quyết định cho phép chuyển mục đích sử dụng đất</td><td>{date}</td></tr></table>'
    records=parse_decisions(mock,job['url'],job['locality'])
    if not records:return None
    record=records[0]; record['source_page']=job['url']
    pdfs=[u for _,u in links(text,job['url']) if '.pdf' in u.lower()]
    if pdfs:record['pdf_url']=pdfs[0]
    return record

def main():
    logs=[]
    for line in (ROOT/'data/download_log.jsonl').read_text(encoding='utf-8').splitlines():
        try:logs.append(json.loads(line))
        except json.JSONDecodeError:continue
    jobs={item['url']:item for item in logs if 'locality' in item}
    for path in (ROOT/'tmp').glob('jobs_*.json'):
        for job in json.loads(path.read_text(encoding='utf-8-sig')):
            if 'locality' in job:jobs[job['url']]=job
    combined={r['decision_id']:r for r in read_csv(ROOT/'data/decisions_2026.csv')}
    counts=collections.Counter()
    sources=collections.defaultdict(set)
    new_details={}; new_pages={}
    for log in logs:
        if log.get('status')!='downloaded' or log['url'] not in jobs:continue
        job=jobs[log['url']]; path=ROOT/log['path']
        if path.suffix!='.html' or not path.exists():continue
        text=path.read_text(encoding='utf-8',errors='replace')
        if 'ninhbinh.gov.vn' not in urlsplit(log['url']).netloc:continue
        sources[job['locality']].add(log['url'])
        records=[]
        if '/detail_' in str(path).replace('\\','/'):
            row=detail_record(text,job)
            if row:records.append(row)
        else:records=parse_decisions(text,job['url'],job['locality'])
        for row in records:
            key=row['decision_id']
            old=combined.get(key)
            if old:
                for field,value in row.items():
                    if value and not old.get(field):old[field]=value
                # Detail pages provide attachment links, while validated data remain intact.
                if row['pdf_url'] and not old.get('pdf_url'):old['pdf_url']=row['pdf_url']
            else:combined[key]=row
        for label,url in links(text,job['url']):
            if decision_title_matches(label) and '.pdf' not in url.lower() and url not in jobs and urlsplit(url).netloc==urlsplit(job['url']).netloc:
                new_details[url]=dict(url=url,path=f'documents/nguon_web/detail_{job["slug"]}_{slug(url)[-35:]}.html',slug=job['slug'],locality=job['locality'])
            if 'search=' in url and 'page=' in url and url not in jobs and urlsplit(url).netloc==urlsplit(job['url']).netloc:
                query=parse_qs(urlsplit(url).query)
                if query.get('search')==['chuyển']:
                    n=query.get('page',['1'])[0]
                    new_pages[url]=dict(url=url,path=f'documents/nguon_web/searchpage_{job["slug"]}_p{n}.html',slug=job['slug'],locality=job['locality'])
    apply_manual_reviews(combined,load_reviews())
    rows=sorted(combined.values(),key=lambda x:(x['locality'],x['issue_date'],x['decision_number']))
    for row in rows:
        for field in FIELDS:row.setdefault(field,'')
        counts[row['locality']]+=1
    write_csv(ROOT/'data/decisions_2026.csv',rows,FIELDS)
    downloaded={x['url']:x for x in logs if x.get('status')=='downloaded'}
    pdf_jobs=[]
    for row in rows:
        if row['pdf_url'] in downloaded:
            row['local_pdf']=downloaded[row['pdf_url']]['path']
        elif row['pdf_url']:
            pdf_jobs.append(dict(url=row['pdf_url'],path=f'documents/quyet_dinh_2026/{slug(row["locality"])}_{row["decision_number"].split("/")[0]}_{row["issue_date"]}.pdf',decision_id=row['decision_id'],source_page=row['source_page']))
    write_csv(ROOT/'data/decisions_2026.csv',rows,FIELDS)
    (ROOT/'tmp/jobs_remaining_pdfs.json').write_text(json.dumps(pdf_jobs,ensure_ascii=False),encoding='utf-8')
    (ROOT/'tmp/jobs_remaining_pages.json').write_text(json.dumps(list(new_details.values())+list(new_pages.values()),ensure_ascii=False),encoding='utf-8')
    coverage=[]
    for locality in read_csv(ROOT/'data/localities.csv'):
        name=locality['locality']; paths=sources.get(name,set())
        coverage.append(dict(locality=name,website=locality['candidate_home'],pages_checked=len(paths),records_found=counts[name],status='found_public_records' if counts[name] else ('searched_no_matching_record' if paths else 'directory_not_fully_accessed'),checked_on='2026-10-19',notes='Phạm vi là các trang đã lưu; chưa khẳng định bao phủ toàn bộ website hoặc toàn bộ quyết định đã ban hành.'))
    write_csv(ROOT/'data/coverage_129.csv',coverage)
    print(json.dumps(dict(records=len(rows),localities=len(counts),counts=dict(counts),remaining_pdfs=len(pdf_jobs),remaining_pages=len(new_details)+len(new_pages)),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
