import fs from 'node:fs';
import path from 'node:path';
import { moduleDir, renderMarkdown } from './content.mjs';

export function getReplyKit() {
  const file = path.join(moduleDir, 'reports', 'bo_phan_hoi_van_ban.md');
  const text = fs.readFileSync(file, 'utf8');
  const sections = text.split(/(?=^## )/m);
  const scenarios = sections.filter(section => /^## S\d{2} /.test(section)).map(section => {
    const [, id, title] = section.match(/^## (S\d{2}) (.+)/);
    const parts = new Map(section.split(/(?=^### )/m).slice(1).map(part => {
      const [heading, ...lines] = part.split('\n');
      return [heading.replace(/^### /, '').trim(), lines.join('\n').trim()];
    }));
    for (const key of ['Khi dùng', 'Điểm cần đối chiếu', 'Dữ liệu và giới hạn', 'Cần bổ sung', 'Đoạn phản hồi', 'Nguồn']) {
      if (!parts.get(key)) throw new Error(`${id}: thiếu ${key}`);
    }
    const render = key => renderMarkdown(parts.get(key), file, `${id}-${key}`).html;
    return {
      id, title, draftTitle: parts.get('Tiêu đề trong văn bản') || title, trigger: parts.get('Khi dùng'),
      check: render('Điểm cần đối chiếu'), evidence: render('Dữ liệu và giới hạn'),
      needed: render('Cần bổ sung'), sources: render('Nguồn'),
      paragraphs: parts.get('Đoạn phản hồi').split(/\n\s*\n/).map(p => p.trim())
    };
  });
  if (new Set(scenarios.map(item => item.id)).size !== scenarios.length) throw new Error('Trùng mã kịch bản');
  const evidence = sections.find(section => section.startsWith('## Dữ liệu đã có'));
  return { scenarios, evidence: renderMarkdown(evidence, file, 'reply-evidence').html };
}
