"""Registro y subida privada mediante broker; nunca recibe credenciales Google."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import zipfile
from urllib.error import HTTPError,URLError
from urllib.parse import urlsplit
from urllib.request import Request,build_opener
from tools.ai_clients import NoRedirects,ProviderError
from tools.episode_package import digest,validate_episode
from tools.approved_voice import hash_file
from tools.push_market_radar import HOST

SHA=re.compile(r'[a-f0-9]{64}')
UUID=re.compile(r'[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}')

class DeliveryClient:
    def __init__(self,*,base=None,token=None,opener=None):
        self.base=(os.getenv('API_BASE_URL','') if base is None else base).rstrip('/')
        self.token=os.getenv('RENDERER_TOKEN','') if token is None else token
        u=urlsplit(self.base)
        if u.scheme!='https' or u.hostname!=HOST or u.port or u.username or u.password or u.path or u.query or u.fragment:
            raise ValueError('Sólo Worker oficial')
        if not isinstance(self.token,str) or len(self.token)<24:raise ValueError('RENDERER_TOKEN requerido')
        self.opener=opener or build_opener(NoRedirects()).open

    def request(self,path,*,method='GET',body=None,data=None,headers=None):
        if not re.fullmatch(r'exports|uploads/[a-f0-9-]{36}(?:/(?:start|chunk|report))?',path):raise ValueError('Ruta inválida')
        h={'Authorization':'Bearer '+self.token,'Accept':'application/json','User-Agent':'FactorDeGigantesDelivery/1.0',**(headers or {})}
        if body is not None:h['Content-Type']='application/json';data=json.dumps(body,ensure_ascii=False).encode()
        req=Request(self.base+'/api/renderer/youtube/'+path,data=data,method=method,headers=h)
        try:
            with self.opener(req,timeout=60) as r:raw=r.read(600001)
        except HTTPError as exc:raise RuntimeError('Broker rechazó operación HTTP '+str(exc.code)) from None
        except (URLError,TimeoutError,ProviderError):raise RuntimeError('Broker de subida no disponible') from None
        if len(raw)>600000:raise ValueError('Respuesta fuera de límite')
        result=json.loads(raw)
        if not isinstance(result,dict) or result.get('ok') is not True or result.get('automatic_publication_allowed') is not False:
            raise ValueError('Operación no confirmada')
        return result

def gh_json(path):
    r=subprocess.run(['gh','api','repos/eler30mr-star/FactordeGigantes/'+path],capture_output=True,timeout=40)
    if r.returncode:raise RuntimeError('GitHub no confirmó la consulta')
    return json.loads(r.stdout)

def download_bundle(run_id,target,*,artifact_id=None,archive_sha=None,allow_missing=False):
    if not isinstance(run_id,str) or not re.fullmatch(r'[1-9]\d{0,15}',run_id):raise ValueError('Run inválido')
    run=gh_json('actions/runs/'+run_id)
    if run.get('path')!='.github/workflows/development-episode.yml' or run.get('head_branch')!='main' or run.get('event')!='workflow_dispatch' or run.get('conclusion')!='success':
        raise ValueError('Sólo exportación canónica terminada de main')
    artifacts=gh_json('actions/runs/'+run_id+'/artifacts?per_page=100')['artifacts']
    candidates=[a for a in artifacts if a['name']=='fdg-episode-narrated-review' and not a['expired'] and (artifact_id is None or str(a['id'])==artifact_id)]
    if not candidates and allow_missing:return None,None
    if len(candidates)!=1:raise ValueError('Artefacto narrado no disponible')
    a=candidates[0];expected=a['digest'].removeprefix('sha256:')
    if not SHA.fullmatch(expected) or (archive_sha is not None and archive_sha!=expected) or not 1<=a['size_in_bytes']<=1_000_000_000:
        raise ValueError('Huella de artefacto inválida')
    target=Path(target);target.mkdir(parents=True,exist_ok=True);archive=target/'review.zip'
    with archive.open('wb') as out:
        result=subprocess.run(['gh','api','repos/eler30mr-star/FactordeGigantes/actions/artifacts/'+str(a['id'])+'/zip'],stdout=out,stderr=subprocess.PIPE,timeout=240)
    if result.returncode or hash_file(archive)!=expected:raise ValueError('Descarga GitHub no coincide con su huella')
    return archive,a

def extract_bundle(archive,target):
    target=Path(target);allowed={'EPISODIO.json','ESTADO_EXPORTACION.json','EPISODIO_PARA_REVISION.mp4','QA_AUDIOVISUAL.json'}
    with zipfile.ZipFile(archive) as z:
        for name in allowed:
            info=z.getinfo(name)
            if info.file_size>2_000_000_000 or (target/name).is_symlink():raise ValueError('Archivo fuera de límite')
            if name.endswith('.json') and info.file_size>250000:raise ValueError('JSON fuera de límite')
            z.extract(name,target)
    report=json.loads((target/'ESTADO_EXPORTACION.json').read_text())
    episode=json.loads((target/'EPISODIO.json').read_text())
    qa=json.loads((target/'QA_AUDIOVISUAL.json').read_text())
    validate_episode(episode)
    movie=target/'EPISODIO_PARA_REVISION.mp4'
    if report.get('contains_narration') is not True or report.get('technical_gate_passed') is not True or qa.get('technical_gate_passed') is not True or qa.get('failures'):
        raise ValueError('Sólo video narrado con QA aprobado')
    if report['episode_sha256']!=digest(episode) or report['sha256']!=hash_file(movie):raise ValueError('Exportación alterada')
    return episode,report,movie

def register(run_id,out,*,client=None,allow_missing=False):
    archive,a=download_bundle(run_id,out,allow_missing=allow_missing)
    if archive is None:return {'ok':True,'skipped':True,'automatic_publication_allowed':False}
    p,r,movie=extract_bundle(archive,out)
    canonical=json.dumps(p,ensure_ascii=False,sort_keys=True,separators=(',',':'))
    return (client or DeliveryClient()).request('exports',method='POST',body={'report':r,'episode_canonical_json':canonical,
        'source_run_id':run_id,'artifact_id':str(a['id']),'archive_sha256':hash_file(archive),'video_bytes':movie.stat().st_size})

def transfer(request_id,out,*,client=None,sleep=time.sleep):
    if not UUID.fullmatch(request_id):raise ValueError('Solicitud inválida')
    client=client or DeliveryClient();path='uploads/'+request_id
    context=client.request(path)
    if context['state']=='uploaded':return context
    archive,_=download_bundle(context['source_run_id'],out,artifact_id=context['artifact_id'],archive_sha=context['archive_sha256'])
    _,r,movie=extract_bundle(archive,out)
    if r['sha256']!=context['export_id'] or movie.stat().st_size!=context['video_bytes']:raise ValueError('Otro archivo fue aprobado')
    client.request(path+'/start',method='POST',body={'sha256':context['export_id'],'bytes':context['video_bytes']})
    size=movie.stat().st_size;offset=None;errors=0;done=None
    with movie.open('rb') as f:
        while done is None:
            try:
                if offset is None:
                    result=client.request(path+'/chunk',method='PUT',data=b'',headers={'Content-Range':f'bytes */{size}','Content-Length':'0'})
                else:
                    if not 0<=offset<size:raise ValueError('Google no confirmó la finalización')
                    f.seek(offset);data=f.read(4*1024*1024)
                    result=client.request(path+'/chunk',method='PUT',data=data,headers={'Content-Type':'video/mp4',
                        'Content-Range':f'bytes {offset}-{offset+len(data)-1}/{size}','Content-Length':str(len(data))})
                if result.get('complete') is True:done=result['video_id'];break
                next_offset=result.get('next_offset')
                if type(next_offset) is not int or not 0<=next_offset<=size or (offset is not None and next_offset<=offset):raise ValueError('Rango no confirmado')
                offset=next_offset;errors=0
            except RuntimeError:
                errors+=1
                if errors>4:raise
                offset=None;sleep(2**errors)
    return client.request(path+'/report',method='POST',body={'video_id':done})

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('register','upload'));p.add_argument('id');p.add_argument('--out',type=Path,required=True)
    p.add_argument('--if-narrated',action='store_true')
    a=p.parse_args()
    result=register(a.id,a.out,allow_missing=a.if_narrated) if a.action=='register' else transfer(a.id,a.out)
    if result.get('skipped'):print('SIN_EXPORTACION_NARRADA_PARA_REGISTRAR');return
    print('EXPORTACION_REGISTRADA_PARA_REVISION' if a.action=='register' else 'SUBIDA_PRIVADA_CONFIRMADA',result.get('export',{}).get('id',''),flush=True)
if __name__=='__main__':main()
