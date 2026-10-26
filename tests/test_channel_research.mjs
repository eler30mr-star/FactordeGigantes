import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFileSync,readdirSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {dispatchChannelResearch,channelResearchContext,storeChannelResearch,storeChannelScript} from '../src/channel-research.mjs';
import worker from '../src/worker.js';
import {editorialFocusSha} from '../src/editorial-focus.mjs';
function setup(){
 const raw=new DatabaseSync(':memory:');for(const p of ['0017_channel_control.sql','0019_episode_research.sql'])raw.exec(readFileSync(new URL('../migrations/'+p,import.meta.url),'utf8'));
 const id=crypto.randomUUID();raw.prepare("INSERT INTO channel_episodes(id,channel,origin,company,topic,instruction) VALUES (?,'factor-de-gigantes','chat','BlackBerry','La pérdida de liderazgo','instrucción del propietario')").run(id);
 let tail=Promise.resolve();const db={prepare(sql){let args=[];return {bind(...a){args=a;return this;},async first(){return raw.prepare(sql).get(...args)||null;},async all(){return {results:raw.prepare(sql).all(...args)};},async run(){return {meta:{changes:Number(raw.prepare(sql).run(...args).changes)}};}};},batch(statements){const next=tail.then(async()=>{raw.exec('BEGIN');try{const r=[];for(const s of statements)r.push(await s.run());raw.exec('COMMIT');return r;}catch(e){raw.exec('ROLLBACK');throw e;}});tail=next.catch(()=>{});return next;}};
 return {id,raw,env:{DB:db,GITHUB_REPO:'eler30mr-star/FactordeGigantes',GITHUB_DISPATCH_TOKEN:'test-github-dispatch-token-0001',ADMIN_TOKEN:'test-owner-private-token-0001',FINAL_AI_INTEGRATION_ENABLED:'1'}};
}
test('manual episode dispatch works with automatic off and sends only persisted identity',async()=>{
 const {env,id}=setup();let count=0;
 const result=await dispatchChannelResearch(env,id,async(url,options)=>{count++;assert.equal(JSON.parse(options.body).inputs.episode_id,id);assert.equal(JSON.parse(options.body).inputs.phase,'episode');assert.equal(JSON.parse(options.body).ref,'main');return {status:204};});
 assert.equal(result.started,true);assert.equal(count,1);
 const context=await channelResearchContext(env,{request_id:result.request_id});assert.equal(context.episode.company,'BlackBerry');assert.equal(context.episode.topic,'La pérdida de liderazgo');
 assert.equal((await dispatchChannelResearch(env,id,()=>assert.fail())).started,false);
});
test('pause rejects before writes or provider/Actions requests',async()=>{
 const {env,id,raw}=setup();env.FINAL_AI_INTEGRATION_ENABLED='0';
 assert.equal((await dispatchChannelResearch(env,id,()=>assert.fail())).reason,'research_paused');
 assert.equal(raw.prepare('SELECT count(*) n FROM channel_episode_research').get().n,0);
});
test('uncertain dispatch blocks resubmission; concurrent requests have one winner',async()=>{
 const {env,id}=setup();let calls=0;
 const fetcher=async()=>{calls++;throw Error('network');};
 const results=await Promise.all([dispatchChannelResearch(env,id,fetcher),dispatchChannelResearch(env,id,fetcher)]);
 assert.equal(calls,1);assert.ok(results.some(r=>r.reason==='dispatch_unknown'));
 assert.equal((await dispatchChannelResearch(env,id,()=>assert.fail())).started,false);
});
test('blocked research preserves selection and allows explicit bounded retry',async()=>{
 const {env,id,raw}=setup();const sent=await dispatchChannelResearch(env,id,async()=>({status:204}));
 await storeChannelResearch(env,{request_id:sent.request_id,blocked:true});
 assert.equal(raw.prepare('SELECT state FROM channel_episodes').get().state,'selected');
 assert.equal((await dispatchChannelResearch(env,id,async()=>({status:204}))).started,true);
});
test('report must match chosen topic and company; ADMIN cannot forge workflow callbacks',async()=>{
 const {env,id}=setup();const sent=await dispatchChannelResearch(env,id,async()=>({status:204}));
 await assert.rejects(()=>storeChannelResearch(env,{request_id:sent.request_id,report:{company:'Otra empresa'}}),RangeError);
 const response=await worker.fetch(new Request('https://factor.test/api/market/channel-episode/research',{method:'POST',headers:{Authorization:'Bearer '+env.ADMIN_TOKEN},body:'{}'}),env);
 assert.equal(response.status,401);
});

test('cited script creates real editorial draft without any legacy market selection or approval',async()=>{
 const {env,id,raw}=setup();
 for(const p of readdirSync(new URL('../migrations/',import.meta.url)).filter(p=>p.endsWith('.sql')).sort())raw.exec(readFileSync(new URL('../migrations/'+p,import.meta.url),'utf8'));
 const fixture=spawnSync('python',['tests/helpers/channel_research_fixture.py'],{cwd:new URL('../',import.meta.url),encoding:'utf8'});
 assert.equal(fixture.status,0,fixture.stderr);
 const {research,script}=JSON.parse(fixture.stdout);
 raw.prepare('UPDATE channel_episodes SET company=? WHERE id=?').run(research.company,id);
 research.editorial_topic='La pérdida de liderazgo';research.selected_episode_id=id;
 research.editorial_focus_review={schema:'fdg_editorial_focus_v1',status:'aligned',topic:research.editorial_topic,
  claims_sha256:await editorialFocusSha(research.editorial_topic,research.candidate_claims),publication_authorized:false,
  judgments:research.candidate_claims.map((c,i)=>({claim_index:i+1,relevance:'central',reason:'Juicio simulado para el contrato del episodio.'}))};
 const request=await dispatchChannelResearch(env,id,async()=>({status:204}));
 const saved=await storeChannelResearch(env,{request_id:request.request_id,report:research});
 script.source_research_run_id=saved.run_id;
 const original=raw.prepare('SELECT report_json FROM market_ai_pipeline_runs WHERE id=?').get(saved.run_id).report_json;
 const unbound=JSON.parse(original);delete unbound.editorial_focus_review;
 raw.prepare('UPDATE market_ai_pipeline_runs SET report_json=? WHERE id=?').run(JSON.stringify(unbound),saved.run_id);
 await assert.rejects(()=>storeChannelScript(env,{request_id:request.request_id,script}),/enfoque elegido/);
 assert.equal(raw.prepare('SELECT count(*) n FROM jobs').get().n,0);
 raw.prepare('UPDATE market_ai_pipeline_runs SET report_json=? WHERE id=?').run(original,saved.run_id);
 // A script failure is retryable without a new source or analyst run.
 await storeChannelResearch(env,{request_id:request.request_id,blocked:true});
 const resumed=await dispatchChannelResearch(env,id,async()=>({status:204}));
 const checkpoint=await channelResearchContext(env,{request_id:resumed.request_id,include_checkpoint:true});
 assert.equal(checkpoint.checkpoint.run_id,saved.run_id);
 assert.equal(checkpoint.checkpoint.report.selected_episode_id,id);
 assert.equal((await channelResearchContext(env,{request_id:resumed.request_id})).checkpoint,undefined);
 // A paused callback cannot read the full saved evidence or continue providers.
 env.FINAL_AI_INTEGRATION_ENABLED='0';
 assert.equal((await channelResearchContext(env,{request_id:resumed.request_id,include_checkpoint:true})).checkpoint,null);
 env.FINAL_AI_INTEGRATION_ENABLED='1';
 request.request_id=resumed.request_id;
 const result=await storeChannelScript(env,{request_id:request.request_id,script});
 assert.equal(result.created,true);
 const again=await storeChannelScript(env,{request_id:request.request_id,script});
 assert.equal(again.job_id,result.job_id);assert.equal(again.created,false);
 assert.equal(raw.prepare('SELECT status FROM jobs WHERE id=?').get(result.job_id).status,'draft');
 assert.equal(raw.prepare('SELECT editor_attested FROM editorial_dossiers WHERE job_id=?').get(result.job_id).editor_attested,0);
 assert.equal(raw.prepare('SELECT count(*) n FROM market_research_queue').get().n,0);
 assert.equal(raw.prepare('SELECT count(*) n FROM market_research_selection_runs').get().n,0);
 assert.equal(raw.prepare('SELECT state FROM channel_episodes WHERE id=?').get(id).state,'review');
});

test('late dispatch acknowledgement cannot revive an already blocked investigation',async()=>{
 const {env,id,raw}=setup();
 await dispatchChannelResearch(env,id,async(url,options)=>{
  const request_id=JSON.parse(options.body).inputs.episode_request_id;
  await storeChannelResearch(env,{request_id,blocked:true});return {status:204};
 });
 assert.equal(raw.prepare('SELECT state FROM channel_episodes').get().state,'selected');
 assert.equal(raw.prepare('SELECT state FROM channel_episode_research').get().state,'blocked');
});

test('legacy empty analyst checkpoint recovers only same-episode lineage and keeps new sources pending',async()=>{
 const {env,id,raw}=setup();
 for(const p of readdirSync(new URL('../migrations/',import.meta.url)).filter(p=>p.endsWith('.sql')).sort())raw.exec(readFileSync(new URL('../migrations/'+p,import.meta.url),'utf8'));
 const fixture=spawnSync('python',['tests/helpers/channel_research_fixture.py'],{cwd:new URL('../',import.meta.url),encoding:'utf8'});
 assert.equal(fixture.status,0,fixture.stderr);const {research,script}=JSON.parse(fixture.stdout);
 raw.prepare('UPDATE channel_episodes SET company=? WHERE id=?').run(research.company,id);
 research.editorial_topic='La pérdida de liderazgo';research.selected_episode_id=id;
 const request=await dispatchChannelResearch(env,id,async()=>({status:204}));
 const parent=await storeChannelResearch(env,{request_id:request.request_id,report:research});
 const empty={...research,candidate_claims:[],reviews:[],analysis_provider:null,status:'sources_only',
  source_quality:{...research.source_quality,claims_requiring_review:0,claim_gaps:[],all_claims_verified:false,ready_for_script:false},
  editorial_replanning:{parent_run_id:parent.run_id,topic_unchanged:true}};
 const latest=await storeChannelResearch(env,{request_id:request.request_id,report:empty});
 const count=raw.prepare('SELECT count(*) n FROM market_ai_pipeline_runs').get().n;
 const context=await channelResearchContext(env,{request_id:request.request_id,include_checkpoint:true});
 assert.equal(context.checkpoint.run_id,latest.run_id);
 assert.deepEqual(context.checkpoint.report.candidate_claims.map(c=>c.statement),research.candidate_claims.map(c=>c.statement));
 assert.deepEqual(context.checkpoint.report.pending_editorial_analysis.sources.evidence_manifest,empty.evidence_manifest);
 assert.equal(context.checkpoint.report.pending_editorial_analysis.parent_run_id,parent.run_id);
 assert.equal(raw.prepare('SELECT count(*) n FROM market_ai_pipeline_runs').get().n,count); // Read preserves history.
 const saved=await storeChannelResearch(env,{request_id:request.request_id,report:context.checkpoint.report});
 script.source_research_run_id=saved.run_id;
 await assert.rejects(()=>storeChannelScript(env,{request_id:request.request_id,script}),/pendientes de análisis/);
 assert.equal(raw.prepare('SELECT count(*) n FROM jobs').get().n,0);
 // An unrelated parent cannot supply facts to this episode, even if the link exists.
 const other={...research,selected_episode_id:crypto.randomUUID()};
 raw.prepare('UPDATE market_ai_pipeline_runs SET report_json=? WHERE id=?').run(JSON.stringify(other),parent.run_id);
 raw.prepare('UPDATE channel_episode_research SET research_run_id=? WHERE id=?').run(latest.run_id,request.request_id);
 assert.equal((await channelResearchContext(env,{request_id:request.request_id,include_checkpoint:true})).checkpoint.report.candidate_claims.length,0);
});

test('checkpoint returns observed primary excerpts only from this exact episode, topic and company',async()=>{
 const {env,id,raw}=setup();
 for(const p of readdirSync(new URL('../migrations/',import.meta.url)).filter(p=>p.endsWith('.sql')).sort())raw.exec(readFileSync(new URL('../migrations/'+p,import.meta.url),'utf8'));
 const request=await dispatchChannelResearch(env,id,async()=>({status:204}));
 const base={selected_episode_id:id,company:'BlackBerry',editorial_topic:'La pérdida de liderazgo',selected_wikidata_id:'Q100',
  candidate_claims:[],evidence_manifest:[{id:'E001',company:'BlackBerry',wikidata_id:'Q100',
   url:'https://corporate.example/report.pdf',source_class:'potential_official_pdf',document_sha256:'a'.repeat(64),
   page:1,excerpt:'Una cita corporativa observada en una versión previa de este mismo episodio, pendiente de contraste independiente.'}]};
 const insert=raw.prepare("INSERT INTO market_ai_pipeline_runs(id,collected_on,wikidata_id,status,analysis_provider,evidence_count,claims_count,report_json) VALUES (?,date('now'),'Q100','sources_only',NULL,1,0,?)");
 const own='ai-'+'a'.repeat(28),current='ai-'+'b'.repeat(28);
 insert.run(own,JSON.stringify(base));
 for(const [n,change] of [{selected_episode_id:crypto.randomUUID()},{company:'Otra empresa'},{editorial_topic:'Otro enfoque'},{selected_wikidata_id:'Q200'}].entries()){
  insert.run('ai-'+String(n+1).repeat(28),JSON.stringify({...base,...change}));
 }
 insert.run(current,JSON.stringify({...base,evidence_manifest:[{...base.evidence_manifest[0],source_class:'public_document_candidate'}]}));
 raw.prepare('UPDATE channel_episode_research SET research_run_id=? WHERE id=?').run(current,request.request_id);
 const before=raw.prepare('SELECT count(*) n FROM market_ai_pipeline_runs').get().n;
 const context=await channelResearchContext(env,{request_id:request.request_id,include_checkpoint:true});
 assert.equal(context.checkpoint.documentary_history.source_run_id,own);
 assert.deepEqual(context.checkpoint.documentary_history.evidence_manifest,base.evidence_manifest);
 assert.equal(raw.prepare('SELECT count(*) n FROM market_ai_pipeline_runs').get().n,before);
 assert.equal((await channelResearchContext(env,{request_id:request.request_id})).checkpoint,undefined);
});
