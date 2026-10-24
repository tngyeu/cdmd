const parseJSON=(s,fallback)=>{try{return JSON.parse(s||'')||fallback}catch{return fallback}};
function areaPair(r){
  let text='<div class="area-pair">'+(r.area_m2?fmt(r.area_m2):'?')+' / '+(r.parcel_area_m2?fmt(r.parcel_area_m2):'?')+'</div>';
  if(!r.parcel_area_m2)text+='<div class="area-context">Chưa rõ tổng thửa</div>';
  if(r.residential_conversion_m2&&Number(r.residential_conversion_m2)!==Number(r.area_m2))text+='<div class="area-context">Sang đất ở: '+fmt(r.residential_conversion_m2)+' m²</div>';
  if(r.area_status==='source_internal_area_conflict')text+='<div class="tag conflict">Số liệu chưa khớp</div>';
  else if(r.area_m2&&r.area_status!=='verified_pdf_identity')text+='<div class="area-context">Chưa khớp đủ số/ngày PDF</div>';
  return text;
}
function detailHTML(r){
  let cs=parseJSON(r.components_json,[]),notes=parseJSON(r.detail_notes_json,[]),initial=parseJSON(r.initial_land_json,{}),post=parseJSON(r.post_land_json,{});
  let label=r.detail_status==='visual_reviewed'?'Đã đọc ảnh PDF':r.detail_status==='text_extracted'?'Đọc từ lớp chữ PDF':r.local_pdf?'PDF cần đọc tiếp':'Chưa có PDF';
  let breakdown=o=>Object.entries(o).map(([c,n])=>e(landLabel(c))+': '+fmt(n)+' m²').join('; ');
  let text='<details class="decision-details"><summary>'+label+(cs.length>1?' · '+cs.length+' phần':'')+'</summary>';
  if(cs.length)text+='<ul>'+cs.map(c=>'<li><strong>'+fmt(c.area_m2)+' m²</strong> '+e(landLabel(c.land_before))+' → '+e(landLabel(c.land_after))+'</li>').join('')+'</ul>';
  if(r.parcel_area_m2)text+='<p><strong>Tổng thửa:</strong> '+fmt(r.parcel_area_m2)+' m².</p>';
  if(Object.keys(initial).length)text+='<p><strong>Trước chuyển:</strong> '+breakdown(initial)+'.</p>';
  if(Object.keys(post).length)text+='<p><strong>Sau chuyển, theo tệp:</strong> '+breakdown(post)+'.</p>';
  if(r.term_after)text+='<p>'+e(r.term_after)+'</p>';
  if(r.land_price_vnd_m2)text+='<p><strong>Giá ghi trong quyết định:</strong> '+fmt(r.land_price_vnd_m2)+' đồng/m².</p>';
  if(notes.length)text+='<ul>'+notes.map(n=>'<li>'+e(n)+'</li>').join('')+'</ul>';
  text+='<p class="small">'+(cs.length?'Các thành phần trên được đọc từ nội dung tệp; mức xác minh số/ngày xem ở cột Xác minh.':e(r.notes))+'</p>';
  if(r.local_pdf&&r.detail_pdf_pages)text+='<p>'+r.detail_pdf_pages.split(',').map(p=>'<a target="_blank" rel="noopener noreferrer" href="'+e(r.local_pdf)+'#page='+e(p)+'">PDF trang '+e(p)+' ↗</a>').join(' · ')+'</p>';
  return text+'<p class="small">Đọc nội dung: '+date(r.detail_checked_on)+' · Kiểm tra nguồn: '+date(r.checked_on)+'</p></details>';
}
function detailMatches(r){
  const f=$('detailFilter').value;
  return !f||(f==='parcel'&&r.parcel_area_m2)||(f==='visual'&&r.detail_status==='visual_reviewed')||(f==='mixed'&&parseJSON(r.components_json,[]).length>1)||(f==='issues'&&parseJSON(r.detail_flags_json,[]).length)||(f==='components'&&parseJSON(r.components_json,[]).length);
}
