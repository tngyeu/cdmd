import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { parse } from 'csv-parse/sync';
import { getReplyKit } from '../lib/reply-content.mjs';

// Inventory and provenance checks, not a certificate of legal validity or eligibility.
const checkedOn = process.argv[2];
if (!/^\d{4}-\d{2}-\d{2}$/.test(checkedOn || '')) throw new Error('Pass the review date explicitly: YYYY-MM-DD');
const moduleDir = path.resolve('ho_so_phap_ly_dat_dai_ninh_binh');
const read = file => fs.readFileSync(path.join(moduleDir, file), 'utf8').replace(/^\uFEFF/, '');
const csv = file => parse(read(file), { columns: true, skip_empty_lines: true });
const hash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const countBy = (rows, key) => rows.reduce((out, row) => { const value = row[key] || '(blank)'; out[value] = (out[value] || 0) + 1; return out; }, {});
const legal = csv('data/legal_documents.csv');
const decisions = csv('data/decisions_2026.csv');
const display = JSON.parse(read('data/display_data.json'));
const nearMatches = JSON.parse(read('data/doi_chieu_549_review_20261021.json'));
const { scenarios } = getReplyKit();
const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/gi, 'd').toLowerCase();
const fileChecks = legal.map(row => ({
  id: row.document_id, file: row.local_file, exists: !!row.local_file && fs.existsSync(path.resolve(moduleDir, row.local_file)),
  hasSourceURL: /^https?:\/\//.test(row.source_url), hasArticleLocator: !!row.relevant_articles.trim(),
  sourceStatus: row.verification_status, currentStatus: row.current_status
}));
const decisionFiles = [...new Set(decisions.map(row => row.local_pdf).filter(Boolean))];
const missingDecisionFiles = decisionFiles.filter(file => !fs.existsSync(path.resolve(moduleDir, file)));
const manifest = JSON.parse(read('documents/ho_so_duy_tan/anhome/source_manifest.json'));
const drawingChecks = manifest.map(row => {
  const file = path.join(moduleDir, 'documents/ho_so_duy_tan/anhome', row.local_file);
  return { file: row.local_file, exists: fs.existsSync(file), hashMatches: fs.existsSync(file) && hash(file) === row.sha256, role: row.role };
});
const sourceLinkChecks = [];
const kit = read('reports/bo_phan_hoi_van_ban.md');
for (const section of kit.split(/(?=^## )/m).filter(item => /^## S\d{2} /.test(item))) {
  const id = section.match(/^## (S\d{2}) /)[1];
  const sources = section.split('### Nguồn\n')[1] || '';
  const links = [...sources.matchAll(/\[[^\]]+\]\(([^)]+)\)/g)].map(match => match[1]);
  const local = links.filter(link => !/^https?:|^\//.test(link));
  sourceLinkChecks.push({
    id, links: links.length,
    missingLocalTargets: local.filter(link => !fs.existsSync(path.resolve(moduleDir, 'reports', decodeURIComponent(link.split('#')[0]))))
  });
}
const audit = {
  checked_on: checkedOn,
  scope: 'Counts, indexed local files, scenario source links and drawing hashes. Does not certify current legal force, completeness of collection, parcel eligibility or success probability.',
  legal: {
    records: legal.length, source_statuses: countBy(legal, 'verification_status'),
    records_without_article_locator: fileChecks.filter(row => !row.hasArticleLocator).map(row => row.id),
    records_without_source_url: fileChecks.filter(row => !row.hasSourceURL).map(row => row.id),
    records_with_no_local_file: fileChecks.filter(row => !row.file).map(row => row.id),
    missing_referenced_files: fileChecks.filter(row => row.file && !row.exists),
    file_checks: fileChecks
  },
  decisions: {
    records: decisions.length, localities: new Set(decisions.map(row => row.locality)).size,
    identity_statuses: countBy(decisions, 'pdf_identity_status'), verification_statuses: countBy(decisions, 'verification_status'),
    area_statuses: countBy(decisions, 'area_status'),
    records_with_local_pdf: decisions.filter(row => row.local_pdf).length,
    unique_referenced_local_pdfs: decisionFiles.length, missing_referenced_files: missingDecisionFiles,
    duy_tan_records: decisions.filter(row => normalize(row.locality).includes('duy tan')).length,
    comparator_549_verified: nearMatches.qualified_cases_verified,
    comparator_549_scope: nearMatches.method,
    display_stats: display.stats,
    record_count_matches_display: decisions.length === display.stats.records
  },
  response_kit: { count: scenarios.length, source_links: sourceLinkChecks },
  case_drawings: drawingChecks,
  input_sha256: Object.fromEntries(['data/legal_documents.csv', 'data/decisions_2026.csv', 'data/display_data.json', 'data/doi_chieu_549_review_20261021.json', 'reports/bo_phan_hoi_van_ban.md'].map(file => [file, hash(path.join(moduleDir, file))]))
};
const output = path.join(moduleDir, 'data', `response_readiness_audit_${checkedOn.replaceAll('-', '')}.json`);
fs.writeFileSync(output, JSON.stringify(audit, null, 2) + '\n');
console.log(JSON.stringify({ output, legal_records: audit.legal.records, legal_source_statuses: audit.legal.source_statuses, missing_legal_files: audit.legal.missing_referenced_files, no_local_file: audit.legal.records_with_no_local_file, missing_article_locators: audit.legal.records_without_article_locator, decision_records: audit.decisions.records, decision_localities: audit.decisions.localities, decision_verification: audit.decisions.verification_statuses, decision_identity: audit.decisions.identity_statuses, decision_areas: audit.decisions.area_statuses, unique_decision_pdfs: decisionFiles.length, missing_decision_files: missingDecisionFiles, duy_tan_records: audit.decisions.duy_tan_records, case_drawings: drawingChecks, scenarios: scenarios.length, missing_scenario_sources: sourceLinkChecks.filter(row => row.missingLocalTargets.length) }, null, 2));
if (audit.legal.missing_referenced_files.length || missingDecisionFiles.length || !audit.decisions.record_count_matches_display || drawingChecks.some(row => !row.hashMatches) || sourceLinkChecks.some(row => row.missingLocalTargets.length)) process.exitCode = 1;
