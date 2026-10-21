"""Envío OIDC de evidencia pública YouTube a D1, sin token compartido."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from tools.push_market_radar import github_oidc_token,HOST

def upload_youtube(report, *, base_url, token, opener=urlopen):
    u=urlsplit(base_url.strip().rstrip("/"))
    if u.scheme!="https" or u.hostname!=HOST or u.port or u.username or u.password \
            or u.path not in ("","/") or u.query or u.fragment:
        raise ValueError("Solo Worker Factor autorizado")
    if not isinstance(token,str) or token.count(".")!=2 or len(token)<40:
        raise ValueError("Identidad GitHub OIDC inválida")
    if not isinstance(report,dict) or report.get("provider")!="youtube_data_api_v3" or \
            report.get("market_study_complete") is not False or \
            report.get("automatic_publication_allowed") is not False:
        raise ValueError("Reporte YouTube no preliminar")
    payload=json.dumps(report,ensure_ascii=False,separators=(",",":")).encode("utf-8")
    if len(payload)>250000: raise ValueError("Payload fuera del límite Worker")
    req=Request(base_url.strip().rstrip("/")+"/api/market/youtube/ingest",data=payload,
        method="POST",headers={"Authorization":"Bearer "+token,
          "Content-Type":"application/json","Accept":"application/json",
          "User-Agent":"FactorDeGigantes-YouTubeMarket/1.0"})
    try:
        with opener(req,timeout=25) as response:
            result=json.load(response)
            if response.status!=201 or result.get("stored_in")!="d1" or \
                result.get("automatic_publication_allowed") is not False:
                raise RuntimeError("API no confirmó evidencia YouTube guardada")
            return result
    except HTTPError as e:
        # Nunca filtrar cuerpo de error ni URL API con clave a los logs.
        raise RuntimeError("API YouTube D1 respondió HTTP "+str(e.code)) from None
    except (URLError,TimeoutError) as e:
        raise RuntimeError("Conexión de guardado falló: "+type(e).__name__) from None

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    a=p.parse_args()
    report=json.loads(a.input.read_text(encoding="utf-8"))
    result=upload_youtube(report,base_url=os.getenv("API_BASE_URL",""),token=github_oidc_token())
    print("YOUTUBE_D1_PERSISTIDO:",result["run_id"],
        "CONSULTAS:",result["queries_seen"],"VIDEOS:",result["video_observations"],
        "PUBLICACION:",result["automatic_publication_allowed"])

if __name__=="__main__":
    main()
