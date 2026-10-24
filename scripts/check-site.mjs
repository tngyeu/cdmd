import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
const root = path.resolve('_site');
assert.ok(fs.existsSync(path.join(root, 'index.html')), 'Run npm run build before checking.');
function walk(dir) { return fs.readdirSync(dir, { withFileTypes: true }).flatMap(entry => entry.isDirectory() ? walk(path.join(dir, entry.name)) : path.join(dir, entry.name)); }
const pages = walk(root).filter(file => file.endsWith('.html') && !file.includes(`${path.sep}tai-lieu${path.sep}`));
const errors = [], ids = new Map();
for (const file of pages) {
  const html = fs.readFileSync(file, 'utf8');
  const pageIds = [...html.matchAll(/\bid="([^"]+)"/g)].map(match => match[1]);
  ids.set(file, new Set(pageIds));
  if (pageIds.length !== new Set(pageIds).size) errors.push(`${path.relative(root, file)}: duplicate HTML id`);
  if (!html.includes('<html lang="vi">')) errors.push(`${file}: missing Vietnamese language`);
  if (!html.includes('id="noi-dung"')) errors.push(`${file}: missing main target`);
  if (html.includes('[object Object]') || html.includes('undefined')) errors.push(`${file}: unresolved data`);
}
let links = 0;
for (const file of pages) {
  const html = fs.readFileSync(file, 'utf8');
  for (const match of html.matchAll(/\b(?:href|src)="([^"]+)"/g)) {
    const href = match[1].replace(/&amp;/g, '&');
    if (!href || /^(https?:|mailto:|tel:|data:)/.test(href)) continue;
    const base = `https://local.test/${path.relative(root, file).split(path.sep).join('/')}`;
    const url = new URL(href, base);
    let target = path.join(root, decodeURIComponent(url.pathname));
    if (url.pathname.endsWith('/')) target = path.join(target, 'index.html');
    links++;
    if (!fs.existsSync(target)) { errors.push(`${path.relative(root, file)} → missing ${decodeURIComponent(url.pathname)}`); continue; }
    if (url.hash && target.endsWith('.html') && ids.has(target) && !ids.get(target).has(decodeURIComponent(url.hash.slice(1)))) errors.push(`${path.relative(root, file)} → missing anchor ${href}`);
  }
}
for (const asset of ['app.js', 'legal.js', 'legal.css', 'legal-library.mjs', 'decisions.js', 'quota.js', 'faq.js', 'ui.js', 'decision-math.mjs', 'site.css', 'search-index.json']) assert.ok(fs.existsSync(path.join(root, 'assets', asset)), `Missing ${asset}`);
const searchIndex = JSON.parse(fs.readFileSync(path.join(root, 'assets/search-index.json'), 'utf8'));
assert.ok(searchIndex.length >= 481, 'Search index lost content');
assert.ok(searchIndex.some(item => item.url === '/phap-ly/van-ban/nb-da08-2026/'), 'User-supplied proposal missing from global search');
if (errors.length) { console.error(errors.join('\n')); process.exitCode = 1; } else console.log(`Verified ${pages.length} pages, ${links} local links, anchors, assets and search index.`);
