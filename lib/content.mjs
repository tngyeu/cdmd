import fs from 'node:fs';
import path from 'node:path';
import { parse } from 'csv-parse/sync';
import MarkdownIt from 'markdown-it';
import { aggregateLocalities, decisionStatus, normalize } from './decision-math.mjs';
import { compareLegal, filterLegal, recentStart } from './legal-library.mjs';

export const root = process.cwd();
export const moduleDir = path.join(root, 'ho_so_phap_ly_dat_dai_ninh_binh');
export const procedureDir = path.join(root, 'nghien_cuu_quy_trinh');
const read = file => fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, '');
const json = file => JSON.parse(read(file));
const csv = file => parse(read(file), { columns: true, skip_empty_lines: true, bom: true });
export const slug = value => normalize(value).replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
export const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
export const fmt = value => value == null || value === '' ? '—' : new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 3 }).format(Number(value));
export const date = value => /^\d{4}-\d{2}-\d{2}$/.test(value || '') ? value.split('-').reverse().join('/') : value || 'Chưa rõ ngày';
export const jsonScript = value => JSON.stringify(value).replace(/</g, '\\u003c').replace(/>/g, '\\u003e').replace(/&/g, '\\u0026');
const reportSpecs = [
  ['search_expanded_20261029', 'Rà mở rộng Google và Bing: thêm 14 quyết định', '/quyet-dinh/ra-mo-rong-20261029/', 'decisions', 'Đọc PDF ở Khánh Hội, Nam Hoa Lư, Đồng Thái, Yên Mô, Nam Định, Giao Hòa; sửa ngày Tây Hoa Lư theo bản lưu.'],
  ['search_supplement_20261029', 'Bổ sung hồ sơ trong tháng gần đây', '/quyet-dinh/bo-sung-20261029/', 'decisions', 'Hai quyết định Xuân Hồng ngày 01/10/2026: 358,4 m² CLN sang ONT; đã đọc PDF, chưa có tổng diện tích thửa.'],
  ['sau_chuyen_don_tinh_20261022', 'Sau khi tỉnh chuyển đơn mà vẫn giữ nguyên quan điểm', '/ho-so-duy-tan/sau-chuyen-don-tinh/', 'response', 'Tám kịch bản, bản phản hồi gửi Chủ tịch tỉnh và bảng đối chiếu sau chuyển đơn; làm rõ hạn mức, phương án 50 m² và lúc cần chuyển sang khiếu nại/khởi kiện.'],
  ['de_nghi_tinh_kiem_tra_50m2_20261022', 'Bản đề nghị Chủ tịch UBND tỉnh kiểm tra về 50 m²', '/ho-so-duy-tan/de-nghi-tinh-kiem-tra/', 'response', 'Bản soạn sẵn đề nghị Chủ tịch UBND tỉnh Ninh Bình chỉ đạo kiểm tra khi Sở chưa làm rõ căn cứ đối với 50 m²; chỉnh sửa, sao chép, tải TXT hoặc in, kèm bảng đối chiếu và nguồn.'],
  ['sau_phan_hoi_so_20261022', 'Nếu Sở cũng chưa làm rõ hoặc đồng ý với phường', '/ho-so-duy-tan/sau-phan-hoi-so/', 'response', 'Tám kịch bản, bản hỏi tiếp Sở và hướng xử lý nếu vẫn không đồng ý 50 m²; căn cứ, tuyến khiếu nại, khởi kiện và mốc thời gian cần giữ.'],
  ['de_nghi_so_huong_dan_50m2_20261022', 'Bản đề nghị Sở hướng dẫn về 50 m²', '/ho-so-duy-tan/de-nghi-so-huong-dan/', 'response', 'Bản soạn sẵn gửi Sở Nông nghiệp và Môi trường khi phường vẫn không đồng ý 50 m² hoặc chưa rõ căn cứ; có bảng đối chiếu và chỉ dẫn chứng cứ.'],
  ['du_thao_bo_sung_50m2_20261022', 'Bản bổ sung phương án 50 m²', '/ho-so-duy-tan/bo-sung-50m2/', 'response', 'Bản soạn sẵn để dùng khi nhận phản hồi: chỉnh sửa, sao chép sang Word, tải TXT hoặc in; có câu hỏi làm rõ hạn mức và điều kiện nếu vẫn không đồng ý.'],
  ['hieu_luc_han_muc_50m2_20261021', 'Hiệu lực, hạn mức và phương án 50 m²', '/ho-so-duy-tan/hieu-luc-han-muc-50/', 'response', 'Rà soát hiệu lực, sửa đổi; phân biệt hạn mức, chuyển một phần không bắt buộc tách và hệ quả tài chính khi chuyển 50 m² trước.'],
  ['muc_san_sang_phan_hoi_20261021', 'Mức sẵn sàng và bản đồ căn cứ', '/ho-so-duy-tan/muc-san-sang/', 'response', 'Đánh giá độ rộng, độ sát hồ sơ và mức kiểm chứng; nối từng lý do phản hồi với nguồn, điều khoản và chứng cứ cần có.'],
  ['duy_tan_tu_choi_50m2', 'Vẫn không đồng ý, kể cả 50 m²', '/ho-so-duy-tan/van-khong-dong-y/', 'response', 'Kịch bản xấu nhất, câu hỏi sát hồ sơ, đoạn bổ sung phương án 50 m² và cách ghi nhận để đề nghị Sở hướng dẫn.'],
  ['bo_phan_hoi_van_ban', 'Bộ kịch bản phản hồi văn bản', '/ho-so-duy-tan/kich-ban-phan-hoi/', 'response', 'Mười một kịch bản có đoạn phản hồi và nguồn đối chiếu, gồm phương án 50 m² và trường hợp vẫn nhất quyết từ chối.'],
  ['duy_tan', 'Hồ sơ Duy Tân', '/ho-so-duy-tan/phan-tich/', 'case', 'Phân tích chi tiết hồ sơ 106 m² CLN → ODT và những dữ liệu cần xác nhận.'],
  ['duy_tan_doc_nhanh', 'Hồ sơ Duy Tân trong hai phút', '/ho-so-duy-tan/doc-nhanh/', 'case', 'Bốn ý cần nhớ, ba ví dụ chuyển diện tích lớn và câu có thể dùng khi trao đổi.'],
  ['duy_tan_tinh_huong_phan_bien', 'Các tình huống và cách phản hồi về 106 m²', '/ho-so-duy-tan/tinh-huong/', 'case', '13 tình huống về nhiều đất, nhu cầu cấp thiết và ưu tiên chỉ tiêu; số liệu, chứng cứ Anhome và đoạn giải trình.'],
  ['duy_tan_doi_dap_kho', 'Diễn tập đối đáp và kiểm tra độ chắc của hồ sơ', '/ho-so-duy-tan/doi-dap/', 'case', 'Tám lượt đối đáp với cán bộ khó tính, điểm có thể giữ chắc, điểm cần thu hẹp và bằng chứng cần bổ sung.'],
  ['doi_chieu_dat_o_549m2', 'Tìm ví dụ đã có từ 549 m² đất ở rồi chuyển thêm', '/ho-so-duy-tan/doi-chieu-549/', 'case', 'Kết quả tìm ngày 21/10: chưa xác minh ví dụ đạt đúng ngưỡng; ba hồ sơ có 427–434 m² đất ở trước chuyển, nguồn và giới hạn đối chiếu.'],
  ['tai_chinh_dat_o_co_san', 'Đất ở có sẵn và tiền chuyển mục đích', '/ho-so-duy-tan/tai-chinh/', 'case', 'Không cộng dồn đất ở hiện có; điều kiện tính tiền và chính sách một lần khi cân nhắc 50 m² hoặc 106 m².'],
  ['bao_ve_ho_so_duy_tan_20261020', 'Căn cứ và giải trình bảo vệ hồ sơ', '/ho-so-duy-tan/bao-ve-ho-so/', 'case', 'Nhu cầu bố trí nhà tránh tiếng ồn, giữ khoảng nhìn nhà thờ họ; căn cứ phản hồi, dự thảo giải trình và cách xin thông tin.'],
  ['legal_overview', 'Cách đọc căn cứ pháp lý', '/phap-ly/cach-doc/', 'legal', 'Đọc đúng quan hệ sửa đổi, loại văn bản và mức độ kiểm chứng.'],
  ['site_content_review_20261019', 'Các điểm đã rà soát & tổ chức lại', '/phap-ly/ra-soat/', 'legal', 'Những điểm dễ hiểu nhầm đã được làm rõ khi nối thủ tục, hồ sơ pháp lý và số liệu.'],
  ['budget_policy', 'Ngân sách & quỹ đất', '/ngan-sach/', 'legal', 'Các số thu, dự toán và đề án quỹ đất trong đúng phạm vi sử dụng.'],
  ['decisions_2026', 'Phạm vi quyết định thu thập', '/quyet-dinh/pham-vi/', 'decisions', 'Nguồn công khai, cách chống trùng và giới hạn của tập quyết định đã thu thập.'],
  ['myloc_download_20261020', 'Mỹ Lộc: danh mục và bộ PDF đã tải', '/quyet-dinh/my-loc/', 'decisions', '94 dòng kết quả, 93 trang văn bản riêng; 40 bản năm 2026 và 53 bản năm 2025. Đã tải 87 PDF, còn 6 tệp nguồn lỗi 403.'],
  ['myloc_area_2026', 'Mỹ Lộc: 40 quyết định chuyển 6.196 m² sang đất ở', '/quyet-dinh/my-loc/dien-tich/', 'decisions', 'Đã đối chiếu Điều 1 của 40 PDF năm 2026: 6.196 m² ODT, tương đương 0,6196 ha; có bảng theo tháng và từng quyết định.'],
  ['decision_reading_notes', 'Ghi chú đọc quyết định', '/quyet-dinh/ghi-chu/', 'decisions', 'Các trường hợp đã đọc ảnh, diện tích và điểm cần đối chiếu.'],
  ['scan_review_20261021', 'Rà soát 14 quyết định từ bản quét', '/quyet-dinh/ra-soat-ban-quet/', 'decisions', 'Bổ sung 8 bản ghi, xác minh thêm 1.604,3 m² chuyển sang đất ở; nguồn, ngày bản ký và trang đối chiếu.'],
  ['research_gaps', 'Dữ liệu cần xác minh', '/nguon-va-gioi-han/', 'legal', 'Phần đã có nguồn, phần còn thiếu và cách tiếp tục kiểm tra.'],
  ['residential_quota_2030', 'Phân tích chỉ tiêu đất ở', '/chi-tieu/phan-tich/', 'quota', 'Căn cứ số liệu, so sánh địa phương và giới hạn của các kịch bản.'],
  ['residential_quota_brief', 'Đọc nhanh: 50,26 ha', '/chi-tieu/doc-nhanh/', 'quota', 'Quy đổi diện tích sang số trường hợp và so với quy mô hộ.'],
  ['search_supplement_20261019', 'Nhật ký bổ sung nguồn', '/nguon-va-gioi-han/bo-sung/', 'legal', 'Những số liệu, nguồn và nhãn xác minh đã được bổ sung ngày 19/10/2026.']
];
const reportRoutes = new Map(reportSpecs.map(([name, , url]) => [path.join(moduleDir, 'reports', `${name}.md`), url]));
reportRoutes.set(path.join(moduleDir, 'reports', 'questions_answers.md'), '/hoi-dap/');
const procedureFiles = fs.readdirSync(procedureDir).filter(name => /\.(pdf|docx)$/i.test(name));
const findPDF = part => procedureFiles.find(name => name.includes(part));
export const sourceFiles = {
  QĐ510: findPDF('QĐ 510-QĐ-UBND ngày'), H42: findPDF('Phụ lục QĐ 510'),
  QĐ64: findPDF('64-2026-QĐ-UBND'), PLI: findPDF('Phụ lục I -'), PLVII: findPDF('Phụ lục VII -')
};
export function fileURL(file) {
  const resolved = path.resolve(file);
  if (reportRoutes.has(resolved)) return reportRoutes.get(resolved);
  if (resolved === path.join(moduleDir, 'chi_tieu_dat_o_2030.html')) return '/chi-tieu/';
  if (resolved === path.join(moduleDir, 'index.html')) return '/';
  if (resolved === path.join(procedureDir, 'nghien_cuu_quy_trinh_chuyen_muc_dich_dat_chuyen_sau.html')) return '/thu-tuc/nghien-cuu/';
  const mapping = [[path.join(moduleDir, 'documents'), '/tai-lieu/'], [path.join(moduleDir, 'data'), '/du-lieu/'], [procedureDir, '/tai-lieu/quy-trinh/']];
  for (const [base, prefix] of mapping) if (resolved.startsWith(base + path.sep)) return prefix + path.relative(base, resolved).split(path.sep).map(encodeURIComponent).join('/');
  return '/tai-lieu/mau-don-de-nghi.docx';
}
export function sourceURL(name, page) { return fileURL(path.join(procedureDir, sourceFiles[name])) + (page ? `#page=${page}` : ''); }
function rewriteLink(href, file) {
  if (/^(https?:|mailto:|tel:|#|\/)/i.test(href)) return href;
  const suffixAt = href.search(/[?#]/);
  const pathname = suffixAt < 0 ? href : href.slice(0, suffixAt);
  const suffix = suffixAt < 0 ? '' : href.slice(suffixAt);
  const resolved = path.resolve(path.dirname(file), decodeURIComponent(pathname));
  return fileURL(resolved) + suffix;
}
export function renderMarkdown(source, file, prefix = 'doc') {
  const toc = [];
  let index = 0;
  const headingIds = new Map();
  const md = new MarkdownIt({ html: true, linkify: true, typographer: false });
  const defaultHeading = md.renderer.rules.heading_open || ((tokens, i, options, env, self) => self.renderToken(tokens, i, options));
  md.renderer.rules.heading_open = (tokens, i, options, env, self) => {
    const title = tokens[i + 1].content;
    const baseId = `${prefix}-${slug(title) || ++index}`;
    const occurrence = (headingIds.get(baseId) || 0) + 1;
    headingIds.set(baseId, occurrence);
    const id = occurrence === 1 ? baseId : `${baseId}-${occurrence}`;
    tokens[i].attrSet('id', id);
    const level = Number(tokens[i].tag.slice(1));
    if (level === 2) toc.push({ title, id });
    return defaultHeading(tokens, i, options, env, self);
  };
  // Older reports refer to source markers in prose; make them real PDF jumps.
  source = source.replace(/\[(QĐ510|H42|QĐ64|PLI|PLVII),\s*PDF tr\.\s*(\d+)([^\]]*)\]/g, (_, code, page, rest) => `[${code}, PDF tr. ${page}${rest}](${sourceURL(code, page)})`);
  source = source.replace(/^# .+\r?\n/, '');
  let html = md.render(source);
  html = html.replace(/\b(href|src)="([^"]+)"/g, (_, attr, value) => `${attr}="${escape(rewriteLink(value.replace(/&amp;/g, '&'), file))}"`);
  html = html.replace(/<a href="([^"]+)"/g, (match, href) => /^(https?:|\/tai-lieu\/)/.test(href) ? `<a target="_blank" rel="noopener noreferrer" href="${href}"` : match);
  html = html.replace(/<table>/g, '<div class="table-scroll" tabindex="0" role="region" aria-label="Tableau de données"><table>').replace(/<\/table>/g, '</table></div>');
  html = html.replace(/aria-label="Tableau de données"/g, 'aria-label="Bảng dữ liệu, có thể cuộn ngang"');
  return { html, toc };
}
export function readReport(name, prefix = name) {
  const file = path.join(moduleDir, 'reports', `${name}.md`);
  let source = read(file);
  const metadata = source.match(/<!--\s*web:\s*({[\s\S]*?})\s*-->/);
  const web = metadata ? JSON.parse(metadata[1]) : {};
  if (metadata) source = source.replace(metadata[0], '');
  const rendered = renderMarkdown(source, file, prefix);
  let preparedDraft = null;
  if (web.preparedDraft) {
    const match = source.match(/^<!-- prepared-draft:start -->\s*\n([\s\S]*?)\n<!-- prepared-draft:end -->/m);
    if (!match?.[1].trim()) throw new Error(`${name}: thiếu nội dung văn bản soạn sẵn`);
    const before = renderMarkdown(source.slice(0, match.index), file, prefix);
    const after = renderMarkdown(source.slice(match.index + match[0].length), file, prefix);
    preparedDraft = { text: match[1].trim(), before: before.html, after: after.html };
    rendered.toc = [...before.toc, ...after.toc];
  }
  return { ...rendered, web, preparedDraft, text: rendered.html.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim() };
}
const topics = [
  { key: 'can-cu', label: 'Điều kiện chuyển mục đích', description: 'Quy định chung, trường hợp cần cho phép và chuỗi văn bản sửa đổi.', icon: 'book', ids: ['LDD31', 'L43', 'NQ254', 'ND102', 'ND226', 'ND49'] },
  { key: 'thu-tuc', label: 'Thẩm quyền & thủ tục', description: 'Ai giải quyết, tiếp nhận và trả kết quả; quyền yêu cầu cung cấp thông tin.', icon: 'route', ids: ['NB64', 'NB43', 'NB192', 'ND151', 'ND118', 'ND367', 'ND309', 'LTC01-2026', 'ND337'] },
  { key: 'quy-hoach', label: 'Quy hoạch & chỉ tiêu', description: 'Phân bổ diện tích, điều chỉnh và đối chiếu chỉ tiêu đất ở.', icon: 'map', ids: ['NB-3279-2026', 'NB162', 'NB1702', 'NB568', 'NB1543'] },
  { key: 'tai-chinh', label: 'Hạn mức & tiền sử dụng đất', description: 'Nguồn gốc đất, hạn mức, bảng giá và cơ chế tài chính.', icon: 'calculator', ids: ['ND50', '103-2024', 'ND291', '71-2024', 'NB193', 'NB194', 'NB86', 'NB38', 'NB33', 'NB76', 'BTC-CV7713-2026'] },
  { key: 'vi-pham', label: 'Vi phạm & xây dựng', description: 'Phân biệt xử lý vi phạm đất đai và trật tự xây dựng.', icon: 'shield', ids: ['ND123', 'ND281', '16-2022'] },
  { key: 'boi-canh', label: 'Chỉ đạo, ngân sách & quỹ đất', description: 'Đề án, nhiệm vụ điều hành và nguồn thu từ đất.', icon: 'folder', ids: ['NB-DA08-2026', 'NB-CV5061-2026', 'CV10108', 'CV6456', 'NB-PL-231-2026', 'NB-PL-201-2026', 'NB-VPUBND-QUYDAT-GIAOBAN-20260326', 'NB-NQ48-2025', 'NB-NQ28-2026', 'NB-KL-QUYDAT-202605'] },
  { key: 'lien-quan', label: 'Luật liên quan cần đối chiếu', description: 'Đã xác nhận thông tin văn bản, chưa đối chiếu điều sửa cho hồ sơ này.', icon: 'layers', ids: [] }
];
export function legalEvidence(status) {
  if (status === 'official_pdf' || status === 'official_original_images') return { label: status === 'official_original_images' ? 'Có ảnh toàn văn gốc' : 'Có PDF nguồn chính thức', tone: 'green' };
  if (status === 'citation_only' || status === 'official_citation') return { label: 'Mới có nguồn viện dẫn', tone: 'muted' };
  if (status === 'official_metadata') return { label: 'Đã xác nhận thông tin', tone: 'blue' };
  if (status === 'historical_attachment') return { label: 'Văn bản lịch sử', tone: 'muted' };
  return { label: 'Cần khớp bản ký', tone: 'amber' };
}
export function getResearch() {
  const display = json(path.join(moduleDir, 'data', 'display_data.json'));
  const collectionScope = json(path.join(moduleDir, 'data', 'decision_collection_scope.json'));
  const editorial = json(path.join(moduleDir, 'data', 'legal_editorial.json'));
  const legal = csv(path.join(moduleDir, 'data', 'legal_documents.csv')).map(row => {
    const item = { ...row, ...editorial.documents[row.document_id] };
    const topic = topics.find(t => t.ids.includes(item.document_id)) || topics.at(-1);
    const isCitation = ['citation_only', 'official_citation'].includes(item.verification_status);
    const classLabels = { quy_dinh_bat_buoc: 'Quy định pháp luật', quyet_dinh_quan_ly: 'Quyết định quản lý / quy hoạch', huong_dan_chi_dao: 'Hướng dẫn / chỉ đạo', thong_bao_quan_ly_dia_phuong: 'Thông báo quản lý địa phương', chi_dao_hanh_chinh: 'Chỉ đạo hành chính', nghi_quyet_ngan_sach: 'Nghị quyết ngân sách', nghi_quyet_dau_tu_cong: 'Nghị quyết đầu tư công' };
    const attachment = (label, file) => ({ label, url: fileURL(path.join(moduleDir, file)) });
    const attachments = {
      LDD31: [...[1, 2, 3].map(part => attachment(`Luật Đất đai · Phần ${part}`, `documents/phap_luat/luat31_${part}.pdf`)), attachment('Hợp nhất 44/VBHN-VPQH · Công báo số 174', 'documents/phap_luat/vbhn44_2026_congbao174.pdf')],
      ND102: [attachment('Hợp nhất 46/VBHN-BNNMT', 'documents/phap_luat/vbhn46_bnnmt_2026.pdf')],
      ND49: [attachment('Nghị định 49 · Bản Công báo có lớp chữ', 'documents/phap_luat/nd49_2026_congbao.pdf')],
      ND367: [attachment('Nghị định 367 · Bản Công báo', 'documents/phap_luat/nd367_2025_congbao.pdf')],
      NQ254: Array.from({ length: 15 }, (_, index) => attachment(`Nghị quyết 254 · Ảnh trang ${index + 1}`, `documents/phap_luat/nq254_2025_trang_${index + 1}.jpg`)),
      NB33: Array.from({ length: 9 }, (_, index) => attachment(`Nghị quyết 33 · Phụ lục ${index + 1}`, `documents/phap_luat/nq33_2026_33_NQ_PL${index + 1}.pdf`)),
      NB38: [attachment('Phụ lục giá đất ODT đã lưu', 'documents/phap_luat/nq38_2025_phu_luc_ODT.pdf')],
      NB193: [attachment('Quyết định 193 · Bản Công báo', 'documents/phap_luat/qd193_2025_congbao.pdf'), attachment('Bản ký từ Bộ Tư pháp · Trùng mã tệp bản tỉnh', 'documents/phap_luat/qd193_2025_ban_ky_moj.pdf')],
      NB43: [attachment('Quyết định 43 · Bản Công báo', 'documents/phap_luat/qd43_2026_congbao.pdf')],
      'NB-3279-2026': [attachment('Biểu tổng hợp toàn tỉnh', 'documents/quy_hoach/3279_2026_bieu_tinh.pdf'), attachment('Bộ phụ lục 129 xã, phường · 258 trang', 'documents/quy_hoach/3279_2026_phu_luc_129.pdf')],
      NB64: [{ label: 'Phụ lục I · Trình tự giao đất, cho thuê đất, chuyển mục đích', url: sourceURL('PLI') }, { label: 'Phụ lục VII · Bộ biểu mẫu đất đai', url: sourceURL('PLVII') }, attachment('Bộ Công báo đầy đủ · 134 trang, thứ tự khác bản tách', 'documents/phap_luat/qd64_2026_congbao_day_du.pdf')]
    }[item.document_id] || [];
    return { ...item, slug: slug(item.document_id), url: `/phap-ly/van-ban/${slug(item.document_id)}/`, topic: topic.key, topicLabel: topic.label,
      classLabel: item.document_class === 'de_an_phat_trien_quy_dat' ? 'Đề án phát triển quỹ đất' : classLabels[item.document_class] || 'Cần đối chiếu tính chất văn bản',
      attachments,
      localURL: item.local_file ? fileURL(path.resolve(moduleDir, item.local_file)) : '', localLabel: isCitation ? 'Mở văn bản có viện dẫn' : 'Mở tệp trong kho',
      evidence: legalEvidence(item.verification_status), primary: !['lien-quan', 'boi-canh'].includes(topic.key),
      related: [], isCitation };
  });
  legal.sort((a, b) => compareLegal(a, b));
  const recent = new Set(filterLegal(legal, { view: 'recent' }, display.stats.cutoff).map(doc => doc.document_id));
  for (const doc of legal) doc.recent = recent.has(doc.document_id);
  for (const item of legal) item.related = legal.filter(other => other.topic === item.topic && other.document_id !== item.document_id).map(other => ({ title: other.title, number: other.number, url: other.url }));
  const reports = reportSpecs.map(([name, title, url, navKey, description]) => {
    const report = readReport(name);
    return { name, title, url, navKey, description, ...report, summary: report.web.summary || description, updatedOn: report.web.updatedOn || '', icon: report.web.icon || 'book' };
  });
  const featuredReports = reports.filter(report => report.web.featured === true).sort((a, b) => (a.web.order || 99) - (b.web.order || 99));
  const updatedOn = [collectionScope.last_targeted_review || display.stats.cutoff, ...reports.map(report => report.updatedOn)].sort().at(-1);
  const pFile = path.join(procedureDir, 'nghien_cuu_quy_trinh_chuyen_muc_dich_dat_chuyen_sau.md');
  const procedureText = read(pFile);
  const procedure = renderMarkdown(procedureText, pFile, 'nghien-cuu');
  const sections = procedureText.split(/(?=^## )/m).filter(s => /^## /.test(s)).map((section, index) => ({ index: index + 1, title: section.split('\n')[0].replace(/^## /, '').trim(), ...renderMarkdown(section, pFile, `chuong-${index + 1}`) }));
  const qaFile = path.join(moduleDir, 'reports', 'questions_answers.md');
  const faq = read(qaFile).split(/(?=^## )/m).filter(s => /^## /.test(s)).map((section, index) => {
    const title = section.split('\n')[0].replace(/^## \d+\s*·\s*/, '').trim();
    const topic = index < 4 ? 'han-muc' : index < 11 ? 'chi-tieu' : index < 15 ? 'tai-chinh' : 'trao-doi';
    return { id: `cau-${index + 1}`, title, topic, ...renderMarkdown(section.substring(section.indexOf('\n')), qaFile, `cau-${index + 1}`) };
  });
  const analysis = json(path.join(moduleDir, 'data', 'residential_quota_analysis.json'));
  const decisions = display.decisions.map(row => ({ ...row, local_pdf: row.local_pdf ? fileURL(path.resolve(moduleDir, row.local_pdf)) : '', status: decisionStatus(row) }));
  const localities = display.coverage.map(row => row.locality).sort((a, b) => a.localeCompare(b, 'vi'));
  const summary = aggregateLocalities(decisions, '', localities).sort((a, b) => b.records - a.records);
  const sources = Object.entries(sourceFiles).map(([code, file]) => ({ code, file, url: sourceURL(code) }));
  const search = [
    ...json(path.join(root, 'src', '_data', 'site.json')).navigation.map(item => ({ title: item.label, url: item.url, type: 'Trang', text: item.label })),
    ...reports.map(item => ({ title: item.title, url: item.url, type: 'Bài phân tích', text: `${item.summary} ${item.text}`, excerpt: item.summary })),
    ...legal.map(item => ({ title: `${item.number} · ${item.title}`, url: item.url, type: 'Văn bản', text: `${item.summary} ${item.topicLabel}` })),
    ...faq.map(item => ({ title: item.title, url: `/hoi-dap/#${item.id}`, type: 'Hỏi đáp', text: item.title })),
    ...decisions.map(item => ({ title: `${item.decision_number} · ${item.locality}`, url: `/quyet-dinh/?q=${encodeURIComponent(item.decision_number)}&locality=${encodeURIComponent(item.locality)}`, type: 'Quyết định', text: `${date(item.issue_date)} ${item.land_before} ${item.land_after}` }))
  ];
  return { stats: display.stats, collectionScope, updatedOn, featuredReports, legal, topics: topics.map(topic => ({ ...topic, count: legal.filter(item => item.topic === topic.key).length })), reports, procedure, sections, faq, analysis, decisions, localities, summary, sources, search,
    legalRecentCount: recent.size, legalUndatedCount: legal.filter(doc => !doc.issued_date).length,
    legalRecentStart: recentStart(display.stats.cutoff), legalYears: [...new Set(legal.map(doc => doc.issued_date?.slice(0, 4)).filter(Boolean))].sort().reverse(),
    months: [...new Set(decisions.map(row => row.issue_date.slice(0, 7)))].sort().reverse(),
    types: [...new Set(decisions.flatMap(row => [row.conversion_group, ...JSON.parse(row.components_json || '[]').map(c => `${c.land_before}->${c.land_after}`)]))].filter(Boolean).sort(),
    quotaBrief: json(path.join(moduleDir, 'data', 'residential_quota_brief.json')),
    households: json(path.join(moduleDir, 'data', 'duy_tan_households.json'))
  };
}
