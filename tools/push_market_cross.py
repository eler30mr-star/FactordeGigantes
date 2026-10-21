"""Persistir coincidencias empresa-noticia con identidad OIDC de GitHub Actions."""
import argparse
import json
import os
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError
from tools.push_market_radar import HOST,github_oidc_token

def upload_cross(report,*,base_url,token,opener=urlopen):
    url=urlsplit(base_url.strip().rstrip("/"))
    if url.scheme!="https" or url.hostname!=HOST or url.username or url.password or \
       url.port or url.path not in ("","/") or url.query or url.fragment:
        raise ValueError("Destino Factor inválido")
    if not isinstance(token,str) or token.count(".")!=2 or len(token)<40:
        raise ValueError("Identidad OIDC requerida")
    if not isinstance(report,dict) or report.get("provider")!="wikimedia_rss_headline_join_v1" or \
       report.get("source_article_verified") is not False or report.get("ready_for_youtube") is not False:
        raise ValueError("Cruce no verificable")
    body=json.dumps(report,ensure_ascii=False,separators=(",",":")).encode("utf-8")
    if len(body)>250000:raise ValueError("Límite de mensaje superado")
    req=Request(base_url.strip().rstrip("/")+"/api/market/cross/ingest",data=body,method="POST",
        headers={"Authorization":"Bearer "+token,"Content-Type":"application/json",
                 "Accept":"application/json","User-Agent":"FactorDeGigantes-MarketJoin/1.0"})
    try:
        with opener(req,timeout=25) as resp:
            data=json.load(resp)
            if resp.status!=201 or data.get("stored_in")!="d1" or \
               data.get("automatic_publication_allowed") is not False:
                raise RuntimeError("Cruce no confirmado en D1")
            return data
    except HTTPError as err:
        raise RuntimeError("Ingesta cruzada HTTP "+str(err.code)) from None
    except (URLError,TimeoutError) as err:
        raise RuntimeError("Fallo de comunicación: "+type(err).__name__) from None

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    a=p.parse_args()
    result=upload_cross(json.loads(a.input.read_text(encoding="utf-8")),
        base_url=os.getenv("API_BASE_URL",""),token=github_oidc_token())
    print("CRUCES_D1_CONFIRMADOS:",result["matched_pairs"],
          "FUENTES_VERIFICADAS:",result["source_article_verified"])

if __name__=="__main__":main()
