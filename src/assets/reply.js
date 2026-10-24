import { buildReplyDraft, missingReplyFields } from './reply-draft.js';
const form = document.querySelector('#reply-form');
const scenarios = JSON.parse(document.querySelector('#reply-data').textContent);
const output = document.querySelector('#reply-output');
const status = document.querySelector('#output-status');
const storageKey = 'duy-tan-reply-v1';
let generated = false;
function read() {
  const data = new FormData(form);
  return { fields: Object.fromEntries(data), selected: data.getAll('scenario'), quotes: Object.fromEntries(scenarios.map(item => [item.id, data.get(`quote-${item.id}`) || ''])) };
}
function syncSelection() {
  const { fields, selected } = read();
  for (const item of scenarios) {
    document.querySelector(`[data-quote-for="${item.id}"]`).hidden = !selected.includes(item.id);
    document.querySelector(`#${item.id}`).classList.toggle('selected', selected.includes(item.id));
  }
  document.querySelector('#selected-count').textContent = selected.length ? `Đã chọn ${selected.length} lý do` : 'Chưa chọn lý do';
  document.querySelector('#kind-note').textContent = fields.responseKind === 'decision'
    ? 'Cần đọc riêng nội dung, người ký, thẩm quyền và ngày nhận để đánh giá việc khiếu nại/khởi kiện. Bản đề nghị ở đây không tự thay đơn khiếu nại và không tự gia hạn thời hiệu.'
    : 'Bộ soạn này tạo văn bản đề nghị làm rõ và xem xét giải quyết hồ sơ. Chưa tự kết luận phường đã từ chối.';
}
function syncOutput() {
  const text = output.value;
  document.querySelector('#reply-print').textContent = text || 'Chưa có dự thảo. Chọn lý do và ghép nội dung trước khi in.';
  for (const id of ['copy-reply', 'download-reply', 'print-reply']) document.getElementById(id).disabled = !text.trim();
}
form.addEventListener('input', () => {
  syncSelection();
  if (generated) document.querySelector('#draft-status').textContent = 'Thông tin đã thay đổi. Dự thảo hiện tại được giữ nguyên; bấm “Ghép dự thảo” để cập nhật. Lưu hoặc sao chép phần sửa tay trước khi ghép lại.';
});
document.querySelector('#make-reply').addEventListener('click', () => {
  const { fields, selected, quotes } = read();
  output.value = buildReplyDraft(fields, scenarios, selected, quotes);
  generated = true;
  const missing = missingReplyFields(fields, selected, quotes);
  document.querySelector('#draft-status').textContent = missing.length
    ? `Dự thảo còn cần điền: ${missing.join(', ')}. Chưa dùng bản còn ngoặc vuông để ký gửi.`
    : 'Đã điền các trường chính. Rà nguyên văn, điều khoản, dữ kiện và tài liệu thực gửi; kiểm tra phần chỉnh tay trước khi ký.';
  syncOutput();
  document.querySelector('#ban-du-thao').scrollIntoView({ behavior: 'smooth', block: 'start' });
  status.textContent = '';
});
output.addEventListener('input', () => { syncOutput(); status.textContent = 'Đang giữ phần bạn chỉnh trực tiếp. Bấm Lưu nếu muốn giữ lại trên trình duyệt.'; });
document.querySelector('#copy-reply').addEventListener('click', async () => {
  try { await navigator.clipboard.writeText(output.value); status.textContent = 'Đã sao chép. Mở Word và dán, sau đó rà định dạng và nội dung trước khi ký.'; }
  catch { output.focus(); output.select(); status.textContent = 'Trình duyệt chưa cho sao chép tự động. Nội dung đã được chọn; nhấn Ctrl+C rồi dán vào Word.'; }
});
document.querySelector('#download-reply').addEventListener('click', () => {
  const url = URL.createObjectURL(new Blob(['\uFEFF', output.value], { type: 'text/plain;charset=utf-8' }));
  const link = document.createElement('a'); link.href = url; link.download = 'du-thao-phan-hoi-duy-tan.txt'; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1500);
  status.textContent = 'Đã tạo bản tải xuống. Đây là dự thảo, cần rà nội dung còn trống và tài liệu đính kèm.';
});
document.querySelector('#print-reply').addEventListener('click', () => { syncOutput(); window.print(); });
document.querySelector('#save-reply').addEventListener('click', () => {
  try {
    localStorage.setItem(storageKey, JSON.stringify({ version: 1, ...read(), output: output.value }));
    document.querySelector('#save-status').textContent = 'Đã lưu thông tin, nhánh chọn và phần chỉnh tay trên trình duyệt này.';
  } catch { document.querySelector('#save-status').textContent = 'Không lưu được trong trình duyệt. Hãy tải bản văn bản để giữ nội dung.'; }
});
document.querySelector('#restore-reply').addEventListener('click', () => {
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey));
    if (saved?.version !== 1 || !saved.fields || !Array.isArray(saved.selected)) throw new Error('missing');
    for (const control of form.elements) {
      if (!control.name) continue;
      if (control.name === 'scenario') control.checked = saved.selected.includes(control.value);
      else if (typeof saved.fields[control.name] === 'string') control.value = saved.fields[control.name];
    }
    output.value = typeof saved.output === 'string' ? saved.output : '';
    generated = !!output.value; syncSelection(); syncOutput();
    document.querySelector('#save-status').textContent = 'Đã khôi phục. Kiểm tra thông tin với văn bản mới trước khi sử dụng.';
    document.querySelector('#draft-status').textContent = 'Bản đã lưu được giữ nguyên, kể cả phần chỉnh tay. Rà lại các chỗ trống và dữ kiện trước khi ký.';
  } catch { document.querySelector('#save-status').textContent = 'Chưa có bản lưu hợp lệ tại địa chỉ web này. Bản đang nhập được giữ nguyên.'; }
});
document.querySelector('#forget-reply').addEventListener('click', () => {
  try {
    localStorage.removeItem(storageKey);
    document.querySelector('#save-status').textContent = 'Đã xóa bản lưu khỏi trình duyệt. Nội dung đang mở vẫn còn để sửa hoặc tải xuống.';
  } catch { document.querySelector('#save-status').textContent = 'Trình duyệt chưa cho xóa bản lưu. Nội dung đang mở vẫn được giữ nguyên.'; }
});
syncSelection(); syncOutput();
