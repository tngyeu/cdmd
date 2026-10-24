import { normalize } from './decision-math.mjs';
const validDate = value => /^\d{4}-\d{2}-\d{2}$/.test(value || '') ? value : null;
export function recentStart(cutoff) {
  const date = new Date(`${cutoff}T00:00:00Z`);
  date.setUTCFullYear(date.getUTCFullYear() - 1);
  return date.toISOString().slice(0, 10);
}
export function compareLegal(a, b, order = 'newest') {
  if (order === 'number') return (a.number || '').localeCompare(b.number || '', 'vi', { numeric: true });
  const left = validDate(a.issued_date), right = validDate(b.issued_date);
  if (left === null || right === null) return left ? -1 : right ? 1 : (a.number || '').localeCompare(b.number || '', 'vi', { numeric: true });
  return (order === 'oldest' ? left.localeCompare(right) : right.localeCompare(left)) || (a.number || '').localeCompare(b.number || '', 'vi', { numeric: true });
}
export function filterLegal(rows, filters = {}, cutoff = '2026-10-19') {
  const query = normalize(filters.q).trim(), start = recentStart(cutoff);
  return rows.filter(row => {
    const date = validDate(row.issued_date);
    const text = row.search || [row.number, row.title, row.summary, row.practical_relevance, row.relationship, row.relevant_articles, row.notes].join(' ');
    return (!query || normalize(text).includes(query)) && (!filters.topic || row.topic === filters.topic)
      && (!filters.evidence || row.evidenceTone === filters.evidence || row.evidence?.tone === filters.evidence)
      && (!filters.year || date?.startsWith(filters.year))
      && (filters.view === 'all' || (filters.view === 'undated' ? !date : date && date >= start && date <= cutoff));
  });
}
