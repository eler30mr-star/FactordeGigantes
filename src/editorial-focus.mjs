// Editorial relevance is separate from source support and human approval.
export async function editorialFocusSha(topic,claims){
 const text=JSON.stringify({topic,claims:claims.map(c=>c.statement)});
 return [...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(text)))].map(n=>n.toString(16).padStart(2,'0')).join('');
}
export async function editorialFocusReady(report){
 if(!report.selected_episode_id||!report.editorial_topic)return true; // Historical queue reports keep their existing contract.
 const r=report.editorial_focus_review,claims=report.candidate_claims;
 if(!r||r.schema!=='fdg_editorial_focus_v1'||r.status!=='aligned'||r.topic!==report.editorial_topic||
   r.publication_authorized!==false||!Array.isArray(r.judgments)||r.judgments.length!==claims.length||!claims.length||
   r.claims_sha256!==await editorialFocusSha(report.editorial_topic,claims))return false;
 const seen=new Set();let central=0;
 for(const row of r.judgments){
  if(!Number.isSafeInteger(row.claim_index)||row.claim_index<1||row.claim_index>claims.length||seen.has(row.claim_index)||
   !['central','supporting'].includes(row.relevance)||typeof row.reason!=='string'||row.reason.length<10||row.reason.length>300)return false;
  seen.add(row.claim_index);if(row.relevance==='central')central++;
 }
 return central>=Math.ceil(claims.length/2);
}
