"""Colectores oficiales de inteligencia de mercado, con coste acotado.

YouTube requiere API key del proyecto; Wikimedia es pública. Ambos devuelven
muestras observadas, no un ranking ni permiso de publicar. No adivina títulos.
"""
from __future__ import annotations

from datetime import date, timedelta, datetime, timezone
import json
import os
import re
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen

API_HOST="https://www.googleapis.com/youtube/v3/"
PAGEVIEWS_HOST="https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
UA="FactorDeGigantes-MarketResearch/0.1 (https://github.com/eler30mr-star/FactordeGigantes; public research)"
MAX_PAYLOAD=1_000_000
MAX_VIDEOS=10
ID=re.compile(r"^[A-Za-z0-9_-]{11}$")
WIKI_TITLE=re.compile(r"^[^\n#?]{2,120}$")


def get_json(url, *, request=None):
    if request is not None:
        return request(url)
    req=Request(url,headers={"User-Agent":UA,"Accept":"application/json"})
    with urlopen(req,timeout=20) as response:
        if response.status != 200:
            raise ValueError("Proveedor devolvió estado no válido")
        raw=response.read(MAX_PAYLOAD+1)
    if len(raw)>MAX_PAYLOAD:
        raise ValueError("Respuesta de fuente demasiado grande")
    return json.loads(raw.decode("utf-8"))


def collect_youtube(topic, *, api_key=None, now=None, request=None, region="MX"):
    """Máx. dos llamadas: search.list y videos.list (hasta 10 videos).

    Los límites y costos de cuota deben verificarse en Google Cloud; el
    producto no utiliza una API sin credenciales válidas o consentimiento.
    """
    if not isinstance(topic,str) or not 4<=len(topic.strip())<=130:
        raise ValueError("Tema corto, excesivo o ausente")
    if region not in {"MX","PE","ES","CO","AR","CL","US"}:
        raise ValueError("Región del estudio no configurada")
    api_key=api_key if api_key is not None else os.getenv("YOUTUBE_DATA_API_KEY")
    if not isinstance(api_key,str) or len(api_key)<20:
        raise RuntimeError("YOUTUBE_DATA_API_KEY ausente: no fingir señales de mercado")
    now=now or date.today()
    if isinstance(now,str):
        now=date.fromisoformat(now)
    after=(now-timedelta(days=90)).isoformat()+"T00:00:00Z"
    def call(method,params):
        params["key"]=api_key
        # La URL contiene una clave: nunca imprimir la URL ni exception HTTP con la URL.
        url=API_HOST+method+"?"+urlencode(params)
        try:
            return get_json(url,request=request)
        except Exception as exc:
            raise RuntimeError(f"Error YouTube {method}: {type(exc).__name__}; revisar cuota y permisos") from None

    first=call("search",{
        "part":"snippet","type":"video","q":topic,
        "publishedAfter":after,"order":"relevance",
        "maxResults":str(MAX_VIDEOS),"safeSearch":"strict","regionCode":region,
        "relevanceLanguage":"es",
    })
    items=first.get("items",[])
    if not isinstance(items,list):
        raise ValueError("Esquema de búsqueda de YouTube no válido")
    ids=[]
    for item in items:
        if isinstance(item,dict):
            key=(item.get("id") or {}).get("videoId") if isinstance(item.get("id"),dict) else None
            if isinstance(key,str) and ID.fullmatch(key) and key not in ids:
                ids.append(key)
    if len(ids)<3:
        raise ValueError("Muestra YouTube insuficiente: no predecir demanda")
    second=call("videos",{
        "part":"snippet,statistics","id":",".join(ids),"maxResults":str(MAX_VIDEOS)
    })
    details=second.get("items",[])
    if not isinstance(details,list):
        raise ValueError("Métricas de video no válidas")
    videos=[]
    for row in details:
        if not isinstance(row,dict) or row.get("id") not in ids:
            continue
        try:
            views=int(row["statistics"]["viewCount"])
            published=datetime.fromisoformat(row["snippet"]["publishedAt"].replace("Z","+00:00")).date()
            age=(now-published).days
            if views<0 or not 0<=age<=90:
                continue
        except (ValueError,KeyError,TypeError):
            continue
        videos.append({
            "video_id":row["id"],
            "url":"https://www.youtube.com/watch?v="+row["id"],
            "view_count":views,
            "published_at":published.isoformat(),
        })
    if len(videos)<3:
        raise ValueError("Sin videos suficientes con vistas y fecha")
    return {
        "observed_at":now.isoformat(),
        "videos":videos,
        "sampled_recent_uploads":len(ids),
        "sample_size":len(videos),
        "search_query":topic,
        "region":region,
        "origin":"youtube_data_api_v3_search_plus_videos",
        "notice":"Muestra parcial; no incluye retención ni CTR de canales ajenos.",
    }


def collect_wikipedia(title, *, language="es", now=None, request=None):
    if not isinstance(title,str) or not WIKI_TITLE.fullmatch(title) or "/" in title:
        raise ValueError("Artículo Wikipedia inválido")
    if language not in {"es","en"}:
        raise ValueError("Idioma Wikipedia no permitido")
    now=now or date.today()
    if isinstance(now,str):
        now=date.fromisoformat(now)
    # Excluir hoy porque las métricas diarias pueden estar incompletas.
    start=now-timedelta(days=14)
    end=now-timedelta(days=1)
    normalized=quote(title.replace(" ","_"),safe="")
    url=(PAGEVIEWS_HOST+f"{language}.wikipedia/all-access/user/"
         f"{normalized}/daily/{start:%Y%m%d}/{end:%Y%m%d}")
    try:
        reply=get_json(url,request=request)
    except Exception as exc:
        raise RuntimeError(f"Error Wikimedia: {type(exc).__name__}") from None
    items=reply.get("items",[])
    if not isinstance(items,list):
        raise ValueError("Datos Wikimedia inválidos")
    daily={}
    for entry in items:
        if not isinstance(entry,dict):
            continue
        try:
            day=datetime.strptime(entry["timestamp"][:8],"%Y%m%d").date()
        except (ValueError,TypeError,KeyError):
            continue
        views=entry.get("views")
        if type(views) is int and 0<=views<=10**12 and start<=day<=end:
            daily[day]=views
    if len(daily)!=14:
        raise ValueError("La serie de Wikipedia no contiene 14 días íntegros")
    last=sum(v for day,v in daily.items() if day>=now-timedelta(days=7))
    prev=sum(v for day,v in daily.items() if day<now-timedelta(days=7))
    return {
        "observed_at":now.isoformat(),
        "url":f"https://{language}.wikipedia.org/wiki/"+quote(title.replace(" ","_"),safe=""),
        "views_last_7d":last,
        "views_previous_7d":prev,
        "source_period_start":start.isoformat(),
        "source_period_end":end.isoformat(),
        "origin":"wikimedia_pageviews_api",
        "notice":"Interés por artículo, no volumen de Google Search ni demanda YouTube.",
    }
