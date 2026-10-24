const clean = value => typeof value === 'string' ? value.trim() : '';
const date = value => /^\d{4}-\d{2}-\d{2}$/.test(value || '') ? value.split('-').reverse().join('/') : clean(value);
const fill = (value, placeholder) => clean(value) || `[${placeholder}]`;

// The draft only uses explicitly selected branches. Missing facts stay visible.
export function buildReplyDraft(fields, scenarios, selectedIds, quotes = {}) {
  const selected = scenarios.filter(item => selectedIds.includes(item.id));
  const blocks = [
    'CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM',
    'Độc lập - Tự do - Hạnh phúc',
    `Duy Tân, ngày ${fill(date(fields.draftDate), 'NGÀY LẬP VĂN BẢN')}`,
    'VĂN BẢN ĐỀ NGHỊ LÀM RÕ VÀ XEM XÉT GIẢI QUYẾT HỒ SƠ',
    'Về hồ sơ đề nghị chuyển 106 m² đất trồng cây lâu năm sang đất ở',
    `Kính gửi: ${fill(fields.recipient, 'CƠ QUAN HOẶC NGƯỜI CÓ THẨM QUYỀN')}.`,
    `Tôi là: ${fill(fields.name, 'HỌ VÀ TÊN')}.\nĐịa chỉ liên hệ: ${fill(fields.address, 'ĐỊA CHỈ LIÊN HỆ')}.\nThông tin liên hệ: ${fill(fields.contact, 'ĐIỆN THOẠI HOẶC CÁCH LIÊN HỆ')}.\nTư cách đối với hồ sơ: ${fill(fields.capacity, 'NGƯỜI SỬ DỤNG ĐẤT HOẶC ĐẠI DIỆN HỢP PHÁP')}.`,
    `Hồ sơ liên quan đến phần 106 m² CLN đề nghị chuyển sang ODT thuộc thửa số ${fill(fields.parcel, 'SỐ THỬA')}, tờ bản đồ số ${fill(fields.mapSheet, 'TỜ BẢN ĐỒ')}, tại ${fill(fields.landAddress, 'ĐỊA CHỈ THỬA ĐẤT')}.`,
    ...(clean(fields.receipt) ? [`Thông tin tiếp nhận hồ sơ theo giấy tờ đang có: ${clean(fields.receipt)}.`] : []),
    `Ngày ${fill(date(fields.receivedDate), 'NGÀY NHẬN THỰC TẾ')}, tôi nhận được văn bản số ${fill(fields.documentNumber, 'SỐ VĂN BẢN')}, ngày ${fill(date(fields.documentDate), 'NGÀY BAN HÀNH')}, của ${fill(fields.issuer, 'CƠ QUAN BAN HÀNH')}. Tôi đề nghị làm rõ và xem xét các nội dung sau:`
  ];
  if (!selected.length) blocks.push('[CHỌN LÝ DO THỰC TẾ TRONG VĂN BẢN ĐỂ GHÉP NỘI DUNG PHẢN HỒI]');
  selected.forEach((item, index) => {
    blocks.push(`${index + 1}. ${item.draftTitle || item.title}`);
    blocks.push(`Nội dung cần đối chiếu trong văn bản: ${fill(quotes[item.id], `TRÍCH NGUYÊN VĂN VÀ TRANG/MỤC CHO ${item.id}`)}`);
    blocks.push(...item.paragraphs);
  });
  if (clean(fields.extra)) blocks.push('Nội dung giải trình bổ sung', clean(fields.extra));
  blocks.push(
    'Kính đề nghị cơ quan trả lời theo từng nội dung nêu trên, chỉ rõ căn cứ và dữ kiện dùng để giải quyết; hướng dẫn những nội dung cần bổ sung nếu có. Tôi sẵn sàng phối hợp kiểm tra, đối chiếu hồ sơ và thực hiện nghĩa vụ theo quy định.',
    'Tài liệu gửi kèm',
    clean(fields.attachments) || '[CHỈ LIỆT KÊ TÀI LIỆU THỰC SỰ GỬI KÈM; NẾU KHÔNG CÓ THÌ XÓA MỤC NÀY]',
    'Người đề nghị\n(Ký và ghi rõ họ tên)\n\n' + fill(fields.name, 'HỌ VÀ TÊN')
  );
  return blocks.join('\n\n');
}

export function missingReplyFields(fields, selectedIds, quotes) {
  const names = { name: 'họ tên', capacity: 'tư cách đối với hồ sơ', address: 'địa chỉ liên hệ', contact: 'cách liên hệ', recipient: 'nơi nhận', issuer: 'cơ quan ban hành', documentNumber: 'số văn bản', documentDate: 'ngày ban hành', receivedDate: 'ngày nhận', draftDate: 'ngày lập', parcel: 'số thửa', mapSheet: 'tờ bản đồ', landAddress: 'địa chỉ thửa đất' };
  const missing = Object.entries(names).filter(([key]) => !clean(fields[key])).map(([, name]) => name);
  if (!selectedIds.length) missing.push('lý do cần phản hồi');
  selectedIds.forEach(id => { if (!clean(quotes[id])) missing.push(`trích nguyên văn ${id}`); });
  return missing;
}
