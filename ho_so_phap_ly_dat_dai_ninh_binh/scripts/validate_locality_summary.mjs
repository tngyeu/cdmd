import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
const data=JSON.parse(fs.readFileSync(root+'data/display_data.json','utf8'));
const context=vm.createContext({});
vm.runInContext(fs.readFileSync(root+'scripts/locality_summary_client.js','utf8'),context);
const names=data.coverage.map(r=>r.locality);
const rows=context.aggregateLocalities(data.decisions,'',names);
for(const actual of rows){
  const expected=data.locality_summary.find(r=>r.locality===actual.locality);
  for(const k of ['records','known_area_records','known_area_m2','residential_area_m2','area_m2','pending_area_m2','missing_area_records','excluded_area_records','unread_area_records'])assert.equal(Number(actual[k]),Number(expected[k]),actual.locality+' '+k);
}
// One mixed decision changes 603 m² but only 208 m² becomes residential land.
const mixed=data.decisions.find(r=>r.decision_id==='xaminhtan|941/QĐ-UBND|2026-06-12');
const all=context.aggregateLocalities([mixed],'',[mixed.locality])[0];
assert.equal(all.records,1);assert.equal(all.known_area_m2,603);assert.equal(all.residential_area_m2,208);
const specific=context.aggregateLocalities([mixed],'CLN->ONT',[mixed.locality])[0];
assert.equal(specific.records,1);assert.equal(specific.known_area_m2,112);assert.equal(specific.residential_area_m2,112);
// A source with contradictory areas remains visible, but contributes no area.
const conflict=data.decisions.find(r=>r.decision_id==='xaphulong|252/QĐ-UBND|2026-03-31');
const bad=context.aggregateLocalities([conflict],'',[conflict.locality])[0];
assert.equal(bad.records,1);assert.equal(bad.known_area_records,0);assert.equal(bad.known_area_m2,0);assert.equal(bad.excluded_area_records,1);
const empty=context.aggregateLocalities([],'',['Phường Duy Tân'])[0];
assert.equal(empty.records,0);assert.equal(empty.known_area_records,0);
const small={locality:'Xã A',records:2,known_area_records:1,known_area_m2:9};
const large={locality:'Xã B',records:10,known_area_records:1,known_area_m2:100};
for(const direction of ['ascending','descending']){
  assert(context.compareLocalitySummary(small,empty,'known_area_m2',direction)<0,'Unknown area remains last');
}
assert(context.compareLocalitySummary(small,large,'records','ascending')<0,'Numeric count ordering');
assert(context.compareLocalitySummary(small,large,'records','descending')>0,'Reverse count ordering');
assert(context.compareLocalitySummary(small,large,'known_area_m2','ascending')<0,'Numeric area ordering');
console.log('PASS locality summary: 129 localities match Decimal totals; mixed-direction scope and conflicting-area exclusions verified.');
