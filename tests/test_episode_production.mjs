import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFileSync,readdirSync,writeFileSync,mkdtempSync,rmSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import worker from '../src/worker.js';
import {storeAiReport} from '../src/ai-research-team.mjs';
import {storeAutonomousDraft} from '../src/autonomous-script-drafts.mjs';
import {manifestSha} from '../src/episode-production.mjs';
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
  r=>r.approved_manifest_sha256='f'.repeat(64),r=>r.resolution=['1280','720']]){
  const report=successfulReport(hash);mutate(report);
  assert.equal((await request(`/api/renderer/jobs/${id}/episode-report`,{method:'POST',body:{status:'ready',run_id:'123456',export:report}})).status,400);
 }
 assert.equal(raw.prepare('SELECT status FROM jobs').get().status,'rendering');
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
