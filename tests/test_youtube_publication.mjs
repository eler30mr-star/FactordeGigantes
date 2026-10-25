import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFileSync} from 'node:fs';
import {encryptYoutube,startYoutubeConnection,youtubeConnectionStatus,finishYoutubeConnection,PUBLICATION_SCOPE} from '../src/youtube-connection.mjs';
import {authorizePublication,reconcilePublication,publicationIntent} from '../src/youtube-publication.mjs';
import worker from '../src/worker.js';
const CID='1234567890-test.apps.googleusercontent.com',CHANNEL='UC'+'a'.repeat(22),ID='a'.repeat(64),VIDEO='Abcdef12345';
const NOW=new Date('2026-10-25T15:00:00Z');
async function setup(){
 const raw=new DatabaseSync(':memory:');raw.exec('PRAGMA foreign_keys=ON');
 for(const name of ['0015_youtube_oauth.sql','0016_youtube_exports.sql','0020_youtube_publications.sql'])raw.exec(readFileSync(new URL('../migrations/'+name,import.meta.url),'utf8'));
 let tail=Promise.resolve();const db={prepare(sql){let args=[];return {bind(...a){args=a;return this;},async first(){return raw.prepare(sql).get(...args)||null;},async all(){return {results:raw.prepare(sql).all(...args)};},async run(){return {meta:{changes:Number(raw.prepare(sql).run(...args).changes)}};}};},batch(stmts){const next=tail.then(async()=>{raw.exec('BEGIN');try{const r=[];for(const s of stmts)r.push(await s.run());raw.exec('COMMIT');return r;}catch(e){raw.exec('ROLLBACK');throw e;}});tail=next.catch(()=>{});return next;}};
 const env={DB:db,YOUTUBE_CLIENT_ID:CID,YOUTUBE_CLIENT_SECRET:'fake-client-secret-000000000',YOUTUBE_CHANNEL_ID:CHANNEL,
  YOUTUBE_TOKEN_ENCRYPTION_KEY:Buffer.alloc(32,3).toString('base64url'),ADMIN_TOKEN:'fake-private-owner-token-000000',RENDERER_TOKEN:'fake-private-render-token-00000'};
 const cipher=await encryptYoutube(env,{access_token:'fake-access-token-00000000',refresh_token:'fake-refresh-token-00000000',client_id:CID,channel_id:CHANNEL},'youtube-connection:primary');
 raw.prepare("INSERT INTO youtube_connections VALUES('primary',?,?,?,?,?,?,?)").run(CHANNEL,'Factor de Gigantes',cipher,PUBLICATION_SCOPE,Math.floor(Date.now()/1000)+3000,1,1);
 const review={video_sha256:ID,watched_video:true,voice_approved:true,facts_checked:true,rights_verified:true,visuals_captions_approved:true,metadata_approved:true};
 raw.prepare("INSERT INTO youtube_exports(id,source_run_id,artifact_id,archive_sha256,video_bytes,episode_json,export_json,metadata_json,state,review_json,target_channel_id,video_id) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)")
 .run(ID,'123','456','b'.repeat(64),20000,'{}','{}',JSON.stringify({madeForKids:false,containsSyntheticMedia:true}),'uploaded',JSON.stringify(review),CHANNEL,VIDEO);
 let remote={id:VIDEO,etag:'"etag-test"',snippet:{channelId:CHANNEL},status:{privacyStatus:'private',license:'youtube',embeddable:false,publicStatsViewable:true}};
 const calls=[];let uncertain=false;
 const fetcher=async(url,options={})=>{calls.push({url,options});if(options.method==='PUT'){
  const body=JSON.parse(options.body);remote={...remote,status:body.status};if(uncertain)throw Error('private network details');return Response.json(remote);
 }return Response.json({items:[remote]});};
 return {env,raw,calls,fetcher,setRemote:r=>{remote=r;},setUncertain:()=>{uncertain=true;}};
}
const body=(extra={})=>({request_id:crypto.randomUUID(),confirmed:true,publication_authorized:true,video_sha256:ID,reviewer:'Editora autorizada',mode:'public',...extra});

test('publication requires separate explicit authorization, hash, review and upload',async()=>{
 const f=await setup();await assert.rejects(()=>authorizePublication(f.env,ID,{...body(),publication_authorized:false},{googleFetch:()=>assert.fail(),now:NOW}),RangeError);
 assert.equal((await authorizePublication(f.env,ID,body({video_sha256:'b'.repeat(64)}),{googleFetch:()=>assert.fail(),now:NOW})).status,409);
 f.raw.exec("UPDATE youtube_exports SET state='review'");assert.equal((await authorizePublication(f.env,ID,body(),{googleFetch:()=>assert.fail(),now:NOW})).status,409);
});
test('publishes only the reviewed video and preserves mutable status fields without changing snippet',async()=>{
 const f=await setup(),intent=body();const result=await authorizePublication(f.env,ID,intent,{googleFetch:f.fetcher,now:NOW});
 assert.equal(result.publication.state,'confirmed');const updates=f.calls.filter(x=>x.options.method==='PUT');assert.equal(updates.length,1);
 const payload=JSON.parse(updates[0].options.body);assert.equal(payload.id,VIDEO);assert.equal(payload.status.privacyStatus,'public');
 assert.equal(payload.status.embeddable,false);assert.equal(payload.snippet,undefined);assert.equal(payload.status.selfDeclaredMadeForKids,false);
 assert.equal((await authorizePublication(f.env,ID,intent,{googleFetch:()=>assert.fail(),now:NOW})).reused,true);
 assert.equal(f.raw.prepare("SELECT count(*) n FROM youtube_export_events WHERE action='publication_authorized'").get().n,1);
});
test('schedule uses future UTC with private visibility and confirms the exact time',async()=>{
 const f=await setup(),date='2026-10-26T15:00:00.000Z';
 const result=await authorizePublication(f.env,ID,body({mode:'scheduled',publish_at:date}),{googleFetch:f.fetcher,now:NOW});
 assert.equal(result.publication.state,'confirmed');const p=JSON.parse(f.calls.find(x=>x.options.method==='PUT').options.body);
 assert.equal(p.status.privacyStatus,'private');assert.equal(p.status.publishAt,date);
 for(const at of ['2026-10-25T15:01:00Z','2026-02-30T12:00:00Z','2026-10-26T15:00:00+01:00'])
  assert.throws(()=>publicationIntent(body({mode:'scheduled',publish_at:at}),NOW),RangeError);
});
test('uncertain update is never resent; read-only reconciliation recovers actual result',async()=>{
 const f=await setup();f.setUncertain();const intent=body();
 const result=await authorizePublication(f.env,ID,intent,{googleFetch:f.fetcher,now:NOW});assert.equal(result.publication.state,'unknown');
 assert.equal((await authorizePublication(f.env,ID,body(),{googleFetch:()=>assert.fail(),now:NOW})).status,409);
 const checked=await reconcilePublication(f.env,ID,{googleFetch:f.fetcher});assert.equal(checked.publication.state,'confirmed');
 assert.equal(f.calls.filter(x=>x.options.method==='PUT').length,1);
});
test('scope extension is optional and publication refuses current upload-only access',async()=>{
 const f=await setup();f.raw.exec("UPDATE youtube_connections SET scopes='https://www.googleapis.com/auth/youtube.upload'");
 assert.equal((await youtubeConnectionStatus(f.env)).publication_scope_granted,false);
 assert.equal((await authorizePublication(f.env,ID,body(),{googleFetch:()=>assert.fail(),now:NOW})).status,409);
 const normal=await startYoutubeConnection(f.env,{confirmed:true});assert.ok(!new URL(normal.authorization_url).searchParams.get('scope').includes(PUBLICATION_SCOPE));
 const extended=await startYoutubeConnection(f.env,{confirmed:true,publication_access:true});assert.ok(new URL(extended.authorization_url).searchParams.get('scope').includes(PUBLICATION_SCOPE));
});
test('wrong channel and changed remote privacy block the update; renderer cannot publish',async()=>{
 const f=await setup();f.setRemote({id:VIDEO,snippet:{channelId:'UC'+'z'.repeat(22)},status:{privacyStatus:'private'}});
 assert.equal((await authorizePublication(f.env,ID,body(),{googleFetch:f.fetcher,now:NOW})).status,409);
 assert.equal(f.calls.filter(x=>x.options.method==='PUT').length,0);
 const req=new Request('https://factor.test/api/youtube/exports/'+ID+'/publication',{method:'POST',headers:{Authorization:'Bearer '+f.env.RENDERER_TOKEN},body:JSON.stringify(body())});
 assert.equal((await worker.fetch(req,f.env)).status,401);
});

test('OAuth extension verifies actual granted scope and preserves connection on incomplete consent',async()=>{
 for(const granted of [false,true]){
  const f=await setup();f.raw.exec("UPDATE youtube_connections SET scopes='old-upload-only'");
  const now=Math.floor(NOW.getTime()/1000),flow=await startYoutubeConnection(f.env,{confirmed:true,publication_access:true},{now});
  const state=new URL(flow.authorization_url).searchParams.get('state');
  const scopes=['https://www.googleapis.com/auth/youtube.readonly','https://www.googleapis.com/auth/youtube.upload',...(granted?[PUBLICATION_SCOPE]:[])].join(' ');
  const googleFetch=async url=>url.includes('oauth2.googleapis.com')?Response.json({access_token:'new-fake-access-token-000000',refresh_token:'new-fake-refresh-token-000000',expires_in:3600,token_type:'Bearer',scope:scopes}):
   Response.json({items:[{id:CHANNEL,snippet:{title:'Factor de Gigantes'}}]});
  const result=await finishYoutubeConnection(new Request('https://factor-de-gigantes.martin30-eler.workers.dev/oauth/youtube/callback?state='+state+'&code=code-test',{
   headers:{Cookie:flow.cookie.split(';')[0]}}),f.env,{now:now+1,googleFetch});
  assert.equal(result.status,303);
  const saved=f.raw.prepare('SELECT scopes FROM youtube_connections').get().scopes;
  assert.equal(saved,granted?scopes:'old-upload-only');
 }
});
