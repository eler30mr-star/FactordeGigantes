import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFileSync} from 'node:fs';
import worker from '../src/worker.js';
import {youtubeConfiguration,startYoutubeConnection,finishYoutubeConnection,youtubeConnectionStatus,
 disconnectYoutube,encryptYoutube,decryptYoutube,youtubeAccessToken,YOUTUBE_CALLBACK} from '../src/youtube-connection.mjs';
const KEY=Buffer.alloc(32,7).toString('base64url');
const TOKEN='test-access-token-DO-NOT-EXPOSE-123456789';
const REFRESH='test-refresh-token-DO-NOT-EXPOSE-123456789';
const SCOPES='https://www.googleapis.com/auth/youtube.readonly https://www.googleapis.com/auth/youtube.upload';
const NOW=1800000000;
function setup(){
 const raw=new DatabaseSync(':memory:');raw.exec(readFileSync(new URL('../migrations/0015_youtube_oauth.sql',import.meta.url),'utf8'));
 const db={prepare(sql){const s=raw.prepare(sql);const stmt=params=>({async first(){return s.get(...params)??null;},
  async run(){return {meta:{changes:Number(s.run(...params).changes)}};}});return {...stmt([]),bind(...p){return stmt(p);}};},
  async batch(statements){raw.exec('BEGIN');try{const r=[];for(const s of statements)r.push(await s.run());raw.exec('COMMIT');return r;}catch(e){raw.exec('ROLLBACK');throw e;}}};
 return {raw,env:{DB:db,YOUTUBE_CLIENT_ID:'1234567890-testclient.apps.googleusercontent.com',
  YOUTUBE_CLIENT_SECRET:'client-secret-private-test-value-123456',YOUTUBE_TOKEN_ENCRYPTION_KEY:KEY,YOUTUBE_CHANNEL_ID:'UC'+'a'.repeat(22)}};
}
function callback(start,{cookie=start.cookie.split(';')[0],state=new URL(start.authorization_url).searchParams.get('state')}={}){
 return new Request(YOUTUBE_CALLBACK+'?code=test-code&state='+encodeURIComponent(state),{headers:{Cookie:cookie}});
}
function google(env,seen=[],{wrong=false,scope=SCOPES}={}){
 return async(url,opts)=>{
  seen.push({url,opts});assert.equal(opts.redirect,'manual');
  if(url.endsWith('/token'))return Response.json({access_token:TOKEN,refresh_token:REFRESH,expires_in:3600,scope,token_type:'Bearer'});
  if(url.endsWith('/revoke'))return new Response(null,{status:200});
  assert.match(url,/^https:\/\/www.googleapis.com\/youtube\/v3\/channels\?/);
  assert.equal(opts.headers.Authorization,'Bearer '+TOKEN);
  return Response.json({items:[{id:wrong?'UC'+'b'.repeat(22):env.YOUTUBE_CHANNEL_ID,snippet:{title:'Factor de Gigantes'}}]});
 };
}
test('consentimiento explícito, origen fijo, PKCE y cookie protegida; state y verifier no se guardan en claro',async()=>{
 const {env,raw}=setup();assert.equal(youtubeConfiguration({}).configured,false);
 assert.equal((await startYoutubeConnection(env,{})).status,400);
 assert.equal((await startYoutubeConnection({...env,YOUTUBE_CLIENT_ID:''},{confirmed:true})).status,503);
 const start=await startYoutubeConnection(env,{confirmed:true},{now:NOW});const u=new URL(start.authorization_url);
 assert.equal(u.origin,'https://accounts.google.com');assert.equal(u.searchParams.get('redirect_uri'),YOUTUBE_CALLBACK);
 assert.equal(u.searchParams.get('scope'),SCOPES);assert.equal(u.searchParams.get('code_challenge_method'),'S256');
 assert.match(start.cookie,/HttpOnly; Secure; SameSite=Lax/);assert.match(start.cookie,/Max-Age=600/);
 const row=raw.prepare('SELECT * FROM youtube_oauth_flows').get();
 assert.ok(!JSON.stringify(row).includes(u.searchParams.get('state')));
 const flow=await decryptYoutube(env,row.payload_encrypted,'youtube-flow:'+row.state_sha256);
 assert.ok(!row.payload_encrypted.includes(flow.verifier));assert.equal(row.expires_at,NOW+600);
 const expected=Buffer.from(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(flow.verifier))).toString('base64url');
 assert.equal(u.searchParams.get('code_challenge'),expected);
});
test('intercambio y canal correcto guardan tokens cifrados; replay no contacta Google ni devuelve credenciales',async()=>{
 const {env,raw}=setup();const start=await startYoutubeConnection(env,{confirmed:true},{now:NOW}),seen=[];
 const r=await finishYoutubeConnection(callback(start),env,{now:NOW+1,googleFetch:google(env,seen)});
 assert.equal(r.status,303);assert.equal(r.headers.get('Location'),'/?youtube=connected');assert.equal(seen.length,2);
 const body=new URLSearchParams(seen[0].opts.body);assert.equal(body.get('grant_type'),'authorization_code');assert.ok(body.get('code_verifier'));
 const row=raw.prepare('SELECT * FROM youtube_connections').get();assert.equal(row.channel_id,env.YOUTUBE_CHANNEL_ID);
 assert.ok(!JSON.stringify(row).includes(TOKEN));assert.ok(!JSON.stringify(row).includes(REFRESH));
 const status=await youtubeConnectionStatus(env);assert.equal(status.connected,true);assert.equal(status.automatic_publication_allowed,false);
 for(const secret of [TOKEN,REFRESH,KEY,env.YOUTUBE_CLIENT_SECRET])assert.ok(!JSON.stringify(status).includes(secret));
 const replay=await finishYoutubeConnection(callback(start),env,{now:NOW+2,googleFetch:()=>{throw Error('No replay');}});
 assert.equal(replay.headers.get('Location'),'/?youtube=not_connected');
});
test('cookie equivocada, state inválido y consentimiento caducado no consumen código ni llaman Google',async()=>{
 const {env}=setup();const start=await startYoutubeConnection(env,{confirmed:true},{now:NOW});let calls=0;
 for(const req of [callback(start,{cookie:''}),callback(start,{cookie:'__Host-fdg-youtube-flow='+'b'.repeat(43)}),callback(start,{state:'invalid'})]){
  const r=await finishYoutubeConnection(req,env,{now:NOW+1,googleFetch:async()=>{calls++;}});assert.equal(r.headers.get('Location'),'/?youtube=not_connected');
 }
 const expired=await finishYoutubeConnection(callback(start),env,{now:NOW+601,googleFetch:async()=>{calls++;}});
 assert.equal(expired.headers.get('Location'),'/?youtube=not_connected');assert.equal(calls,0);
});
test('canal ajeno, permisos incompletos y error remoto nunca crean conexión ni exponen cuerpo de Google',async()=>{
 for(const mode of ['channel','scope','network']){
  const {env,raw}=setup(),start=await startYoutubeConnection(env,{confirmed:true},{now:NOW});
  const provider=mode==='network'?async()=>new Response('SECRET:'+REFRESH,{status:400}):google(env,[],{wrong:mode==='channel',scope:mode==='scope'?'one-scope':SCOPES});
  const r=await finishYoutubeConnection(callback(start),env,{now:NOW+1,googleFetch:provider});
  assert.equal(r.headers.get('Location'),'/?youtube=not_connected');assert.equal(raw.prepare('SELECT COUNT(*) n FROM youtube_connections').get().n,0);
  assert.ok(![...r.headers].flat().join(' ').includes(REFRESH));
 }
});
test('desconexión durante el intercambio invalida el flow y evita resucitar credenciales',async()=>{
 const {env,raw}=setup(),start=await startYoutubeConnection(env,{confirmed:true},{now:NOW});const base=google(env);
 const r=await finishYoutubeConnection(callback(start),env,{now:NOW+1,googleFetch:async(url,opts)=>{
  if(url.includes('/channels?'))raw.prepare('DELETE FROM youtube_oauth_flows').run();return base(url,opts);
 }});
 assert.equal(r.headers.get('Location'),'/?youtube=not_connected');assert.equal(raw.prepare('SELECT COUNT(*) n FROM youtube_connections').get().n,0);
});
test('cifrado usa contexto y clave: manipulación o clave distinta falla; revocar no conserva tokens locales',async()=>{
 const {env,raw}=setup();const cipher=await encryptYoutube(env,{test:TOKEN},'expected');
 await assert.rejects(decryptYoutube(env,cipher,'wrong'));
 await assert.rejects(decryptYoutube({...env,YOUTUBE_TOKEN_ENCRYPTION_KEY:Buffer.alloc(32,9).toString('base64url')},cipher,'expected'));
 const start=await startYoutubeConnection(env,{confirmed:true},{now:NOW});await finishYoutubeConnection(callback(start),env,{now:NOW+1,googleFetch:google(env)});
 assert.equal((await disconnectYoutube(env,{})).status,400);
 const result=await disconnectYoutube(env,{confirmed:true},{googleFetch:async()=>{throw Error('Revocación no disponible');}});
 assert.equal(result.connected,false);assert.equal(result.revocation_confirmed,false);
 assert.equal(raw.prepare('SELECT COUNT(*) n FROM youtube_connections').get().n,0);assert.equal(raw.prepare('SELECT COUNT(*) n FROM youtube_oauth_flows').get().n,0);
});
test('Worker limita la conexión a ADMIN, entrega cookie sólo por cabecera y callback inválido no abre acceso',async()=>{
 const {env}=setup();Object.assign(env,{ADMIN_TOKEN:'admin-private-test-token-123456789',RENDERER_TOKEN:'render-private-test-token-123456789'});
 const req=(path,token=env.ADMIN_TOKEN,method='GET',body)=>new Request('https://test'+path,{method,
  headers:{Authorization:'Bearer '+token,'Content-Type':'application/json'},...(body?{body:JSON.stringify(body)}:{})});
 assert.equal((await worker.fetch(req('/api/youtube/connection',env.RENDERER_TOKEN),env)).status,401);
 assert.equal((await worker.fetch(req('/api/youtube/connect',env.ADMIN_TOKEN,'GET'),env)).status,405);
 const r=await worker.fetch(req('/api/youtube/connect',env.ADMIN_TOKEN,'POST',{confirmed:true}),env);
 assert.equal(r.status,200);assert.match(r.headers.get('Set-Cookie'),/HttpOnly/);const data=await r.json();
 assert.equal(data.cookie,undefined);assert.equal(data.automatic_publication_allowed,false);
 const status=await worker.fetch(req('/api/youtube/connection'),env);assert.equal(status.status,200);
 assert.equal((await status.json()).connected,false);
 const callbackResponse=await worker.fetch(new Request(YOUTUBE_CALLBACK+'?state=forged&code=forged'),env);
 assert.equal(callbackResponse.status,303);assert.equal(callbackResponse.headers.get('Location'),'/?youtube=not_connected');
});
test('cancelación de Google consume estado sin intercambiar credenciales',async()=>{
 const {env,raw}=setup(),start=await startYoutubeConnection(env,{confirmed:true},{now:NOW});
 const request=callback(start),url=new URL(request.url);url.searchParams.set('error','access_denied');
 const r=await finishYoutubeConnection(new Request(url,{headers:request.headers}),env,{now:NOW+1,googleFetch:()=>{throw Error('No intercambio');}});
 assert.equal(r.headers.get('Location'),'/?youtube=cancelled');assert.equal(raw.prepare('SELECT outcome FROM youtube_oauth_flows').get().outcome,'cancelled');
});
test('renovación sólo interna conserva refresh token, y no resucita una conexión desconectada durante la llamada',async()=>{
 const {env,raw}=setup(),start=await startYoutubeConnection(env,{confirmed:true},{now:NOW});
 await finishYoutubeConnection(callback(start),env,{now:NOW+1,googleFetch:google(env)});
 const cached=await youtubeAccessToken(env,{now:NOW+10,googleFetch:()=>{throw Error('No renovar antes de tiempo');}});
 assert.equal(cached.access_token,TOKEN);
 const changed={...env,YOUTUBE_CLIENT_ID:'other-client12345.apps.googleusercontent.com'};
 assert.equal((await youtubeConnectionStatus(changed)).connected,false);
 assert.equal((await youtubeAccessToken(changed,{now:NOW+10,googleFetch:()=>{throw Error('No reutilizar cliente ajeno');}})).ok,false);
 const refreshed=await youtubeAccessToken(env,{now:NOW+4000,googleFetch:async(url,options)=>{
  assert.equal(url,'https://oauth2.googleapis.com/token');assert.equal(new URLSearchParams(options.body).get('grant_type'),'refresh_token');
  return Response.json({access_token:TOKEN+'-new',expires_in:3600,token_type:'Bearer'});
 }});
 assert.equal(refreshed.access_token,TOKEN+'-new');
 const saved=await decryptYoutube(env,raw.prepare('SELECT credentials_encrypted FROM youtube_connections').get().credentials_encrypted,'youtube-connection:primary');
 assert.equal(saved.refresh_token,REFRESH);
 const race=await youtubeAccessToken(env,{now:NOW+8000,googleFetch:async()=>{
  raw.prepare('DELETE FROM youtube_connections').run();return Response.json({access_token:TOKEN+'-lost',expires_in:3600,token_type:'Bearer'});
 }});
 assert.equal(race.ok,false);assert.equal(race.access_token,undefined);assert.equal(raw.prepare('SELECT COUNT(*) n FROM youtube_connections').get().n,0);
});
