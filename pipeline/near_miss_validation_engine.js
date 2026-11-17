/* Shared, dependency-free calculations for offline review and Node regression tests. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.NearMissValidation=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const VERSION=1;
function polygonValid(points){if(!Array.isArray(points)||points.length<3||points.some(p=>!Array.isArray(p)||p.length!==2||p.some(v=>!Number.isFinite(v)||v<0)||p[0]>720||p[1]>480))return false;return Math.abs(points.reduce((s,p,i)=>{let q=points[(i+1)%points.length];return s+p[0]*q[1]-q[0]*p[1];},0))>1;}
function pet(event,annotation){
 const result={pet_s:null,pet_lower_s:null,pet_upper_s:null,signed_time_difference_lower_s:null,signed_time_difference_upper_s:null,pet_units:'s',pet_eligibility:'not_observable',pet_reason:'Shared physical conflict zone and supported occupancy boundaries not yet annotated'};
 const a=annotation||{},z=a.zone||{},o=a.occupancy||{};
 if(event.event_type!=='pedestrian_crossing')return {...result,pet_eligibility:'not_applicable',pet_reason:'Parallel passing has no established shared physical occupancy region'};
 if(!polygonValid(z.points)||z.physical_identity_confirmed!==true||!(z.justification||'').trim()||!(a.reviewer||'').trim())return result;
 const p=o.pedestrian_exit,c=o.car_entry;
 if(!p||!c)return result;
 for(const q of [p,c]){
  if(q.boundary_supported!==true||!['visible','occluded','uncertain'].includes(q.visibility)||!Number.isInteger(q.frame_low)||!Number.isInteger(q.frame_high)||q.frame_low<1||q.frame_high>event.pts.length||q.frame_high<q.frame_low)return {...result,pet_reason:'Invalid or unsupported boundary bracket; verify neighboring frames and visibility'};
  if(q.visibility!=='visible'&&!(q.notes||'').trim())return {...result,pet_reason:'Occluded/uncertain boundary needs explicit evidence bounding its interval'};
 }
 const times=event.pts,dt=event.frame_interval_s;
 function interval(q){let lo=times[q.frame_low-1],hi=times[q.frame_high-1];if(q.frame_low===q.frame_high){lo=Math.max(0,lo-dt/2);hi+=dt/2;}return [lo,hi];}
 const [pl,ph]=interval(p),[cl,ch]=interval(c),low=cl-ph,high=ch-pl;
 result.signed_time_difference_lower_s=low;result.signed_time_difference_upper_s=high;
 if(high<0)return {...result,pet_eligibility:'temporal_overlap',pet_reason:'Car entry precedes pedestrian exit under supported brackets; negative difference is overlap, not positive PET'};
 if(low<0)return {...result,pet_eligibility:'order_uncertain',pet_reason:'Boundary brackets allow both occupancy overlap and sequential occupancy; PET is N/A'};
 return {...result,pet_lower_s:low,pet_upper_s:high,pet_eligibility:'supported_interval',pet_reason:'Reviewer-supported physical-zone occupancy brackets; frame quantization retained; not independently validated adjudication'};
}
function edgeMinimum(annotation){
 const good=(annotation.edges||[]).filter(r=>r.visibility==='visible'&&Number.isFinite(r.cyclist_x_px)&&Number.isFinite(r.car_x_px));
 if(!good.length)return {selected_min_edge_gap_px:null,selected_min_edge_gap_frame:null,edge_eligible_count:0};
 const best=good.reduce((a,b)=>Math.abs(a.cyclist_x_px-a.car_x_px)<=Math.abs(b.cyclist_x_px-b.car_x_px)?a:b);
 return {selected_min_edge_gap_px:Math.abs(best.cyclist_x_px-best.car_x_px),selected_min_edge_gap_frame:best.frame,edge_eligible_count:good.length};
}
function reviewedEvents(events,annotations){return events.map(e=>{const a=annotations.events.find(a=>a.event_id===e.event_id)||{},p=pet(e,a),m=e.metrics;return {...m,...edgeMinimum(a),...p,supported_pet_screen_flag:p.pet_eligibility==='supported_interval'&&m.screening_pet_s!=null?p.pet_upper_s<m.screening_pet_s:null,possible_pet_screen_flag:p.pet_eligibility==='supported_interval'&&m.screening_pet_s!=null?p.pet_lower_s<m.screening_pet_s:null,manual_edge_total_count:(a.edges||[]).length,manual_edge_count:(a.edges||[]).filter(r=>r.frame>=e.metrics.analysis_first_frame&&r.frame<=e.metrics.analysis_last_frame).length,manual_edge_pct:100*(a.edges||[]).filter(r=>r.frame>=e.metrics.analysis_first_frame&&r.frame<=e.metrics.analysis_last_frame).length/e.metrics.expected_frame_count,reviewer:a.reviewer||'',reviewer_notes:a.notes||'',evasive_action:a.evasive_action||'unknown',review_label:e.metrics.review_label};});}
function csv(rows){const keys=Array.from(new Set(rows.flatMap(r=>Object.keys(r))));const escape=v=>'"'+String(v===undefined||v===null?'':typeof v==='object'?JSON.stringify(v):v).replaceAll('"','""')+'"';return keys.map(escape).join(',')+'\n'+rows.map(r=>keys.map(k=>escape(r[k])).join(',')).join('\n')+'\n';}
function validateAnnotations(data,events){
 if(!data||data.schema_version!==VERSION||!Array.isArray(data.events))throw Error('Expected annotation schema_version 1 and events array');
 const ids=new Set();for(const a of data.events){const e=events.find(e=>e.event_id===a.event_id);if(!e||ids.has(a.event_id))throw Error('Unknown or duplicate event ID');ids.add(a.event_id);if(!Array.isArray(a.edges||[])||!Array.isArray(a.footprints||[])||!a.zone&&a.zone!==undefined||a.zone&&(!Array.isArray(a.zone.points||[])||typeof a.zone!=='object')||a.occupancy&&typeof a.occupancy!=='object'||typeof(a.reviewer||'')!=='string'||typeof(a.notes||'')!=='string')throw Error('Invalid annotation collection types');for(const p of a.footprints||[])if(!Number.isInteger(p.frame)||p.frame<1||p.frame>e.pts.length||!polygonValid(p.points))throw Error('Invalid footprint polygon/frame');if(a.source_sha256!==e.source_sha256)throw Error('Source video hash mismatch for '+a.event_id);
  for(const r of a.edges||[]){if(!Number.isInteger(r.frame)||r.frame<1||r.frame>e.pts.length||![r.cyclist_x_px,r.car_x_px].every(v=>Number.isFinite(v)&&v>=0&&v<=720))throw Error('Invalid edge coordinates/frame');}
  if(new Set((a.edges||[]).map(r=>r.frame)).size!==(a.edges||[]).length)throw Error('Duplicate edge frame');
  if(a.zone&&a.zone.points&&a.zone.points.length&&!polygonValid(a.zone.points))throw Error('Conflict zone must be a non-degenerate image polygon');
 }
 return data;
}
return {VERSION,polygonValid,pet,edgeMinimum,reviewedEvents,csv,validateAnnotations};
});
