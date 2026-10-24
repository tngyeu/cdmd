const output = document.querySelector('#prepared-text');
const printText = document.querySelector('#prepared-print');
const status = document.querySelector('#prepared-status');
const copy = document.querySelector('#prepared-copy');
const download = document.querySelector('#prepared-download');
const print = document.querySelector('#prepared-print-button');

function sync() {
  printText.textContent = output.value;
  const empty = !output.value.trim();
  for (const button of [copy, download, print]) button.disabled = empty;
  const missing = [...new Set(output.value.match(/\[[^\]\n]+\]/g) || [])];
  document.querySelector('#prepared-missing').textContent = missing.length
    ? `Còn ${missing.length} mục trong ngoặc vuông cần điền hoặc xử lý. Chưa dùng bản còn chỗ trống để ký gửi.`
    : empty ? 'Nội dung đang trống.' : 'Đã hết chỗ giữ trong ngoặc vuông. Vẫn cần đối chiếu thông tin, căn cứ và tài liệu thực gửi trước khi ký.';
}

output.addEventListener('input', () => {
  sync();
  status.textContent = 'Đang dùng phần bạn chỉnh trong ô. Tải TXT để giữ lại trước khi rời trang.';
});
copy.addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText(output.value);
    status.textContent = 'Đã sao chép riêng văn bản. Dán vào Word và kiểm tra nội dung, định dạng trước khi ký.';
  } catch {
    output.focus(); output.select();
    status.textContent = 'Nội dung đã được chọn. Nhấn Ctrl+C rồi dán vào Word.';
  }
});
download.addEventListener('click', () => {
  const url = URL.createObjectURL(new Blob(['\uFEFF', output.value], { type: 'text/plain;charset=utf-8' }));
  const link = document.createElement('a');
  link.href = url; link.download = download.dataset.filename; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1500);
  status.textContent = 'Đã tạo bản TXT từ nội dung hiện tại. Bản tải không kèm hướng dẫn hoặc bảng nguồn.';
});
print.addEventListener('click', () => { sync(); window.print(); });
window.addEventListener('beforeprint', sync);
sync();
