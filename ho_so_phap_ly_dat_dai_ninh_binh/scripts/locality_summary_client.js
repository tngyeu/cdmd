// Work in thousandths of m², avoiding floating-point accumulation in displayed totals.
const areaUnits=s=>Math.round(Number(s||0)*1000);
const summaryFields=['locality','records','known_area_records','known_area_m2','residential_area_m2','area_m2','pending_area_m2','missing_area_records','excluded_area_records','unread_area_records'];
function aggregateLocalities(rows,type,localities){
  const groups=new Map(localities.map(locality=>[locality,{locality,records:0,known_area_records:0,known_area_m2:0,residential_area_m2:0,area_m2:0,pending_area_m2:0,missing_area_records:0,excluded_area_records:0,unread_area_records:0}]));
  for(const r of rows){
    if(!groups.has(r.locality))continue;
    const g=groups.get(r.locality);g.records++;
    const conflict=r.pdf_identity_status==='shared_pdf_conflict'||r.area_status==='source_internal_area_conflict';
    const usable=!conflict&&r.area_m2&&['verified_pdf_identity','official_attachment_identity_pending'].includes(r.area_status);
    if(!usable){g.missing_area_records++;if(conflict)g.excluded_area_records++;else g.unread_area_records++;continue;}
    let total=areaUnits(r.area_m2),home=areaUnits(r.residential_conversion_m2||(['ONT','ODT','DAT_O'].includes(r.land_after)?r.area_m2:0));
    if(type&&type.includes('->')){
      const cs=JSON.parse(r.components_json||'[]').filter(c=>c.land_before+'->'+c.land_after===type);
      if(cs.length){total=cs.reduce((n,c)=>n+areaUnits(c.area_m2),0);home=cs.reduce((n,c)=>n+(['ONT','ODT','DAT_O'].includes(c.land_after)?areaUnits(c.area_m2):0),0);}
      else if(r.conversion_group!==type){g.missing_area_records++;g.unread_area_records++;continue;}
    }
    g.known_area_records++;g.known_area_m2+=total;g.residential_area_m2+=home;
    if(r.area_status==='verified_pdf_identity')g.area_m2+=total;else g.pending_area_m2+=total;
  }
  return [...groups.values()].map(g=>({...g,known_area_m2:g.known_area_m2/1000,residential_area_m2:g.residential_area_m2/1000,area_m2:g.area_m2/1000,pending_area_m2:g.pending_area_m2/1000}));
}
let summaryDisplayed=[];
let summarySort={key:'records',direction:'descending'};
const summarySortLabels={locality:'Tên xã/phường',records:'Số quyết định',known_area_m2:'Tổng diện tích đọc được',residential_area_m2:'Diện tích sang đất ở',area_m2:'Diện tích đã xác minh',pending_area_m2:'Diện tích chờ đối chiếu',missing_area_records:'Số bản ghi chưa cộng diện tích'};
function compareLocalitySummary(a,b,key=summarySort.key,direction=summarySort.direction){
  const isArea=['known_area_m2','residential_area_m2','area_m2','pending_area_m2'].includes(key);
  const missingA=isArea&&!a.known_area_records,missingB=isArea&&!b.known_area_records;
  if(missingA!==missingB)return missingA?1:-1;
  const value=key==='locality'?a.locality.localeCompare(b.locality,'vi'):Number(a[key])-Number(b[key]);
  return (direction==='ascending'?value:-value)||a.locality.localeCompare(b.locality,'vi');
}
function updateSummarySortHeaders(){
  document.querySelectorAll('.locality-summary-table [data-summary-sort]').forEach(button=>{
    const key=button.dataset.summarySort,active=key===summarySort.key;
    button.setAttribute('aria-pressed',String(active));
    button.closest('th').setAttribute('aria-sort',active?summarySort.direction:'none');
    if(active)button.dataset.direction=summarySort.direction;else delete button.dataset.direction;
    const next=active?(summarySort.direction==='ascending'?'giảm dần':'tăng dần'):(key==='locality'?'tăng dần':'giảm dần');
    button.setAttribute('aria-label',summarySortLabels[key]+': sắp xếp '+next);
  });
  $('summarySort').value=summarySort.key;
}
function renderLocalitySummary(){
  const query=norm($('summarySearch').value),showEmpty=$('summaryShowEmpty').checked,selected=$('localityFilter').value;
  const names=D.coverage.map(r=>r.locality).filter(n=>!selected||n===selected);
  summaryDisplayed=aggregateLocalities(filtered,$('typeFilter').value,names).filter(g=>(showEmpty||g.records||selected)&&(!query||norm(g.locality).includes(query)));
  summaryDisplayed.sort((a,b)=>compareLocalitySummary(a,b));
  updateSummarySortHeaders();
  const cells=(g,total=false)=>{
    const numberOrUnknown=k=>g.known_area_records?fmt(g[k]):'—';
    const name=total?'<strong>Tổng các dòng đang hiển thị</strong>':'<button type="button" class="locality-link" data-locality="'+e(g.locality)+'">'+e(g.locality)+'</button>';
    return '<td>'+name+'</td><td class="num">'+g.records+(g.records?'':'<div class="small">Chưa tìm thấy trong phạm vi lọc</div>')+'</td><td class="num"><strong>'+numberOrUnknown('known_area_m2')+'</strong><div class="small">'+g.known_area_records+' quyết định có diện tích</div></td><td class="num">'+numberOrUnknown('residential_area_m2')+'</td><td class="num verified-area">'+numberOrUnknown('area_m2')+'</td><td class="num pending-area">'+numberOrUnknown('pending_area_m2')+'</td><td class="num">'+g.missing_area_records+(g.excluded_area_records?'<div class="small">Trong đó '+g.excluded_area_records+' xung đột / mâu thuẫn</div>':'')+'</td>';
  };
  $('localitySummaryRows').innerHTML=summaryDisplayed.map(g=>'<tr>'+cells(g)+'</tr>').join('')||'<tr><td colspan="7" class="empty">Không có địa phương phù hợp.</td></tr>';
  const total={locality:'Tổng',records:0,known_area_records:0,known_area_m2:0,residential_area_m2:0,area_m2:0,pending_area_m2:0,missing_area_records:0,excluded_area_records:0,unread_area_records:0};
  for(const g of summaryDisplayed)for(const k of Object.keys(total))if(k!=='locality')total[k]+=Number(g[k]);
  $('localitySummaryTotal').innerHTML='<tr>'+cells(total,true)+'</tr>';
  $('summaryScope').textContent=summaryDisplayed.length+' xã/phường · '+total.records+' bản ghi quyết định trong phạm vi lọc · '+total.known_area_records+' bản ghi đủ số liệu để cộng diện tích · '+summarySortLabels[summarySort.key]+(summarySort.direction==='ascending'?' tăng dần.':' giảm dần.');
  $('localitySummaryRows').querySelectorAll('[data-locality]').forEach(b=>b.onclick=()=>{$('localityFilter').value=b.dataset.locality;renderDecisions();location.hash='decisions-list';});
}
function initLocalitySummary(){
  $('summarySearch').addEventListener('input',renderLocalitySummary);
  $('summarySort').addEventListener('change',()=>{summarySort={key:$('summarySort').value,direction:$('summarySort').value==='locality'?'ascending':'descending'};renderLocalitySummary();});
  document.querySelectorAll('.locality-summary-table [data-summary-sort]').forEach(button=>button.addEventListener('click',()=>{
    const key=button.dataset.summarySort;
    summarySort={key,direction:summarySort.key===key?(summarySort.direction==='ascending'?'descending':'ascending'):(key==='locality'?'ascending':'descending')};
    renderLocalitySummary();
  }));
  $('summaryShowEmpty').addEventListener('change',renderLocalitySummary);
  $('summaryExport').onclick=()=>{
    const quote=s=>'"'+String(s??'').replaceAll('"','""')+'"';
    const csv='\uFEFF'+[summaryFields.map(quote).join(','),...summaryDisplayed.map(r=>summaryFields.map(k=>quote(r[k])).join(','))].join('\r\n');
    const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='thong_ke_xa_phuong_bo_loc.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  };
}
