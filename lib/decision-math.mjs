export const normalize = value => String(value ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/g, 'd').replace(/Đ/g, 'D').toLowerCase();
export const number = value => value == null || String(value).trim() === '' || !Number.isFinite(Number(value)) ? null : Number(value);
export function parseJSON(value, fallback = []) { try { return JSON.parse(value || '') ?? fallback; } catch { return fallback; } }
export function decisionStatus(row) { return row.pdf_identity_status === 'shared_pdf_conflict' ? 'conflict' : row.verification_status; }
export function filterDecisions(rows, filters = {}) {
  const query = normalize(filters.query).trim();
  return rows.filter(row => {
    const components = parseJSON(row.components_json);
    return (!query || normalize([row.decision_number, row.locality, row.land_before, row.land_after, row.notes].join(' ')).includes(query))
      && (!filters.locality || row.locality === filters.locality)
      && (!filters.month || row.issue_date.startsWith(filters.month))
      && (!filters.type || row.conversion_group === filters.type || components.some(c => `${c.land_before}->${c.land_after}` === filters.type))
      && (!filters.status || decisionStatus(row) === filters.status)
      && (!filters.detail || (filters.detail === 'parcel' && number(row.parcel_area_m2) !== null)
        || (filters.detail === 'visual' && row.detail_status === 'visual_reviewed')
        || (filters.detail === 'components' && components.length > 0)
        || (filters.detail === 'mixed' && components.length > 1)
        || (filters.detail === 'issues' && (parseJSON(row.detail_flags_json).length > 0 || ['source_internal_area_conflict', 'shared_pdf_excluded_from_verified_totals'].includes(row.area_status))));
  });
}
const collator = new Intl.Collator('vi', { numeric: true, sensitivity: 'base' });
export function compareRows(a, b, key, direction = 'ascending') {
  const numeric = ['area_m2', 'parcel_area_m2', 'records', 'known_area_m2', 'residential_area_m2', 'pending_area_m2', 'missing_area_records', 'baseline_ha', 'target_ha', 'change_ha'].includes(key);
  const areaSummary = ['known_area_m2', 'residential_area_m2', 'pending_area_m2'].includes(key) || (key === 'area_m2' && 'known_area_records' in a);
  const read = row => areaSummary && !row.known_area_records ? null : numeric ? number(row[key]) : row[key] || null;
  const left = read(a), right = read(b);
  if (left === null || right === null) {
    if (left !== null) return -1;
    if (right !== null) return 1;
  } else {
    const result = numeric ? left - right : collator.compare(left, right);
    if (result) return direction === 'ascending' ? result : -result;
  }
  return collator.compare(a.locality || '', b.locality || '') || collator.compare(a.decision_id || '', b.decision_id || '');
}
// Accumulate thousandths of a square metre, matching the research dataset.
const units = value => Math.round(Number(value || 0) * 1000);
export function aggregateLocalities(rows, type = '', localities = []) {
  const names = localities.length ? localities : [...new Set(rows.map(r => r.locality))];
  const groups = new Map(names.map(locality => [locality, { locality, records: 0, known_area_records: 0, known_area_m2: 0, residential_area_m2: 0, area_m2: 0, pending_area_m2: 0, missing_area_records: 0, excluded_area_records: 0, unread_area_records: 0 }]));
  for (const row of rows) {
    const group = groups.get(row.locality);
    if (!group) continue;
    group.records++;
    const conflict = row.pdf_identity_status === 'shared_pdf_conflict' || row.area_status === 'source_internal_area_conflict';
    const usable = !conflict && number(row.area_m2) !== null && ['verified_pdf_identity', 'official_attachment_identity_pending'].includes(row.area_status);
    if (!usable) { group.missing_area_records++; group[conflict ? 'excluded_area_records' : 'unread_area_records']++; continue; }
    let total = units(row.area_m2), home = units(row.residential_conversion_m2 || (['ODT', 'ONT', 'DAT_O'].includes(row.land_after) ? row.area_m2 : 0));
    if (type && type.includes('->')) {
      const parts = parseJSON(row.components_json).filter(c => `${c.land_before}->${c.land_after}` === type);
      if (parts.length) {
        total = parts.reduce((sum, c) => sum + units(c.area_m2), 0);
        home = parts.reduce((sum, c) => sum + (['ODT', 'ONT', 'DAT_O'].includes(c.land_after) ? units(c.area_m2) : 0), 0);
      } else if (row.conversion_group !== type) { group.missing_area_records++; group.unread_area_records++; continue; }
    }
    group.known_area_records++;
    group.known_area_m2 += total;
    group.residential_area_m2 += home;
    group[row.area_status === 'verified_pdf_identity' ? 'area_m2' : 'pending_area_m2'] += total;
  }
  return [...groups.values()].map(row => Object.fromEntries(Object.entries(row).map(([key, value]) => [key, ['known_area_m2', 'residential_area_m2', 'area_m2', 'pending_area_m2'].includes(key) ? value / 1000 : value])));
}
export function quotaScenario(gainHa, meanM2, years = 5, share = 100) {
  if (![gainHa, meanM2, years, share].every(Number.isFinite) || meanM2 <= 0 || years <= 0 || gainHa < 0 || share < 0 || share > 100) return null;
  const cases = gainHa * 10000 * share / 100 / meanM2;
  return { cases: Math.floor(cases), annual: cases / years, monthly: cases / years / 12, hectares: gainHa * share / 100 };
}
