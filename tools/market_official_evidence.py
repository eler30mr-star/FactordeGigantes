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

def candidates_from_reports(wiki,entities,*,exclude_ids=(),exclude_hosts=()):
    if wiki.get("method")!="wikimedia_wikidata_company_discovery_v1" or \
       entities.get("provider")!="wikidata_news_company_resolution_v1":
        raise ValueError("Se requieren fuentes de empresas verificables por Wikidata")
    if wiki.get("collected_on")!=entities.get("collected_on"):
        raise ValueError("Fuentes observadas en días diferentes")
    seen=set(exclude_ids);hosts=set(exclude_hosts);ordered=[]
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
            host=urlsplit(valid_site).hostname
            if host in hosts:continue
            seen.add(qid)
            hosts.add(host)
            ordered.append({"wikidata_id":qid,"company":name,"official_website_candidate":valid_site,
              "identified_by":"wikidata_p856_via_"+origin})
            if len(ordered)>=LIMIT:return ordered
    return ordered

PROMOTIONAL=("cookie", "cookies", "privacy policy", "política de privacidad",
             "accept all", "accept cookies", "sign up", "newsletter", "suscríbete",
             "advertising", "contact us", "contáctenos", "all rights reserved",
             "explore our", "discover our", "learn more", "click here", "inicio sesión")
DOCUMENTAL=("annual report", "financial report", "quarterly", "revenue", "investment",
            "founded", "history", "manufacturing", "acquisition", "company was",
            "informe anual", "ingresos", "inversión", "fundada", "historia",
            "fabricación", "adquisición", "resultados", "operaciones", "producción")

def documentary_excerpts(blocks, limit=3):
    """Hasta tres pasajes distintos con localizador; la longitud no prueba calidad."""
    ranked=[]
    seen=set()
    for i,block in enumerate(blocks):
        if not isinstance(block,str):continue
        text=" ".join(block.split())
        if not 90<=len(text)<=5000:continue
        lower=text.casefold()
        penalties=sum(token in lower for token in PROMOTIONAL)
        documentary=sum(token in lower for token in DOCUMENTAL)
        dated=bool(re.search(r"(?<!\d)(?:19|20)\d{2}(?!\d)",text))
        # Un párrafo largo o un banner con un año no bastan por sí solos.
        if penalties or not documentary:continue
        excerpt=text[:300]
        if excerpt.casefold() in seen:continue
        seen.add(excerpt.casefold())
        ranked.append((3*min(documentary,3)+2*dated,-i,excerpt,i))
    ranked.sort(reverse=True)
    return [{"excerpt":text,"block_index":index,
             "verification_state":"uncorroborated"}
            for _,_,text,index in ranked[:max(0,min(3,limit))]]


def select_documentary_excerpt(blocks):
    """Selecciona texto REAL potencialmente útil, no reescribe ni inventa.

    Penaliza menús y promociones; prioriza bloques fechados o sobre operaciones.
    No considera las palabras clave como certificación factual.
    """
    candidates=documentary_excerpts(blocks,1)
    if candidates:return candidates[0]["excerpt"],"documentary_candidate"
    ranked=[]
    for i,block in enumerate(blocks):
        if not isinstance(block,str):continue
        excerpt=" ".join(block.split())
        if not 90<=len(excerpt)<=5000:continue
        lower=excerpt.casefold()
        penalties=sum(token in lower for token in PROMOTIONAL)
        documentary=sum(token in lower for token in DOCUMENTAL)
        dated=bool(re.search(r"(?<!\d)(?:19|20)\d{2}(?!\d)",excerpt))
        score=3*min(documentary,3)+2*dated-6*penalties+min(3,len(excerpt)//250)
        ranked.append((score,-i,excerpt))
    if not ranked:
        return (blocks[0][:300] if blocks else None), "insufficient_context"
    best=max(ranked)
    return best[2][:300],"generic_candidate"

def collect_official_evidence(wiki,entities,*,fetcher=fetch_public,previous_report=None):
    excluded_ids=[];excluded_hosts=[]
    if previous_report is not None:
        validate_batch(previous_report,wiki.get("collected_on"))
        # No repetir IA ni rastreo si ya hay contexto o un informe enlazado
        # que el siguiente paso puede recuperar dentro del mismo hostname.
        for page in previous_report["evidence"]:
            excluded_ids.append(page["wikidata_id"])
            excluded_hosts.append(urlsplit(page["official_website_candidate"]).hostname)
            useful=page.get("excerpt_quality")=="documentary_candidate"
            same_host_link=any(urlsplit(d.get("url","")).hostname==
                urlsplit(page.get("resolved_url") or page["official_website_candidate"]).hostname
                for d in page.get("document_link_candidates",[]))
            if useful or same_host_link:
                return empty_batch(wiki["collected_on"],"initial_context_available")
    companies=candidates_from_reports(wiki,entities,exclude_ids=excluded_ids,exclude_hosts=excluded_hosts)
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
            selected_excerpt,excerpt_quality=select_documentary_excerpt(blocks)
            links=find_official_document_links(resolved,body,mime=mime)
            result.update({"status":"candidate_page_readable" if blocks else "candidate_page_unreadable",
                "content_sha256":hashlib.sha256(body).hexdigest(),
                "resolved_url":resolved,"readable_blocks":len(blocks),
                "document_link_candidates":[{
                   "url":p["url"],"category":p["category"],
                   "document_fetched":False,"ownership_verified":False
                } for p in links[:DOC_LIMIT]],
                "short_excerpt":selected_excerpt,"excerpt_quality":excerpt_quality,
                "excerpt_candidates":documentary_excerpts(blocks)})
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


def validate_batch(report,day):
    if (not isinstance(report,dict) or
        report.get("provider")!="wikidata_p856_safe_official_fetch_v1" or
        report.get("collected_on")!=day or report.get("primary_facts_verified")!=0 or
        report.get("ready_for_youtube") is not False or
        not isinstance(report.get("evidence"),list) or len(report["evidence"])>3):
        raise ValueError("Tanda corporativa incompatible")


def empty_batch(day,reason):
    return {"provider":"wikidata_p856_safe_official_fetch_v1","collected_on":day,
        "attempted":0,"readable":0,"evidence":[],"primary_facts_verified":0,
        "market_study_complete":False,"research_automatic":False,
        "ready_for_script":False,"ready_for_youtube":False,"skip_reason":reason}


def combine_batches(first,second):
    day=first.get("collected_on")
    for batch in (first,second):validate_batch(batch,day)
    combined={**first,"evidence":first["evidence"]+second["evidence"]}
    ids=[p["wikidata_id"] for p in combined["evidence"]]
    if len(ids)!=len(set(ids)):raise ValueError("Empresa repetida entre tandas")
    combined["attempted"]=len(ids)
    combined["readable"]=sum(p["status"]=="candidate_page_readable" for p in combined["evidence"])
    combined["local_consolidation_only"]=True
    combined["source_batch_sha256"]=[hashlib.sha256(json.dumps(b,sort_keys=True).encode()).hexdigest()
                                       for b in (first,second)]
    return combined

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--companies",required=True,type=Path)
    p.add_argument("--news-entities",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--previous-report",type=Path)
    p.add_argument("--combine-report",type=Path)
    a=p.parse_args()
    previous=json.loads(a.previous_report.read_text(encoding="utf-8")) if a.previous_report else None
    if a.combine_report:
        if previous is None:raise ValueError("Falta primera tanda")
        r=combine_batches(previous,json.loads(a.combine_report.read_text(encoding="utf-8")))
    else:
        r=collect_official_evidence(
          json.loads(a.companies.read_text(encoding="utf-8")),
          json.loads(a.news_entities.read_text(encoding="utf-8")),previous_report=previous)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("SITIOS_CORPORATIVOS_EXAMINADOS:",r["attempted"],
          "PAGINAS_CON_TEXTO:",r["readable"],
          "HECHOS_APROBADOS:",r["primary_facts_verified"])

if __name__=="__main__":main()

