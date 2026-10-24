import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { compareLegal, filterLegal } from '../lib/legal-library.mjs';
import { getResearch } from '../lib/content.mjs';

test('legal dates sort in both directions with undated documents always last', () => {
  const rows = [{ number: 'old', issued_date: '2024-01-18' }, { number: 'unknown', issued_date: '' }, { number: 'new', issued_date: '2026-09-10' }];
  assert.deepEqual([...rows].sort((a,b) => compareLegal(a,b,'newest')).map(r=>r.number), ['new','old','unknown']);
  assert.deepEqual([...rows].sort((a,b) => compareLegal(a,b,'oldest')).map(r=>r.number), ['old','new','unknown']);
});
test('recent view uses the research cutoff; older and undated sources stay accessible', () => {
  const rows = [{ number:'old', issued_date:'2024-01-18' }, { number:'boundary', issued_date:'2025-10-19' }, { number:'new', issued_date:'2026-07-29' }, { number:'future', issued_date:'2026-10-20' }, { number:'unknown', issued_date:'' }];
  assert.deepEqual(filterLegal(rows).map(r=>r.number), ['boundary','new']);
  assert.deepEqual(filterLegal(rows,{view:'all',year:'2024'}).map(r=>r.number), ['old']);
  assert.deepEqual(filterLegal(rows,{view:'undated'}).map(r=>r.number), ['unknown']);
});
test('user-supplied land fund proposal is indexed with its reviewed source and date', () => {
  const doc = getResearch().legal.find(doc => doc.document_id === 'NB-DA08-2026');
  assert.ok(doc);
  assert.equal(doc.number,'08/ĐA-UBND');
  assert.equal(doc.issued_date,'2026-07-29');
  assert.equal(doc.source_url,'https://ninhbinh.gov.vn/?pageid=27160&p_steering=47854');
  assert.equal(doc.recent,true);
  assert.equal(doc.topic,'boi-canh');
  assert.ok(fs.existsSync('ho_so_phap_ly_dat_dai_ninh_binh/' + doc.local_file));
});
