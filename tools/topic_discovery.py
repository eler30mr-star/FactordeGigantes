"""Descubrimiento autónomo de empresas desde páginas de interés público.

No recibe nombres de empresas del usuario o ChatGPT: obtiene páginas de mayor
interés de Wikipedia y comprueba su tipo de entidad en Wikidata (P31).
Un artículo popular NO equivale a oportunidad para YouTube. El resultado no
activa IA de pago, render ni publicación y pasa luego al radar de mercado.
"""
from __future__ import annotations
import argparse
from collections import deque
from datetime import date, timedelta
import json
from pathlib import Path
import re
from urllib.parse import urlencode, urlsplit, quote, unquote

from tools.market_sources import get_json, SourcePayloadTooLarge

TOP_URL="https://wikimedia.org/api/rest_v1/metrics/pageviews/top/"
WIKIDATA_URL="https://www.wikidata.org/w/api.php"
LANGUAGES=("es","en")
# Tipos directos comunes: compañía, negocio, empresa pública, sociedad cotizada.
# Esto es una clasificación CONSERVADORA: quedan fuera compañías cuyos P31 sean
# subclases no enumeradas; se guardarán métricas de cobertura para mejorar luego.
COMPANY_TYPES={
    "Q783794", # company
    "Q4830453", # business
    "Q891723", # public company
    "Q6881511", # enterprise
    "Q167037", # corporation
    "Q149789", # holding company
}
TOP_ARTICLES_LIMIT=180
CHUNK_SIZE=30
MAX_ENTITY_REQUESTS=12
MAX_ENTRIES=24
TITLE=re.compile(r"^[^\n\r\t|#?]{2,170}$")


def valid_company_title(title):
    if not isinstance(title,str) or not TITLE.fullmatch(title):
        return False
    banned=("special:","category:","file:","template:","wikipedia:",
            "list_of_","anexo:","plantilla:","categoría:","portal:")
    return not title.casefold().startswith(banned) and title != "Main_Page"


def daily_top(lang, observed_day, *, fetch=get_json, limit=TOP_ARTICLES_LIMIT):
    if lang not in LANGUAGES or type(observed_day) is not date:
        raise ValueError("Wiki o fecha inválida")
    if not 1<=limit<=TOP_ARTICLES_LIMIT:
        raise ValueError("Límite de artículos inválido")
    endpoint=(TOP_URL+f"{lang}.wikipedia/all-access/"
              +observed_day.strftime("%Y/%m/%d"))
    body=fetch(endpoint)
    if not isinstance(body,dict) or not isinstance(body.get("items"),list) or not body["items"]:
        raise ValueError("Wikimedia no devolvió ranking diario")
    articles=body["items"][0].get("articles",[])
    if not isinstance(articles,list):
        raise ValueError("Artículos Wikimedia no válidos")
    selection=[]
    seen=set()
    for row in articles:
        if not isinstance(row,dict):
            continue
        article=row.get("article")
        views=row.get("views")
        rank=row.get("rank")
        if not valid_company_title(article) or type(views) is not int or views<0 or type(rank) is not int or rank<1:
            continue
        if article.casefold() in seen:
            continue
        seen.add(article.casefold())
        selection.append({"title":article,"views":views,"rank":rank})
        if len(selection)>=limit:
            break
    return endpoint,selection


def read_entities(lang,titles,*,fetch=get_json):
    if lang not in LANGUAGES or not isinstance(titles,list) or not 1<=len(titles)<=CHUNK_SIZE:
        raise ValueError("Lote Wikidata fuera de presupuesto")
    if any(not valid_company_title(t) for t in titles):
        raise ValueError("Título de artículo inválido")
    params=urlencode({
        "action":"wbgetentities",
        "sites":lang+"wiki",
        "titles":"|".join(titles),
        "props":"claims|sitelinks|labels",
        "sitefilter":lang+"wiki",
        "languages":"es|en",
        "format":"json",
    })
    url=WIKIDATA_URL+"?"+params
    body=fetch(url)
    if not isinstance(body,dict) or not isinstance(body.get("entities"),dict):
        raise ValueError("Wikidata no devolvió entidades")
    return body["entities"]


def property_ids(entity,prop):
    statements=entity.get("claims",{}).get(prop,[])
    found=[]
    for row in statements[:12]:
        try:
            value=row["mainsnak"]["datavalue"]["value"]
            if isinstance(value,dict) and isinstance(value.get("id"),str):
                found.append(value["id"])
        except (KeyError,TypeError,IndexError):
            continue
    return found


def official_site_candidate(entity):
    for claim in entity.get("claims",{}).get("P856",[])[:3]:
        try:
            url=claim["mainsnak"]["datavalue"]["value"]
            parts=urlsplit(url)
            if isinstance(url,str) and parts.scheme=="https" and parts.hostname and not parts.username and not parts.password:
                return url[:1300]
        except (TypeError,KeyError,ValueError):
            pass
    return None


def discover(*, today=None,languages=LANGUAGES,limit=120,max_requests=8,fetch=get_json,
             enrich_interest=False,interest_collector=None):
    """A Wikimedia le damos 3 días de retraso para evitar páginas incompletas.

    El máximo de consultas es estricto; no se ejecutan búsquedas de YouTube ni
    se compone automáticamente un guion sin validar datos de mercado.
    """
    today=today or date.today()
    if isinstance(today,str):
        today=date.fromisoformat(today)
    if type(today) is not date or not 1<=limit<=TOP_ARTICLES_LIMIT or not 1<=max_requests<=MAX_ENTITY_REQUESTS:
        raise ValueError("Configuración de rastreo inválida")
    if not isinstance(languages,(tuple,list)) or not languages or len(set(languages))!=len(languages) or any(l not in LANGUAGES for l in languages):
        raise ValueError("Idiomas de descubrimiento inválidos")
    day=today-timedelta(days=3)
    sources=[]
    candidates={}
    total_queries=0
    total_titles=0
    oversized_batches=[]
    classified_titles=0
    skipped_oversized_titles=0
    unprocessed_titles=0
    for lang in languages:
        top_url,articles=daily_top(lang,day,fetch=fetch,limit=limit)
        sources.append({"language":lang,"top_url":top_url,"article_count":len(articles),
                        "observed_top_day":day.isoformat()})
        total_titles+=len(articles)
        stats={a["title"]:a for a in articles}
        pending=deque([a["title"] for a in articles[offset:offset+CHUNK_SIZE]]
                      for offset in range(0,len(articles),CHUNK_SIZE))
        while pending and total_queries<max_requests:
            subset=pending.popleft()
            # Cada intento, incluso uno rechazado por tamaño, consume el
            # presupuesto. Un título desmesurado no debe tumbar todo el radar.
            total_queries+=1
            try:
                entities=read_entities(lang,subset,fetch=fetch)
            except SourcePayloadTooLarge:
                oversized_batches.append({'language':lang,'batch_size':len(subset),
                    'outcome':'split' if len(subset)>1 else 'skipped_oversized_entity'})
                if len(subset)>1:
                    middle=len(subset)//2
                    pending.appendleft(subset[middle:]);pending.appendleft(subset[:middle])
                else:
                    skipped_oversized_titles+=1
                continue
            classified_titles+=len(subset)
            for entity in entities.values():
                if not isinstance(entity,dict) or not re.fullmatch(r"Q[1-9][0-9]*",str(entity.get("id",""))):
                    continue
                types=sorted(set(property_ids(entity,"P31")) & COMPANY_TYPES)
                if not types:
                    continue
                title=((entity.get("sitelinks") or {}).get(lang+"wiki") or {}).get("title")
                if not isinstance(title,str):
                    continue
                title_key=title.replace(" ","_")
                raw=stats.get(title_key) or stats.get(title)
                if not raw:
                    continue
                key=entity["id"]
                observed={
                    "source":"wikimedia_daily_top_plus_wikidata_p31",
                    "project":lang+".wikipedia",
                    "url":"https://"+lang+".wikipedia.org/wiki/"+quote(title.replace(" ","_"),safe=""),
                    "rank":raw["rank"],"views":raw["views"],"observed_on":day.isoformat(),
                }
                if key not in candidates:
                    labels=entity.get("labels") or {}
                    name=((labels.get("es") or labels.get("en") or {}).get("value") or title)
                    candidates[key]={
                        "wikidata_id":key,"topic":name[:130],
                        "entity_class_candidates":types,
                        "official_website_candidate":official_site_candidate(entity),
                        "discovery_signals":[observed],
                        "status":"identity_candidate_needs_validation",
                        "market_rank_qualified":False,
                        "youtube_data_collected":False,
                        "primary_documents_verified":False,
                        "research_started":False,
                        "youtube_publication_authorized":False,
                    }
                else:
                    candidates[key]["discovery_signals"].append(observed)
            if len(candidates)>=MAX_ENTRIES:
                break
        unprocessed_titles+=sum(map(len,pending))
        if len(candidates)>=MAX_ENTRIES:
            break
    ordered=sorted(candidates.values(),
                   key=lambda x:(-len(x["discovery_signals"]),
                                 -sum(v["views"] for v in x["discovery_signals"]),
                                 x["topic"].casefold()))[:MAX_ENTRIES]
    if enrich_interest:
        if interest_collector is None:
            from tools.market_sources import collect_wikipedia
            interest_collector=collect_wikipedia
        for item in ordered[:6]:
            signal=item["discovery_signals"][0]
            lang=signal["project"].split(".")[0]
            article=unquote(signal["url"].split("/wiki/",1)[1]).replace("_"," ")
            try:
                interest=interest_collector(article,language=lang,now=today)
                # Sin 14 días completos NO hay serie de interés validada.
                if not isinstance(interest,dict) or "views_last_7d" not in interest or "views_previous_7d" not in interest:
                    raise ValueError("Señal sin ventana completa")
                item["wikipedia_interest"]=interest
                item["interest_14d_status"]="measured"
            except (ValueError,RuntimeError,OSError,TimeoutError,KeyError) as exc:
                item["interest_14d_status"]="unavailable"
                item["interest_error_type"]=type(exc).__name__
    return {
        "product":"Factor de Gigantes",
        "method":"wikimedia_wikidata_company_discovery_v1",
        "collected_on":today.isoformat(),
        "data_day":day.isoformat(),
        "articles_considered":total_titles,
        "wikidata_requests":total_queries,
        "wikidata_titles_classified":classified_titles,
        "wikidata_oversized_batches":oversized_batches,
        "wikidata_oversized_titles_skipped":skipped_oversized_titles,
        "wikidata_titles_unprocessed":unprocessed_titles,
        "discovery_coverage":"partial" if skipped_oversized_titles or unprocessed_titles else "complete",
        "sources":sources,
        "candidates":ordered,
        "company_candidates_count":len(ordered),
        "wikipedia_interest_measured_count":sum(x.get("interest_14d_status")=="measured" for x in ordered),
        "market_study_complete":False,
        "youtube_market_verified":False,
        "selected_automatically_for_research":None,
        "ready_for_script":False,
        "ready_for_youtube":False,
        "warning":"Empresas detectadas a partir de interés en Wikipedia; NO se ha verificado demanda ni competencia en YouTube.",
    }


def main():
    p=argparse.ArgumentParser(description="Descubrir empresas reales desde tendencia Wikimedia, sin lista de nombres")
    p.add_argument("--out",type=Path,default=Path("dist/radar/EMPRESAS_DESCUBIERTAS_NO_CLASIFICADAS.json"))
    p.add_argument("--limit",type=int,default=120)
    p.add_argument("--max-requests",type=int,default=8)
    p.add_argument("--today",type=str)
    p.add_argument("--enrich-interest",action="store_true",
                   help="Medir 14 días de visitas por artículo, máximo seis candidatos")
    args=p.parse_args()
    result=discover(today=args.today,limit=args.limit,max_requests=args.max_requests,
                    enrich_interest=args.enrich_interest)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("EMPRESAS_DETECTADAS:",result["company_candidates_count"])
    print("ENTIDADES_OBSERVADAS:",result["articles_considered"],"WIKIDATA_REQUESTS:",result["wikidata_requests"])
    print('WIKIDATA_COBERTURA:',result['discovery_coverage'],
          'TITULOS_PROCESADOS:',result['wikidata_titles_classified'],
          'OMITIDOS_POR_TAMANO:',result['wikidata_oversized_titles_skipped'],
          'PENDIENTES:',result['wikidata_titles_unprocessed'])
    for record in result["candidates"][:8]:
        print("CANDIDATA:",record["wikidata_id"],record["topic"],"fuentes:",len(record["discovery_signals"]))
    print("SERIES_14_DIAS_REALES:",result["wikipedia_interest_measured_count"])
    print("ESTUDIO_DE_MERCADO_COMPLETO:",result["market_study_complete"])
    print("YOUTUBE_HABILITADO:",result["ready_for_youtube"])


if __name__=="__main__":
    main()

