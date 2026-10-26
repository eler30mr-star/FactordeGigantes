const MAX=80*1024*1024,NAME='EPISODIO_PARA_REVISION.mp4';
const hash=async bytes=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');
async function readBounded(stream,limit,signal,progress=()=>{}){
 const reader=stream.getReader(),chunks=[];let size=0;
 try{
  while(true){if(signal?.aborted)throw new DOMException('Cancelado','AbortError');
   const {done,value}=await reader.read();if(done)break;size+=value.byteLength;
   if(size>limit)throw Error('El archivo excede el tamaño permitido');chunks.push(value);progress(size);
  }
 }catch(e){await reader.cancel().catch(()=>{});throw e;}
 const bytes=new Uint8Array(size);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.length;}return bytes;
}
export async function extractPreview(zip,{archiveHash,videoHash,videoBytes,signal}){
 if(!(zip instanceof Uint8Array)||zip.length>MAX||!Number.isSafeInteger(videoBytes)||videoBytes<1||videoBytes>MAX||
  !/^[a-f0-9]{64}$/.test(archiveHash)||!/^[a-f0-9]{64}$/.test(videoHash))throw Error('Metadatos de vista previa inválidos');
 if(await hash(zip)!==archiveHash)throw Error('La huella del paquete no coincide');
 const view=new DataView(zip.buffer,zip.byteOffset,zip.byteLength);
 let end=-1;
 for(let i=zip.length-22;i>=Math.max(0,zip.length-65557);i--){
  if(view.getUint32(i,true)===0x06054b50&&i+22+view.getUint16(i+20,true)===zip.length){end=i;break;}
 }
 if(end<0||view.getUint16(end+4,true)||view.getUint16(end+6,true)||
  view.getUint16(end+8,true)!==view.getUint16(end+10,true))throw Error('Paquete ZIP no compatible');
 const count=view.getUint16(end+10,true),length=view.getUint32(end+12,true),start=view.getUint32(end+16,true);
 if(count>30||start+length!==end)throw Error('Directorio ZIP inválido');
 let found=null,offset=start;
 for(let n=0;n<count;n++){
  if(offset+46>end||view.getUint32(offset,true)!==0x02014b50)throw Error('Entrada ZIP inválida');
  const flags=view.getUint16(offset+8,true),method=view.getUint16(offset+10,true),compressed=view.getUint32(offset+20,true),
   size=view.getUint32(offset+24,true),nameLength=view.getUint16(offset+28,true),extra=view.getUint16(offset+30,true),
   comment=view.getUint16(offset+32,true),local=view.getUint32(offset+42,true);
  if(offset+46+nameLength+extra+comment>end)throw Error('Nombre ZIP incompleto');
  const name=new TextDecoder().decode(zip.subarray(offset+46,offset+46+nameLength));
  if(name===NAME){
   if(found||flags&1||![0,8].includes(method)||size!==videoBytes||compressed>MAX||local+30>start||
      view.getUint32(local,true)!==0x04034b50)throw Error('Video ZIP inválido');
   const localNameLength=view.getUint16(local+26,true),localExtra=view.getUint16(local+28,true),data=local+30+localNameLength+localExtra;
   const localName=new TextDecoder().decode(zip.subarray(local+30,local+30+localNameLength));
   if(localName!==NAME||view.getUint16(local+8,true)!==method||data+compressed>start)throw Error('Video ZIP incoherente');
   found={method,data,compressed};
  }
  offset+=46+nameLength+extra+comment;
 }
 if(offset!==end||!found)throw Error('El paquete no contiene el MP4 esperado');
 const compressed=zip.subarray(found.data,found.data+found.compressed);
 let movie;
 if(found.method===0)movie=compressed;
 else{
  if(typeof DecompressionStream==='undefined')throw Error('Tu navegador no permite preparar el video. Usa la descarga o un navegador actualizado.');
  movie=await readBounded(new Blob([compressed]).stream().pipeThrough(new DecompressionStream('deflate-raw')),videoBytes,signal);
 }
 if(movie.length!==videoBytes||await hash(movie)!==videoHash)throw Error('La huella del video no coincide');
 return new Blob([movie],{type:'video/mp4'});
}
export function mountVideoPreview(root,row,{fetchArchive,documentRef=document,urlApi=URL}){
 const button=documentRef.createElement('button'),status=documentRef.createElement('p'),video=documentRef.createElement('video');
 button.type='button';button.textContent='Ver video en el panel';status.setAttribute('role','status');
 video.controls=true;video.preload='metadata';video.playsInline=true;video.hidden=true;video.style.width='100%';
 video.setAttribute('aria-label',row.title);root.append(button,status,video);
 let objectUrl=null,controller=null,disposed=false;
 button.addEventListener('click',async()=>{
  if(disposed||button.disabled)return;button.disabled=true;controller=new AbortController();
  try{
   status.textContent='Preparando el video para revisión…';
   const response=await fetchArchive('/api/youtube/exports/'+row.id+'/preview',{signal:controller.signal});
   if(!response.ok){const data=await response.json();throw Error(data.error||'Video no disponible');}
   const size=Number(response.headers.get('X-Archive-Bytes'));
   if(!Number.isSafeInteger(size)||size<1||size>MAX)throw Error('Tamaño de video inválido');
   const zip=await readBounded(response.body,size,controller.signal,n=>{status.textContent='Preparando video: '+Math.min(100,Math.floor(100*n/size))+' %';});
   if(zip.length!==size)throw Error('Archivo de video incompleto');
   const blob=await extractPreview(zip,{archiveHash:response.headers.get('X-Archive-SHA256'),videoHash:row.id,
    videoBytes:Number(response.headers.get('X-Video-Bytes')),signal:controller.signal});
   if(disposed)return;
   if(objectUrl)urlApi.revokeObjectURL(objectUrl);
   objectUrl=urlApi.createObjectURL(blob);video.src=objectUrl;video.hidden=false;button.hidden=true;
   status.textContent='Video listo para reproducir. Su revisión y aprobación siguen pendientes.';
  }catch(e){if(!disposed)status.textContent=e.name==='AbortError'?'Preparación cancelada.':e.message;}
  finally{if(!disposed)button.disabled=false;}
 });
 video.addEventListener('error',()=>{if(disposed)return;
  button.hidden=false;button.textContent='Volver a preparar el video';
  status.textContent='El navegador no pudo reproducir el MP4. Puedes volver a preparar el archivo sin regenerar el episodio.';
 });
 return ()=>{disposed=true;controller?.abort();video.pause();video.removeAttribute('src');video.load();if(objectUrl)urlApi.revokeObjectURL(objectUrl);};
}
