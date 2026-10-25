// Private streaming proxy for a registered, immutable narrated export.
// Browser validates archive/video digests before creating a seekable local Blob.
import {boundedUploadJson} from './youtube-exports.mjs';
const REPO='eler30mr-star/FactordeGigantes',BASE='https://api.github.com/repos/'+REPO;
export const PREVIEW_LIMIT=80*1024*1024;
const HASH=/^[a-f0-9]{64}$/;
const failure=(status,message)=>Response.json({error:message},{status,headers:{'Cache-Control':'no-store'}});
function artifactLocation(value){
 const u=new URL(value);
 if(u.protocol!=='https:'||u.port||u.username||u.password||u.hash||
  !['.blob.core.windows.net','.actions.githubusercontent.com','.githubusercontent.com'].some(s=>u.hostname.endsWith(s)))throw Error('Invalid artifact origin');
 return u.href;
}
export async function videoPreview(env,id,{fetcher=fetch}={}){
 if(typeof id!=='string'||!HASH.test(id))return failure(400,'Video inválido');
 const row=await env.DB.prepare('SELECT id,artifact_id,source_run_id,archive_sha256,video_bytes FROM youtube_exports WHERE id=?').bind(id).first();
 if(!row)return failure(404,'Video no registrado');
 if(!HASH.test(row.archive_sha256)||!Number.isSafeInteger(row.video_bytes)||row.video_bytes<1||row.video_bytes>PREVIEW_LIMIT)
  return failure(413,'Este video excede el tamaño de reproducción del panel. Conserva su descarga.');
 if(env.GITHUB_REPO!==REPO||typeof env.GITHUB_DISPATCH_TOKEN!=='string'||env.GITHUB_DISPATCH_TOKEN.length<24)
  return failure(503,'Acceso de lectura de videos no configurado');
 if(!/^[1-9]\d{0,15}$/.test(row.artifact_id)||!/^[1-9]\d{0,15}$/.test(row.source_run_id))return failure(409,'Origen del video inválido');
 const options={redirect:'manual',signal:AbortSignal.timeout(15000),headers:{
  Authorization:'Bearer '+env.GITHUB_DISPATCH_TOKEN,Accept:'application/vnd.github+json',
  'X-GitHub-Api-Version':'2022-11-28','User-Agent':'FactorDeGigantes-Preview'}};
 try{
  const metadata=await fetcher(BASE+'/actions/artifacts/'+row.artifact_id,options);
  if(!metadata.ok)return failure(metadata.status===404?410:502,'El archivo de revisión no está disponible.');
  const a=await boundedUploadJson(metadata);
  if(a.expired===true)return failure(410,'El archivo de revisión ha caducado en GitHub. No se regenerará automáticamente.');
  if(a.expired!==false||String(a.id)!==row.artifact_id||a.name!=='fdg-episode-narrated-review'||String(a.workflow_run?.id)!==row.source_run_id||
    a.digest!=='sha256:'+row.archive_sha256||!Number.isSafeInteger(a.size_in_bytes)||a.size_in_bytes<1||a.size_in_bytes>PREVIEW_LIMIT)
   return failure(409,'El paquete no coincide con el video registrado o excede el límite.');
  const redirect=await fetcher(BASE+'/actions/artifacts/'+row.artifact_id+'/zip',options);
  if(redirect.status!==302)return failure(502,'GitHub no entregó el archivo de revisión.');
  const location=artifactLocation(redirect.headers.get('Location'));
  // Never forward the GitHub credential to the signed storage URL.
  const archive=await fetcher(location,{redirect:'manual',signal:AbortSignal.timeout(120000)});
  if(!archive.ok||!archive.body)return failure(502,'No se pudo recuperar el video. Intenta de nuevo.');
  const declared=archive.headers.get('Content-Length');
  if(declared!==null&&Number(declared)!==a.size_in_bytes){await archive.body.cancel();return failure(502,'Archivo de revisión incompleto.');}
  let bytes=0;
  const bounded=new TransformStream({transform(chunk,controller){bytes+=chunk.byteLength;
    if(bytes>a.size_in_bytes)throw Error('Archive exceeds registered size');controller.enqueue(chunk);},
   flush(){if(bytes!==a.size_in_bytes)throw Error('Truncated archive');}});
  return new Response(archive.body.pipeThrough(bounded),{headers:{
   'Content-Type':'application/zip','Cache-Control':'private, no-store','X-Content-Type-Options':'nosniff',
   'X-Archive-SHA256':row.archive_sha256,'X-Video-SHA256':row.id,
   'X-Video-Bytes':String(row.video_bytes),'X-Archive-Bytes':String(a.size_in_bytes)
  }});
 }catch{return failure(502,'No se pudo preparar la vista previa. Reintenta sin regenerar el episodio.');}
}
