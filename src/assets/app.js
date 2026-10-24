import { normalize } from './decision-math.mjs';
import { $, $$, escapeHTML } from './ui.js';

const navButton = $('[data-toggle-nav]');
const sidebar = $('#sidebar'), mobile = window.matchMedia('(max-width: 720px)');
function syncNav() { sidebar.inert = mobile.matches && !document.body.classList.contains('nav-open'); }
function closeNav() { document.body.classList.remove('nav-open'); navButton?.setAttribute('aria-expanded', 'false'); syncNav(); }
navButton?.addEventListener('click', () => {
  const open = document.body.classList.toggle('nav-open');
  navButton.setAttribute('aria-expanded', String(open));
  syncNav(); if (open) $('.sidebar [data-close-nav]')?.focus();
});
for (const button of $$('[data-close-nav]')) button.addEventListener('click', () => { closeNav(); navButton?.focus(); });
for (const link of $$('.sidebar a')) link.addEventListener('click', closeNav);
window.addEventListener('keydown', event => {
  if (!document.body.classList.contains('nav-open')) return;
  if (event.key === 'Escape') { closeNav(); navButton?.focus(); }
  if (event.key === 'Tab' && mobile.matches) {
    const focusable = $$('.sidebar a, .sidebar button');
    const first = focusable[0], last = focusable.at(-1);
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
  }
});
mobile.addEventListener('change', () => { closeNav(); syncNav(); }); syncNav();
for (const button of $$('[data-print]')) button.addEventListener('click', () => window.print());

const dialog = $('#global-search'), query = $('#global-query'), results = $('#global-results'), status = $('#search-status');
let searchData, loadPromise;
async function ensureSearch() {
  if (searchData) return;
  loadPromise ||= fetch('/assets/search-index.json').then(response => {
    if (!response.ok) throw new Error('search');
    return response.json();
  }).then(data => { searchData = data.map(item => ({ ...item, normalized: normalize(`${item.title} ${item.text}`) })); });
  try { await loadPromise; renderSearch(); } catch { loadPromise = null; status.textContent = 'Chưa tải được mục lục. Hãy thử lại hoặc tra trực tiếp bằng menu bên trái.'; }
}
function renderSearch() {
  if (!searchData) return;
  const words = normalize(query.value).trim().split(/\s+/).filter(Boolean);
  const matches = words.length ? searchData.filter(item => words.every(word => item.normalized.includes(word))).sort((a, b) => {
    const score = item => words.every(word => normalize(item.title).includes(word)) ? 0 : 1;
    return score(a) - score(b);
  }) : searchData.filter(item => item.type === 'Trang');
  status.textContent = words.length ? `${matches.length} kết quả${matches.length > 40 ? ' · Hiện 40 kết quả đầu, thêm từ khóa để thu hẹp' : ''}` : 'Chọn một trang hoặc tìm tên văn bản, số quyết định, tình huống.';
  results.innerHTML = matches.slice(0, 40).map(item => `<a class="global-result" href="${escapeHTML(item.url)}"><span>${escapeHTML(item.type)}</span><div><strong>${escapeHTML(item.title)}</strong><small>${escapeHTML(item.excerpt || item.text)}</small></div></a>`).join('') || '<div class="empty-state"><p>Thử từ khóa ngắn hơn hoặc tên địa phương.</p></div>';
}
function openSearch() { if (dialog.open) return; closeNav(); dialog.showModal(); query.focus(); ensureSearch(); }
for (const button of $$('[data-open-search]')) button.addEventListener('click', openSearch);
$('[data-close-search]')?.addEventListener('click', () => dialog.close());
dialog?.addEventListener('click', event => { if (event.target === dialog) { const rect = dialog.getBoundingClientRect(); if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close(); } });
query?.addEventListener('input', renderSearch);
window.addEventListener('keydown', event => { if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') { event.preventDefault(); openSearch(); } });

function revealHash() {
  if (!location.hash) return;
  let target; try { target = document.getElementById(decodeURIComponent(location.hash.slice(1))); } catch { return; }
  if (!target) return;
  if (target.tagName === 'DETAILS') target.open = true;
  let parent = target.parentElement;
  while (parent) { if (parent.tagName === 'DETAILS') parent.open = true; parent = parent.parentElement; }
}
revealHash(); window.addEventListener('hashchange', revealHash);

const tocLinks = $$('.toc-panel nav a');
if (tocLinks.length && 'IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    const visible = entries.filter(entry => entry.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
    if (!visible.length) return;
    const id = visible[0].target.id;
    for (const link of tocLinks) link.classList.toggle('is-active', link.hash === `#${id}`);
  }, { rootMargin: '-85px 0px -65% 0px', threshold: 0 });
  for (const link of tocLinks) { const target = document.getElementById(link.hash.slice(1)); if (target) observer.observe(target); }
}
