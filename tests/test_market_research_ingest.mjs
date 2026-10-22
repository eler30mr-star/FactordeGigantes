import test from "node:test";
import assert from "node:assert/strict";
import {validateMarketResearch,storeMarketResearch,readMarketResearch} from "../src/market-research-ingest.mjs";
const day=()=>new Date().toISOString().slice(0,10);
function basic(){
 return {source_report_day:day(),source_provider:"market_official_and_pdf_v1",
  status:"skipped_free_tier_not_authorized",provider:null,
  evidence_manifest:[{id:"E001",wikidata_id:"Q53268",company:"Empresa corporativa",
   url:"https://global.toyota/",page:null,source_class:"potential_official_primary",
   document_sha256:"a".repeat(64),
   excerpt:"Los resultados corporativos de 2026 son citados en un ejemplo de pasaje, pero no están verificados ni deben usarse como afirmaciones reales."}],
  evidence_count:1,candidate_claims:[],missing_questions:[],
  facts_verified_automatically:0,ready_for_script:false,ready_for_youtube:false,
  publication_authorized:false};
}
function db(){
 const batches=[],queries=[];
 return {batches,queries,prepare(sql){queries.push(sql);return {
  bind(...args){return {sql,args,async all(){return {results:[]}}}},
  async all(){return {results:[]}}
 }},async batch(stmts){batches.push(stmts);return stmts.map(()=>({success:true}))}};
}
test("sin autorización: guarda evidencia pública observada sin ninguna llamada IA",async()=>{
 const d=db(),r=basic(),a=await storeMarketResearch(d,r),b=await storeMarketResearch(d,r);
 assert.equal(a.run_id,b.run_id);
 assert.equal(a.status,"skipped_free_tier_not_authorized");
 assert.equal(a.evidence_count,1);
 assert.equal(a.candidate_claim_count,0);
 assert.equal(a.verified_claim_count,0);
 assert.equal(a.automatic_publication_allowed,false);
 assert.equal(d.batches.length,2);
 assert.equal(d.batches[0].length,2);
 assert.ok(d.batches[0].every(x=>x.sql.startsWith("INSERT OR IGNORE")));
});
test("con Gemini simulado cita E001 y detecta números que la evidencia no sustenta",async()=>{
 const d=db(),r=basic();
 Object.assign(r,{status:"candidate_claims_generated",provider:"gemini_free",
  model:"gemini-2.5-flash-lite",prompt_sha256:"b".repeat(64),
  candidate_claims:[
    {statement:"En 2026 se registraron resultados corporativos.",evidence_ids:["E001"],
      status:"candidate_unverified",human_verified:false},
    {statement:"La compañía perdió 8982 millones en 2029.",evidence_ids:["E001"],
      status:"candidate_unverified",human_verified:false}],
  missing_questions:["¿Qué documentos independientes confirman la evolución?"]});
 const result=await storeMarketResearch(d,r);
 assert.equal(result.candidate_claim_count,2);
 assert.equal(result.open_question_count,1);
 const stmts=d.batches[0];
 assert.equal(stmts.length,1+1+2+2+1);
 assert.equal(stmts[3].args[3],"unsupported_numbers_need_review");
 assert.ok(stmts.some(x=>x.sql.includes("market_research_claim_evidence")));
 assert.equal(result.verified_claim_count,0);
});
test("rechaza falsos permisos, citas inexistentes, autores y URLs hostiles",async()=>{
 const cases=[
  x=>x.publication_authorized=true,
  x=>x.facts_verified_automatically=1,
  x=>x.ready_for_script=true,
  x=>x.evidence_manifest[0].source_class="unsourced",
  x=>x.evidence_manifest[0].id="E999",
  x=>x.evidence_manifest[0].url="https://127.0.0.1/protected",
  x=>x.evidence_manifest[0].page=8,
  x=>x.evidence_manifest[0].document_sha256="abcdef",
  x=>x.evidence_manifest[0].excerpt="Short",
  x=>x.status="candidate_claims_generated",
  x=>x.candidate_claims=[{statement:"Una afirmación sobre hechos inexistentes",evidence_ids:["E999"],status:"candidate_unverified",human_verified:false}],
 ];
 for(const fn of cases){
  const d=db(),r=basic();fn(r);
  await assert.rejects(storeMarketResearch(d,r));
  assert.equal(d.batches.length,0);
 }
});
test("sin evidencia recuperada persiste observación vacía y permanece bloqueada",async()=>{
 const r=basic(),d=db();
 Object.assign(r,{status:"skipped_no_documentary_evidence",evidence_manifest:[],evidence_count:0});
 const x=await storeMarketResearch(d,r);
 assert.equal(x.evidence_count,0);
 assert.equal(d.batches[0].length,1);
});
test("consulta administrativa retorna causas de revisión y limita tamaño",async()=>{
 const d=db();const v=await readMarketResearch(d,new URL("https://factor.example/api/market/research?limit=20"));
 assert.equal(v.ok,true);
 assert.equal(v.verified_claim_count,0);
 assert.equal(v.automatic_publication_allowed,false);
 assert.equal((await readMarketResearch(d,new URL("https://factor.example/api/market/research?limit=500"))).status,400);
});
