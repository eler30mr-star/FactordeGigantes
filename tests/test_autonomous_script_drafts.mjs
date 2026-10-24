import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFileSync,readdirSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {evidenceLinkSha256,prepareEditorialDraft,storeAutonomousDraft,readEditorialScriptContext} from '../src/autonomous-script-drafts.mjs';
import {storeAiReport,readScriptContext} from '../src/ai-research-team.mjs';
import {validateDossier} from '../src/editorial.mjs';
import worker from '../src/worker.js';

const processResult=spawnSync('python',['-c',`
import sys,json
from datetime import datetime,timezone
sys.path.insert(0,'tests')
from test_documentary_blueprint import fixture
from test_documentary_script import narrative,ScriptTests
from tools.documentary_script import write_script
from tools.ai_research_pipeline import evidence_gaps
r,selection=fixture()
r.update(collected_on=datetime.now(timezone.utc).date().isoformat(),status='candidate_claims_generated',
 analysis_provider='gemini',source_documents=[],classification=[],missing_questions=[],preliminary_claims=[],
 ready_for_youtube=False,stages=[{'provider':'gemini','role':'analyze','status':'success'},
 {'provider':'groq','role':'review','status':'success'}])
for e in r['evidence_manifest']:
 e.update(page=None,excerpt='La Empresa analizada presentó públicamente su informe sobre las operaciones y decisiones empresariales, sujeto a revisión independiente y contraste documental.')
for review in r['reviews']:review.update(reason='Pasajes candidatos con apoyo documental suficiente para revisión.',human_verified=False)
r['source_quality']=evidence_gaps(r['evidence_manifest'],r['candidate_claims'])
s=write_script(r,selection,clients=ScriptTests().configured(),research_run_id='ai-'+'a'*28)
print(json.dumps({'research':r,'script':s},ensure_ascii=False))
`],{cwd:new URL('../',import.meta.url),encoding:'utf8',timeout:20000});
assert.equal(processResult.status,0,processResult.stderr);
const original=JSON.parse(processResult.stdout);
function fixture(){return structuredClone(original);}
function setup(){
 const raw=new DatabaseSync(':memory:');raw.exec('PRAGMA foreign_keys=ON');
 for(const p of readdirSync(new URL('../migrations/',import.meta.url)).filter(p=>p.endsWith('.sql')).sort())
  raw.exec(readFileSync(new URL('../migrations/'+p,import.meta.url),'utf8'));
 let tail=Promise.resolve();
 const db={prepare(sql){const stmt=raw.prepare(sql);const make=params=>({
  async run(){const r=stmt.run(...params);return {meta:{changes:Number(r.changes)}};},
  async all(){return {results:stmt.all(...params)};},async first(){return stmt.get(...params)??null;}
 });return {...make([]),bind(...params){return make(params);}};},batch(stmts){
  const task=tail.then(async()=>{raw.exec('BEGIN');try{const result=[];for(const s of stmts)result.push(await s.run());raw.exec('COMMIT');return result;}
   catch(e){raw.exec('ROLLBACK');throw e;}});tail=task.catch(()=>{});return task;
 }};return {raw,db};
}
async function ready(){
 const {db,raw}=setup(),{research,script}=fixture(),day=research.collected_on;
 raw.prepare('INSERT INTO market_entities(wikidata_id,title,first_seen,last_seen) VALUES (?,?,?,?)').run('Q100',research.company,day,day);
 raw.prepare('INSERT INTO market_research_selection_runs(id,observed_on,method,candidate_count,qualified_count,ranked_snapshot_json) VALUES (?,?,?,?,?,?)').run('selection-test',day,'research_market_priority_v1',1,1,'{}');
 raw.prepare('INSERT INTO market_research_queue(id,wikidata_id,title,selection_run_id,market_score,state) VALUES (?,?,?,?,?,?)').run('rq-fixture','Q100',research.company,'selection-test',55,'researching');
 const saved=await storeAiReport(db,research);script.source_research_run_id=saved.run_id;
 return {db,raw,script,runId:saved.run_id};
}

test('guion Python real cruza huella JS, contrato editorial y SQLite con todas las aprobaciones pendientes',async()=>{
 const {db,raw,script,runId}=await ready();
 const context=await readScriptContext(db,runId);
 assert.equal(script.source_evidence_sha256,await evidenceLinkSha256(context.research));
 const saved=await storeAutonomousDraft(db,{research_run_id:runId,script});assert.equal(saved.created,true);
 const job=raw.prepare('SELECT * FROM jobs WHERE id=?').get(saved.job_id);
 const dossier=raw.prepare('SELECT * FROM editorial_dossiers WHERE job_id=?').get(saved.job_id);
 assert.equal(job.status,'draft');assert.equal(dossier.editor_attested,0);
 const m=JSON.parse(job.manifest_json),d=JSON.parse(dossier.dossier_json);
 assert.equal(validateDossier(d,m).verified_claims,0);
 assert.equal(m.segments.map(s=>s.voiceover).join(' ').split(/\s+/).length,1200);
 assert.ok(m.segments.every(s=>s.voiceover.length<=900));
 assert.equal(d.assets[0].reference_sha256,'78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d');
 assert.equal(raw.prepare('SELECT state FROM market_research_queue').get().state,'review');
 assert.equal(raw.prepare('SELECT COUNT(*) n FROM ai_budget_reservations').get().n,0);
 assert.equal(raw.prepare('PRAGMA foreign_key_check').all().length,0);
 for(const col of ['automatic_factual_approval','automatic_render_approval','publication_authorized'])
  assert.throws(()=>raw.prepare(`UPDATE autonomous_script_drafts SET ${col}=1`).run());
});
test('dos importaciones simultáneas producen un trabajo y un evento, sin sobrescribir edición humana',async()=>{
 const {db,raw,script,runId}=await ready(),body={research_run_id:runId,script};
 const receipts=await Promise.all([storeAutonomousDraft(db,body),storeAutonomousDraft(db,body)]);
 assert.equal(receipts[0].job_id,receipts[1].job_id);assert.equal(receipts.filter(r=>r.created).length,1);
 raw.prepare("UPDATE jobs SET title='Edición editorial humana',status='review'").run();
 raw.prepare("UPDATE editorial_dossiers SET editor_attested=1,editor_name='Editora de prueba'").run();
 assert.equal((await storeAutonomousDraft(db,body)).created,false);
 const context=await readEditorialScriptContext(db,runId);
 assert.deepEqual(context.existing_script_draft.script,script);
 assert.equal(context.existing_script_draft.job_id,receipts[0].job_id);
 assert.equal(raw.prepare('SELECT title FROM jobs').get().title,'Edición editorial humana');
 assert.equal(raw.prepare('SELECT editor_attested FROM editorial_dossiers').get().editor_attested,1);
 assert.equal(raw.prepare('SELECT COUNT(*) n FROM jobs').get().n,1);
 assert.equal(raw.prepare("SELECT COUNT(*) n FROM events WHERE action='autonomous_draft_created'").get().n,1);
 const different=structuredClone(script);different.title='Otro título documental diferente';
 assert.equal((await storeAutonomousDraft(db,{research_run_id:runId,script:different})).status,409);
});
test('alteraciones de procedencia, citas, duración y permisos se rechazan antes de crear trabajo',async()=>{
 for(const change of [s=>s.source_evidence_sha256='0'.repeat(64),s=>s.wikidata_id='Q200',
  s=>s.source_research_run_id='ai-'+'b'.repeat(28),s=>s.publication_authorized=true,
  s=>s.scenes[0].paragraphs[0].human_verified=true,s=>s.scenes[0].paragraphs[0].evidence_ids=['E001'],
  s=>s.narration_word_count=800,s=>s.scenes[0].narration_text='Texto alterado']){
  const {db,raw,script,runId}=await ready();change(script);
  await assert.rejects(storeAutonomousDraft(db,{research_run_id:runId,script}),RangeError);
  assert.equal(raw.prepare('SELECT COUNT(*) n FROM jobs').get().n,0);
 }
});
test('dossier insuficiente no entra al panel aunque aporte huella válida',async()=>{
 const {research,script}=fixture();research.reviews[2].assessment='insufficient_context';
 script.source_evidence_sha256=await evidenceLinkSha256(research);
 await assert.rejects(prepareEditorialDraft(research,script,script.source_research_run_id),RangeError);
});
test('una revisión humana abierta bloquea otra importación y el fallo SQL revierte todo',async()=>{
 const a=await ready();a.raw.prepare("UPDATE market_research_queue SET state='review'").run();
 assert.equal((await storeAutonomousDraft(a.db,{research_run_id:a.runId,script:a.script})).reason,'editorial_review_already_open');
 assert.equal(a.raw.prepare('SELECT COUNT(*) n FROM jobs').get().n,0);
 const b=await ready();b.raw.exec("CREATE TRIGGER simulate_failure BEFORE INSERT ON editorial_dossiers BEGIN SELECT RAISE(ABORT,'fallo de almacenamiento'); END");
 await assert.rejects(storeAutonomousDraft(b.db,{research_run_id:b.runId,script:b.script}));
 for(const table of ['jobs','autonomous_script_drafts','events'])assert.equal(b.raw.prepare(`SELECT COUNT(*) n FROM ${table}`).get().n,0);
 assert.equal(b.raw.prepare('SELECT state FROM market_research_queue').get().state,'researching');
});
test('ruta de ingesta sólo admite OIDC y el origen automático bloquea render de voz alternativa',async()=>{
 const {db,raw,script,runId}=await ready();const env={DB:db,ADMIN_TOKEN:'a'.repeat(32),RENDERER_TOKEN:'r'.repeat(32)};
 for(const token of [env.ADMIN_TOKEN,env.RENDERER_TOKEN]){
  const response=await worker.fetch(new Request('https://test/api/market/ai-pipeline/script-ingest',{
   method:'POST',headers:{Authorization:'Bearer '+token,'Content-Type':'application/json'},body:JSON.stringify({research_run_id:runId,script})}),env);
  assert.equal(response.status,401);
 }
 const saved=await storeAutonomousDraft(db,{research_run_id:runId,script});
 raw.prepare("UPDATE jobs SET status='approved' WHERE id=?").run(saved.job_id);
 let response=await worker.fetch(new Request(`https://test/api/jobs/${saved.job_id}/dispatch`,{method:'POST',headers:{Authorization:'Bearer '+env.ADMIN_TOKEN}}),env);
 assert.equal(response.status,409);
 raw.prepare("UPDATE jobs SET status='queued' WHERE id=?").run(saved.job_id);
 for(const [path,method] of [[`/api/renderer/jobs/${saved.job_id}`,'GET'],[`/api/renderer/jobs/${saved.job_id}/report`,'POST']]){
  response=await worker.fetch(new Request('https://test'+path,{method,headers:{Authorization:'Bearer '+env.RENDERER_TOKEN}}),env);
  assert.equal(response.status,409);
 }
 assert.equal(raw.prepare('SELECT status FROM jobs').get().status,'queued');
});
