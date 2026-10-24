export const $ = (selector, parent = document) => parent.querySelector(selector);
export const $$ = (selector, parent = document) => [...parent.querySelectorAll(selector)];
export const escapeHTML = value => String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
export const fmt = value => value == null || value === '' ? '—' : new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 3 }).format(Number(value));
export const dateVi = value => /^\d{4}-\d{2}-\d{2}$/.test(value || '') ? value.split('-').reverse().join('/') : 'Chưa rõ';
export function readFilters(form) { return Object.fromEntries(new FormData(form)); }
export function initFilters(form, extra = {}) {
  const params = new URLSearchParams(location.search);
  for (const control of [...form.elements]) {
    if (!control.name || !params.has(control.name)) continue;
    const value = params.get(control.name);
    if (control.tagName !== 'SELECT' || [...control.options].some(option => option.value === value)) control.value = value;
  }
  for (const [key, control] of Object.entries(extra)) if (params.has(key) && [...control.options].some(option => option.value === params.get(key))) control.value = params.get(key);
}
export function updateURL(values) {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(values)) if (value) params.set(key, value);
  history.replaceState(null, '', `${location.pathname}${params.size ? `?${params}` : ''}${location.hash}`);
}
export function downloadCSV(name, rows, fields) {
  const quote = value => {
    let string = String(value ?? '');
    // Preserve numeric negatives; prevent text cells from becoming spreadsheet formulas.
    if (/^[=+@-]/.test(string) && !/^-?\d+(\.\d+)?$/.test(string)) string = `'${string}`;
    return `"${string.replaceAll('"', '""')}"`;
  };
  const text = '\uFEFF' + [fields.map(quote).join(','), ...rows.map(row => fields.map(key => quote(row[key])).join(','))].join('\r\n');
  const url = URL.createObjectURL(new Blob([text], { type: 'text/csv;charset=utf-8' }));
  const anchor = document.createElement('a'); anchor.href = url; anchor.download = name; anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
export function setSortState(buttons, key, direction, attribute) {
  for (const button of buttons) {
    const active = button.dataset[attribute] === key;
    button.setAttribute('aria-pressed', String(active));
    const header = button.closest('th');
    if (header && !active) header.removeAttribute('aria-sort');
  }
  const current = buttons.find(button => button.dataset[attribute] === key);
  current?.closest('th')?.setAttribute('aria-sort', direction);
}
