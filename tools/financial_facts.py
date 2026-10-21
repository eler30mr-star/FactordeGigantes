"""Lectura acotada de hechos XBRL públicos SEC y comparación financiera rigurosa.

La SEC publica hechos estructurados con unidades/periodos; una variación entre
presentaciones NO implica falsedad, fraude, error o contradicción verificada.
Solo candidatos a revisión editorial. Sin API pagada, sin publicar ni renderizar.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from urllib.request import Request, HTTPSHandler, build_opener
import ssl

from tools.edgar_discovery import CIK
from tools.research_engine import validate_url, check_public_dns, PublicRedirects, USER_AGENT

# Identificadores explícitos. Sin inferencia de métricas similares de distintos tags.
ALLOWED_TAGS = {
    "Revenues",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "RevenueFromContractWithCustomerIncludingAssessedTax",
    "NetIncomeLoss",
    "Assets",
    "Liabilities",
    "OperatingIncomeLoss",
    "CashAndCashEquivalentsAtCarryingValue",
}
SUPPORTED_FORMS={"10-K", "10-K/A", "10-Q", "10-Q/A", "20-F", "20-F/A", "40-F", "40-F/A"}
MAX_JSON_BYTES=9_000_000
MAX_FACTS_PER_TAG=1000
MAX_OUTPUT_FACTS=180
ACC_NUM=re.compile(r"^\d{10}-\d{2}-\d{6}$")
DATE=re.compile(r"^\d{4}-\d{2}-\d{2}$")
USD_UNITS={"USD"}
NUMBER_PATTERN=re.compile(r"^-?(?:0|[1-9]\d{0,18})(?:\.\d{1,8})?$")


def safe_day(value):
    if not isinstance(value,str) or not DATE.fullmatch(value):
        raise ValueError("Fecha XBRL incorrecta")
    return date.fromisoformat(value)


def decimal_value(value):
    if isinstance(value,bool) or not isinstance(value,(int,float,str)):
        raise ValueError("Valor financiero inválido")
    text=str(value)
    if len(text)>28 or not NUMBER_PATTERN.fullmatch(text):
        raise ValueError("Número XBRL inseguro o con escala inesperada")
    val=Decimal(text)
    if not val.is_finite():
        raise ValueError("Valor no finito")
    return val


def fetch_companyfacts(cik, fetcher=None):
    """Descarga SEC JSON hasta 9MB, HTTPS/DNS público, sin redirects ajenos.

    Un 403/429 no se elude con proxies; se registra como indisponibilidad.
    """
    if not isinstance(cik,str) or not CIK.fullmatch(cik):
        raise ValueError("CIK incorrecto")
    cik=cik.zfill(10)
    url="https://data.sec.gov/api/xbrl/companyfacts/CIK"+cik+".json"
    if fetcher is None:
        validate_url(url)
        check_public_dns(urlsplit(url).hostname)
        opener=build_opener(HTTPSHandler(context=ssl.create_default_context()),PublicRedirects())
        request=Request(url,headers={
            "User-Agent":USER_AGENT,
            "Accept":"application/json",
            "Accept-Encoding":"identity"
        })
        with opener.open(request,timeout=18) as response:
            resolved=response.geturl()
            mime=response.headers.get("Content-Type","").lower()
            length=response.headers.get("Content-Length")
            if length and (not length.isdigit() or int(length)>MAX_JSON_BYTES):
                raise ValueError("JSON SEC supera límite declarado")
            raw=response.read(MAX_JSON_BYTES+1)
    else:
        raw,resolved,mime=fetcher(url)
    if resolved!=url or not isinstance(mime,str) or "json" not in mime.lower() or not isinstance(raw,bytes) or len(raw)>MAX_JSON_BYTES:
        raise ValueError("Respuesta SEC XBRL inesperada o demasiado grande")
    return raw, url


def extract_observations(data, *, document_url, limit=MAX_OUTPUT_FACTS):
    """Extraer hechos solo cuando vienen explícitamente de us-gaap y un filing SEC."""
    if not isinstance(data,dict):
        raise ValueError("Companyfacts debe ser JSON objeto")
    cik=data.get("cik")
    if isinstance(cik,bool) or not isinstance(cik,int) or not 0<cik<=9_999_999_999:
        raise ValueError("CIK no identificado en companyfacts")
    if not document_url.endswith(f"CIK{cik:010d}.json"):
        raise ValueError("CIK de URL y cuerpo no coinciden")
    company=str(data.get("entityName",""))[:120].strip()
    us=data.get("facts",{}).get("us-gaap",{})
    if not isinstance(us,dict):
        raise ValueError("Faltan hechos de taxonomía us-gaap")
    observations=[]
    for tag in sorted(ALLOWED_TAGS):
        fact=us.get(tag)
        if not isinstance(fact,dict) or not isinstance(fact.get("units"),dict):
            continue
        for unit,items in fact["units"].items():
            if unit not in USD_UNITS or not isinstance(items,list):
                continue
            for item in items[:MAX_FACTS_PER_TAG]:
                if not isinstance(item,dict) or item.get("form") not in SUPPORTED_FORMS:
                    continue
                if not ACC_NUM.fullmatch(str(item.get("accn",""))):
                    continue
                try:
                    end=safe_day(item.get("end"))
                    filed=safe_day(item.get("filed"))
                    start=safe_day(item["start"]) if item.get("start") else None
                    value=decimal_value(item.get("val"))
                except (ValueError,InvalidOperation,KeyError):
                    continue
                if start and start>end:
                    continue
                # If instant fact (assets/liabilities) has no start, keep it as instant.
                if not start and tag not in {
                    "Assets","Liabilities","CashAndCashEquivalentsAtCarryingValue"
                }:
                    continue
                if start and tag in {
                    "Assets","Liabilities","CashAndCashEquivalentsAtCarryingValue"
                }:
                    continue
                fy=item.get("fy")
                fp=item.get("fp")
                if isinstance(fy,bool) or not isinstance(fy,int) or not 1900<=fy<=2100:
                    continue
                if fp not in ("FY","Q1","Q2","Q3","Q4"):
                    continue
                observations.append({
                    "entity_cik":f"{cik:010d}",
                    "entity_name_claimed":company,
                    "taxonomy":"us-gaap",
                    "metric":tag, "unit":unit, "value":str(value),
                    "period_kind":"duration" if start else "instant",
                    "start":start.isoformat() if start else None,
                    "end":end.isoformat(), "fiscal_year":fy,
                    "fiscal_period":fp,"form":item["form"],
                    "accession":item["accn"], "filed":filed.isoformat(),
                    "source_url":document_url,
                    "entity_identity_verified":False,"human_verified":False
                })
    # Newest SEC filing first and deterministic output.
    observations.sort(key=lambda x:(x["filed"],x["accession"],x["metric"]),reverse=True)
    return observations[:max(1,min(MAX_OUTPUT_FACTS,int(limit)))]


def compare_observations(observations):
    """Compare *only* same metric/unit/entity/exact start/end/period kind.

    Refilings and different fiscal-year labels may point to same actual dates;
    grouping compares exact dates rather than a guessed calendar-year mapping.
    """
    if not isinstance(observations,list) or len(observations)>MAX_OUTPUT_FACTS:
        raise ValueError("Cantidad de hechos supera el límite")
    groups=defaultdict(list)
    for obs in observations:
        if not isinstance(obs,dict) or obs.get("taxonomy")!="us-gaap":
            raise ValueError("Fuente XBRL inválida")
        metric=obs.get("metric")
        if metric not in ALLOWED_TAGS or obs.get("unit") not in USD_UNITS:
            raise ValueError("Métrica o unidad no homologada")
        entity=obs.get("entity_cik")
        if not isinstance(entity,str) or not re.fullmatch(r"\d{10}",entity):
            raise ValueError("Identificador de empresa faltante")
        end=safe_day(obs.get("end")).isoformat()
        start=obs.get("start")
        if start is not None:
            start=safe_day(start).isoformat()
        kind="duration" if start else "instant"
        if kind!=obs.get("period_kind"):
            raise ValueError("Clase de periodo incoherente")
        if start and start>end:
            raise ValueError("Periodo invertido")
        value=decimal_value(obs.get("value"))
        if not isinstance(obs.get("accession"),str) or not ACC_NUM.fullmatch(obs["accession"]):
            raise ValueError("Falta acceso SEC")
        src=obs.get("source_url")
        if not isinstance(src,str) or not src.startswith("https://data.sec.gov/api/xbrl/companyfacts/CIK"):
            raise ValueError("Fuente SEC no identificada")
        validate_url(src)
        key=(entity,metric,obs["unit"],kind,start,end)
        groups[key].append((obs,value))
    comparisons=[]
    for key,entries in sorted(groups.items()):
        if len(entries)<2:
            continue
        # No llamar contradicción a observaciones idénticas repetidas.
        unique_values=sorted({x[1] for x in entries})
        if len(unique_values)<2:
            continue
        comparisons.append({
            "entity_cik":key[0], "metric":key[1], "unit":key[2],
            "period_kind":key[3],"start":key[4],"end":key[5],
            "distinct_values":[str(v) for v in unique_values],
            "filings":[{"accession":o["accession"],"filed":o["filed"],
                        "value":str(value),"form":o["form"]}
                       for o,value in entries[:8]],
            "classification":"same_period_different_reported_values_review_required",
            "possible_restatement_or_scope_difference":True,
            "proven_contradiction":False,"fraud_claim":False,
            "human_review_required":True
        })
    return {
        "comparisons":comparisons,
        "same_period_differences":len(comparisons),
        "confirmed_contradictions":0,
        "facts_human_verified":0,
        "publication_authorized":False,
        "note":"Diferencias XBRL del mismo periodo pueden reflejar reexpresión, presentación o revisión; no prueban error ni fraude."
    }


def analyze_companyfacts(raw, *, source_url):
    if len(raw)>MAX_JSON_BYTES:
        raise ValueError("Datos XBRL exceden presupuesto")
    obj=json.loads(raw.decode("utf-8"))
    observations=extract_observations(obj,document_url=source_url)
    return {
        "product":"Factor de Gigantes",
        "entity_cik":f"{obj['cik']:010d}",
        "entity_name_reported":str(obj.get("entityName",""))[:120],
        "source_url":source_url,
        "content_sha256":hashlib.sha256(raw).hexdigest(),
        "observation_count":len(observations),
        "observations":observations,
        "comparison":compare_observations(observations),
        "rights_verified":False,"facts_automatically_verified":0,
        "ready_for_documentary":False
    }


def main():
    p=argparse.ArgumentParser(description="Extraer métricas XBRL SEC y comparar solo periodos idénticos")
    p.add_argument("--cik",required=True)
    p.add_argument("--input",type=Path,help="JSON SEC descargado previamente: permite prueba offline")
    p.add_argument("--out",type=Path,default=Path("dist/investigacion"))
    args=p.parse_args()
    if not CIK.fullmatch(args.cik):
        p.error("CIK incorrecto")
    cik=args.cik.zfill(10)
    url=f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    if args.input:
        raw=args.input.read_bytes()
    else:
        raw,url=fetch_companyfacts(cik)
    report=analyze_companyfacts(raw,source_url=url)
    if report["entity_cik"]!=cik:
        raise ValueError("CIK esperado distinto del archivo")
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/"SEC_XBRL_HECHOS_NO_VERIFICADOS.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("XBRL:",report["observation_count"],"hechos estructurados;",
          report["comparison"]["same_period_differences"],"diferencias de periodo idéntico;",
          "0 afirmaciones aprobadas")


if __name__=="__main__":
    main()
