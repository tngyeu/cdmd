let decisionSort = {key: 'issue_date', direction: 'descending'};
const decisionCollator = new Intl.Collator('vi', {numeric: true, sensitivity: 'base'});
const decisionSortLabels = {
  decision_number: 'Số quyết định', issue_date: 'Ngày ban hành', locality: 'Địa phương',
  land_before: 'Từ loại đất', land_after: 'Sang loại đất', area_m2: 'Diện tích chuyển',
  parcel_area_m2: 'Tổng diện tích thửa', verification: 'Mức xác minh'
};
function decisionSortValue(row, key) {
  if (key === 'area_m2' || key === 'parcel_area_m2') {
    const value = row[key];
    return value == null || String(value).trim() === '' || !Number.isFinite(Number(value)) ? null : Number(value);
  }
  if (key === 'verification') return {official_pdf: 0, official_metadata: 1, conflict: 2}[decisionStatus(row)] ?? null;
  if (key === 'land_before' || key === 'land_after') return row[key] ? landLabel(row[key]) : null;
  return row[key] || null;
}
function compareDecisions(a, b) {
  const left = decisionSortValue(a, decisionSort.key), right = decisionSortValue(b, decisionSort.key);
  // Unknown values stay at the end in both directions.
  if (left == null || right == null) {
    if (left != null) return -1;
    if (right != null) return 1;
  } else {
    const result = typeof left === 'number' ? left - right : decisionCollator.compare(left, right);
    if (result) return decisionSort.direction === 'ascending' ? result : -result;
  }
  return b.issue_date.localeCompare(a.issue_date)
    || decisionCollator.compare(a.locality, b.locality)
    || decisionCollator.compare(a.decision_number, b.decision_number)
    || decisionCollator.compare(a.decision_id, b.decision_id);
}
function updateDecisionSortHeaders() {
  document.querySelectorAll('.decision-table th').forEach(th => th.removeAttribute('aria-sort'));
  document.querySelectorAll('.decision-table [data-sort]').forEach(button => {
    const active = button.dataset.sort === decisionSort.key;
    button.setAttribute('aria-pressed', String(active));
    button.dataset.direction = active ? decisionSort.direction : '';
    const descendingNext = active ? decisionSort.direction === 'ascending' : button.dataset.sort === 'issue_date';
    const next = descendingNext ? 'giảm dần' : 'tăng dần';
    button.setAttribute('aria-label', decisionSortLabels[button.dataset.sort] + ': sắp xếp ' + next);
    if (active) button.closest('th').setAttribute('aria-sort', decisionSort.direction);
  });
}
