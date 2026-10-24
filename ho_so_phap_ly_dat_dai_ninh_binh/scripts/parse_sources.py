"""Small, offline helpers for official HTML and Vietnamese numeric tables."""
import csv
import html
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import urljoin
from lxml import html as lhtml

ROOT = Path(__file__).resolve().parents[1]

def clean(value):
    return unicodedata.normalize('NFC', re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]*>", " ", value))).strip())

def decision_title_matches(value):
    """Accept observed title variants without importing procedures or requests."""
    value = clean(value).lower()
    if re.search(r'thu hồi|đính chính|hủy|điều chỉnh|thủ tục|hồ sơ|sử dụng rừng', value):
        return False
    return bool(re.search(
        r'cho phép chuyển (?:đổi )?mục đích'
        r'|quyết định\s+(?:về việc\s+)?chuyển (?:đổi )?mục đích'
        r'|cho phép .{1,180}?được chuyển (?:đổi )?mục đích'
        r'|(?:về việc|v/v)\s+chuyển (?:đổi )?mục đích', value))

def slug(value):
    value = unicodedata.normalize("NFD", value.lower().replace("đ", "d"))
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in value if not unicodedata.combining(c)))

def links(text, base):
    return [(clean(body), urljoin(base, html.unescape(href))) for href,body in re.findall(r'<a\b[^>]*href=[\"\x27]([^\"\x27]+)[\"\x27][^>]*>(.*?)</a>', text, re.S|re.I)]

def write_csv(path, rows, fields=None):
    if not fields:
        fields = list(rows[0])
    with path.open("w", encoding="utf-8-sig", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def parse_quota():
    text = (ROOT/"tmp/3279_2026_phu_luc_129.txt").read_text(encoding="utf-8")
    localities=[]
    quotas=[]
    for match in re.finditer(r"--- PDF PAGE (\d+) ---\s+PHỤ LỤC (\d+)\.\s*PHÂN BỔ CHỈ TIÊU SỬ DỤNG ĐẤT ĐẾN NĂM 2030\s+([^\n]+)", text):
        page, appendix, raw = match.groups()
        name = clean(raw).replace("PHƯƠNG ", "PHƯỜNG ").title().replace("Xã ", "Xã ")
        bare = re.sub(r"^(Xã|Phường) ", "", name)
        localities.append(dict(locality=name, slug=slug(bare), appendix=appendix, pdf_page=page, candidate_home=f"https://{slug(bare)}.ninhbinh.gov.vn/", website_status="candidate_unchecked"))
        if bare == "Duy Tân":
            start=match.start()
            end=text.find("PHỤ LỤC ",match.end())
            section=text[start:end if end>=0 else len(text)]
            section=section.split('* Ghi chú:',1)[0]
            for line in section.splitlines():
                row=re.search(r"\b([A-Z]{2,3})\s+([\d.,]+)\s+([\d.,]+)\s*$",line)
                if not row: continue
                code,v0,v1=row.groups()
                from decimal import Decimal
                a=Decimal(v0.replace('.','').replace(',','.')); b=Decimal(v1.replace('.','').replace(',','.'))
                quotas.append(dict(locality="Phường Duy Tân",document_id="NB-3279-2026",version="2026-08-30_attachment",land_code=code,baseline_year="2025",baseline_ha=str(a),target_year="2030",target_ha=str(b),change_ha=str(b-a),average_2026_2030_ha=str((b-a)/5),unit="ha",verification_status="official_attachment_identity_pending",source_page="https://ninhbinh.gov.vn/?pageid=27160&p_steering=48598",pdf_path="documents/quy_hoach/3279_2026_phu_luc_129.pdf",pdf_page=page if code not in {"DBV","DCH","DKV","TON","TIN","NTD","TVC","PNK","CSD"} else str(int(page)+1),notes="Phụ lục 121; bản đính kèm trống số/ngày. Cần đối chiếu bản ký/phụ lục đóng dấu."))
    assert len(localities)==129, len(localities)
    write_csv(ROOT/"data/localities.csv",localities)
    write_csv(ROOT/"data/land_quotas.csv",quotas)
    return localities

def parse_decisions(text, base, locality):
    out=[]
    tree = lhtml.fromstring(text)
    for element in tree.xpath('//tr'):
        if element.xpath('.//tr'):
            continue
        row = lhtml.tostring(element, encoding='unicode')
        plain=clean(row)
        low=plain.lower()
        if not decision_title_matches(plain): continue
        if not re.search(r"quyết định|qđ",low): continue
        if any(k in low for k in ["thu hồi quyết định", "hủy bỏ", "đính chính", "điều chỉnh quyết định"]): continue
        number=re.search(r"\b(\d+\s*/\s*Q[ĐD]-UBND)\b",plain,re.I)
        # A range describes a PDF bundle, not a single decision. Review its pages.
        if re.search(r'\d+\s*[-–]\s*\d+\s*/\s*Q[ĐD]-UBND',plain,re.I): continue
        date=re.search(r"\b(\d{1,2})/(\d{1,2})/(2026)\b",plain)
        if not (number and date): continue
        d,m,y=date.groups()
        iso=f"{y}-{int(m):02}-{int(d):02}"
        if not "2026-01-01"<=iso<="2026-10-19": continue
        rowlinks=links(row,base)
        pdfs=[url for _,url in rowlinks if '.pdf' in url.lower()]
        details=[url for _,url in rowlinks if re.search(r"chitiet|van-ban-dieu-hanh/\d+",url)]
        num=re.sub(r"\s+","",number.group(1)).upper().replace("QD-", "QĐ-")
        out.append(dict(decision_id=f"{slug(locality)}|{num}|{iso}",locality=locality,issuing_authority=f"UBND {locality}",decision_number=num,issue_date=iso,land_before="",land_after="",conversion_group="chua_xac_dinh",area_m2="",verification_status="official_metadata",source_page=details[0] if details else base,pdf_url=pdfs[0] if pdfs else "",local_pdf="",checked_on="2026-10-19",notes="Số/ngày/trích yếu từ bảng văn bản chính thức; cần đọc PDF để xác minh cơ quan ký, loại đất, diện tích."))
    return list({row['decision_id']:row for row in out}.values())

if __name__ == "__main__":
    localities=parse_quota()
    jobs=[dict(url=row['candidate_home'],path=f"documents/nguon_web/home_{row['slug']}.html",timeout=14) for row in localities]
    (ROOT/'tmp/jobs_homes.json').write_text(json.dumps(jobs,ensure_ascii=False),encoding='utf-8')
    print(f"Parsed {len(localities)} localities")
