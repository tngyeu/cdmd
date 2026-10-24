"""Regression checks for reviewed scans with no extractable Article 1."""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from read_decision_details import apply_scanned_review
import read_decision_details
from manual_reviews import apply_manual_reviews


class ScannedReviewTests(unittest.TestCase):
    def setUp(self):
        self.row=dict(decision_id='scan',land_before='CLN;NTS',land_after='ODT',area_m2='240')
        self.prior=dict(reviewed_on='2026-10-19',page_start=1,page_end=2)
        self.review=dict(pages='1,2',checked_on='2026-10-21',fields={
            'components_json':json.dumps([
                dict(land_before='CLN',land_after='ODT',area_m2='193.7'),
                dict(land_before='NTS',land_after='ODT',area_m2='46.3')]),
            'land_price_vnd_m2':'2000000'},notes=['Đọc Điều 1.'])

    def test_split_mixed_scan_and_apply_evidence(self):
        parts=apply_scanned_review(self.row,self.prior,self.review)
        self.assertEqual([p['area_m2'] for p in parts],['193.7','46.3'])
        self.assertEqual(self.row['conversion_group'],'hon_hop_da_tach')
        self.assertEqual(self.row['residential_conversion_m2'],'240.0')
        self.assertEqual(self.row['land_price_vnd_m2'],'2000000')
        self.assertEqual(self.row['detail_checked_on'],'2026-10-21')
        self.assertIn('Đọc Điều 1.',json.loads(self.row['detail_notes_json']))

    def test_keep_legacy_single_source_review(self):
        self.row.update(land_before='CLN',land_after='ONT',area_m2='65')
        parts=apply_scanned_review(self.row,self.prior)
        self.assertEqual(parts,[dict(land_before='CLN',land_after='ONT',area_m2='65')])
        self.assertEqual(self.row['detail_pdf_pages'],'1,2')
        self.assertEqual(self.row['detail_checked_on'],'2026-10-19')

    def test_do_not_invent_mixed_components(self):
        self.assertEqual(apply_scanned_review(self.row,self.prior),[])
        self.row['land_before']='CLN+NTS'
        self.assertEqual(apply_scanned_review(self.row,self.prior),[])

    def test_reject_mismatched_component_total(self):
        self.row['area_m2']='239'
        with self.assertRaisesRegex(ValueError,'disagree'):
            apply_scanned_review(self.row,self.prior,self.review)

    def test_preserve_parcel_and_post_conversion_review(self):
        self.row.update(land_before='CLN',land_after='ONT',area_m2='150')
        review=dict(pages='1',fields=dict(parcel_area_m2='354.2',post_land_json='{"ONT":"150","CLN":"204.2"}'))
        apply_scanned_review(self.row,self.prior,review)
        self.assertEqual(self.row['parcel_area_m2'],'354.2')
        self.assertEqual(json.loads(self.row['post_land_json']),{'ONT':'150','CLN':'204.2'})
        self.assertNotIn('initial_land_json',self.row)

    def test_catalogue_date_correction_survives_reimport(self):
        wrong='quanghung|1058|2026-10-19';correct='quanghung|1058|2026-09-28';other='quanghung|1059|2026-10-19'
        rows={wrong:{'source':'catalogue'},other:{'keep':True}}
        reviews={correct:dict(record={'decision_id':correct,'issue_date':'2026-09-28'},supersedes_decision_ids=[wrong])}
        apply_manual_reviews(rows,reviews)
        rows[wrong]={'source':'catalogue reimport'}
        apply_manual_reviews(rows,reviews)
        self.assertEqual(set(rows),{correct,other})
        self.assertTrue(rows[other]['keep'])

    def test_correction_cannot_remove_an_unrelated_decision(self):
        with self.assertRaisesRegex(ValueError,'keep locality'):
            apply_manual_reviews({'a|1|2026-01-01':{}},{'b|2|2026-01-01':dict(record={},supersedes_decision_ids=['a|1|2026-01-01'])})

    def test_enrichment_preserves_authoritative_review_fields(self):
        from update_inventory import FIELDS
        components=[dict(land_before='CLN',land_after='ODT',area_m2='193.7'),dict(land_before='NTS',land_after='ODT',area_m2='46.3')]
        record={field:'' for field in FIELDS}
        record.update(decision_id='reviewed',local_pdf='source.pdf',land_before='CLN+NTS',land_after='ODT',area_m2='240',components_json=json.dumps(components),detail_status='visual_reviewed',detail_pdf_pages='2',detail_checked_on='2026-10-20',detail_notes_json='["Ghi chú đã đối chiếu ảnh."]',pdf_identity_status='matched_number_and_date',area_status='verified_pdf_identity')
        row=dict(record,_article='Cho phép chuyển mục đích sử dụng đất.',_pages=['Điều 1. Cho phép chuyển mục đích sử dụng đất. Điều 2.'])
        prior=dict(record=record,reviewed_on='2026-10-20',page_start=1,page_end=2)
        written={}
        def capture(path,values,fields):written[path.name]=values
        folder=Path(__file__).parent/'fixtures/absent-review-root'
        self.assertFalse(folder.exists())
        with patch.object(read_decision_details,'ROOT',folder), patch.object(read_decision_details,'load_texts',return_value=[row]), patch('manual_reviews.load_reviews',return_value={'reviewed':prior}), patch.object(read_decision_details,'write_csv',side_effect=capture), patch('builtins.print'):
            read_decision_details.enrich()
        self.assertEqual(written['decisions_2026.csv'],[record])
        self.assertEqual([r['area_m2'] for r in written['decision_components.csv']],['193.7','46.3'])


if __name__=='__main__':
    unittest.main()
