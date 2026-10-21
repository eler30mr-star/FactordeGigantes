"""Encontrar documentos corporativos originales de SEC EDGAR sin API pagada.

MediaWiki -> Wikidata Q-ID -> P5531/CIK -> SEC submissions JSON -> lista de
archivos públicos. Wikidata sólo da un IDENTIFICADOR CANDIDATO. No se descargan
PDFs pesados, no se leen cifras, no se verifican hechos ni derechos.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.error import HTTPError
import re
from urllib.parse import urlencode

from tools.primary_source_discovery import (
    WIKIDATA_API, QID, lookup_wikidata_id,
)
from tools.research_engine import discover_wikipedia, fetch_public, validate_url

CIK = re.compile(r"^[0-9]{1,10}$")
ACCESSION = re.compile(r"^\d{10}-\d{2}-\d{6}$")
DOCNAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,119}$")
FORMS = {"10-K","10-K/A","10-Q","20-F","20-F/A","40-F","8-K","6-K"}
MAX_FILINGS = 8


def sec_cik_candidate(qid, fetcher=fetch_public):
    if not isinstance(qid, str) or not QID.fullmatch(qid):
        raise ValueError("QID inválido")
    url = WIKIDATA_API + "?" + urlencode({
        "action":"wbgetentities","ids":qid,"props":"claims",
        "format":"json","formatversion":"2"
    })
    raw, _, _ = fetcher(url)
    obj = json.loads(raw.decode("utf-8"))
    claims = obj.get("entities",{}).get(qid,{}).get("claims",{}).get("P5531",[])
    for item in claims[:3]:
        value = item.get("mainsnak",{}).get("datavalue",{}).get("value")
        if isinstance(value,str) and CIK.fullmatch(value):
            return value.zfill(10)
    return None


def sec_filings(cik, fetcher=fetch_public):
    if not isinstance(cik,str) or len(cik)!=10 or not cik.isascii() or not cik.isdigit():
        raise ValueError("CIK debe tener diez dígitos")
    url="https://data.sec.gov/submissions/CIK"+cik+".json"
    raw, resolved, mime=fetcher(url)
    if resolved != url or "json" not in mime.lower():
        raise ValueError("SEC redirigió o no devolvió el archivo JSON esperado")
    data=json.loads(raw.decode("utf-8"))
    recent=data.get("filings",{}).get("recent",{})
    arrays={key:recent.get(key,[]) for key in ("form","accessionNumber","primaryDocument","filingDate")}
    if not all(isinstance(value,list) for value in arrays.values()):
        raise ValueError("Esquema SEC inválido")
    count=min(len(v) for v in arrays.values())
    if count>2000:
        count=2000
    leads=[]
    for i in range(count):
        form,number,document,date=(arrays[key][i] for key in arrays)
        if form not in FORMS or not isinstance(number,str) or not ACCESSION.fullmatch(number):
            continue
        if not isinstance(document,str) or not DOCNAME.fullmatch(document) or ".." in document:
            continue
        if not isinstance(date,str) or not re.fullmatch(r"20\d{2}-\d{2}-\d{2}",date):
            continue
        archive="https://www.sec.gov/Archives/edgar/data/"+str(int(cik))+"/"+number.replace("-","")+"/"+document
        validate_url(archive)
        leads.append({"form":form,"filing_date":date,"accession":number,
                      "document_url":archive,
                      "document_type":"original_regulatory_filing_candidate",
                      "document_content_fetched":False,
                      "facts_verified":0})
        if len(leads)>=MAX_FILINGS:
            break
    return {"submissions_url":url,"company_name_reported":str(data.get("name",""))[:140],
            "filing_candidates":leads}


def discover_sec_leads(topic,fetcher=fetch_public,*,max_entities=3):
    if not isinstance(topic,str) or not 3<=len(topic.strip())<=130:
        raise ValueError("Tema inválido")
    suggestions=discover_wikipedia(topic,fetcher=fetcher)
    max_entities=max(1,min(5,int(max_entities)))
    records=[]
    used_cik=set()
    for item in suggestions[:max_entities]:
        rec={"title":item["title"],"wikidata_item":None,"cik_candidate":None,
             "status":"no_cik_found","filing_candidates":[],"facts_verified":0,
             "entity_verified":False}
        try:
            qid=lookup_wikidata_id(item["title"],fetcher=fetcher)
            if qid:
                rec["wikidata_item"]=qid
                cik=sec_cik_candidate(qid,fetcher=fetcher)
                if cik:
                    rec["cik_candidate"]=cik
                    rec["status"]="cik_candidate_from_wikidata"
                    rec["submissions_url"]="https://data.sec.gov/submissions/CIK"+cik+".json"
                    if cik not in used_cik:
                        used_cik.add(cik)
                        try:
                            sec=sec_filings(cik,fetcher=fetcher)
                            rec.update(sec)
                            rec["status"]="sec_filings_listed" if sec["filing_candidates"] else "sec_no_eligible_filings"
                        except (OSError,ValueError,TimeoutError,UnicodeError,json.JSONDecodeError) as exc:
                            rec["fetch_error_type"]=type(exc).__name__
                            if isinstance(exc,HTTPError):
                                rec["http_status"]=exc.code
        except (OSError,ValueError,TimeoutError,UnicodeError,json.JSONDecodeError) as exc:
            rec["status"]="lookup_unavailable"
            rec["fetch_error_type"]=type(exc).__name__
        records.append(rec)
    return {
        "product":"Factor de Gigantes","topic":topic,
        "method":"mediawiki_to_wikidata_P5531_to_SEC_EDGAR",
        "entities":records,
        "candidate_ciks":sum(r["cik_candidate"] is not None for r in records),
        "filing_candidates":sum(len(r["filing_candidates"]) for r in records),
        "source_primary_host":"www.sec.gov",
        "automatic_fact_verification":False,
        "automatic_rights_verification":False,
        "publication_authorized":False,
        "warning":(
            "CIK obtenido de Wikidata puede ser incompleto, desactualizado o referirse "
            "a una entidad distinta. SEC devuelve metadatos de documentos; cada filing "
            "requiere apertura, cotejo de sociedad, periodo, página, valores, contexto "
            "y revisión editorial. Sin SEC accesible no se simulan filings."
        ),
    }


def main():
    p=argparse.ArgumentParser(description="Localizar expedientes SEC candidatos por tema")
    p.add_argument("--topic",required=True)
    p.add_argument("--max-entities",type=int,default=3)
    p.add_argument("--out",type=Path,default=Path("dist/investigacion"))
    args=p.parse_args()
    report=discover_sec_leads(args.topic,max_entities=args.max_entities)
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/"sec_edgar_documentos_candidatos.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("SEC_EDGAR:",report["candidate_ciks"],"CIK candidatos y",
          report["filing_candidates"],"documentos originales por comprobar; 0 hechos aprobados")


if __name__=="__main__":
    main()
