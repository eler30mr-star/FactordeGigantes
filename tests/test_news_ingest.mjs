import test from "node:test";
import assert from "node:assert/strict";
import {validateNewsReport,storeNewsReport,readNewsLeads} from "../src/news-ingest.mjs";
const fmt=(date)=>date.toISOString().replace(".000Z","Z");
function report(){
 const now=new Date();
 const pub=new Date(now.getTime()-3*3600000);
 return {provider:"google_news_rss",collected_at:fmt(now),
  feeds:[{category:"innovacion",language:"es",region:"MX",
    feed_url:"https://news.google.com/rss/search?q=innovacion&hl=es-MX&gl=MX&ceid=MX:es",items_accepted:1}],
  feeds_succeeded:1,feeds_attempted:4,leads:[{
    id:"news-"+("a".repeat(32)),headline:"Ejemplo ficticio de anuncio empresarial de innovación",
    aggregator_url:"https://news.google.com/rss/articles/CBMiFICTICIO",
    source_label:"Medio ficticio",category:"innovacion",published_at:fmt(pub),
    verification_state:"unverified",youtube_demand_verified:false,editorial_authorized:false
  }],lead_count:1,source_verification_complete:false,youtube_market_verified:false,
  market_study_complete:false,ready_for_script:false,ready_for_youtube:false};
}
function db(){
 const batches=[],queries=[];
 return {batches,queries,prepare(sql){queries.push(sql);return {
   bind(...params){return {sql,params,all:async()=>({results:[]})}},
   all:async()=>({results:[]})
  };},async batch(b){batches.push(b);return b.map(()=>({success:true}));}};
}
test("persiste titulares solo como señales y reutiliza IDs en reintentos",async()=>{
 const database=db();const r=report();
 const first=await storeNewsReport(database,r);
 const second=await storeNewsReport(database,r);
 assert.equal(first.run_id,second.run_id);
 assert.equal(first.leads_seen,1);
 assert.equal(first.market_study_complete,false);
 assert.equal(first.automatic_publication_allowed,false);
 assert.equal(database.batches.length,2);
 assert.ok(database.queries.every(q=>q.startsWith("INSERT ")));
 assert.ok(database.queries.some(q=>q.includes("ON CONFLICT(id)")));
});
test("descarta intentos de introducir noticias falsas o ya aprobadas",async()=>{
 const variants=[
  x=>x.leads[0].source_label="",
  x=>x.leads[0].aggregator_url="https://evil.example/read/article",
  x=>x.leads[0].editorial_authorized=true,
  x=>x.leads[0].youtube_demand_verified=true,
  x=>x.leads[0].published_at="2001-01-01T00:00:00Z",
  x=>x.leads[0].headline="Corto",
  x=>x.feeds[0].feed_url="https://127.0.0.1/admin",
  x=>x.market_study_complete=true,
  x=>x.lead_count=2
 ];
 for(const mutate of variants){
  const item=report(),database=db();mutate(item);
  await assert.rejects(storeNewsReport(database,item),RangeError);
  assert.equal(database.batches.length,0);
 }
});
test("lectura administrativa limitada sin publicación automática",async()=>{
 const database=db();
 const result=await readNewsLeads(database,new URL("https://factor.example/api/market/news?limit=20"));
 assert.equal(result.ok,true);
 assert.equal(result.automatic_publication_allowed,false);
 assert.equal(database.queries.length,2);
 const bad=await readNewsLeads(database,new URL("https://factor.example/api/market/news?limit=999"));
 assert.equal(bad.status,400);
});
