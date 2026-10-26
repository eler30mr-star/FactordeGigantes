import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFileSync,readdirSync} from 'node:fs';
import {channelProgress,completeChannelEpisode} from '../src/channel-progress.mjs';
import {receiveChannelInstruction} from '../src/channel-control.mjs';
import {mountEpisodeWorkbench} from '../public/episode-workbench.js';
import {recoverEpisodeVideo,reportEpisodeDelivery,episodeDeliveryStatus} from '../src/episode-delivery.mjs';
import worker from '../src/worker.js';

function setup(){
 const raw=new DatabaseSync(':memory:');raw.exec('PRAGMA foreign_keys=ON');
 for(const p of readdirSync(new URL('../migrations/',import.meta.url)).filter(p=>p.endsWith('.sql')).sort())raw.exec(readFileSync(new URL('../migrations/'+p,import.meta.url),'utf8'));
 const db={prepare(sql){let args=[];return {bind(...a){args=a;return this;},async first(){return raw.prepare(sql).get(...args)||null;},async all(){return {results:raw.prepare(sql).all(...args)};},async run(){return {meta:{changes:Number(raw.prepare(sql).run(...args).changes)}};}};},async batch(stmts){raw.exec('BEGIN');try{const result=[];for(const s of stmts)result.push(await s.run());raw.exec('COMMIT');return result;}catch(e){raw.exec('ROLLBACK');throw e;}}};
 const env={DB:db,ADMIN_TOKEN:'fake-progress-owner-token-00000',RENDERER_TOKEN:'fake-progress-render-token-0000',FINAL_AI_INTEGRATION_ENABLED:'1'};
 const id=crypto.randomUUID(),requestId=crypto.randomUUID(),jobId=crypto.randomUUID(),hash='a'.repeat(64);
 raw.prepare("INSERT INTO channel_episodes(id,channel,origin,company,topic,instruction) VALUES (?,'factor-de-gigantes','chat','BlackBerry','Su pérdida de liderazgo','instrucción del propietario')").run(id);
 function research(state='sent',checkpoint=null){raw.prepare('INSERT INTO channel_episode_research(id,episode_id,state,research_run_id) VALUES(?,?,?,?)').run(requestId,id,state,checkpoint);}
 function job(status='draft'){
  raw.prepare("INSERT INTO jobs(id,title,format,status,manifest_json) VALUES (?,'Documental del episodio','long',?,?)").run(jobId,status,JSON.stringify({title:'Documental del episodio',angle:'La transformación del mercado móvil',format:'long',sources:['https://example.com/a','https://example.org/b'],segments:[{headline:'Inicio',voiceover:'Una narración pendiente de contrastar.'},{headline:'Después',voiceover:'Otra narración pendiente de contrastar.'}]}));
  raw.prepare("UPDATE channel_episode_research SET state='review',job_id=?,research_run_id='ai-saved' WHERE id=?").run(jobId,requestId);
  raw.prepare("UPDATE channel_episodes SET state='review' WHERE id=?").run(id);
  raw.prepare("INSERT INTO editorial_dossiers(job_id,dossier_json) VALUES (?,'{}')").run(jobId);
 }
 function video(run='123'){
  raw.prepare("INSERT INTO events(job_id,action,note) VALUES (?,'episode_preview_ready',?)").run(jobId,JSON.stringify({run_id:'123',export_sha256:hash,seconds:600}));
  raw.prepare("INSERT INTO youtube_exports(id,source_run_id,artifact_id,archive_sha256,video_bytes,episode_json,export_json,metadata_json) VALUES(?,?, '456',?,20000,'{}','{}','{}')").run(hash,run,'b'.repeat(64));
 }
 function publish(state='confirmed'){
  raw.prepare("UPDATE youtube_exports SET state='uploaded',video_id='Abcdef12345',target_channel_id=? WHERE id=?").run('UC'+'a'.repeat(22),hash);
  raw.prepare("INSERT INTO youtube_publications(export_id,request_id,video_id,channel_id,mode,reviewer,state) VALUES(?,?, 'Abcdef12345',?, 'public','Editora de prueba',?)").run(hash,crypto.randomUUID(),'UC'+'a'.repeat(22),state);
 }
 return {raw,env,id,requestId,jobId,hash,research,job,video,publish};
}

test('episode progress exposes the next real action and does not claim provider/render completion',async()=>{
 const f=setup();let p=await channelProgress(f.env,f.id);assert.equal(p.next_step,'start_research');assert.equal(p.steps[3].state,'pending');
 f.env.FINAL_AI_INTEGRATION_ENABLED='0';p=await channelProgress(f.env,f.id);assert.equal(p.action_enabled,false);assert.equal(p.steps[1].state,'blocked');
 f.research('blocked','ai-saved');p=await channelProgress(f.env,f.id);assert.equal(p.next_step,'resume_research');assert.equal(p.research.checkpoint_available,true);
 f.raw.prepare("INSERT INTO market_ai_pipeline_runs(id,collected_on,wikidata_id,status,analysis_provider,evidence_count,claims_count,report_json) VALUES('ai-saved',date('now'),'Q100','candidate_claims_generated','gemini',1,1,?)")
  .run(JSON.stringify({candidate_claims:[{}],reviews:[],source_quality:{claim_gaps:[{gaps:['no_independent_domain']}]}}));
 p=await channelProgress(f.env,f.id);assert.equal(p.research.checkpoint_stage,'corroboration');assert.equal(p.steps[1].state,'blocked');assert.equal(p.steps[2].state,'pending');
 f.raw.prepare("UPDATE market_ai_pipeline_runs SET report_json=json_set(report_json,'$.editorial_focus_review',json(?)) WHERE id='ai-saved'")
  .run(JSON.stringify({status:'misaligned',research_questions:['¿Qué decisiones causaron el cambio del mercado?']}));
 p=await channelProgress(f.env,f.id);assert.equal(p.research.checkpoint_stage,'focus');assert.equal(p.research.editorial_questions.length,1);
 f.raw.prepare("UPDATE market_ai_pipeline_runs SET report_json=json_set(report_json,'$.editorial_focus_review.status','aligned') WHERE id='ai-saved'").run();
 p=await channelProgress(f.env,f.id);assert.equal(p.research.checkpoint_stage,'focus');assert.equal(p.steps[1].state,'blocked');assert.equal(p.steps[2].state,'pending');
 f.raw.prepare("UPDATE market_ai_pipeline_runs SET report_json=json_set(report_json,'$.pending_editorial_analysis',json(?)) WHERE id='ai-saved'").run(JSON.stringify({sources:{}}));
 p=await channelProgress(f.env,f.id);assert.equal(p.research.checkpoint_stage,'analysis');assert.match(p.message,/análisis/);
 f.env.FINAL_AI_INTEGRATION_ENABLED='1';f.job();p=await channelProgress(f.env,f.id);assert.equal(p.next_step,'submit_script');
 const response=await worker.fetch(new Request('https://factor.test/api/jobs/'+f.jobId+'/submit',{method:'POST',headers:{Authorization:'Bearer '+f.env.ADMIN_TOKEN}}),f.env);
 assert.equal(response.status,200);p=await channelProgress(f.env,f.id);assert.equal(p.next_step,'review_dossier');
 // Existing human editorial gate remains authoritative; progress cannot bypass it.
 const denied=await worker.fetch(new Request('https://factor.test/api/jobs/'+f.jobId+'/approve',{method:'POST',headers:{Authorization:'Bearer '+f.env.ADMIN_TOKEN,'Content-Type':'application/json'},body:'{"confirmed":true}'}),f.env);
 assert.equal(denied.status,409);
 f.raw.prepare("UPDATE jobs SET status='failed' WHERE id=?").run(f.jobId);p=await channelProgress(f.env,f.id);assert.equal(p.next_step,'retry_render');assert.equal(p.preview,null);
});

test('preview is associated by exact job event, video hash AND run; unrelated export never appears',async()=>{
 const f=setup();f.research();f.job('ready');f.video('999');
 let p=await channelProgress(f.env,f.id);assert.equal(p.preview,null);assert.equal(p.next_step,'recover_video');
 f.raw.exec("UPDATE youtube_exports SET source_run_id='123'");p=await channelProgress(f.env,f.id);
 assert.equal(p.preview.export_id,f.hash);assert.equal(p.next_step,'review_video');
 f.raw.exec("UPDATE youtube_exports SET state='approved'");assert.equal((await channelProgress(f.env,f.id)).next_step,'upload_video');
 f.raw.exec("UPDATE youtube_exports SET state='uploaded'");assert.equal((await channelProgress(f.env,f.id)).next_step,'publish_video');
 f.publish('unknown');p=await channelProgress(f.env,f.id);assert.equal(p.next_step,'check_publication');assert.equal(p.steps[5].state,'blocked');
 assert.equal((await completeChannelEpisode(f.env,{episode_id:f.id,confirmed:true})).status,409);
});

function finishedWithoutRegistration(){
 const f=setup();f.research();f.job('ready');f.video();f.raw.exec('DELETE FROM youtube_exports');
 f.env.GITHUB_REPO='eler30mr-star/FactordeGigantes';f.env.GITHUB_DISPATCH_TOKEN='local-delivery-test-token-000000';
 return f;
}

test('HTTP recovery reserves once, only dispatches registration of the selected episode, and exposes completion',async()=>{
 const f=finishedWithoutRegistration(),previous=globalThis.fetch,calls=[];
 globalThis.fetch=async(url,options)=>{
  assert.match(url,/\/register-finished-episode\.yml\/dispatches$/);
  const payload=JSON.parse(options.body);calls.push(payload);
  assert.equal(payload.ref,'main');assert.equal(payload.inputs.source_run_id,'123');assert.equal(payload.inputs.job_id,f.jobId);
  return new Response(null,{status:204});
 };
 const send=(token,path,body)=>worker.fetch(new Request('https://factor.test'+path,{method:'POST',headers:{Authorization:'Bearer '+token,'Content-Type':'application/json'},body:JSON.stringify(body)}),f.env);
 try{
  assert.equal((await send(f.env.RENDERER_TOKEN,'/api/channel-control/recover-video',{episode_id:f.id})).status,401);
  assert.equal((await send(f.env.ADMIN_TOKEN,'/api/channel-control/recover-video',null)).status,400);
  const recover=()=>send(f.env.ADMIN_TOKEN,'/api/channel-control/recover-video',{episode_id:f.id});
  const results=await Promise.all([recover(),recover()]);
  assert.equal((await results[0].json()).started,true);assert.equal((await results[1].json()).started,false);assert.equal(calls.length,1);
  assert.equal((await channelProgress(f.env,f.id)).next_step,'wait');
  const requestId=calls[0].inputs.delivery_request_id;
  assert.equal((await send(f.env.ADMIN_TOKEN,'/api/renderer/jobs/'+f.jobId+'/video-registration',{request_id:requestId,status:'ready'})).status,401);
  assert.equal((await reportEpisodeDelivery(f.env,f.jobId,{request_id:requestId,status:'ready'})).status,409);
  f.raw.prepare("INSERT INTO youtube_exports(id,source_run_id,artifact_id,archive_sha256,video_bytes,episode_json,export_json,metadata_json) VALUES(?,'123','456',?,20000,'{}','{}','{}')").run(f.hash,'b'.repeat(64));
  assert.equal((await send(f.env.RENDERER_TOKEN,'/api/renderer/jobs/'+f.jobId+'/video-registration',{request_id:requestId,status:'ready'})).status,200);
  assert.equal((await channelProgress(f.env,f.id)).next_step,'review_video');
  assert.equal((await recoverEpisodeVideo(f.env,f.id)).reused,true);assert.equal(calls.length,1);
  assert.equal(f.raw.prepare("SELECT count(*) n FROM events WHERE action='render_dispatched'").get().n,0);
 }finally{globalThis.fetch=previous;f.raw.close();}
});

test('failed delivery can retry the same MP4 and stale callbacks cannot release a newer request',async()=>{
 const f=finishedWithoutRegistration(),fetcher=async()=>new Response(null,{status:204});
 try{
  const first=await recoverEpisodeVideo(f.env,f.id,fetcher);
  await reportEpisodeDelivery(f.env,f.jobId,{request_id:first.request_id,status:'failed'});
  assert.equal((await channelProgress(f.env,f.id)).next_step,'recover_video');
  for(let attempt=2;attempt<=4;attempt++){
   const next=await recoverEpisodeVideo(f.env,f.id,fetcher);assert.equal(next.started,true);
   assert.equal((await reportEpisodeDelivery(f.env,f.jobId,{request_id:first.request_id,status:'failed'})).status,409);
   assert.equal((await episodeDeliveryStatus(f.env.DB,f.jobId)).state,'sent');
   await reportEpisodeDelivery(f.env,f.jobId,{request_id:next.request_id,status:'failed'});
  }
  assert.equal((await recoverEpisodeVideo(f.env,f.id,fetcher)).started,true);
  assert.equal(f.raw.prepare("SELECT count(*) n FROM events WHERE action='episode_delivery_requested'").get().n,5);
 }finally{f.raw.close();}
});

test('uncertain dispatch blocks blind repetition; unfinished or unrelated episodes never dispatch registration',async()=>{
 const f=finishedWithoutRegistration();let calls=0;
 try{
  assert.equal((await recoverEpisodeVideo(f.env,crypto.randomUUID(),()=>assert.fail())).status,409);
  const result=await recoverEpisodeVideo(f.env,f.id,async()=>{calls++;throw Error('local network substitute');});
  assert.equal(result.reason,'dispatch_unknown');assert.equal((await channelProgress(f.env,f.id)).next_step,'check_video_delivery');
  assert.equal((await recoverEpisodeVideo(f.env,f.id,()=>assert.fail())).started,false);assert.equal(calls,1);
 }finally{f.raw.close();}
});

test('missing registration callback becomes a visible check instead of waiting indefinitely or dispatching twice',async()=>{
 const f=finishedWithoutRegistration();
 try{
  await recoverEpisodeVideo(f.env,f.id,async()=>new Response(null,{status:204}));
  f.raw.exec("UPDATE events SET created_at=datetime('now','-16 minutes') WHERE action='episode_delivery_requested'");
  assert.equal((await channelProgress(f.env,f.id)).next_step,'check_video_delivery');
  assert.equal((await recoverEpisodeVideo(f.env,f.id,()=>assert.fail('No blind repeated dispatch'))).started,false);
 }finally{f.raw.close();}
});

test('closing needs the exact confirmed publication, is idempotent and frees the next episode slot',async()=>{
 const f=setup();f.research();f.job('ready');f.video();f.publish();
 assert.equal((await completeChannelEpisode(f.env,{episode_id:f.id})).status,400);
 f.raw.exec("UPDATE youtube_publications SET video_id='Different12'");
 assert.equal((await completeChannelEpisode(f.env,{episode_id:f.id,confirmed:true})).status,409);
 f.raw.exec("UPDATE youtube_publications SET video_id='Abcdef12345'");
 const result=await completeChannelEpisode(f.env,{episode_id:f.id,confirmed:true});assert.equal(result.ok,true);
 assert.equal(f.raw.prepare('SELECT state FROM channel_episodes WHERE id=?').get(f.id).state,'completed');
 assert.equal((await completeChannelEpisode(f.env,{episode_id:f.id,confirmed:true})).reused,true);
 assert.equal(f.raw.prepare("SELECT count(*) n FROM events WHERE action='channel_episode_completed'").get().n,1);
 const next=await receiveChannelInstruction(f.env,{request_id:crypto.randomUUID(),revision:0,message:'Haz un video sobre Nokia y su transformación empresarial'});
 assert.equal(next.episode.company,'Nokia');assert.notEqual(next.episode.id,f.id);
 assert.equal(f.raw.prepare('SELECT count(*) n FROM jobs').get().n,1);
});

test('progress and close are ADMIN-only and wrong IDs cannot mutate the episode',async()=>{
 const f=setup();
 for(const path of ['/api/channel-control/progress?episode_id='+f.id,'/api/channel-control/complete']){
  const close=path.endsWith('complete');const response=await worker.fetch(new Request('https://factor.test'+path,{method:close?'POST':'GET',headers:{Authorization:'Bearer '+f.env.RENDERER_TOKEN},...(close?{body:JSON.stringify({confirmed:true,episode_id:f.id})}:{})}),f.env);
  assert.equal(response.status,401);
 }
 assert.equal((await channelProgress(f.env,crypto.randomUUID())).status,404);
 await assert.rejects(()=>channelProgress(f.env,'arbitrary'),RangeError);
 assert.equal(f.raw.prepare('SELECT state FROM channel_episodes').get().state,'selected');
});

class Element{
 constructor(tag='div'){this.tag=tag;this.children=[];this.listeners={};this.dataset={};this.attrs={};this.textContent='';}
 append(...nodes){this.children.push(...nodes);}
 replaceChildren(...nodes){this.children=[...nodes];}
 addEventListener(event,fn){this.listeners[event]=fn;}
 setAttribute(k,v){this.attrs[k]=v;}
 pause(){} removeAttribute(){} load(){}
}
const doc={createElement:tag=>new Element(tag)};
test('workbench shows cited script, uses existing guarded action and keeps new controls enabled after refresh',async()=>{
 const root=new Element(),episode={id:crypto.randomUUID()},job={id:crypto.randomUUID(),status:'draft'};let next='submit_script',refreshes=0;const calls=[];
 const request=async(path,method,body)=>{calls.push({path,method,body});
  if(path.includes('/progress?'))return {episode,job,steps:[{id:'script',label:'Guion',state:'current'}],message:'Guion listo',next_step:next};
  if(path.endsWith('/submit')){next='review_dossier';return {ok:true};}
  return {job:{manifest:{segments:[{headline:'El enfoque',voiceover:'Narración con sus fuentes pendientes de revisión.'}]}}};
 };
 const mounted=mountEpisodeWorkbench(root,{request,documentRef:doc,refresh:async()=>{refreshes++;await mounted.load(episode);},openDossier:async()=>{},openExport:async()=>{},schedule:()=>assert.fail('No polling during review')});
 await mounted.load(episode);await root.children[3].ontoggle?.();
 root.children[3].open=true;await root.children[3].ontoggle();
 assert.equal(root.children[3].children[2].textContent,'Narración con sus fuentes pendientes de revisión.');
 const submit=root.children[2].children.find(b=>b.textContent==='Enviar guion a revisión');await submit.listeners.click();
 assert.equal(refreshes,1);assert.equal(root.children[2].children[0].disabled,false);
 assert.equal(calls.filter(x=>x.path.endsWith('/submit')).length,1);
 mounted.dispose();
});

test('workbench refreshes active work, stops when disposed and disables paused retries',async()=>{
 const root=new Element(),episode={id:crypto.randomUUID()},timers=[];let next='wait',paused=false,cancelled=0;
 const mounted=mountEpisodeWorkbench(root,{documentRef:doc,request:async()=>({episode,steps:[],message:'Procesando',next_step:next,action_enabled:!paused,research:{checkpoint_available:true}}),
  refresh:async()=>{},schedule:(fn,ms)=>{timers.push({fn,ms});return timers.length;},cancel:()=>{cancelled++;}});
 await mounted.load(episode);assert.equal(timers[0].ms,12000);
 next='resume_research';paused=true;await mounted.load(episode);assert.equal(cancelled,1);
 assert.equal(root.children[2].children[0].textContent,'Reanudar desde el guion');assert.equal(root.children[2].children[0].disabled,true);
 mounted.dispose();
});

test('workbench recovery requests registration only and changing episode immediately clears the old preview',async()=>{
 const root=new Element(),first={id:crypto.randomUUID()},second={id:crypto.randomUUID()},calls=[];
 let pending,hold=false,next='recover_video';
 const mounted=mountEpisodeWorkbench(root,{documentRef:doc,request:async(path,method,body)=>{
  calls.push({path,method,body});
  if(method==='POST')return {ok:true,started:true};
  if(hold)return new Promise(resolve=>{pending=resolve;});
  return {episode:first,steps:[],message:'Montaje terminado',next_step:next};
 },refresh:async()=>{},schedule:()=>1,cancel:()=>{}});
 await mounted.load(first);
 const recover=root.children[2].children[0];assert.equal(recover.textContent,'Recuperar video terminado');
 await recover.listeners.click();
 assert.deepEqual(calls.find(c=>c.method==='POST'),{path:'/api/channel-control/recover-video',method:'POST',body:{episode_id:first.id}});
 root.children[4].append(new Element('video'));hold=true;
 const loading=mounted.load(second);assert.equal(root.children[4].children.length,0);
 pending({episode:second,steps:[],message:'Nueva elección',next_step:'start_research',action_enabled:false});
 await loading;mounted.dispose();
});
