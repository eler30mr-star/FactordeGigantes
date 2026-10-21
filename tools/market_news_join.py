"""Relaciona entidades del radar Wikimedia con titulares RSS usando menciones exactas.

Solo una coincidencia literal sugerida; NO valida identidad corporativa ni hechos.
Consume reportes reales ya recogidos. No invoca LLM ni servicios externos.
"""
from __future__ import annotations
import argparse
from datetime import date,datetime,timezone,timedelta
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import urlsplit

QID=re.compile(r"^Q[1-9][0-9]*$")
NEWS_ID=re.compile(r"^news-[a-f0-9]{32}$")
SUFFIXES=("corporation","corp","company","incorporated","inc","limited","ltd",
          "group","holdings","holding","sociedad","anonima","sa","s a","plc")
# Excluir términos vacíos/generales; no contiene nombres concretos de compañías.
GENERIC={"company","companies","corporation","business","enterprise","industria",
         "industrial","technology","technologies","global","international"}
MAX_MATCHES=100

def norm(s):
    chars=unicodedata.normalize("NFKD",s.casefold())
    unaccented="".join(ch for ch in chars if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+"," ",unaccented).strip()

def alias_for(name):
    if not isinstance(name,str):return None
    t=norm(name)
    tokens=t.split()
    while tokens and tokens[-1] in SUFFIXES:
        tokens.pop()
    t=" ".join(tokens)
    if len(t)<6 or t in GENERIC or len(tokens)>6:return None
    return t

def match_company_news(wiki,news):
    if not isinstance(wiki,dict) or wiki.get("method")!="wikimedia_wikidata_company_discovery_v1":
        raise ValueError("Radar Wikimedia inválido")
    if not isinstance(news,dict) or news.get("provider")!="google_news_rss":
        raise ValueError("Radar informativo inválido")
    collected=wiki.get("collected_on")
    if collected!=str(news.get("collected_at",""))[:10]:
        raise ValueError("Fuentes de diferentes fechas: no relacionar")
    today=date.fromisoformat(collected)
    companies=wiki.get("candidates")
    leads=news.get("leads")
    if not isinstance(companies,list) or len(companies)>24 or \
       not isinstance(leads,list) or len(leads)>100:
        raise ValueError("Reportes fuera de presupuesto")
    links=[]
    visited=set()
    for company in companies:
        if not isinstance(company,dict):continue
        qid=company.get("wikidata_id")
        name=company.get("topic")
        alias=alias_for(name)
        if not isinstance(qid,str) or not QID.fullmatch(qid) or not alias:continue
        signals=company.get("discovery_signals")
        if not isinstance(signals,list) or not any(isinstance(x,dict) and \
             x.get("source")=="wikimedia_daily_top_plus_wikidata_p31" for x in signals):
            continue
        # Límites de palabras para evitar coincidir en subcadenas (p.ej. Sony/Sonyx).
        expression=re.compile(r"(?<![a-z0-9])"+re.escape(alias)+r"(?![a-z0-9])")
        for lead in leads:
            if not isinstance(lead,dict) or \
                not isinstance(lead.get("id"),str) or not NEWS_ID.fullmatch(lead["id"]):
                continue
            if lead.get("verification_state")!="unverified" or \
                lead.get("youtube_demand_verified") is not False:continue
            headline=lead.get("headline")
            if not isinstance(headline,str) or not expression.search(norm(headline)):continue
            url=lead.get("aggregator_url")
            if not isinstance(url,str):continue
            parsed=urlsplit(url)
            if parsed.scheme!="https" or parsed.hostname!="news.google.com":continue
            key=(qid,lead["id"])
            if key in visited:continue
            try:
                published=datetime.fromisoformat(lead["published_at"].replace("Z","+00:00")).date()
                if not today-timedelta(days=3)<=published<=today:continue
            except (ValueError,KeyError,TypeError):continue
            visited.add(key)
            links.append({
                "wikidata_id":qid,"news_id":lead["id"],
                "matched_alias":alias,"method":"exact_normalized_headline_v1",
                "headline":headline,"aggregator_url":url,
                "match_status":"candidate_needs_entity_confirmation",
                "source_article_verified":False,
                "youtube_market_verified":False,"editorial_authorized":False
            })
            if len(links)>=MAX_MATCHES:break
        if len(links)>=MAX_MATCHES:break
    return {"provider":"wikimedia_rss_headline_join_v1","collected_on":collected,
        "company_count":len(companies),"news_count":len(leads),"match_count":len(links),
        "matches":links,"market_study_complete":False,
        "source_article_verified":False,"ready_for_script":False,
        "ready_for_youtube":False,
        "warning":"Coincidencias literales sugeridas; ni identidad ni noticia han sido verificadas en su fuente original."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--companies",required=True,type=Path)
    p.add_argument("--news",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    result=match_company_news(json.loads(a.companies.read_text(encoding="utf-8")),
                              json.loads(a.news.read_text(encoding="utf-8")))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("COINCIDENCIAS_PRELIMINARES:",result["match_count"],"DE:",
          result["company_count"],"EMPRESAS; CONFIRMADOS:",result["source_article_verified"])

if __name__=="__main__":
    main()
