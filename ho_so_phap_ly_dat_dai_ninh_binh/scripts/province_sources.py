"""Prefer verified provincial document pages while retaining source caveats."""
import json
from parse_sources import ROOT, write_csv

def apply_province_sources(rows):
    sources = json.loads((ROOT/'data/province_document_sources.json').read_text(encoding='utf-8'))
    for row in rows:
        entry = sources['documents'].get(row['document_id'])
        if entry:
            row.update(entry['updates'])
    return rows

if __name__ == '__main__':
    import csv
    rows = list(csv.DictReader((ROOT/'data/legal_documents.csv').open(encoding='utf-8-sig')))
    write_csv(ROOT/'data/legal_documents.csv', apply_province_sources(rows))
    print('Updated preferred provincial sources; retained all legal records')
