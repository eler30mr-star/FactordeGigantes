import test from "node:test";
import assert from "node:assert/strict";
import {validatePdfEvidence,storePdfEvidence,readPdfEvidence} from "../src/market-pdf-ingest.mjs";
const today=()=>new Date().toISOString().slice(0,10);
function report(){
 return {provider:"official_pdf_evidence_v1",collected_on:today(),attempted:1,text_extracted:1,
  verified_claim_count:0,research_ready:false,script_authorized:false,publication_authorized:false,
  documents:[{wikidata_id:"Q53268",company:"Toyota",
   source_page:"https://global.toyota/",
   document_url:"https://global.toyota/reports/annual.pdf",
   state:"text_extracted",resolved_url:"https://global.toyota/reports/annual.pdf",
   sha256:"a".repeat(64),pages_total:11,facts_verified:0,copyright_permission_verified:false,
   fragments:[{page:4,block_index:0,locator:"PDF página 4, bloque 1",
    excerpt:"Fixture document excerpt about a corporate industrial report, not an actual fact, repeated as demonstrative source material.",
    verification_state:"uncorroborated"}]}]};
}
function db(){
 const writes=[],qs=[];
 return {writes,qs,prepare(sql){qs.push(sql);return {
  bind(...params){return {sql,params,async all(){return {results:[]}}}},
  async all(){return {results:[]}}}},async batch(stmts){writes.push(stmts);return stmts.map(()=>({success:true}))}};
}
test("persistencia D1 por lote: corrida, documento, fragmento paginado",async()=>{
 const d=db(),r=report();
 assert.equal(validatePdfEvidence(r).frags.length,1);
 const x=await storePdfEvidence(d,r),y=await storePdfEvidence(d,r);
 assert.equal(x.run_id,y.run_id);
 assert.equal(x.documents,1);
 assert.equal(x.fragments,1);
 assert.equal(x.verified_claim_count,0);
 assert.equal(x.automatic_publication_allowed,false);
 assert.equal(d.writes[0].length,3);
 assert.ok(d.writes[0].every(s=>s.sql.startsWith("INSERT OR IGNORE")));
});
test("nunca recibe páginas fabricadas, derechos marcados o enlaces ajenos",async()=>{
 const changes=[
  r=>r.documents[0].fragments[0].locator="Página 9",
  r=>r.documents[0].fragments[0].page=12,
  r=>r.documents[0].fragments[0].verification_state="verified",
  r=>r.documents[0].sha256="bad",
  r=>r.documents[0].document_url="https://other.example/annual.pdf",
  r=>r.documents[0].copyright_permission_verified=true,
  r=>r.publication_authorized=true,
  r=>r.text_extracted=0,
  r=>r.documents[0].state="fetch_failed"
 ];
 for(const edit of changes){
  const d=db(),r=report();edit(r);
  await assert.rejects(storePdfEvidence(d,r),RangeError);
  assert.equal(d.writes.length,0);
 }
});
test("si no hay documentos, registra observación vacía sin inventar material",async()=>{
 const r=report();r.documents=[];r.attempted=0;r.text_extracted=0;
 const result=await storePdfEvidence(db(),r);
 assert.equal(result.documents,0);
 assert.equal(result.fragments,0);
});
test("GET privado limita resultados y mantiene puerta editorial",async()=>{
 const d=db(),o=await readPdfEvidence(d,new URL("https://factor.test/api/market/pdf?limit=20"));
 assert.equal(o.ok,true);
 assert.equal(o.facts_verified,0);
 assert.equal(o.automatic_publication_allowed,false);
 assert.equal((await readPdfEvidence(d,new URL("https://factor.test/api/market/pdf?limit=99"))).status,400);
});
