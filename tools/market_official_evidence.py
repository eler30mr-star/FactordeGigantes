"""Recolector autónomo de páginas corporativas candidatas desde Wikidata P856.

Reutiliza el fetcher seguro (DNS público, HTTPS y redirecciones verificadas).
No confirma hechos, derechos ni relación editorial. Nunca descarga multimedia.
Presupuesto estricto: máximo tres sitios, 12 s cada uno, 400 KB de extracto
independiente del contenido original (solo hash y extracto informativo breve).
"""
from __future__ import annotations
import argparse,hashlib,json,re
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlsplit
from tools.research_engine import fetch_public,extract_blocks,validate_url
from tools.official_document_links import find_official_document_links

QID=re.compile(r"^Q[1-9][0-9]*$")
LIMIT=3
DOC_LIMIT=4

def candidates_from_reports(wiki,entities):
    if wiki.get("method")!="wikimedia_wikidata_company_discovery_v1" or \
       entities.get("provider")!="wikidata_news_company_resolution_v1":
        raise ValueError("Se requieren fuentes de empresas verificables por Wikidata")
    if wiki.get("collected_on")!=entities.get("collected_on"):
        raise ValueError("Fuentes observadas en días diferentes")
    seen=set();ordered=[]
    # Priorizar candidatas nacidas de noticias, luego Wikipedia.
    source_sets=[(entities.get("candidates",[]),"news"),(wiki.get("candidates",[]),"wiki")]
    for rows,origin in source_sets:
        if not isinstance(rows,list):raise ValueError("Candidatas no válidas")
        for row in rows:
            if not isinstance(row,dict):continue
            qid=row.get("wikidata_id")
            name=row.get("matched_name") if origin=="news" else row.get("topic")
            site=row.get("official_website_candidate")
            if not isinstance(qid,str) or not QID.fullmatch(qid) or qid in seen:
                continue
            if not isinstance(name,str) or not 4<=len(name)<=130:continue
            if not isinstance(site,str):continue
            try:
                valid_site=validate_url(site)
            except (ValueError,OverflowError):continue
            seen.add(qid)
            ordered.append({"wikidata_id":qid,"company":name,"official_website_candidate":valid_site,
              "identified_by":"wikidata_p856_via_"+origin})
            if len(ordered)>=LIMIT:return ordered
    return ordered

def collect_official_evidence(wiki,entities,*,fetcher=fetch_public):
    companies=candidates_from_reports(wiki,entities)
    collected=wiki["collected_on"]
    evidence=[]
    for company in companies:
        url=company["official_website_candidate"]
        result={**company,"status":"candidate_unreachable",
          "content_sha256":None,"resolved_url":None,"readable_blocks":0,
          "document_link_candidates":[],"short_excerpt":None,
          "source_identity_verified":False,"facts_verified":0,
          "rights_verified":False,"publication_authorized":False}
        try:
            body,resolved,mime=fetcher(url,timeout=12)
            validate_url(resolved)
            if not isinstance(body,bytes) or len(body)>2_000_000:
                raise ValueError("Contenido oficial supera límite")
            blocks=extract_blocks(body,mime)
            links=find_official_document_links(resolved,body,mime=mime)
            result.update({"status":"candidate_page_readable" if blocks else "candidate_page_unreadable",
                "content_sha256":hashlib.sha256(body).hexdigest(),
                "resolved_url":resolved,"readable_blocks":len(blocks),
                "document_link_candidates":[{
                   "url":p["url"],"document_fetched":False,"ownership_verified":False
                } for p in links[:DOC_LIMIT]],
                "short_excerpt":blocks[0][:300] if blocks else None})
        except (OSError,TimeoutError,ValueError,OverflowError,UnicodeError,KeyError,TypeError) as exc:
            result["fetch_error_type"]=type(exc).__name__
        evidence.append(result)
    return {"provider":"wikidata_p856_safe_official_fetch_v1",
      "collected_on":collected,"attempted":len(evidence),
      "readable":sum(r["status"]=="candidate_page_readable" for r in evidence),
      "evidence":evidence,"primary_facts_verified":0,
      "market_study_complete":False,"research_automatic":False,
      "ready_for_script":False,"ready_for_youtube":False,
      "warning":"Fuente oficial potencial: una página accesible o su hash NO certifican hechos, dominio, licencias o identidad."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--companies",required=True,type=Path)
    p.add_argument("--news-entities",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    r=collect_official_evidence(
      json.loads(a.companies.read_text(encoding="utf-8")),
      json.loads(a.news_entities.read_text(encoding="utf-8")))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("SITIOS_CORPORATIVOS_EXAMINADOS:",r["attempted"],
          "PAGINAS_CON_TEXTO:",r["readable"],
          "HECHOS_APROBADOS:",r["primary_facts_verified"])

if __name__=="__main__":main()
