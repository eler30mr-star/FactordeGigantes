"""Descubre compañías mencionadas en noticias, sin lista de nombres preparada.

Wikidata wbsearchentities y P31 comprueban clasificación corporativa. La relación
noticia-empresa es una hipótesis pendiente de contraste; P856 es solo un sitio candidato.
Límites gratuitos estrictos: 8 titulares, 2 fragmentos de nombres por titular,
16 búsquedas + 1 wbgetentities; sin tokens ni contenido de artículos ajenos.
"""
from __future__ import annotations
import argparse
from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import urlencode,urlsplit
from tools.market_sources import get_json
from tools.topic_discovery import COMPANY_TYPES, property_ids

WIKIDATA="https://www.wikidata.org/w/api.php"
MAX_HEADLINES=8
MAX_SEARCHES=16
MAX_RESULTS=4
MAX_ENTITIES=32
QID=re.compile(r"^Q[1-9][0-9]*$")
NEWS=re.compile(r"^news-[0-9a-f]{32}$")
CAPITALIZED=re.compile(r"(?<![\w])(?:[A-ZÁÉÍÓÚÑ][\wÀ-ÿ&.-]{2,})(?:\s+[A-ZÁÉÍÓÚÑ][\wÀ-ÿ&.-]{2,}){0,2}",re.UNICODE)
STOP={"como","cómo","para","from","with","that","this","will","sobre","según","when",
      "first","after","nuevo","nueva","new","more","empresa","empresas","global",
      "ministro","gobierno","presidente","industry","technology","news","perú","mexico",
      "argentina","españa","the","les","las","los","and","business","why","cómo"}

def canon(s):
    return " ".join("".join(ch for ch in unicodedata.normalize("NFKD",s.casefold())
       if not unicodedata.combining(ch)).split())

def names_from_headline(headline):
    if not isinstance(headline,str) or len(headline)>280:return []
    # Los últimos sufijos de medios vienen usualmente tras " - ".
    # No buscar el nombre del propio periódico como compañía tema.
    body=headline.rsplit(" - ",1)[0]
    options=[]
    for match in CAPITALIZED.findall(body):
        val=match.strip(". -")
        tokens=canon(val).split()
        if len(tokens)>3 or not tokens or canon(val) in STOP or \
           any(token in STOP for token in tokens) or len(canon(val))<4:
            continue
        if val.casefold() not in {v.casefold() for v in options}:
            options.append(val)
        if len(options)>=2:break
    return options

def wikidata_search(name,language,fetch):
    if language not in ("es","en") or not name or len(name)>130:
        raise ValueError("Consulta Wikidata inválida")
    url=WIKIDATA+"?"+urlencode({"action":"wbsearchentities","search":name,
      "language":language,"uselang":"es","type":"item","limit":MAX_RESULTS,"format":"json"})
    body=fetch(url)
    if not isinstance(body,dict) or not isinstance(body.get("search"),list):
        raise ValueError("Respuesta Wikidata inválida")
    return [entry["id"] for entry in body["search"][:MAX_RESULTS]
      if isinstance(entry,dict) and isinstance(entry.get("id"),str) and QID.fullmatch(entry["id"])]

def wikidata_details(ids,fetch):
    if not ids:return {}
    if len(ids)>MAX_ENTITIES or any(not QID.fullmatch(q) for q in ids):
        raise ValueError("Lote de entidades inválido")
    url=WIKIDATA+"?"+urlencode({"action":"wbgetentities","ids":"|".join(ids),
      "props":"claims|labels|sitelinks","languages":"es|en","format":"json"})
    body=fetch(url)
    if not isinstance(body,dict) or not isinstance(body.get("entities"),dict):
        raise ValueError("Wikidata no entregó entidades")
    return body["entities"]

def discover_news_entities(report,*,fetch=get_json):
    if not isinstance(report,dict) or report.get("provider")!="google_news_rss":
        raise ValueError("Informe real de noticias obligatorio")
    collected_at=report.get("collected_at")
    try: today=datetime.fromisoformat(collected_at.replace("Z","+00:00")).date()
    except (ValueError,AttributeError):raise ValueError("Fecha de informe incorrecta") from None
    leads=report.get("leads")
    if not isinstance(leads,list) or len(leads)>100 or report.get("lead_count")!=len(leads):
        raise ValueError("Cantidad de noticias inválida")
    # Orden estable: titulares recientes, medio diverso; nunca usar nombres escritos a mano.
    ordered=sorted(leads,key=lambda x:(x.get("published_at",""),x.get("id","")),reverse=True)
    chosen=[];seen_publishers=set()
    for lead in ordered:
        if not isinstance(lead,dict) or not NEWS.fullmatch(str(lead.get("id",""))):
            continue
        if lead.get("verification_state")!="unverified":continue
        source=lead.get("source_label","").casefold()
        if source in seen_publishers:continue
        url=urlsplit(str(lead.get("aggregator_url","")))
        if url.scheme!="https" or url.hostname!="news.google.com":continue
        try:
            d=datetime.fromisoformat(lead["published_at"].replace("Z","+00:00")).date()
            if not today-timedelta(days=3)<=d<=today:continue
        except (ValueError,KeyError,AttributeError):continue
        seen_publishers.add(source);chosen.append(lead)
        if len(chosen)>=MAX_HEADLINES:break
    pending=[];search_count=0;errors=0
    for lead in chosen:
        for name in names_from_headline(lead["headline"]):
            if search_count>=MAX_SEARCHES:break
            search_count+=1
            language="en" if lead.get("category") in ("tecnologia","industria") else "es"
            try:
                ids=wikidata_search(name,language,fetch)
            except (ValueError,RuntimeError,OSError,TimeoutError,KeyError,TypeError):
                errors+=1;continue
            for qid in ids:
                pending.append((qid,lead,name))
    unique_ids=list(dict.fromkeys(qid for qid,_,_ in pending))[:MAX_ENTITIES]
    try:entities=wikidata_details(unique_ids,fetch)
    except (ValueError,RuntimeError,OSError,TimeoutError,KeyError,TypeError):
        entities={};errors+=1
    matches=[];dedupe=set()
    for qid,lead,term in pending:
        if qid not in unique_ids:continue
        entity=entities.get(qid)
        if not isinstance(entity,dict) or entity.get("missing") is not None:
            continue
        if not COMPANY_TYPES.intersection(set(property_ids(entity,"P31"))):
            continue
        labels=entity.get("labels",{})
        if not isinstance(labels,dict):continue
        names=[v.get("value","") for v in labels.values() if isinstance(v,dict)]
        matched=[label for label in names if canon(label)==canon(term)]
        if not matched:continue
        key=(qid,lead["id"])
        if key in dedupe:continue
        dedupe.add(key)
        # Coincidencia Wikidata P31 + etiqueta exacta. Identidad en noticia sigue sin verificarse.
        official_candidate=None
        for statement in entity.get("claims",{}).get("P856",[]):
            try:
                site=statement["mainsnak"]["datavalue"]["value"]
                u=urlsplit(site)
                if u.scheme=="https" and u.hostname and not u.username and not u.password:
                    official_candidate=site
                    break
            except (KeyError,TypeError,ValueError):pass
        matches.append({"wikidata_id":qid,"news_id":lead["id"],
          "matched_name":matched[0],"article_headline":lead["headline"],
          "news_url":lead["aggregator_url"],"source_label":lead["source_label"],
          "wikidata_url":"https://www.wikidata.org/wiki/"+qid,
          "official_website_candidate":official_candidate,
          "evidence_method":"wikidata_p31_and_exact_label_in_headline_v1",
          "identity_verified_in_article":False,"primary_source_verified":False,
          "youtube_market_verified":False,"editorial_authorized":False})
    matches=matches[:16]  # Máximo almacenado por corrida; no consumir peticiones adicionales.
    return {"provider":"wikidata_news_company_resolution_v1","collected_on":today.isoformat(),
      "headlines_examined":len(chosen),"wikidata_searches":search_count,
      "wikidata_requests_max":MAX_SEARCHES+1,"lookup_errors":errors,
      "candidate_count":len(matches),"candidates":matches,
      "market_study_complete":False,"ready_for_script":False,"ready_for_youtube":False,
      "warning":"P31 y etiqueta Wikidata detectan posible empresa, no verifican el hecho ni la identidad que menciona el titular."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--news",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    data=discover_news_entities(json.loads(args.news.read_text(encoding="utf-8")))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("NUEVAS_ENTIDADES_EN_TITULARES:",data["candidate_count"],
      "RSS_EXAMINADOS:",data["headlines_examined"],
      "WIKIDATA_BUSQUEDAS:",data["wikidata_searches"],
      "ERRORES:",data["lookup_errors"],"FUENTES_PRIMARIAS_VERIFICADAS:",False)

if __name__=="__main__":main()
