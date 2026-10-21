"""Persistencia autenticada de titulares RSS en la D1 del radar."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from urllib.error import HTTPError,URLError
from urllib.parse import urlsplit
from urllib.request import Request,urlopen
from tools.push_market_radar import github_oidc_token, HOST


def upload_news(report, *, base_url, token, opener=urlopen):
    base=base_url.strip().rstrip("/") if isinstance(base_url,str) else ""
    u=urlsplit(base)
    if (u.scheme!="https" or u.hostname!=HOST or u.port or u.username or u.password or
            u.path not in ("","/") or u.query or u.fragment):
        raise ValueError("API no corresponde a Factor")
    if not isinstance(token,str) or len(token)<40 or token.count(".")!=2:
        raise ValueError("Identidad OIDC no disponible")
    if (not isinstance(report,dict) or report.get("provider")!="google_news_rss" or
            report.get("source_verification_complete") is not False or
            report.get("ready_for_youtube") is not False):
        raise ValueError("Reporte RSS inválido")
    payload=json.dumps(report,ensure_ascii=False,separators=(",",":")).encode("utf-8")
    if len(payload)>250000: raise ValueError("Reporte excede el máximo de Worker")
    req=Request(base+"/api/market/news/ingest",method="POST",data=payload,headers={
        "Authorization":"Bearer "+token, "Content-Type":"application/json",
        "Accept":"application/json", "User-Agent":"FactorDeGigantes-NewsRadar/1.0"
    })
    try:
        with opener(req,timeout=25) as resp:
            body=json.load(resp)
            if resp.status!=201 or body.get("stored_in")!="d1" or body.get("market_study_complete") is not False:
                raise RuntimeError("D1 no confirmó la escritura de noticias")
            return body
    except HTTPError as e:
        raise RuntimeError("Worker noticias rechazó ingesta HTTP "+str(e.code)) from None
    except (URLError,TimeoutError) as e:
        raise RuntimeError("Worker noticias inaccesible: "+type(e).__name__) from None


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    args=p.parse_args()
    report=json.loads(args.input.read_text(encoding="utf-8"))
    result=upload_news(report,base_url=os.getenv("API_BASE_URL",""),token=github_oidc_token())
    print("NOTICIAS_D1_CONFIRMED:",result["run_id"],"TITULARES:",result["leads_seen"],
          "HECHOS_VERIFICADOS:",result["source_verification_complete"])


if __name__=="__main__":
    main()
