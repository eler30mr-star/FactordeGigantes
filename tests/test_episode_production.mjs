import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFileSync,readdirSync,writeFileSync,mkdtempSync,rmSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import worker from '../src/worker.js';
import {storeAiReport} from '../src/ai-research-team.mjs';
import {storeAutonomousDraft} from '../src/autonomous-script-drafts.mjs';
import {manifestSha,failEpisodeExport} from '../src/episode-production.mjs';
import {receiveChannelInstruction,setAutomaticMode} from '../src/channel-control.mjs';
import {beginOpportunityStudy,finishOpportunityStudy} from '../src/opportunity-control.mjs';
import {dispatchChannelResearch,channelResearchContext,storeChannelResearch,storeChannelScript} from '../src/channel-research.mjs';
import {editorialFocusSha} from '../src/editorial-focus.mjs';
import {channelProgress} from '../src/channel-progress.mjs';
import {registerYoutubeExport} from '../src/youtube-exports.mjs';
const process=spawnSync('python',['tests/helpers/episode_contract.py'],{cwd:new URL('../',import.meta.url),encoding:'utf8'});
assert.equal(process.status,0,process.stderr);const original=JSON.parse(process.stdout);
function setup(){
 const raw=new DatabaseSync(':memory:');raw.exec('PRAGMA foreign_keys=ON');
 for(const p of readdirSync(new URL('../migrations/',import.meta.url)).filter(p=>p.endsWith('.sql')).sort())raw.exec(readFileSync(new URL('../migrations/'+p,import.meta.url),'utf8'));
 let tail=Promise.resolve();
 const db={prepare(sql){const s=raw.prepare(sql);const make=params=>({async first(){return s.get(...params)??null;},async all(){return {results:s.all(...params)};},async run(){return {meta:{changes:Number(s.run(...params).changes)}};}});return {...make([]),bind(...params){return make(params);}};},batch(stmts){const result=tail.then(async()=>{raw.exec('BEGIN');try{const out=[];for(const s of stmts)out.push(await s.run());raw.exec('COMMIT');return out;}catch(e){raw.exec('ROLLBACK');throw e;}});tail=result.catch(()=>{});return result;}};
 return {raw,db};
}
async function ready(){
 const {raw,db}=setup(),{research,script}=structuredClone(original),day=research.collected_on;
 raw.prepare('INSERT INTO market_entities(wikidata_id,title,first_seen,last_seen) VALUES (?,?,?,?)').run('Q100',research.company,day,day);
 raw.prepare('INSERT INTO market_research_selection_runs(id,observed_on,method,candidate_count,qualified_count,ranked_snapshot_json) VALUES (?,?,?,?,?,?)').run('selection-test',day,'research_market_priority_v1',1,1,'{}');
 raw.prepare('INSERT INTO market_research_queue(id,wikidata_id,title,selection_run_id,market_score,state) VALUES (?,?,?,?,?,?)').run('rq-test','Q100',research.company,'selection-test',55,'researching');
 const saved=await storeAiReport(db,research);script.source_research_run_id=saved.run_id;
 const draft=await storeAutonomousDraft(db,{research_run_id:saved.run_id,script});const id=draft.job_id;
 let dossier=JSON.parse(raw.prepare('SELECT dossier_json FROM editorial_dossiers WHERE job_id=?').get(id).dossier_json);
 dossier.claims.forEach(c=>{c.reviewed_by='Editora de pruebas';c.evidence.forEach(e=>e.status='verificada');});
 dossier.assets.forEach(a=>a.rights_status='verificado');
 raw.prepare("UPDATE editorial_dossiers SET dossier_json=?,editor_attested=1,editor_name='Editora de pruebas' WHERE job_id=?").run(JSON.stringify(dossier),id);
 raw.prepare("UPDATE jobs SET status='approved' WHERE id=?").run(id);
 const env={DB:db,ADMIN_TOKEN:'a'.repeat(32),RENDERER_TOKEN:'r'.repeat(32),GITHUB_DISPATCH_TOKEN:'test-not-real',GITHUB_REPO:'eler30mr-star/FactordeGigantes'};
 const request=(path,{method='GET',body,admin=false}={})=>worker.fetch(new Request('https://test'+path,{method,headers:{Authorization:'Bearer '+(admin?env.ADMIN_TOKEN:env.RENDERER_TOKEN),'Content-Type':'application/json'},...(body?{body:JSON.stringify(body)}:{})}),env);
 return {raw,db,id,env,request};
}
function successfulReport(hash){return {schema:'fdg_episode_export_v1',sha256:'a'.repeat(64),episode_sha256:'b'.repeat(64),
 approved_manifest_sha256:hash,canonical_reference_sha256:'78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d',
 canonical_reference_unchanged:true,contains_narration:true,voice_kind:'canonical_qwen_pending_audition',technical_gate_passed:true,
 actual_seconds:600,generated_voice_takes:60,resolution:[1280,720],fps:12,
 human_factual_approval:false,commercial_rights_verified:false,publication_authorized:false};}

// Both entry points traverse the real D1/Worker/Python contracts. Research,
// editorial decisions and renderer reports are explicit local test fixtures.
// No inference, real approval, canonical narration or new production is claimed.
test('both selected-entry paths keep one episode through research, script, guarded render and registered panel video',async()=>{
 const topic='Las decisiones que transformaron su mercado',company=original.research.company;
 for(const mode of ['chat','automatic']){
  const {raw,db}=setup(),previous=globalThis.fetch,dispatches=[];
  const env={DB:db,ADMIN_TOKEN:'local-owner-fixture-token-0000',RENDERER_TOKEN:'local-render-fixture-token-000',
   GITHUB_DISPATCH_TOKEN:'local-dispatch-fixture-token-000',GITHUB_REPO:'eler30mr-star/FactordeGigantes',
   FINAL_AI_INTEGRATION_ENABLED:'1',YOUTUBE_SELECTOR_VALIDATED:'1'};
  const now=new Date(),day=now.toISOString().slice(0,10),published=new Date(now-10*86400000).toISOString().slice(0,10);
  const send=(path,method='GET',body,renderer=false)=>worker.fetch(new Request('https://factor.test'+path,{method,
   headers:{Authorization:'Bearer '+(renderer?env.RENDERER_TOKEN:env.ADMIN_TOKEN),'Content-Type':'application/json'},
   ...(body?{body:JSON.stringify(body)}:{})}),env);
  globalThis.fetch=async(url,options)=>{
   assert.match(url,/^https:\/\/api.github.com\/repos\/eler30mr-star\/FactordeGigantes\/actions\/workflows\/(topic-discovery-smoke|development-episode)\.yml\/dispatches$/);
   const body=JSON.parse(options.body);assert.equal(body.ref,'main');dispatches.push(body.inputs);
   return new Response(null,{status:204});
  };
  try{
   let episodeId;
   if(mode==='chat'){
    const choice=await receiveChannelInstruction(env,{request_id:crypto.randomUUID(),revision:0,message:'Haz un video sobre '+company+' y '+topic});
    episodeId=choice.episode.id;
   }else{
    await setAutomaticMode(env,{request_id:crypto.randomUUID(),revision:0,enabled:true});
    episodeId=crypto.randomUUID();assert.equal((await beginOpportunityStudy(env,{id:episodeId},now)).allowed,true);
    let serial=1;const videos=[],baselines=[],candidates=[];
    for(const [k,name] of [company,'Empresa alternativa'].entries()){
     const ids=[];
     for(let n=0;n<4;n++){const id='v'+String(serial++).padStart(10,'0');ids.push(id);videos.push({id,title:name+' transforma la industria',
      channel_id:'UC'+String(k*3+n%3).padStart(22,'0'),published_on:published,views:k?2500:3000,duration_seconds:600});}
     for(let n=0;n<3;n++){const channel='UC'+String(k*3+n).padStart(22,'0');baselines.push({channel_id:channel,videos:[0,1,2].map(()=>({
      id:'v'+String(serial++).padStart(10,'0'),title:'Otra historia empresarial',channel_id:channel,published_on:published,views:1000,duration_seconds:600}))});}
     candidates.push({company:name,topic,rationale:'Propuesta simulada con rendimiento relativo observado.',niche_reason:'Historia de decisiones e innovación empresarial.',video_ids:ids});
    }
    const report={schema:'fdg_youtube_opportunity_study_v2',source:'youtube_data_api_v3',observed_on:day,extraction_provider:'local-fixture',
     videos,baselines,candidates,queries:[{query:'Historia de empresas tecnología',video_ids:videos.map(v=>v.id)},{query:'Innovación y decisiones empresariales',video_ids:videos.map(v=>v.id)}]};
    assert.equal((await finishOpportunityStudy(env,{id:episodeId,report},now)).state,'selected');
   }
   assert.equal(raw.prepare('SELECT count(*) n FROM channel_episodes').get().n,1);
   const launched=await dispatchChannelResearch(env,episodeId);assert.equal(launched.started,true);
   const context=await channelResearchContext(env,{request_id:launched.request_id});assert.equal(context.episode.company,company);
   const {research,script}=structuredClone(original);
   raw.prepare('INSERT INTO market_entities(wikidata_id,title,first_seen,last_seen) VALUES (?,?,?,?)').run('Q100',company,day,day);
   Object.assign(research,{selected_episode_id:episodeId,editorial_topic:topic});
   research.editorial_focus_review={schema:'fdg_editorial_focus_v1',status:'aligned',topic,publication_authorized:false,
    claims_sha256:await editorialFocusSha(topic,research.candidate_claims),judgments:research.candidate_claims.map((_,i)=>({
     claim_index:i+1,relevance:'central',reason:'Juicio simulado exclusivamente para comprobar este contrato.'}))};
   const saved=await storeChannelResearch(env,{request_id:launched.request_id,report:research});script.source_research_run_id=saved.run_id;
   const draft=await storeChannelScript(env,{request_id:launched.request_id,script});assert.equal(draft.ok,true);const jobId=draft.job_id;
   assert.equal((await channelProgress(env,episodeId)).next_step,'submit_script');
   assert.equal((await send('/api/jobs/'+jobId+'/submit','POST',{})).status,200);
   assert.equal((await send('/api/jobs/'+jobId+'/approve','POST',{confirmed:true})).status,409);
   const dossier=(await (await send('/api/jobs/'+jobId+'/dossier')).json()).dossier;
   dossier.claims.forEach(c=>{c.reviewed_by='Revisor local simulado';c.evidence.forEach(e=>e.status='verificada');});
   dossier.assets.forEach(a=>a.rights_status='verificado');
   assert.equal((await send('/api/jobs/'+jobId+'/dossier','PUT',dossier)).status,200);
   assert.equal((await send('/api/jobs/'+jobId+'/dossier/attest','POST',{confirmed:true,reviewer:'Revisor local simulado'})).status,200);
   assert.equal((await send('/api/jobs/'+jobId+'/approve','POST',{confirmed:true})).status,200);
   assert.equal((await send('/api/jobs/'+jobId+'/dispatch','POST',{})).status,200);
   const input=await (await send('/api/renderer/jobs/'+jobId+'/episode','GET',null,true)).json();
   const folder=mkdtempSync('/tmp/fdg-lifecycle-');writeFileSync(folder+'/context.json',JSON.stringify(input));
   const prepared=spawnSync('python',['-c',`import json,sys\nfrom tools.episode_package import from_autonomous,digest\nc=json.load(open(sys.argv[1]))\np=from_autonomous(c['script'],c['research'])\np['title']=c['manifest']['title'];p['central_question']=c['manifest']['angle']\nprint(json.dumps({'episode':p,'canonical':json.dumps(p,ensure_ascii=False,sort_keys=True,separators=(',',':')),'sha':digest(p)}))`,folder+'/context.json'],
    {cwd:new URL('../',import.meta.url),encoding:'utf8',timeout:20000});rmSync(folder,{recursive:true});
   assert.equal(prepared.status,0,prepared.stderr);const pkg=JSON.parse(prepared.stdout);assert.equal(pkg.episode.company,company);
   const report={...successfulReport(input.approved_manifest_sha256),episode_sha256:pkg.sha,
    chapters:pkg.episode.scenes.map((s,i)=>({id:s.id,title:s.headline,start_seconds:i*100,end_seconds:(i+1)*100}))};
   assert.equal((await send('/api/renderer/jobs/'+jobId+'/episode-report','POST',{status:'ready',run_id:'987654',export:report},true)).status,200);
   assert.equal((await channelProgress(env,episodeId)).next_step,'recover_video');
   await registerYoutubeExport(env,{report,episode_canonical_json:pkg.canonical,source_run_id:'987654',artifact_id:'123456',archive_sha256:'c'.repeat(64),video_bytes:20000},
    {githubFetch:async url=>new Response(JSON.stringify(url.includes('/actions/runs/')?{
     path:'.github/workflows/development-episode.yml',head_branch:'main',event:'workflow_dispatch',repository:{full_name:env.GITHUB_REPO},status:'completed',conclusion:'success'}:
     {name:'fdg-episode-narrated-review',expired:false,workflow_run:{id:987654},digest:'sha256:'+'c'.repeat(64)}))});
   const progress=await channelProgress(env,episodeId);assert.equal(progress.next_step,'review_video');assert.equal(progress.preview.export_id,report.sha256);
   assert.equal(progress.episode.id,episodeId);assert.equal(progress.episode.origin,mode);assert.equal(progress.publication_authorized,false);
   assert.equal(dispatches.length,2);assert.equal(dispatches[0].phase,'episode');assert.equal(dispatches[1].job_id,jobId);
   assert.equal(raw.prepare('SELECT count(*) n FROM channel_episode_research').get().n,1);
  }finally{globalThis.fetch=previous;raw.close();}
 }
});

test('panel despacha motor canónico, entrega trazabilidad aprobada y Python prepara el mismo episodio',async()=>{
 const {id,raw,request}=await ready();const previous=globalThis.fetch;let dispatch;
 globalThis.fetch=async(url,options)=>{dispatch={url,body:JSON.parse(options.body)};return new Response(null,{status:204});};
 try{
  assert.equal((await request(`/api/jobs/${id}/dispatch`,{method:'POST',admin:true})).status,200);
  assert.match(dispatch.url,/development-episode\.yml/);assert.equal(dispatch.body.inputs.mode,'final_ai');
  assert.equal(dispatch.body.inputs.confirm_final_test,'true');
  assert.equal((await request(`/api/renderer/jobs/${id}`)).status,409);
  const response=await request(`/api/renderer/jobs/${id}/episode`);assert.equal(response.status,200);
  const context=await response.json();assert.equal(context.job_id,id);assert.equal(context.automatic_publication_allowed,false);
  assert.equal(raw.prepare('SELECT status FROM jobs').get().status,'rendering');
  const folder=mkdtempSync('/tmp/fdg-episode-context-');writeFileSync(folder+'/context.json',JSON.stringify(context));
  const checked=spawnSync('python',['-c',`import json,sys\nfrom tools.episode_package import from_autonomous,voice_plan\nc=json.load(open(sys.argv[1]))\np=from_autonomous(c['script'],c['research'])\nprint(json.dumps({'words':voice_plan(p)['narration_words'],'origin':p['origin']}))`,folder+'/context.json'],{cwd:new URL('../',import.meta.url),encoding:'utf8',timeout:20000});rmSync(folder,{recursive:true});
  assert.equal(checked.status,0,checked.stderr);assert.equal(JSON.parse(checked.stdout).words,1200);
 }finally{globalThis.fetch=previous;}
});
test('no entrega material a token ADMIN ni sin atestación; cambiar narración exige nueva trazabilidad',async()=>{
 const {id,raw,request}=await ready();raw.prepare("UPDATE jobs SET status='queued'").run();
 assert.equal((await request(`/api/renderer/jobs/${id}/episode`,{admin:true})).status,401);
 raw.prepare('UPDATE editorial_dossiers SET editor_attested=0').run();
 assert.equal((await request(`/api/renderer/jobs/${id}/episode`)).status,409);
 assert.equal(raw.prepare('SELECT status FROM jobs').get().status,'queued');
 raw.prepare('UPDATE editorial_dossiers SET editor_attested=1').run();
 const manifest=JSON.parse(raw.prepare('SELECT manifest_json FROM jobs').get().manifest_json);
 manifest.segments[0].voiceover=manifest.segments[0].voiceover.replace(/\S+/u,'Cambio');
 raw.prepare('UPDATE jobs SET manifest_json=?').run(JSON.stringify(manifest));
 const response=await request(`/api/renderer/jobs/${id}/episode`);assert.equal(response.status,409);
 assert.equal((await response.json()).reason,'edited_narration_requires_trace_update');
});
test('señal técnica, permisos inventados o QA fallido jamás se reportan como documental narrado',async()=>{
 const {id,raw,request}=await ready();raw.prepare("UPDATE jobs SET status='rendering'").run();
 const hash=await manifestSha(raw.prepare('SELECT manifest_json FROM jobs').get().manifest_json);
 for(const mutate of [r=>r.contains_narration=false,r=>r.voice_kind='technical_test_signal',r=>r.publication_authorized=true,
  r=>r.technical_gate_passed=false,r=>r.canonical_reference_sha256='f'.repeat(64),r=>r.actual_seconds=450,
  r=>r.approved_manifest_sha256='f'.repeat(64),r=>r.resolution=['1280','720'],r=>r.sha256=[r.sha256],r=>r.episode_sha256=[r.episode_sha256]]){
  const report=successfulReport(hash);mutate(report);
  assert.equal((await request(`/api/renderer/jobs/${id}/episode-report`,{method:'POST',body:{status:'ready',run_id:'123456',export:report}})).status,400);
 }
 assert.equal(raw.prepare('SELECT status FROM jobs').get().status,'rendering');
});
test('callback de fallo atrasado no revoca un episodio listo ni cambia su ejecución recuperable',async()=>{
 const {id,raw,db}=await ready();raw.prepare("UPDATE jobs SET status='rendering'").run();
 const stale=raw.prepare('SELECT * FROM jobs WHERE id=?').get(id);
 raw.prepare("UPDATE jobs SET status='ready'").run();
 const result=await failEpisodeExport(db,stale,'123456');assert.equal(result.status,409);
 assert.equal(raw.prepare('SELECT status FROM jobs').get().status,'ready');
 assert.equal(raw.prepare("SELECT COUNT(*) n FROM events WHERE action='episode_failed_attempt'").get().n,0);
});
test('resultado canónico válido queda ready una sola vez y el panel recibe enlace oficial sin autorización de publicación',async()=>{
 const {id,raw,request}=await ready();raw.prepare("UPDATE jobs SET status='rendering'").run();
 const hash=await manifestSha(raw.prepare('SELECT manifest_json FROM jobs').get().manifest_json);
 const body={status:'ready',run_id:'123456',export:successfulReport(hash)};
 const first=await request(`/api/renderer/jobs/${id}/episode-report`,{method:'POST',body});assert.equal(first.status,200);
 const second=await request(`/api/renderer/jobs/${id}/episode-report`,{method:'POST',body});assert.equal((await second.json()).reused,true);
 assert.equal(raw.prepare("SELECT COUNT(*) n FROM events WHERE action='episode_preview_ready'").get().n,1);
 const detail=await request(`/api/jobs/${id}`,{admin:true});const preview=(await detail.json()).preview;
 assert.equal(preview.run_url,'https://github.com/eler30mr-star/FactordeGigantes/actions/runs/123456');
 assert.equal(preview.publication_authorized,false);assert.equal(raw.prepare('SELECT status FROM jobs').get().status,'ready');
});
test('fallo conserva aprobación y reintento recupera el run anterior sin duplicar despacho',async()=>{
 const {id,raw,request}=await ready();raw.prepare("UPDATE jobs SET status='rendering'").run();
 assert.equal((await request(`/api/renderer/jobs/${id}/episode-report`,{method:'POST',body:{status:'failed',run_id:'24680'}})).status,200);
 assert.equal(raw.prepare('SELECT editor_attested FROM editorial_dossiers').get().editor_attested,1);
 const previous=globalThis.fetch;let dispatch,calls=0;
 globalThis.fetch=async(url,options)=>{calls++;dispatch=JSON.parse(options.body);return new Response(null,{status:204});};
 try{
  assert.equal((await request(`/api/jobs/${id}/retry-render`,{method:'POST',admin:true})).status,200);
  assert.equal(dispatch.inputs.resume_run_id,'24680');assert.equal(calls,1);
  assert.equal((await request(`/api/jobs/${id}/retry-render`,{method:'POST',admin:true})).status,409);
  assert.equal(calls,1);
 }finally{globalThis.fetch=previous;}
});

