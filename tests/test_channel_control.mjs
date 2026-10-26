import test from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFileSync} from 'node:fs';
import worker from '../src/worker.js';
import {channelStatus,setAutomaticMode,receiveChannelInstruction,automaticGate} from '../src/channel-control.mjs';
import {mountChannelControl} from '../public/channel-control.js';

const ADMIN='private-owner-token-testing-0001',RENDER='private-render-token-testing-0001';
function database(){
 const raw=new DatabaseSync(':memory:');
 raw.exec('PRAGMA foreign_keys=ON');
 raw.exec(readFileSync(new URL('../migrations/0017_channel_control.sql',import.meta.url),'utf8'));
 const prepare=sql=>{
  let args=[];return {bind(...values){args=values;return this;},
   async first(){return raw.prepare(sql).get(...args)||null;},
   async all(){return {results:raw.prepare(sql).all(...args)};},
   async run(){return {meta:{changes:Number(raw.prepare(sql).run(...args).changes)}};}
  };
 };
 return {raw,prepare,async batch(statements){
  raw.exec('BEGIN');try{const out=[];for(const s of statements)out.push(await s.run());raw.exec('COMMIT');return out;}
  catch(e){raw.exec('ROLLBACK');throw e;}
 }};
}
const environment=()=>({DB:database(),ADMIN_TOKEN:ADMIN,RENDERER_TOKEN:RENDER,FINAL_AI_INTEGRATION_ENABLED:'0'});
const op=(revision,extra={})=>({revision,request_id:crypto.randomUUID(),...extra});
const chat='Haz un video sobre BlackBerry y por qué perdió el mercado';
const post=(path,body,token=ADMIN)=>new Request('https://factor.test'+path,{
 method:'POST',headers:{Authorization:'Bearer '+token,'Content-Type':'application/json'},body:JSON.stringify(body)
});

test('default off, persistent mode, no selector bypass and no providers',async()=>{
 const env=environment();
 const off=await channelStatus(env);assert.equal(off.automatic_enabled,false);assert.equal(off.allowed,false);
 const enabled=await setAutomaticMode(env,op(0,{enabled:true}));assert.equal(enabled.automatic_enabled,true);
 const reloaded=await channelStatus({...env});assert.equal(reloaded.automatic_enabled,true);assert.equal(reloaded.revision,1);
 assert.equal(reloaded.reason,'research_paused');assert.equal(reloaded.allowed,false);
 assert.equal((await automaticGate({...env,FINAL_AI_INTEGRATION_ENABLED:'1'})).allowed,false);
 assert.equal(env.DB.raw.prepare('SELECT count(*) AS n FROM channel_control_events').get().n,1);
 assert.equal((await setAutomaticMode(env,op(1,{enabled:false}))).automatic_enabled,false);
 assert.equal((await channelStatus(env)).reason,'automatic_off');
});

test('lease rejects delayed switch and replay cannot reactivate after switch off',async()=>{
 const env=environment(),first=op(0,{enabled:true});
 await setAutomaticMode(env,first);
 await setAutomaticMode(env,op(1,{enabled:false}));
 const replay=await setAutomaticMode(env,first);assert.equal(replay.replayed,true);
 assert.equal((await automaticGate(env)).automatic_enabled,false);
 assert.equal((await setAutomaticMode(env,op(0,{enabled:true}))).status,409);
 assert.equal((await channelStatus(env)).revision,2);
});

test('mode off permits chat selection, stores exact company/topic without deep research',async()=>{
 const env=environment(),body=op(0,{message:chat});
 const result=await receiveChannelInstruction(env,body);
 assert.equal(result.state,'selected');assert.equal(result.episode.company,'BlackBerry');
 assert.equal(result.episode.topic,'por qué perdió el mercado');assert.equal(result.publication_authorized,false);
 const status=await channelStatus(env);assert.equal(status.episode.origin,'chat');assert.equal(status.automatic_enabled,false);
 assert.match(status.conversation[0].reply,/pausada/);
 assert.equal((await receiveChannelInstruction(env,body)).replayed,true);
 assert.equal(env.DB.raw.prepare('SELECT count(*) AS n FROM channel_episodes').get().n,1);
 const another=await receiveChannelInstruction(env,op(1,{message:'Haz un video sobre Nokia y su transformación'}));
 assert.equal(another.status,409);assert.equal((await channelStatus(env)).episode.company,'BlackBerry');
});

test('ambiguous chat asks company then topic and reload retains dialogue',async()=>{
 const env=environment();
 assert.equal((await receiveChannelInstruction(env,op(0,{message:'Quiero hacer otro video'}))).state,'clarification');
 const company=await receiveChannelInstruction({...env},op(1,{message:'Nokia'}));
 assert.match(company.reply,/enfoque/);assert.equal(company.episode,null);
 const selected=await receiveChannelInstruction({...env},op(2,{message:'Su transformación después del teléfono'}));
 assert.equal(selected.episode.company,'Nokia');assert.match(selected.episode.topic,/transformación/);
 const status=await channelStatus(env);assert.equal(status.conversation.length,3);
 assert.equal(env.DB.raw.prepare('SELECT pending_company FROM channel_control').get().pending_company,'');
});

test('a competing stale chat cannot overwrite mode or create an episode',async()=>{
 const env=environment();await setAutomaticMode(env,op(0,{enabled:true}));
 const stale=await receiveChannelInstruction(env,op(0,{message:chat}));assert.equal(stale.status,409);
 assert.equal((await channelStatus(env)).episode,null);
 const accepted=await receiveChannelInstruction(env,op(1,{message:chat}));assert.equal(accepted.state,'selected');
 await setAutomaticMode(env,op(2,{enabled:false}));
 assert.equal((await channelStatus(env)).episode.id,accepted.episode.id);
});

test('changed payload cannot reuse operation id; validation does not write',async()=>{
 const env=environment(),body=op(0,{enabled:true});await setAutomaticMode(env,body);
 assert.equal((await setAutomaticMode(env,{...body,enabled:false})).status,409);
 for(const invalid of [op(1,{enabled:'true'}),{revision:-1,request_id:crypto.randomUUID(),enabled:false}])
  await assert.rejects(()=>setAutomaticMode(env,invalid),RangeError);
 for(const message of ['<script>','x'.repeat(601),'text\nwith control'])
  await assert.rejects(()=>receiveChannelInstruction(env,op(1,{message})),RangeError);
 assert.equal((await channelStatus(env)).revision,1);
});

test('schema is additive/idempotent and unique active episode protects two producers',()=>{
 const db=database();db.raw.exec("CREATE TABLE existing_data(value); INSERT INTO existing_data VALUES ('preserve');");
 db.raw.exec(readFileSync(new URL('../migrations/0017_channel_control.sql',import.meta.url),'utf8'));
 assert.equal(db.raw.prepare('SELECT value FROM existing_data').get().value,'preserve');
 db.raw.exec("INSERT INTO channel_episodes(id,channel,origin,company,topic,instruction) VALUES ('a','factor-de-gigantes','chat','Nokia','Historia de Nokia','test')");
 assert.throws(()=>db.raw.exec("INSERT INTO channel_episodes(id,channel,origin,company,topic,instruction) VALUES ('b','factor-de-gigantes','chat','Apple','Historia de Apple','test')"),/UNIQUE/);
});

test('API enforces ADMIN, methods, malformed input and missing migration',async()=>{
 const env=environment();
 for(const token of ['',RENDER]){
  assert.equal((await worker.fetch(post('/api/channel-control/mode',op(0,{enabled:true}),token),env)).status,401);
  assert.equal((await worker.fetch(post('/api/market/automation-control',{},token),env)).status,401);
 }
 assert.equal((await worker.fetch(post('/api/channel-control/chat',op(0,{message:chat})),env)).status,200);
 assert.equal((await worker.fetch(post('/api/channel-control/chat',{message:chat}),env)).status,400);
 assert.equal((await worker.fetch(post('/api/channel-control',{}),env)).status,405);
 assert.equal((await worker.fetch(new Request('https://factor.test/api/channel-control',{headers:{Authorization:'Bearer '+ADMIN}}),env)).status,200);
 const missing={...env,DB:{prepare(){throw Error('no such table: channel_control');}}};
 assert.equal((await worker.fetch(new Request('https://factor.test/api/channel-control',{headers:{Authorization:'Bearer '+ADMIN}}),missing)).status,503);
});

class Element{
 constructor(){this.listeners={};this.children=[];this.value='';this.textContent='';this.attrs={};}
 addEventListener(event,fn){this.listeners[event]=fn;}
 append(child){this.children.push(child);}
 replaceChildren(){this.children=[];}
 setAttribute(key,value){this.attrs[key]=value;}
}
test('panel explains an insufficient observed sample without presenting a company selection',async()=>{
 const elements=new Map();
 const doc={getElementById(id){if(!elements.has(id))elements.set(id,new Element());return elements.get(id);},createElement(){return new Element();}};
 const request=async path=>path==='/api/market/opportunity-study'?{study:{
  state:'insufficient',observed_on:'2026-10-25',rankings:[],selected:null,
  sample_summary:{observed_videos:2,comparable_long_videos:2,distinct_channels:1,recent_examples:1},
  minimum_sample_reasons:['need_four_comparable_long_videos','need_three_observed_channels','need_two_recent_examples']
 }}:{automatic_enabled:false,message:'Esperando tu instrucción.',conversation:[],episode:null,revision:0};
 await mountChannelControl({request,documentRef:doc}).load();
 const paragraphs=elements.get('channel-study').children.map(p=>p.textContent);
 assert.ok(paragraphs.some(p=>p.includes('2 videos largos comparables, 1 canal y 1 ejemplo reciente')));
 assert.ok(paragraphs.some(p=>p.startsWith('Todavía no se puede elegir:')&&p.includes('cuatro videos')&&p.includes('tres canales')&&p.includes('recientes')));
 assert.equal(elements.get('channel-episode').children.length,0);
 assert.ok(paragraphs.every(p=>!p.includes('undefined')));
});

test('panel switch reflects saved state, chat reaches API, rendering is text only',async()=>{
 const env=environment(),elements=new Map();
 const doc={getElementById(id){if(!elements.has(id))elements.set(id,new Element());return elements.get(id);},createElement(){return new Element();}};
 const calls=[];
 const request=async(path,method='GET',body)=>{
  calls.push({path,method,body});
  if(method==='GET')return channelStatus(env);
  return path.endsWith('/mode')?setAutomaticMode(env,body):receiveChannelInstruction(env,body);
 };
 const mounted=mountChannelControl({request,documentRef:doc});await mounted.load();
 assert.equal(elements.get('automatic-toggle').textContent,'Automático: apagado');
 await elements.get('automatic-toggle').listeners.click();
 assert.equal(elements.get('automatic-toggle').attrs['aria-checked'],'true');
 doc.getElementById('channel-message').value=chat;
 await elements.get('channel-chat-form').listeners.submit({preventDefault(){}});
 assert.equal((await channelStatus(env)).episode.company,'BlackBerry');
 assert.equal(calls.filter(c=>c.path.endsWith('/chat')).length,1);
 assert.equal(elements.get('channel-message').value,'');
});
