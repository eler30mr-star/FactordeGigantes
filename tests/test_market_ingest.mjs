import test from "node:test";
import assert from "node:assert/strict";
import {validateMarketReport,persistMarketReport} from "../src/market-ingest.mjs";

const report=()=>({
 method:"wikimedia_wikidata_company_discovery_v1",
 collected_on:"2026-10-21",data_day:"2026-10-18",wikidata_requests:12,
 articles_considered:360,company_candidates_count:1,wikipedia_interest_measured_count:1,
 market_study_complete:false,ready_for_youtube:false,youtube_market_verified:false,ready_for_script:false,
 candidates:[{
  wikidata_id:"Q16956307",topic:"Theranos",market_rank_qualified:false,
  youtube_data_collected:false,primary_documents_verified:false,research_started:false,
  youtube_publication_authorized:false,official_website_candidate:null,
  discovery_signals:[{source:"wikimedia_daily_top_plus_wikidata_p31",
   project:"en.wikipedia",observed_on:"2026-10-18",rank:37,views:58877,
   url:"https://en.wikipedia.org/wiki/Theranos"}],
  interest_14d_status:"measured",
  wikipedia_interest:{origin:"wikimedia_pageviews_api",
   observed_at:"2026-10-21",url:"https://en.wikipedia.org/wiki/Theranos",
   source_period_start:"2026-10-07",source_period_end:"2026-10-20",
   views_last_7d:291435,views_previous_7d:55952}
 }]
});
function mockDB(){
 const writes=[];
 return {writes,prepare(sql){
  assert.ok(sql.startsWith("INSERT "),"Solo INSERT/UPSERT permitidos");
  return {bind(...params){return {sql,params}}};
 },async batch(batch){
  writes.push(batch);
  return batch.map(()=>({success:true}));
 }};
}
test("aplica lote atómico con historial y sin permisos de publicación",async()=>{
 const db=mockDB();
 const one=await persistMarketReport(db,report());
 const two=await persistMarketReport(db,report());
 assert.equal(one.run_id,two.run_id);
 assert.equal(one.entities_seen,1);
 assert.equal(one.windows_seen,1);
 assert.equal(one.market_study_complete,false);
 assert.equal(one.automatic_publication_allowed,false);
 assert.equal(db.writes.length,2);
 assert.equal(db.writes[0].length,4);
 assert.ok(db.writes[0][0].sql.includes("INSERT OR IGNORE INTO market_runs"));
 assert.equal(db.writes[0][3].params.at(-1),one.run_id);
});
test("rechaza fuentes falsas, fechas imposibles y métricas negativas antes de D1",async()=>{
 const variants=[
   r=>r.candidates[0].discovery_signals[0].url="https://fake.example/wiki/Theranos",
   r=>r.candidates[0].wikipedia_interest.source_period_start="2026-10-08",
   r=>r.candidates[0].discovery_signals[0].views=-1,
   r=>r.collected_on="2026-02-30",
   r=>r.candidates[0].market_rank_qualified=true,
   r=>r.ready_for_youtube=true,
   r=>r.wikipedia_interest_measured_count=2,
   r=>r.candidates[0].discovery_signals[0].url="https://en.wikipedia.org.evil.test/wiki/Theranos",
 ];
 for(const change of variants){
  const data=report(),db=mockDB();change(data);
  await assert.rejects(persistMarketReport(db,data),RangeError);
  assert.equal(db.writes.length,0);
 }
});
test("rechaza duplicados QID y protege límites de presupuesto",()=>{
 const r=report();
 r.candidates.push(structuredClone(r.candidates[0]));
 r.company_candidates_count=2;
 assert.throws(()=>validateMarketReport(r),RangeError);
 const no=report();no.wikidata_requests=13;
 assert.throws(()=>validateMarketReport(no),RangeError);
});
