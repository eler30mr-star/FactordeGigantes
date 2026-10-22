"""Puente de nuevas entidades/decisiones D1 bajo OIDC de GitHub Actions.

Cada endpoint está fijado y el JWT nunca se imprime. No hay publicación YouTube.
"""
from __future__ import annotations
import argparse,json,os
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from urllib.parse import urlsplit
from tools.push_market_radar import HOST,github_oidc_token

PATHS={"entities":"/api/market/entities/ingest","official":"/api/market/official/ingest","pdf":"/api/market/pdf/ingest","research":"/api/market/research/ingest","assess":"/api/market/assess/run"}

def post_report(*,mode,base_url,token,report=None,opener=urlopen):
    if mode not in PATHS:raise ValueError("Operación no permitida")
    base=base_url.strip().rstrip("/") if isinstance(base_url,str) else ""
    u=urlsplit(base)
    if u.scheme!="https" or u.hostname!=HOST or u.path not in ("","/") or \
       u.username or u.password or u.port or u.query or u.fragment:
        raise ValueError("Solo Worker Factor permitido")
    if not isinstance(token,str) or len(token)<40 or token.count(".")!=2:
        raise ValueError("GitHub OIDC ausente")
    if mode in ("entities","official","pdf","research"):
        expected={"entities":"wikidata_news_company_resolution_v1","official":"wikidata_p856_safe_official_fetch_v1","pdf":"official_pdf_evidence_v1","research":"market_official_and_pdf_v1"}[mode]
        if mode=="research":
            denied=(report.get("ready_for_script") is not False or
                    report.get("publication_authorized") is not False or
                    report.get("facts_verified_automatically") != 0)
            matches_provider=report.get("source_provider")==expected
        else:
            denied=((report.get("research_ready") is not False or
                      report.get("publication_authorized") is not False) if mode=="pdf"
                     else (report.get("market_study_complete") is not False or
                           report.get("ready_for_youtube") is not False))
            matches_provider=report.get("provider")==expected
        if not isinstance(report,dict) or not matches_provider or denied:
            raise ValueError("Evidencia sin procedencia")
        body=json.dumps(report,ensure_ascii=False,separators=(",",":")).encode("utf-8")
        if len(body)>250000:raise ValueError("Reporte fuera de límite")
    else:
        if report is not None:raise ValueError("Evaluación se construye exclusivamente desde D1")
        body=b"{}"
    req=Request(base+PATHS[mode],method="POST",data=body,headers={
       "Authorization":"Bearer "+token,"Content-Type":"application/json",
       "Accept":"application/json","User-Agent":"FactorDeGigantes-DataGate/1.0"})
    try:
        with opener(req,timeout=35) as response:
            result=json.load(response)
            if response.status!=201 or result.get("stored_in")!="d1" or \
               result.get("automatic_publication_allowed") is not False or \
               result.get("ok") is not True:
                raise RuntimeError("D1 no confirmó inserción sin publicación")
            if mode=="assess" and (result.get("selected_wikidata_id") is not None or
                                     result.get("qualified_count")!=0):
                raise RuntimeError("La selección requiere fuentes y una puerta editorial independiente")
            return result
    except HTTPError as exc:
        raise RuntimeError("Ingreso D1 "+mode+" falló HTTP "+str(exc.code)) from None
    except (URLError,TimeoutError) as exc:
        raise RuntimeError("Comunicación D1 "+mode+" falló: "+type(exc).__name__) from None

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=list(PATHS),required=True)
    p.add_argument("--input",type=Path)
    a=p.parse_args()
    if a.mode in ("entities","official","pdf","research") and not a.input:p.error("Se requiere --input")
    data=json.loads(a.input.read_text(encoding="utf-8")) if a.mode in ("entities","official","pdf","research") else None
    result=post_report(mode=a.mode,report=data,
      base_url=os.getenv("API_BASE_URL",""),token=github_oidc_token())
    if a.mode=="assess":
        print("EVALUACIONES_D1:",result["candidates_evaluated"],
          "SELECCION_AUTOMATICA:",result["selected_wikidata_id"],
          "DOCUMENTALES_AUTORIZADOS:",result["automatic_publication_allowed"])
    elif a.mode=="research":
        print("EXPEDIENTES_IA_D1:",result["run_id"],"ESTADO:",result["status"],
          "EVIDENCIAS:",result["evidence_count"],
          "AFIRMACIONES_CANDIDATAS:",result["candidate_claim_count"],
          "HECHOS_VERIFICADOS:",result["verified_claim_count"])
    elif a.mode=="pdf":
        print("PDF_PERSISTIDOS_D1:",result["documents"],
          "CITAS_LOCALIZADAS:",result["fragments"],
          "HECHOS_VERIFICADOS:",result["verified_claim_count"])
    elif a.mode=="official":
        print("SITIOS_CANDIDATOS_D1:",result["pages_attempted"],
          "SITIOS_LEIBLES:",result["pages_readable"],
          "HECHOS_VERIFICADOS:",result["primary_facts_verified"])
    else:
        print("NUEVAS_ENTIDADES_D1:",result["candidates_seen"],
          "FUENTES_PRIMARIAS_VERIFICADAS:",result["primary_sources_verified"])

if __name__=="__main__":main()
