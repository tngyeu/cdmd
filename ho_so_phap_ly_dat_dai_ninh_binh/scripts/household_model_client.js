function capacityModel(){
  const inputs=['meanArea','quotaArea'];
  if(inputs.some(id=>!$(id).checkValidity()||$(id).value.trim()==='')){
    ['caseCapacity','householdCoverage','annualCapacity','monthlyCapacity'].forEach(id=>$(id).textContent='—');
    $('modelSummary').textContent='Nhập diện tích mỗi trường hợp lớn hơn 0 và diện tích đối chiếu không âm.';
    return;
  }
  const mean=Number($('meanArea').value),ha=Number($('quotaArea').value),cases=Math.floor(ha*10000/mean);
  $('caseCapacity').textContent=fmt(cases,0);
  $('householdCoverage').textContent=fmt(cases/D.households.households*100,2)+'%';
  $('annualCapacity').textContent='≈ '+fmt(ha*10000/mean/5,1);
  $('monthlyCapacity').textContent='≈ '+fmt(ha*10000/mean/60,1);
  $('modelSummary').textContent=fmt(ha)+' ha × 10.000 / '+fmt(mean)+' m² = '+fmt(cases,0)+' trường hợp tương đương. Bình quân chia 5 năm hoặc 60 tháng của cả kỳ 01/01/2026–31/12/2030; chưa trừ phần năm 2026 đã dùng. Quy đổi thành hộ chỉ khi mỗi hộ có một lần chuyển.';
}
['meanArea','quotaArea'].forEach(id=>$(id).addEventListener('input',capacityModel));
$('use106').onclick=()=>{$('meanArea').value='106';capacityModel();};
$('resetModel').onclick=()=>{$('meanArea').value='150';$('quotaArea').value='50.26';capacityModel();};
capacityModel();
