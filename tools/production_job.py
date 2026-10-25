"""Puente autenticado Worker → motor genérico; sin claves ni llamadas de IA."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
from urllib.error import HTTPError,URLError
from urllib.parse import urlsplit
from urllib.request import Request,build_opener

from tools.ai_clients import NoRedirects
from tools.episode_package import from_autonomous,validate_episode
from tools.episode_voice import atomic_json
from tools.push_market_radar import HOST

UUID=re.compile(r'[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}')


class ProductionClient:
    def __init__(self,*,base=None,token=None,opener=None):
        self.base=(os.getenv('API_BASE_URL','') if base is None else base).rstrip('/')
        self.token=os.getenv('RENDERER_TOKEN','') if token is None else token
        u=urlsplit(self.base)
        if u.scheme!='https' or u.hostname!=HOST or u.port or u.username or u.password or u.path or u.query or u.fragment:
            raise ValueError('Sólo Worker oficial de Factor de Gigantes')
        if not isinstance(self.token,str) or len(self.token)<24:raise ValueError('RENDERER_TOKEN requerido')
        self.opener=opener or build_opener(NoRedirects()).open

    def request(self,job_id,path,body=None):
        if not isinstance(job_id,str) or not UUID.fullmatch(job_id):raise ValueError('Trabajo inválido')
        if path not in ('episode','episode-report'):raise ValueError('Ruta de producción inválida')
        headers={'Authorization':'Bearer '+self.token,'User-Agent':'FactorDeGigantesProduction/1.0','Accept':'application/json'}
        if body is not None:headers['Content-Type']='application/json'
        request=Request(self.base+'/api/renderer/jobs/'+job_id+'/'+path,
            data=json.dumps(body,ensure_ascii=False).encode() if body is not None else None,headers=headers,
            method='POST' if body is not None else 'GET')
        try:
            with self.opener(request,timeout=30) as response:
                raw=response.read(260001)
                if len(raw)>260000:raise ValueError('Respuesta de producción fuera de límite')
                result=json.loads(raw)
        except HTTPError as exc:raise RuntimeError('Worker rechazó producción, HTTP '+str(exc.code)) from None
        except (URLError,TimeoutError):raise RuntimeError('Worker de producción no disponible') from None
        if not isinstance(result,dict) or result.get('ok') is not True or result.get('automatic_publication_allowed') is not False:
            raise ValueError('Respuesta de producción no confirmada')
        return result


def prepare_job(job_id,out,*,client=None):
    client=client or ProductionClient()
    context=client.request(job_id,'episode')
    if context.get('job_id')!=job_id or not re.fullmatch('[a-f0-9]{64}',context.get('approved_manifest_sha256','')):
        raise ValueError('Contexto de otro trabajo')
    package=from_autonomous(context['script'],context['research'])
    package['title']=context['manifest']['title'];package['central_question']=context['manifest']['angle']
    validate_episode(package)
    target=Path(out);target.mkdir(parents=True,exist_ok=True)
    atomic_json(target/'EPISODIO.json',package)
    atomic_json(target/'PIPELINE_CONTEXT.json',{'job_id':job_id,
        'approved_manifest_sha256':context['approved_manifest_sha256'],'automatic_publication_allowed':False})
    return package


def report_job(job_id,out,*,status,run_id,client=None):
    if status not in ('ready','failed') or not isinstance(run_id,str) or not re.fullmatch(r'\d{1,20}',run_id):
        raise ValueError('Estado o ejecución inválidos')
    payload={'status':status,'run_id':run_id}
    if status=='ready':
        folder=Path(out)
        report=json.loads((folder/'ESTADO_EXPORTACION.json').read_text(encoding='utf-8'))
        context=json.loads((folder/'PIPELINE_CONTEXT.json').read_text(encoding='utf-8'))
        if context['job_id']!=job_id or report.get('contains_narration') is not True or report.get('technical_gate_passed') is not True:
            raise ValueError('No reportar señal técnica ni otro trabajo como episodio narrado')
        report['approved_manifest_sha256']=context['approved_manifest_sha256']
        atomic_json(folder/'ESTADO_EXPORTACION.json',report)
        payload['export']=report
    return (client or ProductionClient()).request(job_id,'episode-report',payload)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('prepare','report'));parser.add_argument('job_id')
    parser.add_argument('--out',type=Path,required=True);parser.add_argument('--status',choices=('ready','failed'))
    a=parser.parse_args()
    if a.action=='prepare':prepare_job(a.job_id,a.out);print('PAQUETE_APROBADO_RECUPERADO:',a.job_id)
    else:
        if not a.status:parser.error('--status requerido')
        report_job(a.job_id,a.out,status=a.status,run_id=os.getenv('GITHUB_RUN_ID',''))
        print('EPISODIO_REPORTADO:',a.status)


if __name__=='__main__':main()
