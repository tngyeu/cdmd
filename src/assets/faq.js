import { normalize } from './decision-math.mjs';
import { $, $$, initFilters, readFilters, updateURL } from './ui.js';
const form = $('#faq-filters');
const items = $$('.faq-item').map(item => ({ item, text: normalize(item.textContent) }));
initFilters(form);
function render() {
  const filters = readFilters(form), query = normalize(filters.q).trim();
  let count = 0;
  for (const { item, text } of items) { item.hidden = !!((query && !text.includes(query)) || (filters.topic && item.dataset.topic !== filters.topic)); if (!item.hidden) count++; }
  $('#faq-count').textContent = `${count} / ${items.length} tình huống`;
  $('#faq-empty').hidden = count > 0;
  updateURL(filters);
}
form.addEventListener('input', render); form.addEventListener('reset', () => requestAnimationFrame(render));
$('#faq-expand').addEventListener('click', () => { for (const { item } of items) if (!item.hidden) item.open = true; });
$('#faq-collapse').addEventListener('click', () => { for (const { item } of items) item.open = false; });
function openHash() {
  const item = document.getElementById(location.hash.slice(1));
  if (!item?.classList.contains('faq-item')) return;
  if (item.hidden) { form.reset(); render(); }
  item.open = true;
  requestAnimationFrame(() => item.scrollIntoView({ block: 'start' }));
}
render(); openHash(); window.addEventListener('hashchange', openHash);
