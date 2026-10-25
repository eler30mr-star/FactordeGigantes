import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFileSync,readdirSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {dispatchChannelResearch,channelResearchContext,storeChannelResearch,storeChannelScript} from '../src/channel-research.mjs';
import worker from '../src/worker.js';
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
 const request=await dispatchChannelResearch(env,id,async()=>({status:204}));
 const saved=await storeChannelResearch(env,{request_id:request.request_id,report:research});
 script.source_research_run_id=saved.run_id;
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
