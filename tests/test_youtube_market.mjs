import test from "node:test";
import assert from "node:assert/strict";
import {validateYoutubeStudy,persistYoutubeStudy,readYoutubeMarket} from "../src/youtube-market.mjs";
const today=()=>new Date().toISOString().slice(0,10);
const prior=(n)=>new Date(Date.parse(today()+"T00:00:00Z")-n*86400000).toISOString().slice(0,10);
function report(){
 const videos=[1,2,3].map(i=>({
  video_id:"videoid000"+i,url:"https://www.youtube.com/watch?v=videoid000"+i,
  view_count:i*1000,published_at:prior(4),channel_id:"UC"+String(i).repeat(22)
 }));
 const q=region=>({wikidata_id:"Q16956307",topic:"Empresa documental",region,
  observed_on:today(),sample_size:3,uploads_sampled:3,
  median_daily_views:500,distinct_channels:3,evidence_state:"observed_sample",
  videos:structuredClone(videos)});
 return {provider:"youtube_data_api_v3",collected_on:today(),candidate_count:1,
  region_count:2,queries_attempted:2,quota_units_max:202,state:"measured",
  queries:[q("MX"),q("ES")],complete_comparisons:2,market_study_complete:false,
  research_automatic:false,ready_for_script:false,ready_for_youtube:false,
  automatic_publication_allowed:false};
}
function db(){
 const writes=[];
 return {writes,prepare(sql){return {bind(...params){return {sql,params,
  async all(){return {results:[]};}}},async all(){return {results:[]};}};},
  async batch(statements){writes.push(statements);return statements.map(()=>({success:true}));}};
}
test("valida fuentes YouTube y persiste transacción idempotente de dos regiones",async()=>{
 const d=db(),r=report();
 assert.equal(validateYoutubeStudy(r).queries.length,2);
 const first=await persistYoutubeStudy(d,r),again=await persistYoutubeStudy(d,r);
 assert.equal(first.run_id,again.run_id);
 assert.equal(first.queries_seen,2);
 assert.equal(first.video_observations,6);
 assert.equal(first.automatic_publication_allowed,false);
 assert.equal(d.writes.length,2);
 assert.equal(d.writes[0].length,9);
 assert.ok(d.writes[0].every(s=>s.sql.startsWith("INSERT OR IGNORE")));
});
test("rechaza datos privados supuestos, muestras falsas y falsos permisos antes de DB",async()=>{
 const cases=[
  x=>x.automatic_publication_allowed=true,
  x=>x.queries[0].videos[0].view_count=-1,
  x=>x.queries[0].median_daily_views=5000,
  x=>x.queries[0].videos[0].channel_id="fake",
  x=>x.queries[0].videos[0].url="https://youtube.evil.test/watch?v=videoid0001",
  x=>x.queries[1].region="MX",
  x=>x.quota_units_max=9999,
  x=>x.queries[0].videos[0].published_at=prior(91),
  x=>x.queries[0].evidence_state="insufficient_sample",
  x=>x.market_study_complete=true,
 ];
 for(const edit of cases){
  const r=report(),d=db();edit(r);
  await assert.rejects(persistYoutubeStudy(d,r),RangeError);
  assert.equal(d.writes.length,0);
 }
});
test("lectura D1 protegible por ruta de administración y tamaño limitado",async()=>{
 const d=db();
 const res=await readYoutubeMarket(d,new URL("https://factor.example/api/market/youtube?limit=20"));
 assert.equal(res.ok,true);
 assert.equal(res.market_study_complete,false);
 assert.equal(res.automatic_publication_allowed,false);
 assert.equal((await readYoutubeMarket(d,new URL("https://factor.example/api/market/youtube?limit=100"))).status,400);
});
