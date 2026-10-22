"""Cruce autónomo de candidatas Wikimedia con YouTube Data API v3.

Usa únicamente empresas detectadas en el propio radar. Máximo 2 empresas x
2 regiones, una search.list y una videos.list por pareja (techo 4 búsquedas + 4 lecturas = 8 unidades en dos depósitos de cuota).
Jamás obtiene métricas privadas, autoriza documental ni invoca API sin permiso.
"""
from __future__ import annotations
import argparse
from datetime import date
import json
import os
from pathlib import Path
from statistics import median
import re
from tools.market_sources import collect_youtube

QID=re.compile(r"Q[1-9][0-9]*\Z")
REGIONS=("MX","ES")
MAX_CANDIDATES=2
MAX_QUERY_PAIRS=4
QUOTA_CAP=8


def choose_candidates(discovery):
    if not isinstance(discovery,dict) or discovery.get("method")!="wikimedia_wikidata_company_discovery_v1":
        raise ValueError("Se requiere informe de descubrimiento verificable")
    candidates=discovery.get("candidates")
    if not isinstance(candidates,list):
        raise ValueError("Sin candidatas validadas")
    picked=[]
    seen=set()
    for c in candidates:
        if not isinstance(c,dict): continue
        key=c.get("wikidata_id")
        title=c.get("topic")
        if not isinstance(key,str) or not QID.fullmatch(key) or key in seen or \
            not isinstance(title,str) or not 4<=len(title.strip())<=130:
            continue
        # Nunca promover Wikidata sin haber observado fuente concreta Wikimedia.
        signals=c.get("discovery_signals")
        if not isinstance(signals,list) or not signals or \
            not any(isinstance(s,dict) and s.get("source")=="wikimedia_daily_top_plus_wikidata_p31"
                    and str(s.get("url","")).startswith(("https://en.wikipedia.org/wiki/",
                                                          "https://es.wikipedia.org/wiki/")) for s in signals):
            continue
        seen.add(key)
        picked.append({"wikidata_id":key,"topic":title.strip()})
        if len(picked)==MAX_CANDIDATES:break
    return picked


def study(discovery, *, api_key, now=None, collector=collect_youtube):
    today=now or date.today()
    if isinstance(today,str):today=date.fromisoformat(today)
    if not isinstance(today,date):raise ValueError("Fecha inválida")
    selected=choose_candidates(discovery)
    # El reporte solo existe cuando se autoriza expresamente una cuota gratis.
    if not isinstance(api_key,str) or len(api_key)<20:
        raise RuntimeError("YOUTUBE_DATA_API_KEY ausente; no se realizará ningún consumo")
    if not selected:
        return {"state":"no_candidates","collected_on":today.isoformat(),"queries":[],"queries_attempted":0}
    queries=[]
    count=0
    for item in selected:
        for region in REGIONS:
            if count>=MAX_QUERY_PAIRS:break
            count+=1
            try:
                observed=collector(item["topic"],api_key=api_key,region=region,now=today)
                if observed.get("origin")!="youtube_data_api_v3_search_plus_videos" or \
                        observed.get("observed_at")!=today.isoformat():
                    raise ValueError("Procedencia YouTube insuficiente")
                videos=observed.get("videos",[])
                if not 3<=len(videos)<=10:raise ValueError("Muestra no comparable")
                ages=[max(1,(today-date.fromisoformat(v["published_at"])).days) for v in videos]
                velocities=[v["view_count"]/age for v,age in zip(videos,ages)]
                channel_ids={v["channel_id"] for v in videos if v.get("channel_id")}
                queries.append({
                    "wikidata_id":item["wikidata_id"],"topic":item["topic"],
                    "region":region,"observed_on":today.isoformat(),
                    "uploads_sampled":observed["sampled_recent_uploads"],
                    "sample_size":len(videos),"median_daily_views":round(median(velocities),2),
                    "distinct_channels":len(channel_ids),
                    "evidence_state":"observed_sample","videos":videos
                })
            except (ValueError,KeyError,TypeError,RuntimeError,ZeroDivisionError) as exc:
                # Los fallos son eventos, nunca métricas = 0 inventadas.
                queries.append({"wikidata_id":item["wikidata_id"],"topic":item["topic"],
                   "region":region,"observed_on":today.isoformat(),
                   "uploads_sampled":0,"sample_size":0,"median_daily_views":None,
                   "distinct_channels":0,"evidence_state":"insufficient_sample",
                   "error_type":type(exc).__name__,"videos":[]})
                if hasattr(exc,'category'):
                    queries[-1]['error_category']=exc.category
                    queries[-1]['http_status']=exc.http_status
                # Ante error de cuota, credencial o red detiene llamadas posteriores.
                if isinstance(exc,RuntimeError): break
        if queries and queries[-1].get("error_type") in {"RuntimeError","YoutubeApiError"}:break
    measured=sum(q["evidence_state"]=="observed_sample" for q in queries)
    return {
      "provider":"youtube_data_api_v3","collected_on":today.isoformat(),
      "candidate_count":len(selected),"region_count":len(REGIONS),
      "queries_attempted":count,"quota_units_max":min(QUOTA_CAP,2*count),
      "state":"measured" if measured==count and count==len(selected)*len(REGIONS) else "partial",
      "queries":queries,"complete_comparisons":measured,
      "market_study_complete":False,"research_automatic":False,
      "ready_for_script":False,"ready_for_youtube":False,
      "automatic_publication_allowed":False,
      "interpretation":"Muestra parcial de videos recientes, NO cuota real gastada, demanda total, retención, CTR ni garantía de visitas"
    }


def main():
    p=argparse.ArgumentParser(description="Medir competencia YouTube bajo presupuesto gratuito")
    p.add_argument("--discovery",type=Path,required=True)
    p.add_argument("--out",type=Path,default=Path("dist/radar/YOUTUBE_MUESTRAS_NO_CALIFICADAS.json"))
    a=p.parse_args()
    if os.getenv("YOUTUBE_MARKET_BUDGET_ENABLED")!="1":
        print("YOUTUBE_ESTUDIO_OMITIDO: permiso explícito de cuota gratuita no habilitado")
        return
    key=os.getenv("YOUTUBE_DATA_API_KEY","")
    if len(key)<20:
        print("YOUTUBE_ESTUDIO_OMITIDO: API key no configurada; cero llamadas")
        return
    report=study(json.loads(a.discovery.read_text(encoding="utf-8")),api_key=key)
    if report.get("state")=="no_candidates":
        print("YOUTUBE_ESTUDIO_OMITIDO: no hubo compañías verificadas en el radar")
        return
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("YOUTUBE_API_MUESTRAS:",report["complete_comparisons"],"de",report["queries_attempted"],
          "pares empresa-región; CUOTA_MAXIMA_ESTIMADA:",report["quota_units_max"],
          "APROBACION_PUBLICACION:",report["automatic_publication_allowed"])
    for q in report['queries']:
        print('YOUTUBE_MUESTRA:',q['wikidata_id'],q['region'],q['evidence_state'],
              'VIDEOS:',q['sample_size'],'ERROR:',q.get('error_category',q.get('error_type','ninguno')),
              'HTTP:',q.get('http_status'))


if __name__=="__main__":
    main()

