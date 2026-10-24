"""Content-bound visual reviews, including disjoint decisions in a scanned bundle."""
import hashlib
import json
from pypdf import PdfReader
from parse_sources import ROOT, slug


def load_reviews():
    path = ROOT / 'data/pdf_manual_reviews.json'
    if not path.exists():
        return {}
    reviews = json.loads(path.read_text(encoding='utf-8'))
    result = {}
    for review in reviews:
        row = review['record']
        key = row['decision_id']
        assert key not in result
        assert key == f"{slug(row['locality'])}|{row['decision_number']}|{row['issue_date']}"
        target = (ROOT / row['local_pdf']).resolve()
        assert target.is_relative_to(ROOT) and target.is_file()
        assert hashlib.sha256(target.read_bytes()).hexdigest() == review['sha256'], key
        assert 1 <= review['page_start'] <= review['page_end'] <= len(PdfReader(target).pages)
        assert review['page_start'] <= int(row['content_pdf_page']) <= review['page_end']
        assert row['verification_status'] in {'official_metadata', 'official_pdf'}
        if row['area_status'] == 'verified_pdf_identity':
            assert row['verification_status'] == 'official_pdf'
            assert row['pdf_identity_status'] == 'matched_number_and_date'
        result[key] = review
    return result


def disjoint_reviewed_bundle(ids, reviews):
    if not all(key in reviews for key in ids):
        return False
    spans = sorted((reviews[key]['page_start'], reviews[key]['page_end']) for key in ids)
    return all(left[1] < right[0] for left, right in zip(spans, spans[1:]))


def apply_manual_reviews(combined, reviews):
    """Replace only explicitly reviewed catalogue identities, never all same-number rows."""
    for key, review in reviews.items():
        for previous in review.get('supersedes_decision_ids', []):
            if previous == key or previous.rsplit('|',1)[0] != key.rsplit('|',1)[0]:
                raise ValueError('Identity correction must keep locality and decision number: '+previous)
            combined.pop(previous,None)
        combined.setdefault(key,{}).update(review['record'])
