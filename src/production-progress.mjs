// Consulta de sólo lectura. No inicia trabajos, modelos ni búsquedas.
const REPO='eler30mr-star/FactordeGigantes';
const BASE='https://api.github.com/repos/'+REPO;
const WORKFLOW='.github/workflows/development-episode.yml';
const STATES=new Set(['queued','in_progress','completed','waiting','requested','pending']);
const CONCLUSIONS=new Set(['success','failure','cancelled','timed_out','skipped','action_required','neutral','stale','startup_failure']);
const id=value=>typeof value==='number'&&Number.isSafeInteger(value)&&value>0;
const unavailable=(status,error)=>({ok:false,status,error});

async function boundedJson(response){
 const reader=response.body?.getReader();if(!reader)throw new Error('Respuesta vacía');
 const chunks=[];let size=0;
 while(true){
  const {done,value}=await reader.read();if(done)break;
  size+=value.byteLength;
  if(size>600000){await reader.cancel();throw new Error('Respuesta demasiado grande');}
  chunks.push(value);
 }
 const bytes=new Uint8Array(size);let offset=0;
 for(const c of chunks){bytes.set(c,offset);offset+=c.byteLength;}
 return JSON.parse(new TextDecoder().decode(bytes));
}

function runView(run){
 if(!run||!id(run.id)||run.path!==WORKFLOW||run.head_branch!=='main'||
    run.event!=='workflow_dispatch'||run.repository?.full_name!==REPO||!STATES.has(run.status)||
    (run.status==='completed'&&!CONCLUSIONS.has(run.conclusion)))return null;
 return {id:String(run.id),title:String(run.display_title||run.name||'Producción').slice(0,180),
  status:run.status,conclusion:run.status==='completed'?run.conclusion:null,
  created_at:run.created_at,updated_at:run.updated_at,
  run_url:'https://github.com/'+REPO+'/actions/runs/'+run.id,publication_authorized:false};
}

async function request(env,path,githubFetch){
 const response=await githubFetch(BASE+path,{headers:{
  Authorization:'Bearer '+env.GITHUB_DISPATCH_TOKEN,Accept:'application/vnd.github+json',
  'X-GitHub-Api-Version':'2022-11-28','User-Agent':'FactorDeGigantes-Produccion'
 },redirect:'manual',signal:AbortSignal.timeout(6000)});
 if(!response.ok)return unavailable(response.status===404?404:502,
  response.status===404?'Ejecución no disponible':'No se pudo consultar producción en GitHub. Revisa acceso Actions o disponibilidad.');
 return {ok:true,data:await boundedJson(response)};
}

const jobState=job=>!job?{status:'waiting',conclusion:null}:
 {status:STATES.has(job.status)?job.status:'waiting',
  conclusion:job.status==='completed'&&CONCLUSIONS.has(job.conclusion)?job.conclusion:null};

export function summarizeProduction(run,jobs,artifacts){
 const view=runView(run);if(!view)throw new RangeError('Ejecución de producción inválida');
 const latest=new Map();
 for(const j of jobs){
  if(!/^voice \(SC\d{2}\)$/.test(j.name)||!id(j.id))continue;
  const scene=j.name.match(/SC\d{2}/)[0];
  if(!latest.has(scene)||j.id>latest.get(scene).id)latest.set(scene,j);
 }
 const scenes=[...latest].map(([scene,j])=>({scene,...jobState(j)})).sort((a,b)=>a.scene.localeCompare(b.scene));
 const completed=scenes.filter(s=>s.conclusion==='success').length;
 const failed=scenes.filter(s=>s.status==='completed'&&!['success','skipped'].includes(s.conclusion)).length;
 const results=[];
 for(const [name,label,jobName,containsNarration] of [
  ['fdg-episode-narrated-review','Video narrado para revisión','narrated',true],
  ['fdg-episode-technical-review','Montaje técnico sin locución','technical',false]
 ]){
  if(jobs.find(j=>j.name===jobName)?.conclusion!=='success')continue;
  const artifact=artifacts.find(a=>a.name===name&&a.expired===false&&id(a.id)&&
    Number.isSafeInteger(a.size_in_bytes)&&a.size_in_bytes>0);
  if(artifact)results.push({label,contains_narration:containsNarration,size_bytes:artifact.size_in_bytes,
   expires_at:artifact.expires_at,download_url:view.run_url+'/artifacts/'+artifact.id});
 }
 return {ok:true,run:view,preparation:jobState(jobs.find(j=>j.name==='prepare')),
  narration:{total:scenes.length,completed,failed,scenes},
  assembly:jobState(jobs.find(j=>j.name===((scenes.length>0)?'narrated':'technical'))),
  results,automatic_publication_allowed:false,
  note:'Escenas contadas desde Actions. Un resultado técnico o narrado sigue sujeto a revisión humana.'};
}

export async function readProductionProgress(env,runId=null,githubFetch=fetch){
 if(env.GITHUB_REPO!==REPO||typeof env.GITHUB_DISPATCH_TOKEN!=='string'||env.GITHUB_DISPATCH_TOKEN.length<24)
  return unavailable(503,'Configura el acceso de lectura a GitHub Actions para consultar producción.');
 if(runId!==null&&(typeof runId!=='string'||!/^\d{1,16}$/.test(runId)||!id(Number(runId))))
  return unavailable(400,'Identificador de ejecución inválido');
 try{
  if(runId===null){
   const response=await request(env,'/actions/workflows/development-episode.yml/runs?branch=main&event=workflow_dispatch&per_page=8',githubFetch);
   if(!response.ok)return response;
   if(!Array.isArray(response.data.workflow_runs))throw new Error('Lista inválida');
   return {ok:true,runs:response.data.workflow_runs.slice(0,8).map(runView).filter(Boolean),automatic_publication_allowed:false};
  }
  const run=await request(env,'/actions/runs/'+runId,githubFetch);if(!run.ok)return run;
  if(!runView(run.data))return unavailable(404,'No es una ejecución de producción de main');
  const [jobs,artifacts]=await Promise.all([
   request(env,'/actions/runs/'+runId+'/jobs?filter=latest&per_page=100',githubFetch),
   request(env,'/actions/runs/'+runId+'/artifacts?per_page=100',githubFetch)
  ]);
  if(!jobs.ok)return jobs;if(!artifacts.ok)return artifacts;
  if(!Array.isArray(jobs.data.jobs)||!Array.isArray(artifacts.data.artifacts)||jobs.data.total_count>100||artifacts.data.total_count>100)
   throw new Error('Estado incompleto');
  return summarizeProduction(run.data,jobs.data.jobs,artifacts.data.artifacts);
 }catch{return unavailable(502,'Estado de producción no disponible. No se ha iniciado ni repetido ningún trabajo.');}
}
