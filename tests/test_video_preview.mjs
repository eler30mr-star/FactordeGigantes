import test from 'node:test';
import assert from 'node:assert/strict';
import {deflateRawSync} from 'node:zlib';
import {videoPreview,PREVIEW_LIMIT} from '../src/video-preview.mjs';
import {extractPreview,mountVideoPreview} from '../public/video-preview.js';
import worker from '../src/worker.js';
const sha=async bytes=>Buffer.from(await crypto.subtle.digest('SHA-256',bytes)).toString('hex');
function archive(movie,{compressed=false,name='EPISODIO_PARA_REVISION.mp4'}={}){
 const file=Buffer.from(name),body=compressed?deflateRawSync(movie):movie;
 const local=Buffer.alloc(30);local.writeUInt32LE(0x04034b50);local.writeUInt16LE(compressed?8:0,8);
 local.writeUInt32LE(body.length,18);local.writeUInt32LE(movie.length,22);local.writeUInt16LE(file.length,26);
 const central=Buffer.alloc(46);central.writeUInt32LE(0x02014b50);central.writeUInt16LE(compressed?8:0,10);
 central.writeUInt32LE(body.length,20);central.writeUInt32LE(movie.length,24);central.writeUInt16LE(file.length,28);
 const end=Buffer.alloc(22);end.writeUInt32LE(0x06054b50);end.writeUInt16LE(1,8);end.writeUInt16LE(1,10);
 end.writeUInt32LE(46+file.length,12);end.writeUInt32LE(30+file.length+body.length,16);
 return Buffer.concat([local,file,body,central,file,end]);
}
async function fixture(){
 const movie=Buffer.from('ftyp-isom-test-movie'),zip=archive(movie),id=await sha(movie),digest=await sha(zip);
 const row={id,artifact_id:'456',source_run_id:'123',archive_sha256:digest,video_bytes:movie.length};
 const env={DB:{prepare(){return {bind(){return this;},async first(){return row;}};}},GITHUB_REPO:'eler30mr-star/FactordeGigantes',
  GITHUB_DISPATCH_TOKEN:'fake-github-preview-token-testing',ADMIN_TOKEN:'fake-admin-preview-token-testing',RENDERER_TOKEN:'fake-render-preview-token-testing'};
 const meta={id:456,name:'fdg-episode-narrated-review',expired:false,size_in_bytes:zip.length,workflow_run:{id:123},digest:'sha256:'+digest};
 return {env,row,meta,movie,zip,id,digest};
}

test('private preview streams exact archive, no credential on storage redirect',async()=>{
 const f=await fixture(),calls=[];
 const response=await videoPreview(f.env,f.id,{fetcher:async(url,options)=>{
  calls.push({url,options});
  if(url.endsWith('/zip'))return new Response(null,{status:302,headers:{Location:'https://results.blob.core.windows.net/artifact?sig=private'}});
  if(url.includes('api.github.com'))return Response.json(f.meta);
  assert.equal(options.headers,undefined);assert.equal(options.redirect,'manual');
  return new Response(f.zip,{headers:{'Content-Length':String(f.zip.length)}});
 }});
 assert.equal(response.status,200);assert.equal(calls.length,3);
 assert.equal(response.headers.get('X-Archive-SHA256'),f.digest);
 assert.equal(response.headers.get('Cache-Control'),'private, no-store');
 assert.equal(response.headers.has('Location'),false);
 assert.deepEqual(Buffer.from(await response.arrayBuffer()),f.zip);
});

test('expired, wrong digest, wrong run, oversized and hostile redirect cannot expose content',async()=>{
 const f=await fixture();
 for(const [change,status] of [[{expired:true},410],[{digest:'sha256:'+'b'.repeat(64)},409],
  [{workflow_run:{id:999}},409],[{size_in_bytes:PREVIEW_LIMIT+1},409]]){
  let calls=0;const r=await videoPreview(f.env,f.id,{fetcher:async()=>{calls++;return Response.json({...f.meta,...change});}});
  assert.equal(r.status,status);assert.equal(calls,1);
 }
 let calls=0;
 const r=await videoPreview(f.env,f.id,{fetcher:async url=>{
  calls++;return url.endsWith('/zip')?new Response(null,{status:302,headers:{Location:'https://evil.test/steal'}}):Response.json(f.meta);
 }});
 assert.equal(r.status,502);assert.equal(calls,2);
 assert.ok(!(await r.text()).includes(f.env.GITHUB_DISPATCH_TOKEN));
});

test('truncated/oversized stream errors before browser playback',async()=>{
 const f=await fixture();
 const r=await videoPreview(f.env,f.id,{fetcher:async url=>{
  if(url.endsWith('/zip'))return new Response(null,{status:302,headers:{Location:'https://results.blob.core.windows.net/artifact'}});
  if(url.includes('api.github.com'))return Response.json(f.meta);
  return new Response(f.zip.subarray(0,20));
 }});
 await assert.rejects(()=>r.arrayBuffer(),/Truncated/);
});

test('ZIP stored and deflated MP4 both yield seekable browser Blob after SHA verification',async()=>{
 const f=await fixture();
 for(const compressed of [false,true]){
  const zip=archive(f.movie,{compressed});const blob=await extractPreview(zip,{archiveHash:await sha(zip),videoHash:f.id,videoBytes:f.movie.length});
  assert.equal(blob.type,'video/mp4');assert.deepEqual(Buffer.from(await blob.arrayBuffer()),f.movie);
 }
});

test('wrong archive/video hashes, missing MP4 and malformed central directory are rejected',async()=>{
 const f=await fixture(),options={archiveHash:f.digest,videoHash:f.id,videoBytes:f.movie.length};
 await assert.rejects(()=>extractPreview(f.zip,{...options,archiveHash:'0'.repeat(64)}),/paquete/);
 await assert.rejects(()=>extractPreview(f.zip,{...options,videoHash:'0'.repeat(64)}),/video/);
 const wrong=archive(f.movie,{name:'other.mp4'});
 await assert.rejects(async()=>extractPreview(wrong,{...options,archiveHash:await sha(wrong)}));
 const bad=Buffer.from(f.zip);bad[bad.length-22]=0;
 await assert.rejects(async()=>extractPreview(bad,{...options,archiveHash:await sha(bad)}));
});

test('ADMIN only, GET only, missing export and invalid ID cannot initiate artifact fetch',async()=>{
 const f=await fixture();
 const req=(token,method='GET')=>new Request('https://factor.test/api/youtube/exports/'+f.id+'/preview',{method,headers:{Authorization:'Bearer '+token}});
 for(const token of ['',f.env.RENDERER_TOKEN])assert.equal((await worker.fetch(req(token),f.env)).status,401);
 assert.equal((await worker.fetch(req(f.env.ADMIN_TOKEN,'POST'),f.env)).status,405);
 assert.equal((await videoPreview(f.env,'../invalid')).status,400);
 const missing={...f.env,DB:{prepare(){return {bind(){return this;},async first(){return null;}};}}};
 assert.equal((await videoPreview(missing,f.id)).status,404);
});

class Node{
 constructor(){this.children=[];this.events={};this.style={};this.hidden=false;}
 append(...nodes){this.children.push(...nodes);}setAttribute(){}removeAttribute(){}pause(){}load(){}
 addEventListener(name,fn){this.events[name]=fn;}
}
test('panel mounts real video controls after preparation and releases Blob on refresh',async()=>{
 const f=await fixture(),root=new Node(),urls=[];let revoked='';
 const cleanup=mountVideoPreview(root,{id:f.id,title:'Video de prueba'},{documentRef:{createElement(){return new Node();}},
  urlApi:{createObjectURL(blob){urls.push(blob);return 'blob:local-preview';},revokeObjectURL(url){revoked=url;}},
  fetchArchive:async()=>new Response(f.zip,{headers:{'X-Archive-Bytes':String(f.zip.length),'X-Archive-SHA256':f.digest,'X-Video-Bytes':String(f.movie.length)}})});
 const [button,status,video]=root.children;assert.equal(video.controls,true);assert.equal(video.hidden,true);
 await button.events.click();assert.equal(video.src,'blob:local-preview');assert.equal(video.hidden,false);
 assert.match(status.textContent,/pendientes/);assert.equal(urls.length,1);cleanup();assert.equal(revoked,'blob:local-preview');
});

test('decoder errors allow preparing the same file again and release the previous Blob',async()=>{
 const f=await fixture(),root=new Node(),revoked=[];let created=0,downloads=0;
 const dispose=mountVideoPreview(root,{id:f.id,title:'Muestra de reproducción'},{documentRef:{createElement(){return new Node();}},
  urlApi:{createObjectURL(){return 'blob:preview-'+(++created);},revokeObjectURL(url){revoked.push(url);}},
  fetchArchive:async()=>{downloads++;return new Response(f.zip,{headers:{'X-Archive-Bytes':String(f.zip.length),'X-Archive-SHA256':f.digest,'X-Video-Bytes':String(f.movie.length)}});}});
 const [button,status,video]=root.children;
 await button.events.click();assert.equal(button.hidden,true);
 video.events.error();assert.equal(button.hidden,false);assert.match(status.textContent,/sin regenerar/);
 await button.events.click();assert.equal(downloads,2);assert.equal(video.src,'blob:preview-2');assert.deepEqual(revoked,['blob:preview-1']);
 dispose();assert.deepEqual(revoked,['blob:preview-1','blob:preview-2']);
 const old=status.textContent;video.events.error();assert.equal(status.textContent,old);
});
