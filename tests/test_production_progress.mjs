import test from 'node:test';
import assert from 'node:assert/strict';
import {readProductionProgress,summarizeProduction} from '../src/production-progress.mjs';
import worker from '../src/worker.js';
const env={GITHUB_REPO:'eler30mr-star/FactordeGigantes',GITHUB_DISPATCH_TOKEN:'private-github-test-token-never-return',
 ADMIN_TOKEN:'private-admin-test-token-never-return',RENDERER_TOKEN:'private-render-test-token-never-return',DB:{}};
const run={id:123,event:'workflow_dispatch',path:'.github/workflows/development-episode.yml',head_branch:'main',
 repository:{full_name:env.GITHUB_REPO},display_title:'Episodio · final_ai',status:'in_progress',conclusion:null,run_attempt:1};
const job=(id,name,status='completed',conclusion='success')=>({id,name,status,conclusion});
const jobs=[job(1,'prepare'),job(2,'voice (SC01)'),job(3,'voice (SC02)','in_progress',null),
 job(4,'voice (SC03)','queued',null),job(5,'voice (SC04)','completed','failure')];
const artifact={id:456,name:'fdg-episode-narrated-review',expired:false,size_in_bytes:1000,
 expires_at:'2026-11-01T00:00:00Z',archive_download_url:'https://evil.test/do-not-use'};
const response=data=>Response.json(data);

test('avance cuenta escenas reales, conserva éxitos anteriores y no anuncia exportación antes de montar',()=>{
 const result=summarizeProduction({...run,run_attempt:2},[...jobs,job(6,'voice (SC04)','in_progress',null)],[artifact]);
 assert.equal(result.narration.total,4);assert.equal(result.narration.completed,1);assert.equal(result.narration.failed,0);
 assert.equal(result.narration.scenes[3].status,'in_progress');assert.equal(result.assembly.status,'waiting');
 assert.deepEqual(result.results,[]);assert.equal(result.automatic_publication_allowed,false);
});
test('descargas son oficiales, distinguen señal técnica y narración, y excluyen artefactos caducados',()=>{
 let r=summarizeProduction(run,[...jobs,job(7,'narrated')],[artifact]);
 assert.equal(r.results[0].download_url,'https://github.com/eler30mr-star/FactordeGigantes/actions/runs/123/artifacts/456');
 assert.equal(r.results[0].contains_narration,true);assert.ok(!JSON.stringify(r).includes('evil.test'));
 assert.equal(summarizeProduction(run,[job(7,'narrated')],[{...artifact,expired:true}]).results.length,0);
 assert.equal(summarizeProduction(run,[job(7,'narrated','completed','failure')],[artifact]).results.length,0);
 r=summarizeProduction(run,[job(7,'technical')],[{...artifact,name:'fdg-episode-technical-review'}]);
 assert.equal(r.results[0].contains_narration,false);assert.equal(r.narration.total,0);
});
test('listado usa sólo el workflow canónico y filtra otras ramas, eventos o repositorios',async()=>{
 let calls=0;
 const r=await readProductionProgress(env,null,async(url,options)=>{
  calls++;assert.match(url,/development-episode.yml\/runs\?branch=main&event=workflow_dispatch&per_page=8$/);
  assert.equal(options.redirect,'manual');assert.equal(options.headers.Authorization,'Bearer '+env.GITHUB_DISPATCH_TOKEN);
  return response({workflow_runs:[run,{...run,id:124,head_branch:'feature'},{...run,id:125,path:'.github/workflows/render.yml'},
   {...run,id:126,event:'pull_request'},{...run,id:127,repository:{full_name:'foreign/repo'}}]});
 });
 assert.equal(calls,1);assert.equal(r.runs.length,1);assert.equal(r.runs[0].id,'123');
 assert.ok(!JSON.stringify(r).includes(env.GITHUB_DISPATCH_TOKEN));
});
test('detalle verifica el run antes de leer jobs y artefactos; entradas inválidas no hacen red',async()=>{
 let calls=[];
 const r=await readProductionProgress(env,'123',async url=>{
  calls.push(url);
  return response(url.includes('/jobs?')?{jobs,total_count:jobs.length}:url.includes('/artifacts?')?{artifacts:[],total_count:0}:run);
 });
 assert.equal(r.ok,true);assert.equal(calls.length,3);assert.equal(r.narration.completed,1);
 calls=[];
 for(const value of ['../secret','123?x=1','0','9007199254740999'])
  assert.equal((await readProductionProgress(env,value,async()=>{calls.push(1);})).status,400);
 assert.equal(calls.length,0);
 const wrong=await readProductionProgress(env,'123',async()=>{calls.push(1);return response({...run,path:'another.yml'});});
 assert.equal(wrong.status,404);assert.equal(calls.length,1);
});
test('permisos, red, cuerpos excesivos o paginación incompleta no se convierten en éxito ni filtran secretos',async()=>{
 assert.equal((await readProductionProgress({...env,GITHUB_DISPATCH_TOKEN:''},null,()=>{throw Error('No red');})).status,503);
 for(const fake of [async()=>{throw Error(env.GITHUB_DISPATCH_TOKEN);},async()=>new Response('secret',{status:403}),
  async()=>new Response('x'.repeat(600001)),async()=>response({workflow_runs:'incorrecto'})]){
  const result=await readProductionProgress(env,null,fake);assert.equal(result.status,502);
  assert.ok(!JSON.stringify(result).includes(env.GITHUB_DISPATCH_TOKEN));
 }
 const result=await readProductionProgress(env,'123',async url=>response(url.includes('/jobs?')?{jobs,total_count:101}:url.includes('/artifacts?')?{artifacts:[],total_count:0}:run));
 assert.equal(result.status,502);
});
test('API sólo ADMIN y GET; token renderer no puede leer progreso y no hay escrituras D1',async()=>{
 const req=(token,method='GET')=>new Request('https://test/api/production/runs',{method,headers:{Authorization:'Bearer '+token}});
 assert.equal((await worker.fetch(req('invalid'),env)).status,401);
 assert.equal((await worker.fetch(req(env.RENDERER_TOKEN),env)).status,401);
 assert.equal((await worker.fetch(req(env.ADMIN_TOKEN,'POST'),env)).status,405);
 const before=globalThis.fetch;globalThis.fetch=async()=>response({workflow_runs:[run]});
 try{
  const r=await worker.fetch(req(env.ADMIN_TOKEN),env);assert.equal(r.status,200);
  assert.equal((await r.json()).runs.length,1);assert.equal(r.headers.get('Cache-Control'),'no-store');
 }finally{globalThis.fetch=before;}
});
