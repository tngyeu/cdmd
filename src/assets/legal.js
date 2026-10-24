import { compareLegal, filterLegal, recentStart } from './legal-library.mjs';
import { $, $$, initFilters, readFilters, updateURL, dateVi } from './ui.js';
const form = $('#legal-filters'), sort = $('#legal-sort'), list = $('#legal-rows');
const documents = JSON.parse($('#legal-data').textContent);
const rows = new Map($$('.legal-record').map(row => [row.dataset.id, row]));
const cutoff = $('#legal-data').dataset.cutoff;
initFilters(form, { sort });
if (!['recent', 'all', 'undated'].includes(form.elements.view.value)) form.elements.view.value = 'recent';
function render() {
  const filters = readFilters(form);
  const matches = filterLegal(documents, filters, cutoff).sort((a, b) => compareLegal(a, b, sort.value));
  for (const row of rows.values()) row.hidden = true;
  for (const doc of matches) { const row = rows.get(doc.document_id); row.hidden = false; list.append(row); }
  for (const button of $$('.legal-view-tabs [data-view]')) button.setAttribute('aria-pressed', String(button.dataset.view === filters.view));
  $('#legal-count').textContent = `${matches.length} / ${documents.length} văn bản`;
  $('#legal-scope').textContent = filters.view === 'recent' ? `Từ ${dateVi(recentStart(cutoff))} đến ${dateVi(cutoff)} · Văn bản nền cũ được thu gọn.` : filters.view === 'undated' ? 'Thiếu ngày ban hành đã xác định; không dùng ngày hội nghị hoặc ngày tải thay thế.' : 'Toàn bộ chỉ mục · Ngày chưa rõ luôn ở cuối khi sắp xếp theo ngày.';
  $('#legal-empty').hidden = matches.length > 0;
  $('#legal-older-note').hidden = filters.view !== 'recent';
  $('#legal-sort-arrow').textContent = sort.value === 'oldest' ? '↑' : sort.value === 'newest' ? '↓' : '↕';
  const header = $('#legal-date-sort').closest('th');
  if (sort.value === 'number') header.removeAttribute('aria-sort'); else header.setAttribute('aria-sort', sort.value === 'oldest' ? 'ascending' : 'descending');
  $('#legal-date-sort').setAttribute('aria-label', `Ngày ban hành: sắp xếp ${sort.value === 'newest' ? 'cũ nhất trước' : 'mới nhất trước'}`);
  updateURL({ ...filters, view: filters.view === 'recent' ? '' : filters.view, sort: sort.value === 'newest' ? '' : sort.value });
}
form.addEventListener('input', event => {
  if (event.target.name === 'year' && event.target.value) form.elements.view.value = 'all';
  render();
});
sort.addEventListener('change', render);
$('#legal-date-sort').addEventListener('click', () => { sort.value = sort.value === 'newest' ? 'oldest' : 'newest'; render(); });
form.addEventListener('reset', () => { sort.value = 'newest'; requestAnimationFrame(render); });
for (const button of $$('[data-view]')) button.addEventListener('click', () => { form.elements.view.value = button.dataset.view; if (button.dataset.view !== 'all') form.elements.year.value = ''; render(); });
render();
