import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFileSync,readdirSync} from 'node:fs';
import {reserveAiBudget,validateAiReport,storeAiReport,readAiReports,classifyWithCloudflare} from '../src/ai-research-team.mjs';
import worker from '../src/worker.js';

function setup(){
 const raw=new DatabaseSync(':memory:');raw.exec('PRAGMA foreign_keys=ON');
 for(const p of readdirSync(new URL('../migrations/',import.meta.url)).filter(p=>p.endsWith('.sql')).sort())
   raw.exec(readFileSync(new URL('../migrations/'+p,import.meta.url),'utf8'));
 const db={prepare(sql){const stmt=raw.prepare(sql);const make=params=>({
  async run(){const r=stmt.run(...params);return {meta:{changes:Number(r.changes)}};},
  async all(){return {results:stmt.all(...params)};},async first(){return stmt.get(...params)??null;}
 });return {...make([]),bind(...params){return make(params);}};},async batch(stmts){
   raw.exec('BEGIN');try{const r=[];for(const s of stmts)r.push(await s.run());raw.exec('COMMIT');return r;}
   catch(e){raw.exec('ROLLBACK');throw e;}
 }};
 return {db,raw};
}
const now=new Date();
function report(){return {schema:'fdg_ai_pipeline_v1',collected_on:now.toISOString().slice(0,10),
 selected_wikidata_id:'Q100',company:'Empresa ejemplo',status:'candidate_claims_generated',analysis_provider:'qwen',
 evidence_manifest:[{id:'E001',wikidata_id:'Q100',company:'Empresa ejemplo',url:'https://www.justice.gov/example',
  document_sha256:'a'.repeat(64),page:null,source_class:'public_authority_candidate',
  excerpt:'La Empresa ejemplo declaró en 2018 que se encontraba bajo revisión de las autoridades por sus operaciones y estados financieros públicos.'}],
 candidate_claims:[{statement:'La Empresa ejemplo fue investigada en 2099.',evidence_ids:['E001'],status:'candidate_unverified',human_verified:false}],
 preliminary_claims:[],reviews:[],classification:[],source_documents:[],missing_questions:[],
 stages:[{provider:'qwen',role:'extract',status:'success'}],facts_verified_automatically:0,
 ready_for_script:false,ready_for_youtube:false,publication_authorized:false};}

test('reservas D1 tienen límite diario, mensual y no pueden reutilizarse',async()=>{
 const {db}=setup(),day=new Date('2026-10-22T12:00:00Z');
 const results=await Promise.all(Array.from({length:12},(_,i)=>reserveAiBudget(db,'tavily','test-'+i,day)));
 assert.equal(results.filter(r=>r.allowed).length,8);
 assert.equal((await reserveAiBudget(db,'tavily','test-0',new Date('2026-10-23'))).allowed,false);
 for(let d=1;d<=10;d++)for(let i=0;i<4;i++)await reserveAiBudget(db,'exa',`oct-${d}-${i}`,new Date(`2026-10-${String(d).padStart(2,'0')}`));
 for(let d=11;d<=15;d++)for(let i=0;i<4;i++)await reserveAiBudget(db,'exa',`oct-${d}-${i}`,new Date(`2026-10-${d}`));
 assert.equal((await reserveAiBudget(db,'exa','exhausted-month',new Date('2026-10-16'))).allowed,false);
 assert.equal((await reserveAiBudget(db,'exa','next-month',new Date('2026-11-01'))).allowed,true);
 await assert.rejects(reserveAiBudget(db,'paid-provider','invalid'),RangeError);
});
test('ingesta conserva citas e impide aprobación, mezclas e inventar referencias',()=>{
 validateAiReport(report());
 for(const mutate of [r=>r.ready_for_script=true,r=>r.facts_verified_automatically=1,
  r=>r.evidence_manifest[0].wikidata_id='Q200',r=>r.evidence_manifest[0].url='https://127.0.0.1/private',
  r=>r.candidate_claims[0].evidence_ids=['E999'],r=>r.stages=[],
  r=>r.preliminary_claims=[{...r.candidate_claims[0],human_verified:true}]]){
  const r=report();mutate(r);assert.throws(()=>validateAiReport(r),RangeError);
 }
});
test('corroboración por fuente única no puede indicar verificación factual',()=>{
 const r=report();
 r.source_quality={
  unique_documents:1,independent_domains:1,regulatory_primary_domains:1,
  claims_requiring_review:1,all_claims_verified:false,ready_for_script:false,
  claim_gaps:[{claim_index:1,cited_documents:1,independent_domains:1,
   regulatory_primary_cited:true,gaps:['only_one_document','no_independent_domain'],
   verification_state:'requires_corroboration'}]
 };
 assert.doesNotThrow(()=>validateAiReport(r));
 r.source_quality.all_claims_verified=true;
 assert.throws(()=>validateAiReport(r),RangeError);
 r.source_quality.all_claims_verified=false;
 r.source_quality.claim_gaps[0].cited_documents=2;
 assert.throws(()=>validateAiReport(r),RangeError);
});

test('historial SQLite real idempotente, alerta numérica y puertas SQL cerradas',async()=>{
 const {db,raw}=setup();const first=await storeAiReport(db,report()),second=await storeAiReport(db,report());
 assert.equal(first.run_id,second.run_id);
 const out=await readAiReports(db);assert.equal(out.runs.length,1);
 assert.equal(out.runs[0].report.candidate_claims[0].numeric_support_state,'unsupported_numbers_need_review');
 assert.throws(()=>raw.prepare('UPDATE market_ai_pipeline_runs SET publication_authorized=1').run());
 assert.equal(raw.prepare('PRAGMA foreign_key_check').all().length,0);
});
test('citas de una sola noticia devuelven la cola a búsqueda de fuentes independientes',async()=>{
 const {db,raw}=setup(),r=report(),day=new Date().toISOString().slice(0,10);
 raw.prepare('INSERT INTO market_entities(wikidata_id,title,first_seen,last_seen) VALUES (?,?,?,?)')
   .run('Q100','Empresa ejemplo',day,day);
 raw.prepare('INSERT INTO market_research_selection_runs(id,observed_on,method,candidate_count,qualified_count,ranked_snapshot_json) VALUES (?,?,?,?,?,?)')
   .run('selection-test',day,'research_market_priority_v1',1,1,'{}');
 raw.prepare('INSERT INTO market_research_queue(id,wikidata_id,title,selection_run_id,market_score,state) VALUES (?,?,?,?,?,?)')
   .run('rq-fixture','Q100','Empresa ejemplo','selection-test',55,'researching');
 r.source_quality={
  unique_documents:1,independent_domains:1,regulatory_primary_domains:1,
  claims_requiring_review:1,all_claims_verified:false,ready_for_script:false,
  claim_gaps:[{claim_index:1,cited_documents:1,independent_domains:1,
   regulatory_primary_cited:true,gaps:['only_one_document','no_independent_domain'],
   verification_state:'requires_corroboration'}]
 };
 const output=await storeAiReport(db,r);
 assert.equal(output.queue_state,'awaiting_sources');
 assert.equal(output.reason,'independent_sources_required');
 assert.equal(raw.prepare("SELECT state FROM market_research_queue WHERE id='rq-fixture'").get().state,'awaiting_sources');
 assert.equal(raw.prepare("SELECT script_authorized FROM market_research_queue WHERE id='rq-fixture'").get().script_authorized,0);
 raw.prepare("UPDATE market_research_queue SET state='review' WHERE id='rq-fixture'").run();
 await storeAiReport(db,r);
 assert.equal(raw.prepare("SELECT state FROM market_research_queue WHERE id='rq-fixture'").get().state,'review');
 assert.equal(raw.prepare("PRAGMA foreign_key_check").all().length,0);
});

test('Cloudflare sin modalidad gratuita confirmada nunca invoca IA',async()=>{
 const out=await classifyWithCloudflare({AI:{run(){assert.fail('inferencia sin modalidad confirmada');}}},{});
 assert.equal(out.status,'free_mode_unconfirmed');
});
test('clasificador Cloudflare admite solo categorías y reserva antes de inferir',async()=>{
 const {db}=setup();let calls=0;
 const env={DB:db,CLOUDFLARE_AI_FREE_CONFIRMED:'1',AI:{async run(model,body){
  calls++;assert.equal(model,'@cf/meta/llama-3.1-8b-instruct');assert.equal(body.max_tokens,512);
  return {response:JSON.stringify({classification:[{evidence_id:'E001',category:'documentary'}]})};
 }}};
 const payload={request_id:'classify-001',evidence:report().evidence_manifest.map(e=>({id:e.id,excerpt:e.excerpt}))};
 assert.equal((await classifyWithCloudflare(env,payload)).status,'success');
 assert.equal((await classifyWithCloudflare(env,payload)).status,'budget_denied');
 assert.equal(calls,1);
});
test('ninguna escritura IA admite tokens ADMIN o RENDERER',async()=>{
 const env={ADMIN_TOKEN:'a'.repeat(32),RENDERER_TOKEN:'r'.repeat(32),DB:{}};
 for(const path of ['/api/market/ai-budget/reserve','/api/market/ai-classify','/api/market/ai-pipeline/ingest'])
  for(const auth of ['',env.ADMIN_TOKEN,env.RENDERER_TOKEN]){
   const r=await worker.fetch(new Request('https://factor.test'+path,{method:'POST',headers:{Authorization:'Bearer '+auth}}),env,{});
   assert.equal(r.status,401);
  }
 assert.equal((await worker.fetch(new Request('https://factor.test/api/market/ai-pipeline'),env,{})).status,401);
 const {db}=setup();env.DB=db;
 assert.equal((await worker.fetch(new Request('https://factor.test/api/market/ai-pipeline',{
  headers:{Authorization:'Bearer '+env.ADMIN_TOKEN}}),env,{})).status,200);
});
