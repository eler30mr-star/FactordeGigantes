import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFileSync} from 'node:fs';
import {registerYoutubeExport,reviewYoutubeExport,queueYoutubeUpload,resumeYoutubeUpload,startYoutubeUpload,
 transferYoutubeChunk,finishYoutubeUpload,listYoutubeExports,uploadContext} from '../src/youtube-exports.mjs';
import {encryptYoutube} from '../src/youtube-connection.mjs';
import {manifestSha} from '../src/episode-production.mjs';
import worker from '../src/worker.js';
const TOKEN='fake-google-access-token-do-not-expose-123456789';
const CHANNEL='UC'+'a'.repeat(22),CID='1234567890-test.apps.googleusercontent.com';
function canonical(x){return JSON.stringify(x===null||typeof x!=='object'?x:Array.isArray(x)?x.map(v=>JSON.parse(canonical(v))):Object.fromEntries(Object.keys(x).sort().map(k=>[k,JSON.parse(canonical(x[k]))])));}
async function fixture(){
 const raw=new DatabaseSync(':memory:');raw.exec('PRAGMA foreign_keys=ON');
 for(const f of ['0001_initial.sql','0015_youtube_oauth.sql','0016_youtube_exports.sql'])raw.exec(readFileSync(new URL('../migrations/'+f,import.meta.url),'utf8'));
 let tail=Promise.resolve();const db={prepare(sql){const s=raw.prepare(sql),f=p=>({async first(){return s.get(...p)??null;},async all(){return {results:s.all(...p)};},async run(){return {meta:{changes:Number(s.run(...p).changes)}};}});return {...f([]),bind(...p){return f(p);}};},batch(statements){const next=tail.then(async()=>{raw.exec('BEGIN');try{const r=[];for(const s of statements)r.push(await s.run());raw.exec('COMMIT');return r;}catch(e){raw.exec('ROLLBACK');throw e;}});tail=next.catch(()=>{});return next;}};
 const env={DB:db,YOUTUBE_CLIENT_ID:CID,YOUTUBE_CLIENT_SECRET:'fake-client-secret-do-not-expose-123456789',
  YOUTUBE_TOKEN_ENCRYPTION_KEY:Buffer.alloc(32,3).toString('base64url'),YOUTUBE_CHANNEL_ID:CHANNEL,
  GITHUB_REPO:'eler30mr-star/FactordeGigantes',GITHUB_DISPATCH_TOKEN:'fake-github-test-token-do-not-expose-123456789',ADMIN_TOKEN:'fake-admin-token-123456789012345',RENDERER_TOKEN:'fake-render-token-123456789012345'};
 const enc=await encryptYoutube(env,{access_token:TOKEN,refresh_token:TOKEN+'-refresh',client_id:CID,channel_id:CHANNEL},'youtube-connection:primary');
 raw.prepare("INSERT INTO youtube_connections VALUES('primary',?,?,?,?,?,?,?)").run(CHANNEL,'Factor de Gigantes',enc,'scope',Math.floor(Date.now()/1000)+3600,1,1);
 const p=JSON.parse(readFileSync(new URL('../research/theranos-development/EPISODIO_DESARROLLO.json',import.meta.url),'utf8'));
 const episode_canonical_json=canonical(p),report={schema:'fdg_episode_export_v1',sha256:'a'.repeat(64),episode_sha256:await manifestSha(episode_canonical_json),
  canonical_reference_sha256:p.canonical_voice_sha256,canonical_reference_unchanged:true,contains_narration:true,voice_kind:'canonical_qwen_pending_audition',
  technical_gate_passed:true,actual_seconds:600,generated_voice_takes:56,human_factual_approval:false,commercial_rights_verified:false,publication_authorized:false,
  chapters:p.scenes.map((s,i)=>({id:s.id,title:s.headline,start_seconds:i*75,end_seconds:(i+1)*75}))};
 const body={episode_canonical_json,report,source_run_id:'123',artifact_id:'456',archive_sha256:'b'.repeat(64),video_bytes:20000};
 const githubFetch=async url=>Response.json(url.includes('/artifacts/')?{name:'fdg-episode-narrated-review',expired:false,workflow_run:{id:123},digest:'sha256:'+body.archive_sha256}:
  {path:'.github/workflows/development-episode.yml',head_branch:'main',event:'workflow_dispatch',repository:{full_name:env.GITHUB_REPO},status:'completed',conclusion:'success'});
 return {raw,env,body,githubFetch,id:report.sha256};
}
async function staged(){const f=await fixture();await registerYoutubeExport(f.env,f.body,{githubFetch:f.githubFetch});return f;}
const approve=metadata=>({confirmed:true,reviewer:'Editora de pruebas',watched_video:true,voice_approved:true,facts_checked:true,rights_verified:true,visuals_captions_approved:true,metadata_approved:true,
 metadata:{...metadata,madeForKids:false,privacyStatus:'private'}});
async function queued(){const f=await staged();const metadata=JSON.parse(f.raw.prepare('SELECT metadata_json FROM youtube_exports').get().metadata_json);
 await reviewYoutubeExport(f.env,f.id,approve(metadata));const q=await queueYoutubeUpload(f.env,f.id,{confirmed:true},{githubFetch:async()=>new Response(null,{status:204})});return {...f,requestId:q.request_id};}
const SESSION='https://www.googleapis.com/upload/youtube/v3/videos?upload_id=fake-session-private-capability';

test('registro validado e idempotente queda en revisión, nunca acredita permisos humanos',async()=>{
 const f=await staged();assert.equal(f.raw.prepare('SELECT state FROM youtube_exports').get().state,'review');
 assert.equal(f.raw.prepare('SELECT COUNT(*) n FROM youtube_export_events').get().n,1);
 const r=await registerYoutubeExport(f.env,f.body,{githubFetch:()=>{throw Error('No repetir red');}});assert.equal(r.reused,true);
 const list=await listYoutubeExports(f.env);assert.equal(list.exports[0].origin,'codex_development_research');assert.deepEqual(list.exports[0].review,{});
 assert.equal(list.exports[0].metadata.madeForKids,null);assert.equal(list.automatic_publication_allowed,false);
});
test('señal técnica, aprobación inventada o hash alterado se rechazan antes de crear registro',async()=>{
 for(const mutate of [b=>b.report.contains_narration=false,b=>b.report.human_factual_approval=true,b=>b.episode_canonical_json+=' ',b=>b.report.chapters[0].start_seconds=10]){
  const f=await fixture();mutate(f.body);await assert.rejects(registerYoutubeExport(f.env,f.body,{githubFetch:()=>{throw Error('No red');}}));
  assert.equal(f.raw.prepare('SELECT COUNT(*) n FROM youtube_exports').get().n,0);
 }
});
test('derechos, audición y audiencia requieren aprobación explícita y sólo privado',async()=>{
 const f=await staged(),m=JSON.parse(f.raw.prepare('SELECT metadata_json FROM youtube_exports').get().metadata_json);
 assert.equal((await queueYoutubeUpload(f.env,f.id,{confirmed:true})).status,409);
 const b=approve(m);b.rights_verified=false;assert.equal((await reviewYoutubeExport(f.env,f.id,b)).status,400);
 await assert.rejects(reviewYoutubeExport(f.env,f.id,{...approve(m),metadata:{...m,madeForKids:false,privacyStatus:'public'}}));
 await assert.rejects(reviewYoutubeExport(f.env,f.id,{...approve(m),metadata:{...m,madeForKids:null}}));
 assert.equal((await reviewYoutubeExport(f.env,f.id,approve(m))).ok,true);
});
test('cola se reserva una vez; sesión única cifrada y CI nunca recibe credenciales Google',async()=>{
 const f=await queued();assert.ok(f.requestId);assert.equal((await queueYoutubeUpload(f.env,f.id,{confirmed:true})).status,409);
 let inserts=0;const googleFetch=async(url,opts)=>{inserts++;assert.match(url,/notifySubscribers=false/);assert.equal(JSON.parse(opts.body).status.privacyStatus,'private');
  assert.equal(opts.headers.Authorization,'Bearer '+TOKEN);return new Response(null,{status:200,headers:{Location:SESSION}});};
 const a=await startYoutubeUpload(f.env,f.requestId,{sha256:f.id,bytes:20000},{googleFetch});assert.equal(a.session_ready,true);
 const b=await startYoutubeUpload(f.env,f.requestId,{sha256:f.id,bytes:20000},{googleFetch});assert.equal(b.session_ready,true);assert.equal(inserts,1);
 const row=f.raw.prepare('SELECT session_encrypted FROM youtube_exports').get();assert.ok(!row.session_encrypted.includes(SESSION));
 assert.ok(!JSON.stringify([a,b,await uploadContext(f.env,f.requestId)]).includes(TOKEN));assert.ok(!JSON.stringify(a).includes(SESSION));
});
test('rango se valida antes de Google; transferencia reanudable y confirmación privada idempotente',async()=>{
 const f=await queued();await startYoutubeUpload(f.env,f.requestId,{sha256:f.id,bytes:20000},{googleFetch:async()=>new Response(null,{headers:{Location:SESSION}})});
 const wrong=new Request('https://test',{method:'PUT',headers:{'Content-Length':'5','Content-Range':'bytes 0-99/20000'},body:new Uint8Array(5)});
 assert.equal((await transferYoutubeChunk(f.env,f.requestId,wrong,{googleFetch:()=>{throw Error('No red');}})).status,400);
 const probe=new Request('https://test',{method:'PUT',headers:{'Content-Length':'0','Content-Range':'bytes */20000'}});
 assert.equal((await transferYoutubeChunk(f.env,f.requestId,probe,{googleFetch:async()=>new Response(null,{status:308,headers:{Range:'bytes=0-99'}})})).next_offset,100);
 const chunk=new Request('https://test',{method:'PUT',headers:{'Content-Length':'20000','Content-Range':'bytes 0-19999/20000'},body:new Uint8Array(20000)});
 const sent=await transferYoutubeChunk(f.env,f.requestId,chunk,{googleFetch:async()=>Response.json({id:'abcde123456'},{status:201})});assert.equal(sent.complete,true);
 const verify=async()=>Response.json({items:[{id:'abcde123456',snippet:{channelId:CHANNEL},status:{privacyStatus:'private'}}]});
 assert.equal((await finishYoutubeUpload(f.env,f.requestId,{video_id:sent.video_id},{googleFetch:verify})).ok,true);
 assert.equal((await finishYoutubeUpload(f.env,f.requestId,{video_id:sent.video_id},{googleFetch:()=>{throw Error('No repetir');}})).reused,true);
 assert.equal(f.raw.prepare('SELECT state FROM youtube_exports').get().state,'uploaded');
});
test('fallo incierto no crea otra sesión; reanudar conserva la misma solicitud y canal',async()=>{
 const f=await queued();const before=f.requestId;
 let passed;assert.equal((await resumeYoutubeUpload(f.env,f.id,{confirmed:true},{githubFetch:async(url,opts)=>{passed=JSON.parse(opts.body).inputs.request_id;return new Response(null,{status:204});}})).ok,true);assert.equal(passed,before);
 const r=await startYoutubeUpload(f.env,f.requestId,{sha256:f.id,bytes:20000},{googleFetch:async()=>{throw Error(TOKEN);}});assert.equal(r.status,502);
 assert.equal((await startYoutubeUpload(f.env,f.requestId,{sha256:f.id,bytes:20000},{googleFetch:()=>{throw Error('No red');}})).status,409);
 assert.equal((await resumeYoutubeUpload(f.env,f.id,{confirmed:true})).status,409);assert.ok(!JSON.stringify(r).includes(TOKEN));
});
test('ADMIN y renderer tienen funciones separadas; ningún registro o permiso se fabrica por GET',async()=>{
 const f=await staged();const req=(path,token,method='GET')=>new Request('https://test'+path,{method,headers:{Authorization:'Bearer '+token}});
 assert.equal((await worker.fetch(req('/api/youtube/exports',f.env.RENDERER_TOKEN),f.env)).status,401);
 assert.equal((await worker.fetch(req('/api/renderer/youtube/exports',f.env.ADMIN_TOKEN,'POST'),f.env)).status,401);
 assert.equal((await worker.fetch(req('/api/youtube/exports',f.env.ADMIN_TOKEN),f.env)).status,200);
 assert.equal(f.raw.prepare('SELECT state FROM youtube_exports').get().state,'review');
});
