import { filterDecisions, compareRows, aggregateLocalities, normalize, parseJSON } from './decision-math.mjs';
import { $, $$, escapeHTML as e, fmt, dateVi, readFilters, initFilters, updateURL, downloadCSV, setSortState } from './ui.js';
const rows = JSON.parse($('#decision-data').textContent), localities = JSON.parse($('#locality-data').textContent);
const form = $('#decision-filters');
let filtered = [], displayedSummary = [], sort = { key: 'issue_date', direction: 'descending' }, summarySort = { key: 'records', direction: 'descending' };
initFilters(form);
const landNames = { CLN: 'Cây lâu năm', ODT: 'Đất ở đô thị', ONT: 'Đất ở nông thôn', NTS: 'Nuôi trồng thủy sản', HNK: 'Cây hằng năm khác', LUA: 'Đất trồng lúa', LUC: 'Chuyên trồng lúa', BHK: 'Cây hằng năm khác', DAT_O: 'Đất ở' };
const land = code => `<span title="${e(landNames[code] || code)}">${e(code || '—')}</span>`;
const sourceLink = (url, label) => url ? `<a href="${e(url)}" target="_blank" rel="noopener noreferrer">${label} ↗</a>` : '';
function detailHTML(row) {
  const components = parseJSON(row.components_json), notes = parseJSON(row.detail_notes_json), initial = parseJSON(row.initial_land_json, {}), post = parseJSON(row.post_land_json, {});
  const label = row.detail_status === 'visual_reviewed' ? 'Đã đọc ảnh PDF' : row.detail_status === 'text_extracted' ? 'Đọc từ lớp chữ PDF' : row.local_pdf ? 'PDF cần đọc tiếp' : 'Chưa có PDF';
  const breakdown = object => Object.entries(object).map(([key, value]) => `${e(key)}: ${fmt(value)} m²`).join('; ');
  return `<details><summary>${label}${components.length > 1 ? ` · ${components.length} phần` : ''}</summary>
    ${components.length ? `<ul>${components.map(part => `<li><strong>${fmt(part.area_m2)} m²</strong> ${e(part.land_before)} → ${e(part.land_after)}</li>`).join('')}</ul>` : ''}
    ${row.parcel_area_m2 ? `<p><strong>Tổng thửa:</strong> ${fmt(row.parcel_area_m2)} m².</p>` : ''}
    ${Object.keys(initial).length ? `<p><strong>Trước chuyển:</strong> ${breakdown(initial)}.</p>` : ''}
    ${Object.keys(post).length ? `<p><strong>Sau chuyển theo tệp:</strong> ${breakdown(post)}.</p>` : ''}
    ${row.term_after ? `<p>${e(row.term_after)}</p>` : ''}
    ${row.land_price_vnd_m2 ? `<p><strong>Giá ghi trong quyết định:</strong> ${fmt(row.land_price_vnd_m2)} đồng/m². Chưa phải tổng tiền sử dụng đất phải nộp.</p>` : ''}
    ${notes.length ? `<ul>${notes.map(note => `<li>${e(note)}</li>`).join('')}</ul>` : ''}
    <p>${e(row.notes)}</p><p class="small">${e(row.issuing_authority)}</p>
    ${row.local_pdf && row.detail_pdf_pages ? `<p>${row.detail_pdf_pages.split(',').map(page => sourceLink(`${row.local_pdf}#page=${encodeURIComponent(page.trim())}`, `PDF trang ${e(page.trim())}`)).join(' · ')}</p>` : ''}
    <p class="small">Đọc nội dung: ${dateVi(row.detail_checked_on)} · Kiểm tra nguồn: ${dateVi(row.checked_on)}</p></details>`;
}
function renderRow(row) {
  const status = row.status === 'official_pdf' ? '<span class="badge green">PDF khớp số/ngày</span>' : row.status === 'conflict' ? '<span class="badge amber">Xung đột định danh</span>' : '<span class="badge blue">Thông tin trang nguồn</span>';
  const areaStatus = row.area_status === 'verified_pdf_identity' ? 'Diện tích đã xác minh' : row.area_status === 'official_attachment_identity_pending' ? 'Diện tích chờ khớp PDF' : row.area_status === 'source_internal_area_conflict' || row.area_status === 'shared_pdf_excluded_from_verified_totals' ? 'Diện tích bị loại khỏi tổng' : 'Diện tích cần đọc / đối chiếu';
  return `<tr><td><strong>${e(row.decision_number || 'Chưa rõ số')}</strong><small>${dateVi(row.issue_date)}</small></td><td>${e(row.locality)}</td><td>${land(row.land_before)}</td><td>${land(row.land_after)}</td>
    <td class="num"><strong>${fmt(row.area_m2)}</strong><small>Thửa: ${fmt(row.parcel_area_m2)}</small>${row.residential_conversion_m2 && Number(row.residential_conversion_m2) !== Number(row.area_m2) ? `<small>Sang đất ở: ${fmt(row.residential_conversion_m2)}</small>` : ''}</td>
    <td>${status}<small>${areaStatus}</small></td><td>${sourceLink(row.source_page, 'Trang nguồn')}${sourceLink(row.local_pdf, 'PDF trong kho')}${detailHTML(row)}</td></tr>`;
}
function summaryCells(row, isTotal = false) {
  const value = key => row.known_area_records ? fmt(row[key]) : '—';
  return `<td>${isTotal ? 'Tổng các dòng đang hiển thị' : `<button type="button" class="locality-button" data-select-locality="${e(row.locality)}">${e(row.locality)}</button>`}</td><td class="num">${fmt(row.records)}</td><td class="num"><strong>${value('known_area_m2')}</strong><small>${row.known_area_records} QĐ có diện tích</small></td><td class="num">${value('residential_area_m2')}</td><td class="num">${value('area_m2')}</td><td class="num">${value('pending_area_m2')}</td><td class="num">${row.missing_area_records}${row.excluded_area_records ? `<small>${row.excluded_area_records} xung đột / mâu thuẫn</small>` : ''}</td>`;
}
function renderSummary() {
  const filters = readFilters(form), query = normalize($('#summary-query').value).trim(), showEmpty = $('#summary-empty').checked;
  const names = localities.filter(name => !filters.locality || name === filters.locality);
  displayedSummary = aggregateLocalities(filtered, filters.type, names).filter(row => (row.records || showEmpty || filters.locality) && (!query || normalize(row.locality).includes(query)));
  displayedSummary.sort((a, b) => compareRows(a, b, summarySort.key, summarySort.direction));
  $('#summary-rows').innerHTML = displayedSummary.map(row => `<tr>${summaryCells(row)}</tr>`).join('') || '<tr><td colspan="7">Chưa có địa phương phù hợp bộ lọc. Có thể bật “Hiện nơi chưa có bản ghi”.</td></tr>';
  const total = { locality: 'Tổng', records: 0, known_area_records: 0, known_area_m2: 0, residential_area_m2: 0, area_m2: 0, pending_area_m2: 0, missing_area_records: 0, excluded_area_records: 0, unread_area_records: 0 };
  for (const row of displayedSummary) for (const key of Object.keys(total)) if (key !== 'locality') total[key] = Math.round((total[key] + Number(row[key])) * 1000) / 1000;
  $('#summary-total').innerHTML = `<tr>${summaryCells(total, true)}</tr>`;
  $('#summary-count').textContent = `${displayedSummary.length} địa phương · ${total.records} bản ghi · ${total.known_area_records} bản ghi đủ số liệu để cộng diện tích`;
  setSortState($$('[data-summary-sort]'), summarySort.key, summarySort.direction, 'summarySort');
}
function render() {
  const filters = readFilters(form);
  filtered = filterDecisions(rows, { ...filters, query: filters.q });
  filtered.sort((a, b) => compareRows(a, b, sort.key, sort.direction));
  $('#decision-rows').innerHTML = filtered.map(renderRow).join('') || '<tr><td colspan="7">Không có quyết định phù hợp. Thử bỏ bớt bộ lọc hoặc tìm tên địa phương ngắn hơn.</td></tr>';
  $('#decision-count').textContent = `${filtered.length} / ${rows.length} bản ghi · Hiển thị toàn bộ kết quả lọc`;
  setSortState($$('[data-sort]'), sort.key, sort.direction, 'sort');
  updateURL(filters); renderSummary();
}
let debounce;
form.addEventListener('input', event => { clearTimeout(debounce); if (event.target.type === 'search') debounce = setTimeout(render, 120); else render(); });
form.addEventListener('reset', () => { clearTimeout(debounce); sort = { key: 'issue_date', direction: 'descending' }; requestAnimationFrame(render); });
for (const button of $$('[data-sort]')) button.addEventListener('click', () => { const key = button.dataset.sort; sort = { key, direction: sort.key === key && sort.direction === 'ascending' ? 'descending' : 'ascending' }; render(); });
for (const button of $$('[data-summary-sort]')) button.addEventListener('click', () => { const key = button.dataset.summarySort; summarySort = { key, direction: summarySort.key === key && summarySort.direction === 'ascending' ? 'descending' : 'ascending' }; renderSummary(); });
$('#summary-query').addEventListener('input', renderSummary); $('#summary-empty').addEventListener('change', renderSummary);
$('#summary-rows').addEventListener('click', event => { const button = event.target.closest('[data-select-locality]'); if (button) { form.elements.locality.value = button.dataset.selectLocality; render(); $('#danh-sach').scrollIntoView({ block: 'start', behavior: 'smooth' }); } });
$('#export-decisions').addEventListener('click', () => downloadCSV('quyet_dinh_bo_loc.csv', filtered, ['decision_number', 'issue_date', 'locality', 'issuing_authority', 'land_before', 'land_after', 'area_m2', 'parcel_area_m2', 'residential_conversion_m2', 'verification_status', 'pdf_identity_status', 'area_status', 'source_page', 'pdf_url', 'local_pdf', 'notes']));
$('#export-summary').addEventListener('click', () => downloadCSV('thong_ke_dia_phuong_bo_loc.csv', displayedSummary, ['locality', 'records', 'known_area_records', 'known_area_m2', 'residential_area_m2', 'area_m2', 'pending_area_m2', 'missing_area_records', 'excluded_area_records', 'unread_area_records']));
render();
