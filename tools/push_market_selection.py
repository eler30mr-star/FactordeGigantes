"""Solicita priorización desde observaciones D1; guarda la identidad elegida.

El runner no proporciona puntuaciones ni autoriza guion/video. Usa el mismo
OIDC efímero del radar, sin credencial administrativa ni clave YouTube aquí.
"""
import argparse,json,os
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from urllib.parse import urlsplit
from tools.push_market_radar import HOST,github_oidc_token


def select_research(base_url,token,*,opener=urlopen):
    u=urlsplit(base_url)
    if (u.scheme!='https' or u.hostname!=HOST or u.path not in ('','/') or
        u.username or u.password or u.port or u.query or u.fragment):
        raise ValueError('Solo Worker de Factor permitido')
    if not isinstance(token,str) or token.count('.')!=2 or len(token)<40:
        raise ValueError('OIDC inválido')
    req=Request(base_url.rstrip('/')+'/api/market/research-selection/run',
        method='POST',data=b'{}',headers={'Authorization':'Bearer '+token,
            'Content-Type':'application/json','User-Agent':'FactorDeGigantes-ResearchSelection/1.0'})
    try:
        with opener(req,timeout=35) as response:
            body=response.read(250001)
            if len(body)>250000:raise ValueError('Selección fuera de presupuesto')
            out=json.loads(body)
            if (response.status!=201 or out.get('ok') is not True or
                out.get('stored_in')!='d1' or out.get('automatic_publication_allowed') is not False or
                out.get('script_authorized') is not False):
                raise ValueError('Selección sin confirmación de D1')
            qid=out.get('selected_wikidata_id')
            queue=out.get('research_queue')
            if qid is not None:
                import re
                if (not re.fullmatch(r'Q[1-9][0-9]*',qid) or
                    not isinstance(queue,dict) or queue.get('wikidata_id')!=qid or
                    queue.get('state') not in {'awaiting_sources','researching','review'}):
                    raise ValueError('Identidad de cola inconsistente')
            return out
    except HTTPError as exc:
        raise RuntimeError('Selección D1 HTTP '+str(exc.code)) from None
    except (URLError,TimeoutError):
        raise RuntimeError('No se pudo confirmar selección D1') from None


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    out=select_research(os.getenv('API_BASE_URL',''),github_oidc_token())
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print('SELECCION_INVESTIGACION_D1:',out['selected_wikidata_id'],
          'COLA:',(out.get('research_queue') or {}).get('id'),
          'CANDIDATOS_COMPARABLES:',out['qualified_count'],
          'GUION_AUTORIZADO:',out['script_authorized'])

if __name__=='__main__':main()
