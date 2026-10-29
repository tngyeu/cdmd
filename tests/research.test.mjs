import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { parse } from 'csv-parse/sync';
import { normalize, compareRows, filterDecisions, aggregateLocalities, quotaScenario } from '../lib/decision-math.mjs';
import { getResearch } from '../lib/content.mjs';

test('Vietnamese search matches accents and Đ', () => {
  assert.equal(normalize('Đất ở Phường Duy Tân'), 'dat o phuong duy tan');
});
test('missing numeric values remain last in both sort directions', () => {
  const rows = [{ area_m2: '' }, { area_m2: '106' }, { area_m2: '0' }, { area_m2: '20.1' }];
  assert.deepEqual([...rows].sort((a, b) => compareRows(a, b, 'area_m2', 'ascending')).map(r => r.area_m2), ['0', '20.1', '106', '']);
  assert.deepEqual([...rows].sort((a, b) => compareRows(a, b, 'area_m2', 'descending')).map(r => r.area_m2), ['106', '20.1', '0', '']);
});
test('mixed conversions contribute only matching components, conflicts never contribute area', () => {
  const rows = [
    { locality: 'A', area_m2: '250', area_status: 'verified_pdf_identity', land_before: 'HỖN HỢP', land_after: 'HỖN HỢP', components_json: JSON.stringify([{ land_before: 'CLN', land_after: 'ODT', area_m2: '106' }, { land_before: 'CLN', land_after: 'TMD', area_m2: '144' }]) },
    { locality: 'A', area_m2: '9999', area_status: 'source_internal_area_conflict', conversion_group: 'CLN->ODT' },
    { locality: 'A', area_m2: '8888', area_status: 'verified_pdf_identity', pdf_identity_status: 'shared_pdf_conflict', conversion_group: 'CLN->ODT' }
  ];
  const matches = filterDecisions(rows, { type: 'CLN->ODT' });
  assert.equal(matches.length, 3);
  const [summary] = aggregateLocalities(matches, 'CLN->ODT', ['A']);
  assert.equal(summary.known_area_m2, 106);
  assert.equal(summary.area_m2, 106);
  assert.equal(summary.residential_area_m2, 106);
  assert.equal(summary.excluded_area_records, 2);
});
test('all locality totals match the reviewed source summary', () => {
  const research = getResearch();
  const original = parse(fs.readFileSync('ho_so_phap_ly_dat_dai_ninh_binh/data/locality_summary_2026.csv', 'utf8'), { columns: true, bom: true, skip_empty_lines: true });
  assert.equal(research.decisions.length, 462);
  assert.equal(research.legal.length, 52);
  assert.equal(research.faq.length, 22);
  assert.equal(research.localities.length, 129);
  assert.equal(research.analysis.quotas.length, 129);
  for (const row of original) {
    const actual = research.summary.find(item => item.locality === row.locality);
    assert.ok(actual, row.locality);
    for (const key of ['records', 'known_area_records', 'known_area_m2', 'residential_area_m2', 'area_m2', 'pending_area_m2', 'missing_area_records', 'excluded_area_records']) assert.equal(Number(actual[key]), Number(row[key]), `${row.locality}: ${key}`);
  }
});
test('each legal entry belongs to exactly one topic and citations retain their source role', () => {
  const research = getResearch();
  assert.equal(research.topics.reduce((sum, topic) => sum + topic.count, 0), research.legal.length);
  const citation = research.legal.find(doc => doc.document_id === 'NB568');
  assert.equal(citation.isCitation, true);
  assert.equal(citation.localLabel, 'Mở văn bản có viện dẫn');
  assert.notEqual(citation.evidence.tone, 'green');
});
test('quota model is a fixed-period scenario, with explicit share and invalid input handling', () => {
  assert.equal(quotaScenario(50.26, 150).cases, 3350);
  assert.equal(quotaScenario(50.26, 106).cases, 4741);
  assert.equal(quotaScenario(50.26, 150, 5, 50).cases, 1675);
  assert.equal(quotaScenario(50.26, 0), null);
  assert.equal(quotaScenario(50.26, 150, 5, 101), null);
});
