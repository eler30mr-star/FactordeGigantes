// OAuth oficial, independiente de publicar. Nunca devuelve tokens al navegador.
export const YOUTUBE_CALLBACK='https://factor-de-gigantes.martin30-eler.workers.dev/oauth/youtube/callback';
const SCOPES=['https://www.googleapis.com/auth/youtube.readonly','https://www.googleapis.com/auth/youtube.upload'];
export const PUBLICATION_SCOPE='https://www.googleapis.com/auth/youtube.force-ssl';
const COOKIE='__Host-fdg-youtube-flow';
const encoder=new TextEncoder();
const seconds=()=>Math.floor(Date.now()/1000);
const b64=bytes=>btoa(String.fromCharCode(...bytes)).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/g,'');
const unb64=text=>Uint8Array.from(atob(text.replace(/-/g,'+').replace(/_/g,'/')),c=>c.charCodeAt(0));
const random=()=>b64(crypto.getRandomValues(new Uint8Array(32)));
const sha=async text=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',encoder.encode(text)))].map(x=>x.toString(16).padStart(2,'0')).join('');
const cookie=(value,age)=>`${COOKIE}=${value}; Path=/; Max-Age=${age}; HttpOnly; Secure; SameSite=Lax`;
const validToken=t=>typeof t==='string'&&t.length>=20&&t.length<=8192&&!/[\x00-\x20\x7f]/.test(t);
const failure=(status,error)=>({ok:false,status,error});

export function youtubeConfiguration(env){
 const checks={
  YOUTUBE_CLIENT_ID:typeof env.YOUTUBE_CLIENT_ID==='string'&&/^[\w-]{10,180}\.apps\.googleusercontent\.com$/.test(env.YOUTUBE_CLIENT_ID),
  YOUTUBE_CLIENT_SECRET:validToken(env.YOUTUBE_CLIENT_SECRET),
  YOUTUBE_TOKEN_ENCRYPTION_KEY:typeof env.YOUTUBE_TOKEN_ENCRYPTION_KEY==='string'&&/^[\w-]{43}$/.test(env.YOUTUBE_TOKEN_ENCRYPTION_KEY),
  YOUTUBE_CHANNEL_ID:typeof env.YOUTUBE_CHANNEL_ID==='string'&&/^UC[\w-]{22}$/.test(env.YOUTUBE_CHANNEL_ID)
 };
 return {configured:Object.values(checks).every(Boolean),missing:Object.keys(checks).filter(k=>!checks[k])};
}

export async function encryptYoutube(env,value,context){
 const raw=unb64(env.YOUTUBE_TOKEN_ENCRYPTION_KEY||'');
 if(raw.length!==32)throw new Error('Clave de cifrado inválida');
 const key=await crypto.subtle.importKey('raw',raw,'AES-GCM',false,['encrypt']);
 const iv=crypto.getRandomValues(new Uint8Array(12));
 const data=await crypto.subtle.encrypt({name:'AES-GCM',iv,additionalData:encoder.encode(context)},key,encoder.encode(JSON.stringify(value)));
 return JSON.stringify({v:1,iv:b64(iv),data:b64(new Uint8Array(data))});
}
export async function decryptYoutube(env,text,context){
 if(typeof text!=='string'||text.length>50000)throw new Error('Sobre cifrado inválido');
 const box=JSON.parse(text);if(box.v!==1||typeof box.iv!=='string'||typeof box.data!=='string')throw new Error('Sobre cifrado inválido');
 const raw=unb64(env.YOUTUBE_TOKEN_ENCRYPTION_KEY||'');if(raw.length!==32)throw new Error('Clave de cifrado inválida');
 const key=await crypto.subtle.importKey('raw',raw,'AES-GCM',false,['decrypt']);
 const data=await crypto.subtle.decrypt({name:'AES-GCM',iv:unb64(box.iv),additionalData:encoder.encode(context)},key,unb64(box.data));
 return JSON.parse(new TextDecoder().decode(data));
}
async function googleJson(url,options,googleFetch){
 const response=await googleFetch(url,{...options,redirect:'manual',signal:AbortSignal.timeout(12000)});
 if(!response.ok)throw new Error('Google no confirmó la operación');
 const reader=response.body?.getReader();if(!reader)throw new Error('Respuesta vacía');
 const chunks=[];let size=0;
 while(true){const {done,value}=await reader.read();if(done)break;size+=value.byteLength;
  if(size>150000){await reader.cancel();throw new Error('Respuesta fuera de límite');}chunks.push(value);}
 const data=new Uint8Array(size);let offset=0;for(const c of chunks){data.set(c,offset);offset+=c.byteLength;}
 return JSON.parse(new TextDecoder().decode(data));
}
async function tokenRequest(env,fields,googleFetch){
 return googleJson('https://oauth2.googleapis.com/token',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},
  body:new URLSearchParams({client_id:env.YOUTUBE_CLIENT_ID,client_secret:env.YOUTUBE_CLIENT_SECRET,...fields}).toString()},googleFetch);
}
export async function youtubeConnectionStatus(env){
 const config=youtubeConfiguration(env);
 const row=await env.DB.prepare("SELECT channel_id,channel_title,scopes,connected_at,credentials_encrypted FROM youtube_connections WHERE id='primary'").first();
 const last=await env.DB.prepare("SELECT outcome FROM youtube_oauth_flows WHERE outcome NOT IN ('pending','connected') ORDER BY claimed_at DESC LIMIT 1").first();
 let connected=false;
 if(config.configured&&row?.channel_id===env.YOUTUBE_CHANNEL_ID)try{
  const saved=await decryptYoutube(env,row.credentials_encrypted,'youtube-connection:primary');
  connected=saved.client_id===env.YOUTUBE_CLIENT_ID&&saved.channel_id===row.channel_id&&validToken(saved.refresh_token);
 }catch{}
 return {ok:true,...config,connected,connection_stored:!!row,channel:connected?{id:row.channel_id,title:row.channel_title,connected_at:row.connected_at}:null,
  publication_scope_granted:connected&&typeof row?.scopes==='string'&&row.scopes.split(' ').includes(PUBLICATION_SCOPE),
  last_connection_result:last?.outcome||null,callback_url:YOUTUBE_CALLBACK,automatic_publication_allowed:false};
}
export async function startYoutubeConnection(env,payload,{now=seconds()}={}){
 if(payload?.confirmed!==true)return failure(400,'Confirma que deseas conectar el canal mediante Google.');
 const config=youtubeConfiguration(env);if(!config.configured)return failure(503,'Falta configuración OAuth del canal. Consulta los campos indicados en el panel.');
 const state=random(),browser=random(),verifier=random(),stateSha=await sha(state);
 const challenge=b64(new Uint8Array(await crypto.subtle.digest('SHA-256',encoder.encode(verifier))));
 const encrypted=await encryptYoutube(env,{verifier,client_id:env.YOUTUBE_CLIENT_ID,channel_id:env.YOUTUBE_CHANNEL_ID,publication_access:payload.publication_access===true},'youtube-flow:'+stateSha);
 await env.DB.batch([
  env.DB.prepare('DELETE FROM youtube_oauth_flows WHERE expires_at<?').bind(now),
  env.DB.prepare('INSERT INTO youtube_oauth_flows(state_sha256,cookie_sha256,payload_encrypted,expires_at) VALUES(?,?,?,?)')
   .bind(stateSha,await sha(browser),encrypted,now+600)
 ]);
 const url=new URL('https://accounts.google.com/o/oauth2/v2/auth');
 url.search=new URLSearchParams({client_id:env.YOUTUBE_CLIENT_ID,redirect_uri:YOUTUBE_CALLBACK,response_type:'code',
  scope:[...SCOPES,...(payload.publication_access===true?[PUBLICATION_SCOPE]:[])].join(' '),access_type:'offline',prompt:'consent',state,code_challenge:challenge,code_challenge_method:'S256'}).toString();
 return {ok:true,status:200,authorization_url:url.href,cookie:cookie(browser,600),automatic_publication_allowed:false};
}
function redirect(result){return new Response(null,{status:303,headers:{Location:'/?youtube='+result,
 'Set-Cookie':cookie('',0),'Cache-Control':'no-store','Referrer-Policy':'no-referrer'}});}
export async function finishYoutubeConnection(request,env,{now=seconds(),googleFetch=fetch}={}){
 const url=new URL(request.url),state=url.searchParams.get('state');
 const browser=(request.headers.get('Cookie')||'').split(';').map(c=>c.trim()).find(c=>c.startsWith(COOKIE+'='))?.slice(COOKIE.length+1);
 if(request.method!=='GET'||!youtubeConfiguration(env).configured||!/^[-\w]{43}$/.test(state||'')||!/^[-\w]{43}$/.test(browser||''))return redirect('not_connected');
 let stateSha;
 try{
  stateSha=await sha(state);
  const claimed=await env.DB.prepare(`UPDATE youtube_oauth_flows SET claimed_at=?,outcome='processing'
   WHERE state_sha256=? AND cookie_sha256=? AND claimed_at IS NULL AND expires_at>?`)
   .bind(now,stateSha,await sha(browser),now).run();
  if(claimed.meta?.changes!==1)return redirect('not_connected');
  if(url.searchParams.has('error')){
   await env.DB.prepare("UPDATE youtube_oauth_flows SET outcome='cancelled' WHERE state_sha256=?").bind(stateSha).run();return redirect('cancelled');
  }
  const code=url.searchParams.get('code');if(!code||code.length>4096||/[\x00-\x20]/.test(code))throw new Error('Código inválido');
  const row=await env.DB.prepare('SELECT payload_encrypted FROM youtube_oauth_flows WHERE state_sha256=?').bind(stateSha).first();
  const flow=await decryptYoutube(env,row.payload_encrypted,'youtube-flow:'+stateSha);
  if(flow.client_id!==env.YOUTUBE_CLIENT_ID||flow.channel_id!==env.YOUTUBE_CHANNEL_ID)throw new Error('Configuración cambió');
  const tokens=await tokenRequest(env,{code,grant_type:'authorization_code',redirect_uri:YOUTUBE_CALLBACK,code_verifier:flow.verifier},googleFetch);
  if(!validToken(tokens.access_token)||!validToken(tokens.refresh_token)||!Number.isFinite(tokens.expires_in)||
   tokens.expires_in<60||tokens.expires_in>86400||tokens.token_type?.toLowerCase()!=='bearer'||typeof tokens.scope!=='string'||
   !SCOPES.every(s=>tokens.scope.split(' ').includes(s))||(flow.publication_access===true&&!tokens.scope.split(' ').includes(PUBLICATION_SCOPE)))throw new Error('Permisos incompletos');
  const channels=await googleJson('https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true&maxResults=50',
   {headers:{Authorization:'Bearer '+tokens.access_token}},googleFetch);
  const channel=Array.isArray(channels.items)?channels.items.find(c=>c.id===env.YOUTUBE_CHANNEL_ID):null;
  if(!channel){
   await env.DB.prepare("UPDATE youtube_oauth_flows SET outcome='channel_mismatch' WHERE state_sha256=?").bind(stateSha).run();return redirect('not_connected');
  }
  const cipher=await encryptYoutube(env,{access_token:tokens.access_token,refresh_token:tokens.refresh_token,
   client_id:env.YOUTUBE_CLIENT_ID,channel_id:channel.id},'youtube-connection:primary');
  const result=await env.DB.batch([
   env.DB.prepare(`INSERT INTO youtube_connections(id,channel_id,channel_title,credentials_encrypted,scopes,token_expires_at,connected_at,updated_at)
    SELECT 'primary',?,?,?,?,?,?,? WHERE EXISTS(SELECT 1 FROM youtube_oauth_flows WHERE state_sha256=? AND claimed_at=? AND expires_at>?)
    ON CONFLICT(id) DO UPDATE SET channel_id=excluded.channel_id,channel_title=excluded.channel_title,
    credentials_encrypted=excluded.credentials_encrypted,scopes=excluded.scopes,token_expires_at=excluded.token_expires_at,
    connected_at=excluded.connected_at,updated_at=excluded.updated_at`)
    .bind(channel.id,String(channel.snippet?.title||'Canal autorizado').slice(0,160),cipher,tokens.scope,now+tokens.expires_in,now,now,stateSha,now,now),
   env.DB.prepare("UPDATE youtube_oauth_flows SET outcome='connected' WHERE state_sha256=? AND EXISTS(SELECT 1 FROM youtube_connections WHERE id='primary' AND credentials_encrypted=?)").bind(stateSha,cipher)
  ]);
  return redirect(result[0].meta?.changes===1?'connected':'not_connected');
 }catch{
  if(stateSha)try{await env.DB.prepare("UPDATE youtube_oauth_flows SET outcome='failed' WHERE state_sha256=? AND outcome='processing'").bind(stateSha).run();}catch{}
  return redirect('not_connected');
 }
}
export async function disconnectYoutube(env,payload,{googleFetch=fetch}={}){
 if(payload?.confirmed!==true)return failure(400,'Confirma que deseas desconectar el canal.');
 const row=await env.DB.prepare("SELECT credentials_encrypted FROM youtube_connections WHERE id='primary'").first();
 let token;try{if(row)token=(await decryptYoutube(env,row.credentials_encrypted,'youtube-connection:primary')).refresh_token;}catch{}
 await env.DB.batch([env.DB.prepare('DELETE FROM youtube_oauth_flows'),env.DB.prepare("DELETE FROM youtube_connections WHERE id='primary'")]);
 let revoked=!row;
 if(token)try{const r=await googleFetch('https://oauth2.googleapis.com/revoke',{method:'POST',redirect:'manual',
  headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams({token}).toString(),signal:AbortSignal.timeout(12000)});revoked=r.ok;await r.body?.cancel();}catch{}
 return {ok:true,connected:false,revocation_confirmed:revoked,automatic_publication_allowed:false};
}

// Uso interno del futuro subidor; ninguna ruta entrega este resultado al navegador.
export async function youtubeAccessToken(env,{googleFetch=fetch,now=seconds()}={}){
 if(!youtubeConfiguration(env).configured)return failure(503,'Falta configuración OAuth del canal.');
 try{
  const row=await env.DB.prepare("SELECT * FROM youtube_connections WHERE id='primary'").first();
  if(!row||row.channel_id!==env.YOUTUBE_CHANNEL_ID)return failure(409,'Conecta el canal autorizado antes de continuar.');
  const saved=await decryptYoutube(env,row.credentials_encrypted,'youtube-connection:primary');
  if(!validToken(saved.refresh_token)||saved.client_id!==env.YOUTUBE_CLIENT_ID||saved.channel_id!==row.channel_id)throw new Error('Requiere consentimiento');
  if(row.token_expires_at>now+60&&validToken(saved.access_token))return {ok:true,access_token:saved.access_token};
  const next=await tokenRequest(env,{grant_type:'refresh_token',refresh_token:saved.refresh_token},googleFetch);
  if(!validToken(next.access_token)||!Number.isFinite(next.expires_in)||next.expires_in<60||next.expires_in>86400||
    next.token_type?.toLowerCase()!=='bearer'||(next.scope!==undefined&&
      (typeof next.scope!=='string'||!SCOPES.every(s=>next.scope.split(' ').includes(s)))))throw new Error('Renovación no confirmada');
  if(next.refresh_token!==undefined&&!validToken(next.refresh_token))throw new Error('Credencial inválida');
  const cipher=await encryptYoutube(env,{access_token:next.access_token,refresh_token:next.refresh_token||saved.refresh_token,
   client_id:env.YOUTUBE_CLIENT_ID,channel_id:row.channel_id},'youtube-connection:primary');
  const update=await env.DB.prepare(`UPDATE youtube_connections SET credentials_encrypted=?,token_expires_at=?,updated_at=?
    WHERE id='primary' AND channel_id=? AND credentials_encrypted=?`)
   .bind(cipher,now+next.expires_in,now,row.channel_id,row.credentials_encrypted).run();
  if(update.meta?.changes!==1)return failure(409,'La conexión cambió; vuelve a comprobar el canal.');
  return {ok:true,access_token:next.access_token};
 }catch{return failure(409,'No se pudo renovar la autorización. Vuelve a conectar el canal con Google.');}
}

