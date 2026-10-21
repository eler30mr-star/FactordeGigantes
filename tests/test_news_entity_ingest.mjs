import test from "node:test";
import assert from "node:assert/strict";
import {validateNewsEntities,storeNewsEntities} from "../src/news-entity-ingest.mjs";

function report(){
 return {provider:"wikidata_news_company_resolution_v1",
  collected_on:new Date().toISOString().slice(0,10),
  headlines_examined:2,wikidata_searches:2,wikidata_requests_max:17,lookup_errors:0,
  candidate_count:1,market_study_complete:false,ready_for_script:false,ready_for_youtube:false,
  candidates:[{wikidata_id:"Q53268",news_id:"news-"+"a".repeat(32),
   matched_name:"Toyota",article_headline:"Toyota anuncia innovación industrial en América",
   news_url:"https://news.google.com/rss/articles/TEST",
   source_label:"Medio de ejemplo",
   wikidata_url:"https://www.wikidata.org/wiki/Q53268",
   official_website_candidate:"https://global.toyota/",
   evidence_method:"wikidata_p31_and_exact_label_in_headline_v1",
   identity_verified_in_article:false,primary_source_verified:false,
   youtube_market_verified:false,editorial_authorized:false}]};
}
function db(){
 const batches=[];return {batches,prepare(sql){return {bind(...params){return {sql,params}}}},
 async batch(stmts){batches.push(stmts);return stmts.map(()=>({success:true}))}};
}
test("persistencia solo de entidad sugerida y expediente pendiente",async()=>{
 const d=db(),r=report();
 assert.equal(validateNewsEntities(r).length,1);
 const one=await storeNewsEntities(d,r),two=await storeNewsEntities(d,r);
 assert.equal(one.run_id,two.run_id);
 assert.equal(one.candidates_seen,1);
 assert.equal(one.primary_sources_verified,false);
 assert.equal(one.automatic_publication_allowed,false);
 assert.equal(d.batches[0].length,2);
 assert.ok(d.batches[0][1].sql.includes("ON CONFLICT"));
});
test("no acepta identidades engañosas, SSRF ni autorizaciones falsas",async()=>{
 const changes=[
  x=>x.candidates[0].wikidata_url="https://www.wikidata.org.evil.test/wiki/Q53268",
  x=>x.candidates[0].news_url="https://localhost/private",
  x=>x.candidates[0].matched_name="SpaceX",
  x=>x.candidates[0].primary_source_verified=true,
  x=>x.candidates[0].editorial_authorized=true,
  x=>x.candidates[0].official_website_candidate="http://internal.test",
  x=>x.candidates[0].wikidata_id="Q0",
  x=>x.candidate_count=0,
 ];
 for(const change of changes){
  const r=report(),d=db();change(r);
  await assert.rejects(storeNewsEntities(d,r));
  assert.equal(d.batches.length,0);
 }
});
test("puede registrar corrida real sin coincidencias, no inventa empresas",async()=>{
 const r=report(),d=db();r.candidates=[];r.candidate_count=0;
 const out=await storeNewsEntities(d,r);
 assert.equal(out.candidates_seen,0);
 assert.equal(d.batches[0].length,1);
});
