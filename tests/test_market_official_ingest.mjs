import test from "node:test";
import assert from "node:assert/strict";
import {validateOfficialEvidence,storeOfficialEvidence,readOfficialEvidence} from "../src/market-official-ingest.mjs";
const today=()=>new Date().toISOString().slice(0,10);
function report(){
 return {provider:"wikidata_p856_safe_official_fetch_v1",
  collected_on:today(),attempted:1,readable:1,primary_facts_verified:0,
  market_study_complete:false,research_automatic:false,ready_for_script:false,ready_for_youtube:false,
  evidence:[{wikidata_id:"Q53268",company:"Toyota",
   official_website_candidate:"https://global.toyota/",
   identified_by:"wikidata_p856_via_news",status:"candidate_page_readable",
   resolved_url:"https://global.toyota/",content_sha256:"a".repeat(64),readable_blocks:2,
   document_link_candidates:[{url:"https://global.toyota/report.pdf",
     document_fetched:false,ownership_verified:false}],
   short_excerpt:"Texto de prueba sobre las operaciones de una empresa de automóviles.",
   source_identity_verified:false,facts_verified:0,rights_verified:false,
   publication_authorized:false}]};
}
function db(){
 const batches=[],queries=[];
 return {batches,queries,prepare(sql){queries.push(sql);return {
 bind(...params){return {sql,params,async all(){return {results:[]};}}},
 async all(){return {results:[]};}
 }},async batch(stmts){batches.push(stmts);return stmts.map(()=>({success:true}))}};
}
test("guarda hashes de páginas con fuente y sin verificar hechos",async()=>{
 const d=db(),r=report();assert.equal(validateOfficialEvidence(r).length,1);
 const x=await storeOfficialEvidence(d,r),y=await storeOfficialEvidence(d,r);
 assert.equal(x.run_id,y.run_id);
 assert.equal(x.pages_readable,1);
 assert.equal(x.primary_facts_verified,0);
 assert.equal(x.automatic_publication_allowed,false);
 assert.equal(d.batches[0].length,2);
});
test("rechaza sitios no HTTPS, hashes falsos y atribuciones comerciales",async()=>{
 const edits=[
  r=>r.evidence[0].official_website_candidate="http://global.toyota/",
  r=>r.evidence[0].resolved_url="https://localhost/admin",
  r=>r.evidence[0].content_sha256="not-a-hash",
  r=>r.evidence[0].rights_verified=true,
  r=>r.evidence[0].source_identity_verified=true,
  r=>r.evidence[0].facts_verified=1,
  r=>r.evidence[0].publication_authorized=true,
  r=>r.evidence[0].document_link_candidates[0].document_fetched=true,
  r=>r.readable=2
 ];
 for(const edit of edits){
  const r=report(),d=db();edit(r);
  await assert.rejects(storeOfficialEvidence(d,r));
  assert.equal(d.batches.length,0);
 }
});
test("perfila fallos de red sin simular respuestas",async()=>{
 const r=report();
 Object.assign(r.evidence[0],{status:"candidate_unreachable",resolved_url:null,
   content_sha256:null,readable_blocks:0,document_link_candidates:[],short_excerpt:null});
 r.readable=0;
 const x=await storeOfficialEvidence(db(),r);
 assert.equal(x.pages_readable,0);
});
test("consulta oficial solo informativa, sin autorización",async()=>{
 const d=db(),out=await readOfficialEvidence(d,new URL("https://factor.test/api/market/official?limit=20"));
 assert.equal(out.ok,true);
 assert.equal(out.primary_facts_verified,0);
 assert.equal(out.automatic_publication_allowed,false);
 assert.equal((await readOfficialEvidence(d,new URL("https://factor.test/api/market/official?limit=300"))).status,400);
});
