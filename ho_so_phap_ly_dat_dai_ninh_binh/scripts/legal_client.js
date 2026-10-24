const legalSortLabels = {number:'Số hiệu',title:'Tên văn bản',group:'Nhóm',issuer:'Cơ quan',issued_date:'Ngày ban hành',effective_date:'Ngày hiệu lực',verification_status:'Chất lượng nguồn'};
let legalSort = {key:'issued_date',direction:'descending'};
const legalCollator = new Intl.Collator('vi',{numeric:true,sensitivity:'base'});
function compareLegal(a,b){
  const key=legalSort.key, x=a[key]||'', y=b[key]||'';
  if(!x||!y){if(x)return -1;if(y)return 1;}
  else {const comparison=legalCollator.compare(x,y);if(comparison)return legalSort.direction==='ascending'?comparison:-comparison;}
  return legalCollator.compare(a.number,b.number)||legalCollator.compare(a.document_id,b.document_id);
}
function updateLegalHeaders(){
  document.querySelectorAll('.legal-table th').forEach(th=>th.removeAttribute('aria-sort'));
  document.querySelectorAll('[data-legal-sort]').forEach(button=>{
    const key=button.dataset.legalSort, active=key===legalSort.key;
    button.setAttribute('aria-pressed',String(active));
    button.dataset.direction=active?legalSort.direction:'';
    const next=active?(legalSort.direction==='ascending'?'giảm dần':'tăng dần'):(key.endsWith('_date')?'giảm dần':'tăng dần');
    button.setAttribute('aria-label',legalSortLabels[key]+': sắp xếp '+next);
    if(active)button.closest('th').setAttribute('aria-sort',legalSort.direction);
  });
}
function renderLegal(){
  const q=norm($('legalSearch').value),g=$('legalGroup').value,s=$('legalStatus').value;
  const rows=D.legal.filter(r=>(!q||norm([r.number,r.title,r.issuer,r.summary,r.practical_relevance,r.relevant_articles,r.relationship,r.notes].join(' ')).includes(q))&&(!g||r.group===g)&&(!s||(s==='original'?original(r.verification_status):s==='secondary'?r.verification_status==='secondary':!original(r.verification_status)&&r.verification_status!=='secondary')));
  rows.sort(compareLegal);updateLegalHeaders();
  $('legalCount').textContent=rows.length+' / '+D.legal.length+' văn bản · '+legalSortLabels[legalSort.key]+(legalSort.direction==='descending'?' giảm dần':' tăng dần')+' · Ô chưa rõ luôn ở cuối';
  $('legalRows').innerHTML=rows.map(r=>'<tr data-document-id="'+e(r.document_id)+'"><td><span class="source-id">'+e(r.number)+'</span><span class="title">'+e(r.title)+'</span><span class="tag">'+e(r.group)+'</span><div class="small">'+e(r.issuer)+'</div></td><td>'+date(r.issued_date)+'<div class="small">Hiệu lực từ:<br>'+date(r.effective_date)+'</div></td><td class="legal-description"><p>'+e(r.summary)+'</p><p class="legal-relevance"><strong>Điểm cần đọc: </strong>'+e(r.practical_relevance)+'</p><div class="small">'+e(r.summary_basis)+'</div></td><td><span class="tag '+(original(r.verification_status)?'pdf':'warn')+'">'+legalLabel(r.verification_status)+'</span><p class="small">'+e(r.current_status)+'</p><details><summary>Quan hệ và kiểm chứng</summary>'+(r.relevant_articles?'<p><strong>Điều khoản:</strong> '+e(r.relevant_articles)+'</p>':'')+(r.relationship?'<p><strong>Quan hệ:</strong> '+e(r.relationship)+'</p>':'')+(r.notes?'<p>'+e(r.notes)+'</p>':'')+'<p>Kiểm tra: '+date(r.checked_on)+'</p></details></td><td><div class="table-links">'+(r.source_url?'<a href="'+e(r.source_url)+'" target="_blank" rel="noopener noreferrer">Trang nguồn ↗</a>':'')+(r.local_file?'<a href="'+e(r.local_file)+'" target="_blank" rel="noopener noreferrer">'+(r.local_file.endsWith('.pdf')?'PDF đã lưu':'Tệp tham chiếu')+' ↗</a>':'')+'</div></td></tr>').join('')||'<tr><td colspan="5" class="empty">Không có văn bản phù hợp bộ lọc.</td></tr>';
}
['legalSearch','legalGroup','legalStatus'].forEach(id=>$(id).addEventListener(id==='legalSearch'?'input':'change',renderLegal));
document.querySelectorAll('[data-legal-sort]').forEach(button=>button.addEventListener('click',()=>{
  const key=button.dataset.legalSort;
  legalSort={key,direction:key===legalSort.key?(legalSort.direction==='ascending'?'descending':'ascending'):(key.endsWith('_date')?'descending':'ascending')};
  renderLegal();
}));
$('resetLegal').addEventListener('click',()=>{
  ['legalSearch','legalGroup','legalStatus'].forEach(id=>$(id).value='');
  legalSort={key:'issued_date',direction:'descending'};renderLegal();
});
document.querySelectorAll('[data-legal-group]').forEach(button=>button.addEventListener('click',()=>{
  $('resetLegal').click();$('legalGroup').value=button.dataset.legalGroup;renderLegal();
  $('legalGroup').focus();
}));
