import test from "node:test";
import assert from "node:assert/strict";
import {validateEntityNewsJoin,storeEntityNewsJoin,readEntityNewsJoin} from "../src/market-cross-signals.mjs";
function fixture(){
  return {provider:"wikimedia_rss_headline_join_v1",
    collected_on:new Date().toISOString().slice(0,10),
    company_count:1,news_count:1,match_count:1,
    market_study_complete:false,source_article_verified:false,
    ready_for_script:false,ready_for_youtube:false,
    matches:[{wikidata_id:"Q221062",news_id:"news-"+"a".repeat(32),
      matched_alias:"dupont",method:"exact_normalized_headline_v1",
      headline:"DuPont announces an industrial breakthrough",
      aggregator_url:"https://news.google.com/rss/articles/CBMiTEST",
      match_status:"candidate_needs_entity_confirmation",
      source_article_verified:false,youtube_market_verified:false,
      editorial_authorized:false}]};
}
function db(){
 const writes=[];
 return {writes,prepare(sql){return {bind(...args){return {sql,args,async all(){return {results:[]}}}},async all(){return {results:[]}}}},
  async batch(stmts){writes.push(stmts);return stmts.map(()=>({success:true}))}};
}
test("inserta cruce atómico, identificador estable y preserva estado editorial",async()=>{
 const d=db(),r=fixture();
 const x=await storeEntityNewsJoin(d,r),y=await storeEntityNewsJoin(d,r);
 assert.equal(x.run_id,y.run_id);
 assert.equal(x.matched_pairs,1);
 assert.equal(x.source_article_verified,false);
 assert.equal(x.automatic_publication_allowed,false);
 assert.equal(d.writes[0].length,2);
 assert.ok(d.writes[0][1].sql.includes("ON CONFLICT"));
});
test("rechaza empresa inexistente en el titular, aprobaciones y enlaces falsos",async()=>{
 const changes=[
  r=>r.matches[0].matched_alias="empresa",r=>r.matches[0].editorial_authorized=true,
  r=>r.matches[0].source_article_verified=true,r=>r.matches[0].aggregator_url="https://evil.test/feed",
  r=>r.matches[0].headline="Noticia sin relación empresarial",
  r=>r.matches[0].news_id="not-news",r=>r.match_count=2
 ];
 for(const change of changes){
  const r=fixture(),d=db();change(r);
  await assert.rejects(storeEntityNewsJoin(d,r));
  assert.equal(d.writes.length,0);
 }
});
test("lectura de cruces limitada y sin autorización de publicación",async()=>{
 const d=db();
 const out=await readEntityNewsJoin(d,new URL("https://factor.example/api/market/cross?limit=20"));
 assert.equal(out.ok,true);
 assert.equal(out.market_study_complete,false);
 assert.equal(out.automatic_publication_allowed,false);
 assert.equal((await readEntityNewsJoin(d,new URL("https://factor.example/api/market/cross?limit=999"))).status,400);
});
