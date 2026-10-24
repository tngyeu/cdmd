"""Apply reviewed descriptions and supplementary records without losing source caveats."""
import csv
import json
from parse_sources import ROOT, write_csv

def apply_legal_editorial(rows):
    editorial = json.loads((ROOT/'data/legal_editorial.json').read_text(encoding='utf-8'))
    by_id = {row['document_id']: row for row in rows}
    for entry in editorial['new_documents']:
        by_id.setdefault(entry['document_id'], {}).update(entry)
    for key, updates in editorial['documents'].items():
        if key not in by_id:
            raise ValueError('Editorial entry has no source record: ' + key)
        by_id[key].update(updates)
    result = list(by_id.values())
    fields = list(dict.fromkeys(key for row in result for key in row))
    for row in result:
        if not row.get('summary') or not row.get('practical_relevance') or not row.get('summary_basis'):
            raise ValueError('Missing reviewed description: ' + row['document_id'])
        for field in fields:
            row.setdefault(field, '')
    return result

if __name__ == '__main__':
    rows = list(csv.DictReader((ROOT/'data/legal_documents.csv').open(encoding='utf-8-sig')))
    result = apply_legal_editorial(rows)
    write_csv(ROOT/'data/legal_documents.csv',result)
    print(f'Updated {len(result)} legal records with reviewed descriptions')
