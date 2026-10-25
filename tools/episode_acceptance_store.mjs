// Uses production persistence functions against an isolated SQLite acceptance DB.
// No remote bindings, tokens, workflow dispatches, renders, or publication.
import {DatabaseSync} from 'node:sqlite';
import {readFileSync,readdirSync} from 'node:fs';
import {channelResearchContext,storeChannelResearch,storeChannelScript} from '../src/channel-research.mjs';
const input=JSON.parse(readFileSync(0,'utf8'));
const raw=new DatabaseSync('dist/final-directed-acceptance/ACEPTACION.sqlite');
raw.exec('PRAGMA foreign_keys=ON');
for(const file of readdirSync('migrations').filter(f=>f.endsWith('.sql')).sort())raw.exec(readFileSync('migrations/'+file,'utf8'));
const DB={prepare(sql){let args=[];return {bind(...values){args=values;return this;},async first(){return raw.prepare(sql).get(...args)||null;},async all(){return {results:raw.prepare(sql).all(...args)};},async run(){return {meta:{changes:Number(raw.prepare(sql).run(...args).changes)}};}};},async batch(statements){raw.exec('BEGIN');try{const rows=[];for(const s of statements)rows.push(await s.run());raw.exec('COMMIT');return rows;}catch(e){raw.exec('ROLLBACK');throw e;}}};
const env={DB,FINAL_AI_INTEGRATION_ENABLED:'1'};
let result;
if(input.action==='init'){
 const {episode_id,request_id,company,topic}=input.identity;
 raw.prepare("INSERT OR IGNORE INTO channel_episodes(id,channel,origin,company,topic,instruction) VALUES(?,'factor-de-gigantes','chat',?,?,'PRUEBA INTEGRADA AISLADA: no es una instrucción de producción')").run(episode_id,company,topic);
 raw.prepare("INSERT OR IGNORE INTO channel_episode_research(id,episode_id,state) VALUES(?,?,'reserved')").run(request_id,episode_id);
 result={ok:true};
}else if(input.action==='context')result=await channelResearchContext(env,input.body);
else if(input.action==='research')result=await storeChannelResearch(env,input.body);
else if(input.action==='script')result=await storeChannelScript(env,input.body);
else throw Error('Operación de aceptación inválida');
raw.close();process.stdout.write(JSON.stringify(result));
