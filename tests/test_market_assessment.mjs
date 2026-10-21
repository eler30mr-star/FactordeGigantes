import test from "node:test";
import assert from "node:assert/strict";
import {evaluateMarketEvidence,assessMarketFromD1,readMarketAssessments} from "../src/market-assessment.mjs";
const DAY=new Date().toISOString().slice(0,10);
function dbr(){
 const writes=[],sqls=[];
 const db={writes,sqls,prepare(sql){sqls.push(sql);return {
  bind(...params){return {sql,params,async all(){return {results:[]}}}},
  async all(){
   if(sql.includes("FROM market_entities e"))return {results:[
    {wikidata_id:"Q53268",title:"Empresa pública",wikipedia_windows:2}]};
   if(sql.includes("FROM market_news_entity_candidates"))return {results:[
    {wikidata_id:"Q53268",title:"Empresa pública",mentions:3},
    {wikidata_id:"Q777",title:"Entidad emergente",mentions:1}]};
   if(sql.includes("FROM market_youtube_queries"))return {results:[
    {wikidata_id:"Q53268",regions:2}]};
   return {results:[]};
  }}},async batch(x){writes.push(x);return x.map(()=>({success:true}))}};
 return db;
}
test("detecta cobertura múltiple pero bloquea guion y selección sin documentos primarios",()=>{
 const r=evaluateMarketEvidence({wiki:[{wikidata_id:"Q53268",title:"Toyota",wikipedia_windows:3}],
  news:[{wikidata_id:"Q53268",title:"Toyota",mentions:2}],
  youtube:[{wikidata_id:"Q53268",regions:2}]},DAY);
 assert.equal(r.candidates_evaluated,1);
 assert.equal(r.candidates[0].readiness,"awaiting_primary");
 assert.equal(r.candidates[0].news_mention_count,2);
 assert.equal(r.selected_wikidata_id,null);
 assert.equal(r.qualified_count,0);
 assert.equal(r.candidates[0].qualified_for_research,false);
});
test("falta YouTube y fuentes primarias; no convierte Wikidata en mercado",()=>{
 const r=evaluateMarketEvidence({wiki:[{wikidata_id:"Q123",title:"Firma",wikipedia_windows:2}]},DAY);
 assert.equal(r.candidates[0].readiness,"awaiting_youtube_and_primary");
 assert.equal(r.selected_wikidata_id,null);
 assert.equal(r.candidates[0].youtube_region_samples,0);
 assert.equal(r.automatic_publication_allowed,false);
});
test("consulta tablas D1 y persiste evaluación reproducible, sin autorizar",async()=>{
 const db=dbr();
 const a=await assessMarketFromD1(db),b=await assessMarketFromD1(db);
 assert.equal(a.run_id,b.run_id);
 assert.equal(a.candidates_evaluated,2);
 assert.equal(a.qualified_count,0);
 assert.equal(db.writes.length,2);
 assert.equal(db.writes[0].length,3);
 assert.ok(db.sqls.every(q=>q.startsWith("SELECT ")||q.startsWith("INSERT OR IGNORE")));
});
test("vista administrativa limita consultas",async()=>{
 const db=dbr();
 const a=await readMarketAssessments(db,new URL("https://factor.test/api/market/opportunities?limit=20"));
 assert.equal(a.ok,true);
 assert.equal(a.selected_for_research,null);
 assert.equal((await readMarketAssessments(db,new URL("https://factor.test/api/market/opportunities?limit=300"))).status,400);
});
