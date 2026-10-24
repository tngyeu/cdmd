const vn = (n,p=2) => Number(n).toLocaleString('vi-VN',{maximumFractionDigits:p});

export function createQuotaBrief(d) {
  const years=5,months=60,mean=150,gain=d.gain_m2,total=d.households.households;
  const capacityRows=d.households.capacity_scenarios.map(r=>({...r,annual_equivalent:gain/r.mean_m2/years}));
  const monthlyCapacity= gain/mean/months;
  const capacityPer1000=monthlyCapacity/total*1000;
  const benchmarkRows=d.observed_comparisons.map(r=>({...r,capacity_to_observed_rate:capacityPer1000/r.cases_per_1000_households_month}));
  const east=benchmarkRows.find(r=>r.locality==='Phường Đông A');
  const reference=benchmarkRows.find(r=>r.locality==='Xã Khánh Thiện');
  const annualCases=reference.count*12/reference.period_months,periodCases=annualCases*years;
  const projection={source_locality:reference.locality,source_count:reference.count,source_period_months:reference.period_months,period_start:'2026-01-01',period_end:'2030-12-31',annual_cases:annualCases,period_cases:periodCases,mean_m2:mean,area_ha:periodCases*mean/10000,province_rank_confirmed:false,ranking_scope:'Ba nguồn đối chiếu trong hồ sơ; khác kỳ và cách ghi nhận'};
  const data={mean_m2:mean,years,months,full_ha:gain/10000,capacity_rows:capacityRows,monthly_capacity:monthlyCapacity,monthly_capacity_per_1000_households:capacityPer1000,benchmark_rows:benchmarkRows,projection};
  const lines=[
    '# Duy Tân: 50,26 ha đáp ứng được bao nhiêu trường hợp?', '',
    '## 1. Căn cứ và chỉ tiêu', '',
    '**Quyết định 3279/QĐ-UBND ngày 30/08/2026, UBND tỉnh Ninh Bình:** Điều 1 và Phụ lục 121 ghi ODT Duy Tân từ **269,76 ha (2025) lên 320,02 ha (2030)**, tăng ròng **50,26 ha**; ONT bằng 0. [Trang tỉnh](https://ninhbinh.gov.vn/?pageid=27160&p_steering=48598) · [Phụ lục, tr. 241](../documents/quy_hoach/3279_2026_phu_luc_129.pdf#page=241).', '',
    '[Điều 2 khoản 4](../documents/quy_hoach/3279_2026_quyet_dinh.pdf#page=3) yêu cầu chuyển mục đích phù hợp chỉ tiêu và báo cáo thực hiện. **50,26 ha là mức tăng cả kỳ, chưa phải phần còn lại cho hộ.** Đã đọc số/ngày và chữ ký/dấu của quyết định; riêng dòng dẫn số/ngày trên phụ lục còn trống.', '',
    '## 2. Tính ngược từ 50,26 ha', '',
    `Duy Tân có **${vn(total,0)} hộ, ${vn(d.households.population,0)} người**, theo [nguồn phường công bố 04/06/2026](${d.households.source_url}). Chia **502.600 m²** cho diện tích chuyển mỗi trường hợp:`, '',
    '| Phần chuyển/trường hợp | Số trường hợp tương đương | So với số hộ Duy Tân | Chia đều 5 năm |',
    '| ---: | ---: | ---: | ---: |',
    ...capacityRows.map(r=>`| ${r.mean_m2} m² | ${vn(r.household_capacity,0)} | ${vn(r.share_of_baseline_percent)}% | ≈ ${vn(r.annual_equivalent,0)}/năm |`), '',
    '**Mốc 150 m²:** khoảng **3.350 trường hợp**, hay **670/năm ≈ 56/tháng** trong cả kỳ **01/01/2026–31/12/2030**. Tương đương số hộ chỉ khi mỗi hộ chuyển một lần; đây là sức chứa quy đổi, chưa phải số hộ có nhu cầu hoặc được cấp phép.', '',
    '## 3. So với Đông A, mức tăng này khá lớn', '',
    `**Hai phường có quy mô gần nhau:** Đông A có [9.406 hộ, 31.980 người](${east.demographics.source_url}); Duy Tân có **8.934 hộ, 27.849 người**.`, '',
    `- **Đông A thực tế công bố:** [15 hồ sơ chuyển mục đích được tiếp nhận, giải quyết trong tháng 8/2026](${east.source_url}).`,
    '- **50,26 ha của Duy Tân:** quy đổi được khoảng **56 trường hợp mỗi tháng trong 5 năm**, nếu mỗi trường hợp chuyển 150 m² và dùng toàn bộ mức tăng.', '',
    '**Hiểu đơn giản:** sức chứa quy đổi này **gần gấp 4 lần** số hồ sơ Đông A công bố trong tháng đó. Vì vậy, **50,26 ha là mức tăng khá lớn so với nhịp hồ sơ đang quan sát được ở Đông A**.', '',
    '**Để chốt còn dư hay thiếu:** cần phường cung cấp phần đã dùng, đã phân bổ cho dự án và còn dành cho hộ. Số 15 là hồ sơ trong một tháng, chưa phải 15 hộ đã được phép chuyển sang đất ở hoặc mức nhu cầu cả năm.', '',
    '<details id="higherPace"><summary>Khánh Thiện: 82 trường hợp/quý, quy đổi đến 2030</summary>', '',
    `Theo [báo cáo trên cổng xã Khánh Thiện](${reference.source_url}), xã đã cho phép chuyển mục đích **${reference.count} trường hợp trong quý I/2026**, tính từ **01/01/2026**. Đây là mức ghi nhận cao nhất trong ba nguồn đang đối chiếu; chưa có thống kê đủ để khẳng định nhiều nhất toàn tỉnh.`, '',
    `**Nếu Duy Tân có cùng nhịp ${reference.count} trường hợp/quý** trong giai đoạn **01/01/2026–31/12/2030**, sẽ tương đương khoảng **${vn(periodCases,0)} trường hợp**. Giả định mỗi trường hợp chuyển sang đất ở ${mean} m², cần **${vn(projection.area_ha)} ha — gần một nửa mức tăng 50,26 ha**.`, '',
    '*Đây là ngoại suy từ báo cáo quý I; nguồn chưa nêu diện tích hoặc xác nhận mọi trường hợp đều chuyển sang đất ở.*', '',
    '</details>', ''
  ];
  return {data,markdown:lines.join('\n')};
}
