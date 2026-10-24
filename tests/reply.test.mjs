import test from 'node:test';
import assert from 'node:assert/strict';
import { getReplyKit } from '../lib/reply-content.mjs';
import { buildReplyDraft, missingReplyFields } from '../src/assets/reply-draft.js';

const { scenarios } = getReplyKit();
test('reply kit is sourced from all eleven complete Markdown scenarios', () => {
  assert.equal(scenarios.length, 11);
  assert.equal(new Set(scenarios.map(item => item.id)).size, 11);
  for (const item of scenarios) {
    assert.ok(item.sources.includes('href='));
    assert.ok(item.needed && item.evidence && item.check);
    assert.equal(item.paragraphs.length, 2);
  }
});
test('50 m² and firm refusal branches stay optional and preserve the original application', () => {
  const partial = scenarios.find(item => item.id === 'S09');
  const firm = scenarios.find(item => item.id === 'S11');
  const partialDraft = buildReplyDraft({}, scenarios, ['S09'], {});
  assert.ok(partialDraft.includes('106 m²'));
  assert.ok(partialDraft.includes('sẵn sàng điều chỉnh đề nghị xuống 50 m²'));
  assert.ok(partialDraft.includes('chưa trình bày rằng hồ sơ 106 m² đã được thay thế'));
  assert.ok(!partialDraft.includes(firm.paragraphs[0]));
  const firmDraft = buildReplyDraft({}, scenarios, ['S11'], {});
  assert.ok(firmDraft.includes(firm.paragraphs[0]));
  assert.ok(firmDraft.includes(`1. ${firm.draftTitle}`));
  assert.ok(!firmDraft.includes(firm.title));
  assert.ok(firmDraft.includes('[TRÍCH NGUYÊN VĂN VÀ TRANG/MỤC CHO S11]'));
  assert.ok(!firmDraft.includes(partial.paragraphs[0]));
  assert.ok(!firmDraft.includes('cố tình'));
});
test('draft includes only selected reasons and preserves the exact quote', () => {
  const quote = 'Trang 2, mục 1: "Chưa đủ cơ sở". <không thực thi HTML>';
  const result = buildReplyDraft({}, scenarios, ['S05', 'S05'], { S05: quote });
  assert.ok(result.includes(quote));
  assert.ok(result.includes(scenarios.find(item => item.id === 'S05').paragraphs[0]));
  assert.ok(!result.includes(scenarios[0].paragraphs[0]));
  assert.equal(result.split('1. Không phù hợp quy hoạch').length, 2);
});
test('blank inputs never invent a receipt date, denial reason or supplied attachment', () => {
  const result = buildReplyDraft({}, scenarios, [], {});
  assert.ok(result.includes('[NGÀY NHẬN THỰC TẾ]'));
  assert.ok(result.includes('[CHỌN LÝ DO THỰC TẾ'));
  assert.ok(result.includes('[CHỈ LIỆT KÊ TÀI LIỆU THỰC SỰ GỬI KÈM'));
  assert.ok(!result.includes('06/10/2026'));
  assert.ok(!result.includes('20/10/2026'));
  assert.ok(missingReplyFields({}, ['S01'], {}).includes('trích nguyên văn S01'));
});
test('dates and actual attachments remain separate from the source library', () => {
  const fields = { documentDate: '2026-10-22', receivedDate: '2026-10-24', draftDate: '2026-10-25', attachments: '1. Bản sao văn bản nhận được, 2 trang.', receipt: 'Mã hồ sơ do người dùng điền' };
  const result = buildReplyDraft(fields, scenarios, ['S07'], {});
  assert.ok(result.includes('Ngày 24/10/2026, tôi nhận được'));
  assert.ok(result.includes('ngày 22/10/2026'));
  assert.ok(result.includes(fields.attachments));
  assert.ok(!result.includes('ĐƠN KHIẾU NẠI'));
  assert.ok(result.includes('[TRÍCH NGUYÊN VĂN VÀ TRANG/MỤC CHO S07]'));
});
