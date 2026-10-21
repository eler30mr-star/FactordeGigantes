"""Anexar hechos financieros SEC estructurados a la investigación manual.

Usa los CIK candidatos que entregó EDGAR, no les concede identidad verificada.
Si SEC bloquea la consulta, deja un diagnóstico en el artefacto y NO inventa datos.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from tools.financial_facts import fetch_companyfacts, analyze_companyfacts


def probe_candidates(edgar_report, *, fetcher=None):
    records=edgar_report.get("entities",[])
    if not isinstance(records,list):
        raise ValueError("Formato EDGAR inválido")
    ciks=[]
    for record in records[:5]:
        cik=record.get("cik_candidate") if isinstance(record,dict) else None
        if isinstance(cik,str) and len(cik)==10 and cik.isdigit() and cik not in ciks:
            ciks.append(cik)
    # Solo la primera entidad candidata para controlar minutos y peticiones.
    result={
        "product":"Factor de Gigantes",
        "method":"sec_edgar_to_companyfacts_us_gaap",
        "candidate_ciks":ciks,
        "status":"no_identifier",
        "analysis":None,
        "facts_verified_automatically":0,
        "identity_verified":False,
        "copyright_verified":False,
        "publication_authorized":False
    }
    if not ciks:
        return result
    cik=ciks[0]
    try:
        raw,url=fetch_companyfacts(cik,fetcher=fetcher)
        result["analysis"]=analyze_companyfacts(raw,source_url=url)
        result["status"]="retrieved_structured_candidates"
    except (HTTPError,URLError,ValueError,OSError,TimeoutError,UnicodeError,json.JSONDecodeError) as exc:
        result["status"]="sec_unavailable_or_unreadable"
        result["error_type"]=type(exc).__name__
        if isinstance(exc,HTTPError):
            result["http_status"]=exc.code
    return result


def main():
    parser=argparse.ArgumentParser(description="Extraer datos XBRL preliminares de un CIK candidato")
    parser.add_argument("--edgar-report",type=Path,required=True)
    parser.add_argument("--out",type=Path,default=Path("dist/investigacion"))
    args=parser.parse_args()
    report=json.loads(args.edgar_report.read_text(encoding="utf-8"))
    out=probe_candidates(report)
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/"METRICAS_SEC_CANDIDATAS_NO_VERIFICADAS.json").write_text(
        json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("XBRL_PROBE:",out["status"],"observaciones:",
          (out["analysis"] or {}).get("observation_count",0),
          "hechos humanos verificados: 0",flush=True)


if __name__=="__main__":
    main()
