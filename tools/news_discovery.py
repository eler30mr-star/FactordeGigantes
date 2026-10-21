"""Radar complementario de titulares actuales: Google News RSS, sin claves ni IA.

Un titular no es un hecho verificado ni un indicador de demanda YouTube.
Registra agregador, medio atribuido, fecha, categoría de búsqueda y procedencia.
No extrae nombres de empresas por heurísticas no confiables.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from hashlib import sha256
import json
from pathlib import Path
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

HOST="news.google.com"
# Consultas amplias del nicho; NO nombres de empresas, historias o ganadores preparados.
FEEDS=(
    ("empresas", "es", "PE", "empresas adquisición inversión when:2d"),
    ("innovacion", "es", "MX", "innovación tecnología empresas when:2d"),
    ("tecnologia", "en", "US", "technology company breakthrough when:2d"),
    ("industria", "en", "US", "manufacturing industry companies when:2d"),
)
MAX_ITEMS_PER_FEED=25
MAX_RESPONSE_BYTES=400_000
MAX_LEADS=100


def news_feed_url(language,region,query):
    if language not in ("es","en") or region not in ("PE","MX","US") or not query:
        raise ValueError("Feed fuera de configuración")
    return "https://news.google.com/rss/search?"+urlencode({
        "q":query,"hl":language+"-"+region,"gl":region,"ceid":region+":"+language
    })


def fetch_rss(url, *, opener=urlopen):
    parsed=urlsplit(url)
    if parsed.scheme!="https" or parsed.hostname!=HOST or parsed.path!="/rss/search":
        raise ValueError("URL RSS fuera de lista permitida")
    req=Request(url,headers={"User-Agent":"FactorDeGigantes-NewsScout/1.0",
        "Accept":"application/rss+xml, application/xml"})
    with opener(req,timeout=18) as response:
        content=response.read(MAX_RESPONSE_BYTES+1)
    if len(content)>MAX_RESPONSE_BYTES: raise ValueError("Feed RSS excede 400 KB")
    if b"<!DOCTYPE" in content.upper() or b"<!ENTITY" in content.upper():
        raise ValueError("XML no permitido")
    return content


def parse_news_rss(data, category, *, now):
    if category not in {"empresas","innovacion","tecnologia","industria"}:
        raise ValueError("Categoría inválida")
    if not isinstance(data,(bytes,bytearray)) or len(data)>MAX_RESPONSE_BYTES:
        raise ValueError("RSS inválido")
    if b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
        raise ValueError("XML con DTD/ENTITY no permitido")
    root=ET.fromstring(data)
    if root.tag!="rss": raise ValueError("No es RSS 2.0")
    channel=root.find("channel")
    if channel is None: raise ValueError("Canal ausente")
    found=[]
    for item in channel.findall("item")[:MAX_ITEMS_PER_FEED]:
        title=(item.findtext("title") or "").strip()
        link=(item.findtext("link") or "").strip()
        publisher=(item.findtext("source") or "").strip()
        pub=(item.findtext("pubDate") or "").strip()
        if not 12<=len(title)<=280 or not 2<=len(publisher)<=120:
            continue
        if "\n" in title or "\r" in title or "\x00" in title: continue
        try:
            u=urlsplit(link)
            if u.scheme!="https" or u.hostname not in ("news.google.com","www.google.com") or \
                    not u.path.startswith(("/rss/articles/","/articles/","/read/")) or \
                    u.username or u.password or u.port or len(link)>1600:
                continue
            stamp=parsedate_to_datetime(pub)
            if stamp.tzinfo is None: continue
            stamp=stamp.astimezone(timezone.utc)
            if not now-timedelta(hours=72)<=stamp<=now+timedelta(minutes=10):
                continue
        except (TypeError,ValueError,OverflowError):
            continue
        # La atribución del medio es una etiqueta del agregador, NO comprobación de publicación.
        fingerprint=sha256((title.casefold()+"|"+publisher.casefold()+"|"+
                            stamp.date().isoformat()).encode("utf-8")).hexdigest()[:32]
        found.append({
            "id":"news-"+fingerprint,
            "headline":title,"aggregator_url":link,"source_label":publisher,
            "category":category,"published_at":stamp.isoformat().replace("+00:00","Z"),
            "verification_state":"unverified",
            "youtube_demand_verified":False,"editorial_authorized":False
        })
    return found


def discover_news(*,now=None,fetch=fetch_rss):
    now=now or datetime.now(timezone.utc)
    if now.tzinfo is None: raise ValueError("Momento UTC requerido")
    now=now.astimezone(timezone.utc)
    rows={}
    sources=[]
    failures=[]
    for category,lang,region,query in FEEDS:
        url=news_feed_url(lang,region,query)
        try:
            items=parse_news_rss(fetch(url),category,now=now)
            for item in items:
                rows.setdefault(item["id"],item)
            sources.append({"category":category,"language":lang,"region":region,
                            "feed_url":url,"items_accepted":len(items)})
        except (OSError,ValueError,ET.ParseError,TimeoutError,RuntimeError) as exc:
            failures.append({"category":category,"error_type":type(exc).__name__})
    if not sources:
        raise RuntimeError("Ninguna fuente RSS respondió de forma válida")
    leads=sorted(rows.values(),key=lambda i:(i["published_at"],i["id"]),reverse=True)[:MAX_LEADS]
    return {
        "provider":"google_news_rss","collected_at":now.isoformat().replace("+00:00","Z"),
        "feeds":sources,"feeds_attempted":len(FEEDS),"feeds_succeeded":len(sources),
        "feed_failures":failures,"lead_count":len(leads),"leads":leads,
        "source_verification_complete":False,"youtube_market_verified":False,
        "market_study_complete":False,"ready_for_script":False,"ready_for_youtube":False,
        "warning":"Titulares y atribuciones del agregador: comprobar artículo original y hechos. No miden demanda YouTube."
    }


def main():
    parser=argparse.ArgumentParser(description="Descubrimiento periodístico de empresas y tecnología sin IA")
    parser.add_argument("--out",type=Path,default=Path("dist/radar/NOTICIAS_NO_VERIFICADAS.json"))
    args=parser.parse_args()
    report=discover_news()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("RADAR_NOTICIAS:",report["lead_count"],
          "titulares; FEEDS_EXITOSOS:",report["feeds_succeeded"],
          "de",report["feeds_attempted"],
          "MERCADO_YOUTUBE_VERIFICADO:",report["youtube_market_verified"])


if __name__=="__main__":
    main()
