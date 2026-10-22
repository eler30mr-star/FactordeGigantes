import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFileSync,readdirSync} from 'node:fs';
import {rankResearchMarket,selectResearchFromD1} from '../src/market-research-selection.mjs';
import worker from '../src/worker.js';
const DAY='2026-10-22';
function data(){
 const entities=[{wikidata_id:'Q100',title:'Compañía uno'},{wikidata_id:'Q200',title:'Compañía dos'}];
 const wiki=entities.map((e,i)=>({wikidata_id:e.wikidata_id,observed_at:DAY,
   period_start:'2026-10-08',period_end:'2026-10-21',views_last_7d:i?6000:2000,views_previous_7d:1000}));
 const videos=entities.flatMap((e,index)=>['MX','ES'].flatMap(region=>[1,2,3].map(i=>({
   wikidata_id:e.wikidata_id,region,observed_on:DAY,video_id:'v'+String(index).repeat(9)+i,
   published_on:'2026-10-18',view_count:1000*i,channel_id:'UC'+String(i).repeat(22),source_run_id:'ytrun-fixture'
 }))));
 return {entities,wiki,videos};
}
test('compara dos empresas y deduplica videos compartidos por regiones',()=>{
 const r=rankResearchMarket(data(),DAY);
 assert.equal(r.proposed_wikidata_id,'Q200');
 assert.equal(r.qualified_count,2);
 assert.equal(r.rankings[0].youtube_unique_videos,3);
 assert.equal(r.rankings[0].median_daily_views,500);
 assert.equal(r.rankings[0].youtube_region_samples,2);
 assert.equal(r.rankings[0].script_authorized,false);
 assert.equal(r.rankings[0].verified_claims,0);
 assert.equal(r.publication_authorized,false);
});
test('sin región, fecha reciente o ventana independiente no elige ganador',()=>{
 for(const edit of [d=>d.videos=d.videos.filter(v=>v.region==='MX'),
   d=>d.videos.forEach(v=>v.observed_on='2026-10-10'),d=>d.wiki=[]]){
  const d=data();edit(d);const r=rankResearchMarket(d,DAY);
  assert.equal(r.proposed_wikidata_id,null);assert.equal(r.qualified_count,0);
 }
 const d=data();d.videos[0].view_count=-1;
 assert.throws(()=>rankResearchMarket(d,DAY),RangeError);
});
function sqliteD1(){
 const db=new DatabaseSync(':memory:');db.exec('PRAGMA foreign_keys=ON');
 for(const path of readdirSync(new URL('../migrations/',import.meta.url)).filter(p=>p.endsWith('.sql')).sort())
  db.exec(readFileSync(new URL('../migrations/'+path,import.meta.url),'utf8'));
 return db;
}
// El adaptador usa SQLite real con los mismos SQL que emite el módulo.
function adapter(db){
 return {prepare(sql){const prepared=db.prepare(sql);const make=params=>({
   async all(){return {results:prepared.all(...params)};},
   async first(){return prepared.get(...params)??null;},
   async execute(){return prepared.run(...params);}
  });return {...make([]),bind(...params){return make(params);}};},
  async batch(stmts){db.exec('BEGIN');try{const r=[];for(const s of stmts)r.push(await s.execute());db.exec('COMMIT');return r;}
   catch(e){db.exec('ROLLBACK');throw e;}}
 };
}
test('selección D1 real, historial idempotente y una única cola activa',async()=>{
 const raw=sqliteD1(),fixture=data();
 for(const e of fixture.entities){
  raw.prepare('INSERT INTO market_entities(wikidata_id,title,first_seen,last_seen) VALUES (?,?,?,?)')
     .run(e.wikidata_id,e.title,DAY,DAY);
 }
 // Cargar las tablas del radar respetando el esquema real, sin simular D1.
 raw.prepare('INSERT INTO market_runs(id,collection_day,data_day,source_method,detected_count) VALUES (?,?,?,?,?)')
   .run('market-fixture',DAY,'2026-10-19','wikimedia_wikidata_company_discovery_v1',2);
 for(const w of fixture.wiki){
  raw.prepare('INSERT INTO market_interest_windows(run_id,wikidata_id,observed_at,source_url,period_start,period_end,views_last_7d,views_previous_7d) VALUES (?,?,?,?,?,?,?,?)')
    .run('market-fixture',w.wikidata_id,DAY,'https://es.wikipedia.org/wiki/Fixture',w.period_start,w.period_end,w.views_last_7d,w.views_previous_7d);
 }
 raw.prepare('INSERT INTO market_youtube_runs(id,collected_on,provider,region_count,candidate_count,queries_attempted,quota_units_max,state) VALUES (?,?,?,?,?,?,?,?)')
   .run('ytrun-fixture',DAY,'youtube_data_api_v3',2,2,4,8,'measured');
 for(const e of fixture.entities)for(const region of ['MX','ES'])
  raw.prepare('INSERT INTO market_youtube_queries(run_id,wikidata_id,topic,region,observed_on,sample_size,uploads_sampled,median_daily_views,distinct_channels,evidence_state) VALUES (?,?,?,?,?,?,?,?,?,?)')
    .run('ytrun-fixture',e.wikidata_id,e.title,region,DAY,3,3,500,3,'observed_sample');
 for(const v of fixture.videos)
  raw.prepare('INSERT INTO market_youtube_videos(run_id,wikidata_id,region,video_id,published_on,view_count,channel_id,video_url) VALUES (?,?,?,?,?,?,?,?)')
    .run('ytrun-fixture',v.wikidata_id,v.region,v.video_id,v.published_on,v.view_count,v.channel_id,'https://www.youtube.com/watch?v='+v.video_id);
 const db=adapter(raw),now=new Date(DAY+'T12:00:00Z');
 const first=await selectResearchFromD1(db,now),second=await selectResearchFromD1(db,now);
 assert.equal(first.selected_wikidata_id,'Q200');
 assert.equal(first.research_queue.state,'awaiting_sources');
 assert.equal(first.run_id,second.run_id);
 assert.equal(raw.prepare('SELECT count(*) AS n FROM market_research_queue').get().n,1);
 assert.equal(raw.prepare('SELECT count(*) AS n FROM market_research_selection_runs').get().n,1);
 assert.equal(raw.prepare('PRAGMA foreign_key_check').all().length,0);
 assert.equal(first.automatic_publication_allowed,false);
});
test('OIDC protege selección y ADMIN protege lectura de la cola',async()=>{
 const env={ADMIN_TOKEN:'a'.repeat(32),RENDERER_TOKEN:'r'.repeat(32),DB:{}};
 for(const auth of ['',env.ADMIN_TOKEN,env.RENDERER_TOKEN]){
  const response=await worker.fetch(new Request('https://factor.test/api/market/research-selection/run',{
    method:'POST',headers:{Authorization:'Bearer '+auth}}),env,{});
  assert.equal(response.status,401);
 }
 const response=await worker.fetch(new Request('https://factor.test/api/market/research-queue'),env,{});
 assert.equal(response.status,401);
});
