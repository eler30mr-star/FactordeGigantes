import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFileSync} from 'node:fs';
import {assessOpportunityStudy} from '../src/opportunity-study.mjs';
import {beginOpportunityStudy,finishOpportunityStudy,checkOpportunityStudy,failOpportunityStudy} from '../src/opportunity-control.mjs';
const NOW=new Date('2026-10-25T12:00:00Z');
const vid=n=>'v'+String(n).padStart(10,'0'),channel=n=>'UC'+String(n).padStart(22,'0');
function sample(){
 const videos=[],baselines=[],candidates=[];let serial=1;
 for(const [k,company] of ['Empresa Alfa','Empresa Beta'].entries()){
  const ids=[];
  for(let n=0;n<4;n++){
   const id=vid(serial++);ids.push(id);videos.push({id,title:company+' transforma la industria',channel_id:channel(k*3+n%3),
    published_on:'2026-10-15',views:k?2500:3000,duration_seconds:600});
  }
  for(let n=0;n<3;n++)baselines.push({channel_id:channel(k*3+n),videos:[0,1,2].map(i=>({id:vid(serial++),title:'Otra historia tecnológica',
   channel_id:channel(k*3+n),published_on:'2026-10-15',views:1000,duration_seconds:600}))});
  candidates.push({company,topic:'Las decisiones que transformaron su mercado',rationale:'Hay ejemplos medidos de interés relativo en varios canales.',
   niche_reason:'Su transformación tecnológica encaja con la identidad del canal.',video_ids:ids});
 }
 return {schema:'fdg_youtube_opportunity_study_v2',source:'youtube_data_api_v3',observed_on:'2026-10-25',extraction_provider:'gemini',videos,baselines,candidates,
  queries:[{query:'historia de empresas tecnología',video_ids:videos.map(v=>v.id)},{query:'innovación auge y caída',video_ids:videos.map(v=>v.id)}]};
}
function db(){
 const raw=new DatabaseSync(':memory:');raw.exec('PRAGMA foreign_keys=ON');
 for(const file of ['0017_channel_control.sql','0018_opportunity_studies.sql'])raw.exec(readFileSync(new URL('../migrations/'+file,import.meta.url),'utf8'));
 raw.exec('UPDATE channel_control SET automatic_enabled=1');
 let tail=Promise.resolve();
 const prepare=sql=>{let args=[];return {bind(...p){args=p;return this;},async first(){return raw.prepare(sql).get(...args)||null;},
  async all(){return {results:raw.prepare(sql).all(...args)};},async run(){return {meta:{changes:Number(raw.prepare(sql).run(...args).changes)}};}};};
 return {raw,prepare,batch(statements){const next=tail.then(async()=>{raw.exec('BEGIN');try{const r=[];for(const s of statements)r.push(await s.run());raw.exec('COMMIT');return r;}catch(e){raw.exec('ROLLBACK');throw e;}});tail=next.catch(()=>{});return next;}};
}

test('selects from two genuinely comparable companies, preserving evidence and limits',()=>{
 const out=assessOpportunityStudy(sample(),NOW);assert.equal(out.selected.company,'Empresa Alfa');assert.equal(out.rankings.length,2);
 assert.equal(out.rankings[0].baseline_channels,3);assert.equal(out.rankings[0].median_relative_average_views,3);
 assert.equal(out.publication_authorized,false);assert.ok(out.limitations.some(s=>s.includes('no crecimiento')));
});

test('one measurable company, missing channel baselines and Shorts cannot force a choice',()=>{
 for(const change of [r=>r.candidates.pop(),r=>r.baselines=[],r=>r.videos.forEach(v=>v.duration_seconds=50)]){
  const s=sample();change(s);assert.equal(assessOpportunityStudy(s,NOW).selected,null);
 }
});

test('a single viral outlier is not sufficient relative performance',()=>{
 const r=sample();for(const v of r.videos)v.views=100;
 r.videos[0].views=10000000;
 const result=assessOpportunityStudy(r,NOW);assert.equal(result.selected,null);
 assert.ok(result.rankings.every(c=>c.reasons.includes('no_consistent_relative_outperformance')));
});

test('stale data, duplicates and fabricated references are rejected',()=>{
 for(const change of [r=>r.observed_on='2026-10-20',r=>r.videos.push(r.videos[0]),
  r=>r.queries[0].video_ids.push('unknown0000'),r=>r.baselines[0].videos[0].channel_id=channel(999)]){
  const r=sample();change(r);assert.throws(()=>assessOpportunityStudy(r,NOW),RangeError);
 }
 const r=sample();r.candidates[0].company='Empresa Inventada';assert.equal(assessOpportunityStudy(r,NOW).selected,null);
 assert.equal(assessOpportunityStudy(sample(),NOW,['Empresa Alfa']).selected,null);
});

test('off or paused returns before reservation; daily reservation is atomic and bounded',async()=>{
 const database=db(),env={DB:database,FINAL_AI_INTEGRATION_ENABLED:'0'};
 assert.equal((await beginOpportunityStudy(env,{id:crypto.randomUUID()},NOW)).allowed,false);
 env.FINAL_AI_INTEGRATION_ENABLED='1';database.raw.exec('UPDATE channel_control SET automatic_enabled=0');
 assert.equal((await beginOpportunityStudy(env,{id:crypto.randomUUID()},NOW)).allowed,false);
 database.raw.exec('UPDATE channel_control SET automatic_enabled=1');
 const attempts=await Promise.all([beginOpportunityStudy(env,{id:crypto.randomUUID()},NOW),beginOpportunityStudy(env,{id:crypto.randomUUID()},NOW)]);
 assert.equal(attempts.filter(x=>x.allowed).length,1);assert.equal(database.raw.prepare('SELECT count(*) n FROM channel_opportunity_studies').get().n,1);
});

test('initial scoring is calibration only until explicitly validated with real studies',async()=>{
 const env={DB:db(),FINAL_AI_INTEGRATION_ENABLED:'1'},id=crypto.randomUUID();
 await beginOpportunityStudy(env,{id},NOW);
 const result=await finishOpportunityStudy(env,{id,report:sample()},NOW);
 assert.equal(result.state,'calibration');assert.equal(env.DB.raw.prepare('SELECT count(*) n FROM channel_episodes').get().n,0);
});

test('mode change before finish cancels selection; validated study creates only one episode',async()=>{
 const env={DB:db(),FINAL_AI_INTEGRATION_ENABLED:'1',YOUTUBE_SELECTOR_VALIDATED:'1'},id=crypto.randomUUID();
 await beginOpportunityStudy(env,{id},NOW);env.DB.raw.exec('UPDATE channel_control SET automatic_enabled=0,revision=revision+1');
 assert.equal((await finishOpportunityStudy(env,{id,report:sample()},NOW)).state,'cancelled');
 assert.equal(env.DB.raw.prepare('SELECT count(*) n FROM channel_episodes').get().n,0);
 const active={DB:db(),FINAL_AI_INTEGRATION_ENABLED:'1',YOUTUBE_SELECTOR_VALIDATED:'1'},second=crypto.randomUUID();
 await beginOpportunityStudy(active,{id:second},NOW);
 assert.equal((await finishOpportunityStudy(active,{id:second,report:sample()},NOW)).state,'selected');
 assert.equal((await finishOpportunityStudy(active,{id:second,report:sample()},NOW)).replayed,true);
 const episode=active.DB.raw.prepare('SELECT * FROM channel_episodes').get();
 assert.equal(episode.origin,'automatic');assert.equal(episode.company,'Empresa Alfa');
 assert.equal(active.DB.raw.prepare('SELECT count(*) n FROM channel_episodes').get().n,1);
});

test('an incomplete study leaves a visible blocker and cannot overwrite a selected result',async()=>{
 const env={DB:db(),FINAL_AI_INTEGRATION_ENABLED:'1'},id=crypto.randomUUID();
 await beginOpportunityStudy(env,{id},NOW);
 assert.equal((await failOpportunityStudy(env,{id,reason:'study_incomplete'})).state,'insufficient');
 assert.equal((await finishOpportunityStudy(env,{id,report:sample()},NOW)).state,'insufficient');
 assert.equal(env.DB.raw.prepare('SELECT count(*) n FROM channel_episodes').get().n,0);
});
