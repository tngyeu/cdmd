import fs from 'node:fs';
import path from 'node:path';
import { date, escape, fmt, jsonScript, sourceURL } from './lib/content.mjs';

const icons = {
  home: '<path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1Z"/>',
  route: '<circle cx="5" cy="5" r="2"/><circle cx="19" cy="19" r="2"/><path d="M7 5h8a4 4 0 0 1 0 8H9a4 4 0 0 0 0 8h7"/>',
  folder: '<path d="M3 7V5a1 1 0 0 1 1-1h5l2 3h9a1 1 0 0 1 1 1v11a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1Z"/>',
  book: '<path d="M12 5c-3-2-6-2-10-1v15c4-1 7-1 10 1 3-2 6-2 10-1V4c-4-1-7-1-10 1Z"/><path d="M12 5v15"/>',
  table: '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M3 15h18M9 3v18"/>',
  chart: '<path d="M3 3v18h18M7 16v-5m5 5V7m5 9V4"/>',
  help: '<circle cx="12" cy="12" r="9"/><path d="M9 9a3 3 0 0 1 6 0c0 2-3 2-3 5m0 3h.01"/>',
  search: '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
  arrow: '<path d="M5 12h14m-5-5 5 5-5 5"/>',
  chevron: '<path d="m9 5 7 7-7 7"/>',
  check: '<path d="m5 12 4 4L19 6"/>',
  map: '<path d="m9 3-6 3v15l6-3 6 3 6-3V3l-6 3-6-3Zm0 0v15m6-12v15"/>',
  calculator: '<rect x="5" y="2" width="14" height="20" rx="2"/><path d="M8 6h8M8 11h1m6 0h1m-8 4h1m6 0h1m-8 4h1m6 0h1"/>',
  shield: '<path d="m12 2 9 4v6c0 5-9 10-9 10S3 17 3 12V6l9-4Z"/><path d="m8 12 3 3 5-6"/>',
  layers: '<path d="m12 2 10 5-10 5L2 7l10-5Zm-10 10 10 5 10-5M2 17l10 5 10-5"/>',
  download: '<path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/>',
  external: '<path d="M14 3h7v7m0-7L10 14M10 3H3v18h18v-7"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v6m0-10h.01"/>',
  menu: '<path d="M3 6h18M3 12h18M3 18h18"/>',
  close: '<path d="m6 6 12 12M6 18 18 6"/>',
  print: '<path d="M6 9V3h12v6M6 17H3V9h18v8h-3M6 14h12v7H6Z"/>',
  leaf: '<path d="M20 3C5 1 1 9 5 16c7 5 16-1 15-13Z"/><path d="m4 21 11-12"/>'
};
export default function (config) {
  config.addFilter('fmt', fmt);
  config.addFilter('dateVi', date);
  config.addFilter('jsonScript', jsonScript);
  config.addFilter('sourceURL', sourceURL);
  config.addFilter('escapeText', escape);
  config.addShortcode('icon', (name, cls = '') => `<svg class="icon ${escape(cls)}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${icons[name] || icons.book}</svg>`);
  config.addPassthroughCopy({ 'src/assets': 'assets', 'lib/decision-math.mjs': 'assets/decision-math.mjs', 'lib/legal-library.mjs': 'assets/legal-library.mjs', 'ho_so_phap_ly_dat_dai_ninh_binh/documents': 'tai-lieu' });
  // Match root documents with a glob so parentheses in filenames stay literal;
  // never copy the research folder's temporary render/OCR directories.
  config.addPassthroughCopy({ 'nghien_cuu_quy_trinh/*.{pdf,docx}': 'tai-lieu/quy-trinh' });
  for (const file of fs.readdirSync('ho_so_phap_ly_dat_dai_ninh_binh/data').filter(name => /\.(csv|json)$/i.test(name))) config.addPassthroughCopy({ [path.join('ho_so_phap_ly_dat_dai_ninh_binh/data', file)]: `du-lieu/${file}` });
  config.addPassthroughCopy({ 'Don_de_nghi_giai_quyet_ho_so_chuyen_muc_dich_su_dung_dat.docx': 'tai-lieu/mau-don-de-nghi.docx' });
  config.addWatchTarget('./ho_so_phap_ly_dat_dai_ninh_binh/reports/');
  config.addWatchTarget('./ho_so_phap_ly_dat_dai_ninh_binh/data/');
  config.addWatchTarget('./nghien_cuu_quy_trinh/*.md');
  config.setServerPassthroughCopyBehavior('passthrough');
  return { dir: { input: 'src', output: '_site', includes: '_includes', data: '_data' }, templateFormats: ['njk', '11ty.js'], htmlTemplateEngine: 'njk' };
}
