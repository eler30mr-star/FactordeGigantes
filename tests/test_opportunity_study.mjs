import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFileSync,readdirSync} from 'node:fs';
import {generateKeyPairSync,sign} from 'node:crypto';
import worker from '../src/worker.js';
import {MARKET_AUDIENCE} from '../src/github-oidc.mjs';
import {assessOpportunityStudy} from '../src/opportunity-study.mjs';
import {beginOpportunityStudy,finishOpportunityStudy,checkOpportunityStudy,failOpportunityStudy,latestOpportunityStudy} from '../src/opportunity-control.mjs';
const NOW=new Date('2026-10-25T12:00:00Z');
const vid=n=>'v'+String(n).padStart(10,'0'),channel=n=>'UC'+String(n).padStart(22,'0');
function sample(observedOn='2026-10-25'){
 const published=new Date(Date.parse(observedOn+'T00:00:00Z')-10*86400000).toISOString().slice(0,10);
 const videos=[],baselines=[],candidates=[];let serial=1;
 for(const [k,company] of ['Empresa Alfa','Empresa Beta'].entries()){
  const ids=[];
  for(let n=0;n<4;n++){
   const id=vid(serial++);ids.push(id);videos.push({id,title:company+' transforma la industria',channel_id:channel(k*3+n%3),
    published_on:published,views:k?2500:3000,duration_seconds:600});
  }
  for(let n=0;n<3;n++)baselines.push({channel_id:channel(k*3+n),videos:[0,1,2].map(i=>({id:vid(serial++),title:'Otra historia tecnológica',
   channel_id:channel(k*3+n),published_on:published,views:1000,duration_seconds:600}))});
  candidates.push({company,topic:'Las decisiones que transformaron su mercado',rationale:'Hay ejemplos medidos de interés relativo en varios canales.',
   niche_reason:'Su transformación tecnológica encaja con la identidad del canal.',video_ids:ids});
 }
 return {schema:'fdg_youtube_opportunity_study_v2',source:'youtube_data_api_v3',observed_on:observedOn,extraction_provider:'gemini',videos,baselines,candidates,
  queries:[{query:'historia de empresas tecnología',video_ids:videos.map(v=>v.id)},{query:'innovación auge y caída',video_ids:videos.map(v=>v.id)}]};
}
function db(){
 const raw=new DatabaseSync(':memory:');raw.exec('PRAGMA foreign_keys=ON');
 for(const file of readdirSync(new URL('../migrations/',import.meta.url)).filter(p=>p.endsWith('.sql')).sort())
  raw.exec(readFileSync(new URL('../migrations/'+file,import.meta.url),'utf8'));
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

test('sample coverage is computed from dated long videos, ignoring supplied summaries',()=>{
 const r=sample();r.sample_summary={observed_videos:999,comparable_long_videos:999,distinct_channels:999,recent_examples:999};
 const complete=assessOpportunityStudy(r,NOW);
 assert.deepEqual(complete.sample_summary,{observed_videos:8,comparable_long_videos:8,distinct_channels:6,recent_examples:8});
 assert.deepEqual(complete.minimum_sample_reasons,[]);
 r.videos.forEach((v,i)=>{v.channel_id=channel(0);if(i<3)v.duration_seconds=60;else v.published_on='2026-08-01';});
 const insufficient=assessOpportunityStudy(r,NOW);
 assert.deepEqual(insufficient.sample_summary,{observed_videos:8,comparable_long_videos:5,distinct_channels:1,recent_examples:0});
 assert.deepEqual(insufficient.minimum_sample_reasons,['need_three_observed_channels','need_two_recent_examples']);
 assert.equal(insufficient.selected,null);
});

test('empty observations persist as an insufficient study and expose missing evidence to the panel',async()=>{
 const env={DB:db(),FINAL_AI_INTEGRATION_ENABLED:'1',YOUTUBE_SELECTOR_VALIDATED:'1'},id=crypto.randomUUID();
 const r=sample();r.videos=[];r.candidates=[];r.baselines=[];r.queries.forEach(q=>q.video_ids=[]);
 r.extraction_provider='not_invoked_insufficient_evidence';
 try{
  await beginOpportunityStudy(env,{id},NOW);
  const result=await finishOpportunityStudy(env,{id,report:r},NOW);
  assert.equal(result.state,'insufficient');assert.equal(result.assessment.selected,null);
  const visible=(await latestOpportunityStudy(env)).study;
  assert.deepEqual(visible.sample_summary,{observed_videos:0,comparable_long_videos:0,distinct_channels:0,recent_examples:0});
  assert.deepEqual(visible.minimum_sample_reasons,['need_four_comparable_long_videos','need_three_observed_channels','need_two_recent_examples']);
  assert.equal(env.DB.raw.prepare('SELECT count(*) n FROM channel_episodes').get().n,0);
  assert.equal(env.DB.raw.prepare('SELECT count(*) n FROM channel_episode_research').get().n,0);
 }finally{env.DB.raw.close();}
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

// Exercise the actual HTTP handlers, OIDC signatures and D1 transitions together.
// The only outbound calls accepted here are local JWKS and dispatch substitutes.
function apiSession(t,{validated=true}={}){
 const database=db(),env={DB:database,FINAL_AI_INTEGRATION_ENABLED:'1',
  YOUTUBE_SELECTOR_VALIDATED:validated?'1':'0',GITHUB_REPO:'eler30mr-star/FactordeGigantes',
  GITHUB_DISPATCH_TOKEN:'fake-local-dispatch-token-00000',ADMIN_TOKEN:'fake-local-owner-token-000000'};
 const {publicKey,privateKey}=generateKeyPairSync('rsa',{modulusLength:2048});
 const now=Math.floor(Date.now()/1000),b64=o=>Buffer.from(JSON.stringify(o)).toString('base64url');
 const header=b64({alg:'RS256',typ:'JWT',kid:'local-selected-episode-proof'});
 const claims=b64({iss:'https://token.actions.githubusercontent.com',aud:MARKET_AUDIENCE,
  repository_id:'1426522491',repository:env.GITHUB_REPO,ref:'refs/heads/main',
  workflow_ref:env.GITHUB_REPO+'/.github/workflows/topic-discovery-smoke.yml@refs/heads/main',
  event_name:'workflow_dispatch',runner_environment:'github-hosted',iat:now-1,nbf:now-1,exp:now+240});
 const input=header+'.'+claims;
 const token=input+'.'+sign('RSA-SHA256',Buffer.from(input),privateKey).toString('base64url');
 const dispatched=[],trace=[],previous=globalThis.fetch;
 globalThis.fetch=async(url,options)=>{
  if(url==='https://token.actions.githubusercontent.com/.well-known/jwks')return {ok:true,json:async()=>({keys:[{
   ...publicKey.export({format:'jwk'}),kid:'local-selected-episode-proof',alg:'RS256',use:'sig'}]})};
  assert.equal(url,'https://api.github.com/repos/'+env.GITHUB_REPO+'/actions/workflows/topic-discovery-smoke.yml/dispatches','Unexpected network request; no real services allowed');
  const body=JSON.parse(options.body);assert.equal(body.inputs.phase,'episode');
  const episode=database.raw.prepare('SELECT * FROM channel_episodes WHERE id=?').get(body.inputs.episode_id);
  assert.ok(episode,'Selection must exist before dispatch');assert.equal(episode.state,'selected');
  if(episode.origin==='automatic')assert.equal(database.raw.prepare('SELECT state FROM channel_opportunity_studies WHERE id=?').get(episode.id).state,'selected');
  const reservation=database.raw.prepare('SELECT episode_id,state FROM channel_episode_research WHERE id=?').get(body.inputs.episode_request_id);
  assert.equal(reservation.episode_id,episode.id);assert.equal(reservation.state,'reserved');
  trace.push('selection_persisted_before_research');dispatched.push(body.inputs);
  return {status:204};
 };
 let disposed=false;
 const dispose=()=>{if(disposed)return;disposed=true;globalThis.fetch=previous;database.raw.close();};
 t.after(dispose);
 const request=async(path,body)=>{
  const response=await worker.fetch(new Request('https://factor.test'+path,{method:'POST',
   headers:{Authorization:'Bearer '+(path.startsWith('/api/channel-control')?env.ADMIN_TOKEN:token),'Content-Type':'application/json'},
   body:JSON.stringify(body)}),env);
  return {status:response.status,body:await response.json()};
 };
 return {database,env,dispatched,trace,request,dispose};
}

test('HTTP selection precedes research, only the winner is dispatched, and replay does not spend another request',async t=>{
 const f=apiSession(t),id=crypto.randomUUID();
 const premature=await f.request('/api/channel-control/research',{episode_id:crypto.randomUUID()});
 assert.equal(premature.body.started,false);assert.equal(f.dispatched.length,0);
 assert.equal((await f.request('/api/market/opportunity-study/start',{id})).body.allowed,true);
 assert.equal(f.database.raw.prepare('SELECT count(*) n FROM channel_episodes').get().n,0);
 assert.equal(f.database.raw.prepare('SELECT count(*) n FROM channel_episode_research').get().n,0);
 const report=sample(new Date().toISOString().slice(0,10));
 const selected=await f.request('/api/market/opportunity-study/finish',{id,report});
 assert.equal(selected.status,200);assert.equal(selected.body.state,'selected');assert.equal(selected.body.pipeline.started,true);
 assert.equal(f.dispatched.length,1);assert.deepEqual(f.trace,['selection_persisted_before_research']);
 const context=await f.request('/api/market/channel-episode/context',{request_id:f.dispatched[0].episode_request_id});
 assert.equal(context.body.allowed,true);assert.equal(context.body.episode.company,selected.body.assessment.selected.company);
 assert.equal(context.body.episode.company,'Empresa Alfa');assert.equal(context.body.episode.topic,selected.body.assessment.selected.topic);
 const replay=await f.request('/api/market/opportunity-study/finish',{id,report});assert.equal(replay.body.replayed,true);
 assert.equal(f.dispatched.length,1);assert.equal(f.database.raw.prepare('SELECT count(*) n FROM channel_episode_research').get().n,1);
 assert.equal(f.database.raw.prepare('SELECT count(*) n FROM ai_budget_reservations').get().n,0);
 assert.equal(f.database.raw.prepare('SELECT count(*) n FROM market_entities').get().n,0); // No company catalogue was built.
});

test('HTTP insufficient or unvalidated study never starts deep research',async t=>{
 for(const calibrated of [false,true]){
  const f=apiSession(t,{validated:calibrated}),id=crypto.randomUUID();
  await f.request('/api/market/opportunity-study/start',{id});
  const report=sample(new Date().toISOString().slice(0,10));if(calibrated)report.candidates.pop();
  const result=await f.request('/api/market/opportunity-study/finish',{id,report});
  assert.equal(result.body.state,calibrated?'insufficient':'calibration');assert.equal(f.dispatched.length,0);
  assert.equal(f.database.raw.prepare('SELECT count(*) n FROM channel_episodes').get().n,0);
  assert.equal(f.database.raw.prepare('SELECT count(*) n FROM channel_episode_research').get().n,0);
  assert.equal(f.database.raw.prepare('SELECT count(*) n FROM ai_budget_reservations').get().n,0);
  f.dispose();
 }
});

test('HTTP turning automatic off before study completion cancels selection and prevents research dispatch',async t=>{
 const f=apiSession(t),id=crypto.randomUUID();
 await f.request('/api/market/opportunity-study/start',{id});
 await f.request('/api/channel-control/mode',{revision:0,request_id:crypto.randomUUID(),enabled:false});
 const result=await f.request('/api/market/opportunity-study/finish',{id,report:sample(new Date().toISOString().slice(0,10))});
 assert.equal(result.body.state,'cancelled');assert.equal(f.dispatched.length,0);
 assert.equal(f.database.raw.prepare('SELECT count(*) n FROM channel_episodes').get().n,0);
 assert.equal(f.database.raw.prepare('SELECT count(*) n FROM channel_episode_research').get().n,0);
});

test('HTTP owner chat with automatic off preserves the exact choice and starts the same selected-episode path once',async t=>{
 const f=apiSession(t);f.database.raw.exec('UPDATE channel_control SET automatic_enabled=0');
 const instruction={revision:0,request_id:crypto.randomUUID(),message:'Haz un video sobre Empresa Beta y cómo cambió su mercado'};
 const selected=await f.request('/api/channel-control/chat',instruction);
 assert.equal(selected.status,200);assert.equal(selected.body.episode.company,'Empresa Beta');assert.equal(selected.body.pipeline.started,true);
 const context=await f.request('/api/market/channel-episode/context',{request_id:f.dispatched[0].episode_request_id});
 assert.equal(context.body.episode.company,'Empresa Beta');assert.equal(context.body.episode.topic,'cómo cambió su mercado');
 assert.equal(context.body.episode.origin,'chat');assert.equal(context.body.allowed,true);
 assert.equal(f.database.raw.prepare('SELECT count(*) n FROM channel_opportunity_studies').get().n,0);
 assert.equal(f.database.raw.prepare('SELECT automatic_enabled FROM channel_control').get().automatic_enabled,0);
 await f.request('/api/channel-control/chat',instruction);assert.equal(f.dispatched.length,1);
 assert.equal(f.database.raw.prepare('SELECT count(*) n FROM ai_budget_reservations').get().n,0);
});
