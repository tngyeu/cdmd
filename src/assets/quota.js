import { normalize, compareRows, quotaScenario } from './decision-math.mjs';
import { $, $$, escapeHTML as e, fmt, initFilters, readFilters, updateURL, downloadCSV, setSortState } from './ui.js';
const quotas = JSON.parse($('#quota-data').textContent), form = $('#quota-filters');
let sorted = [], sort = { key: 'locality', direction: 'ascending' };
initFilters(form);
function renderModel() {
  const mean = Number($('#mean-area').value), share = Number($('#quota-share').value), years = Number($('#quota-years').value);
  const scenario = quotaScenario(50.26, mean, years, share);
  $('#mean-output').value = fmt(mean);
  for (const button of $$('[data-mean]')) { const active = Number(button.dataset.mean) === mean; button.classList.toggle('is-active', active); button.setAttribute('aria-pressed', String(active)); }
  if (!scenario) return;
  $('#model-cases').textContent = fmt(scenario.cases);
  $('#model-monthly').textContent = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2 }).format(scenario.monthly);
  $('#model-formula').textContent = `${fmt(scenario.hectares * 10000)} m² ÷ ${fmt(mean)} m² = ${fmt(scenario.cases)} trường hợp (lấy phần nguyên).`;
  const percent = scenario.cases / 8934 * 100;
  $('#household-fill').style.width = `${Math.min(100, percent)}%`;
  $('#household-comparison').textContent = `${fmt(scenario.cases)} trường hợp tương đương khoảng ${new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2 }).format(percent)}% số hộ.`;
}
$('#quota-model').addEventListener('input', renderModel);
for (const button of $$('[data-mean]')) button.addEventListener('click', () => { $('#mean-area').value = button.dataset.mean; renderModel(); });
function renderTable() {
  const filters = readFilters(form), query = normalize(filters.q).trim();
  sorted = quotas.filter(row => !query || normalize(row.locality).includes(query)).map(row => ({ locality: row.locality, ...row[filters.land], appendix: row.appendix, pdf_page: row.pdf_page, land_code: filters.land }));
  sorted.sort((a, b) => compareRows(a, b, sort.key, sort.direction));
  $('#quota-rows').innerHTML = sorted.map(row => `<tr${row.locality === 'Phường Duy Tân' ? ' class="highlight-row"' : ''}><td>${e(row.locality)}</td><td class="num">${fmt(row.baseline_ha)}</td><td class="num">${fmt(row.target_ha)}</td><td class="num">${Number(row.change_ha) > 0 ? '+' : ''}${fmt(row.change_ha)}</td><td><a href="/tai-lieu/quy_hoach/3279_2026_phu_luc_129.pdf#page=${row.pdf_page}" target="_blank" rel="noopener">PL ${row.appendix} · tr. ${row.pdf_page} ↗</a></td></tr>`).join('') || '<tr><td colspan="5">Không có địa phương khớp từ khóa. Thử tên ngắn hơn hoặc đặt lại bộ lọc.</td></tr>';
  $('#quota-count').textContent = `${sorted.length} / 129 địa phương · ${filters.land} · Đơn vị: ha`;
  setSortState($$('[data-quota-sort]'), sort.key, sort.direction, 'quotaSort');
  updateURL({ ...filters, land: filters.land === 'ODT' ? '' : filters.land });
}
form.addEventListener('input', renderTable); form.addEventListener('reset', () => requestAnimationFrame(renderTable));
for (const button of $$('[data-quota-sort]')) button.addEventListener('click', () => { const key = button.dataset.quotaSort; sort = { key, direction: sort.key === key && sort.direction === 'ascending' ? 'descending' : 'ascending' }; renderTable(); });
$('#export-quota').addEventListener('click', () => downloadCSV('chi_tieu_dat_o_bo_loc.csv', sorted, ['locality', 'land_code', 'baseline_ha', 'target_ha', 'change_ha', 'status', 'appendix', 'pdf_page']));
renderModel(); renderTable();
