"""Persistencia SQLite/D1-compatible del descubridor; sin writes remotos.

Se ejecuta primero localmente para garantizar que migración 0004 sea aditiva,
idempotente y mantenga datos históricamente fechados. No aprueba publicaciones.
"""
from __future__ import annotations
import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from urllib.parse import urlsplit

QID=re.compile(r"^Q[1-9][0-9]*$")
WIKI_PROJECT=re.compile(r"^(es|en)\.wikipedia$")
METHOD="wikimedia_wikidata_company_discovery_v1"


def validated_url(value):
    if not isinstance(value,str) or len(value)>1300:
        raise ValueError("URL inválida")
    parts=urlsplit(value)
    if parts.scheme!="https" or not parts.hostname or parts.username or parts.password:
        raise ValueError("Solo URLs HTTPS")
    return value


def import_market_report(connection, report):
    if not isinstance(report,dict) or report.get("method")!=METHOD:
        raise ValueError("Este importador solo admite informes de descubrimiento reconocidos")
    candidates=report.get("candidates")
    if not isinstance(candidates,list) or len(candidates)>24:
        raise ValueError("Candidatas fuera de presupuesto")
    collection=report.get("collected_on")
    observed=report.get("data_day")
    date.fromisoformat(collection)
    date.fromisoformat(observed)
    if observed>collection or report.get("company_candidates_count")!=len(candidates):
        raise ValueError("Metadatos del radar inconsistentes")
    fingerprint=hashlib.sha256(json.dumps(report,ensure_ascii=False,sort_keys=True,
                                           separators=(",",":")).encode("utf-8")).hexdigest()
    run_id="market-"+fingerprint[:24]
    count_signals=0
    count_windows=0
    # Python sqlite3 y Cloudflare D1 utilizan el mismo SQL de estas tablas;
    # la transacción protege la integridad local; la ejecución remota D1 es
    # parte de una etapa futura que requerirá endpoint autenticado.
    with connection:
        connection.execute(
            "INSERT OR IGNORE INTO market_runs(id,collection_day,data_day,source_method,detected_count,study_complete) VALUES (?,?,?,?,?,0)",
            (run_id,collection,observed,METHOD,len(candidates)),
        )
        seen=set()
        for row in candidates:
            if not isinstance(row,dict):
                raise ValueError("Entidad malformada")
            qid=row.get("wikidata_id")
            title=row.get("topic")
            if not isinstance(qid,str) or not QID.fullmatch(qid) or qid in seen or not isinstance(title,str) or not 3<=len(title)<=130:
                raise ValueError("ID y nombre de empresa inválidos o duplicados")
            seen.add(qid)
            website=row.get("official_website_candidate")
            if website is not None:
                validated_url(website)
            connection.execute(
                """INSERT INTO market_entities(wikidata_id,title,first_seen,last_seen,official_website_candidate)
                   VALUES(?,?,?,?,?)
                   ON CONFLICT(wikidata_id) DO UPDATE SET
                   title=excluded.title,
                   last_seen=MAX(last_seen,excluded.last_seen),
                   official_website_candidate=COALESCE(excluded.official_website_candidate,official_website_candidate),
                   updated_at=datetime('now')""",
                (qid,title,collection,collection,website),
            )
            signals=row.get("discovery_signals")
            if not isinstance(signals,list) or not 1<=len(signals)<=4:
                raise ValueError("Entidad sin señal de descubrimiento")
            for signal in signals:
                if not isinstance(signal,dict):
                    raise ValueError("Señal malformada")
                project=signal.get("project")
                day=signal.get("observed_on")
                rank=signal.get("rank")
                views=signal.get("views")
                url=validated_url(signal.get("url"))
                if not isinstance(project,str) or not WIKI_PROJECT.fullmatch(project) or date.fromisoformat(day)>date.fromisoformat(collection):
                    raise ValueError("Proveedor de páginas o fecha inválidos")
                if urlsplit(url).hostname != project+".org":
                    raise ValueError("Dominio de señal diferente del proyecto")
                if type(rank) is not int or rank<1 or type(views) is not int or views<0:
                    raise ValueError("Métrica de página inválida")
                connection.execute(
                    """INSERT INTO market_pageview_observations
                       (wikidata_id,project,observation_day,rank,top_day_views,source_url,run_id)
                       VALUES(?,?,?,?,?,?,?)
                       ON CONFLICT(wikidata_id,project,observation_day)
                       DO UPDATE SET rank=excluded.rank,top_day_views=excluded.top_day_views,
                                     source_url=excluded.source_url,run_id=excluded.run_id""",
                    (qid,project,day,rank,views,url,run_id),
                )
                count_signals+=1
            interest=row.get("wikipedia_interest")
            if interest is not None and row.get("interest_14d_status")=="measured":
                if not isinstance(interest,dict):
                    raise ValueError("Serie de 14 días inválida")
                starts=interest.get("source_period_start")
                ends=interest.get("source_period_end")
                window_url=validated_url(interest.get("url"))
                measured=interest.get("observed_at")
                start_day=date.fromisoformat(starts)
                end_day=date.fromisoformat(ends)
                observed_day=date.fromisoformat(measured)
                if (end_day-start_day).days!=13 or (observed_day-end_day).days not in (1,2):
                    raise ValueError("Ventana de interés incompleta o incorrecta")
                last=interest.get("views_last_7d")
                previous=interest.get("views_previous_7d")
                if type(last) is not int or last<0 or type(previous) is not int or previous<0:
                    raise ValueError("Vistas de la ventana inválidas")
                if urlsplit(window_url).hostname not in ("en.wikipedia.org","es.wikipedia.org"):
                    raise ValueError("Serie de Wikimedia con host inesperado")
                connection.execute(
                    """INSERT INTO market_interest_windows
                       (wikidata_id,observed_at,source_url,period_start,period_end,
                        views_last_7d,views_previous_7d,run_id)
                       VALUES(?,?,?,?,?,?,?,?)
                       ON CONFLICT(wikidata_id,observed_at,source_url)
                       DO UPDATE SET views_last_7d=excluded.views_last_7d,
                         views_previous_7d=excluded.views_previous_7d,run_id=excluded.run_id""",
                    (qid,measured,window_url,starts,ends,last,previous,run_id),
                )
                count_windows+=1
    return {
        "run_id":run_id,"entities_seen":len(candidates),
        "pageview_observations_upserted":count_signals,
        "interest_windows_upserted":count_windows,
        "remote_d1_write_performed":False,
        "market_study_complete":False,
        "youtube_publication_authorized":False,
    }


def main():
    p=argparse.ArgumentParser(description="Guardar expediente de radar a SQLite local, contrato compatible D1")
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--database",type=Path,required=True)
    p.add_argument("--migrations-dir",type=Path,default=Path("migrations"))
    args=p.parse_args()
    data=json.loads(args.input.read_text(encoding="utf-8"))
    args.database.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(args.database) as db:
        db.execute("PRAGMA foreign_keys=ON")
        # Demo local: usa 0004 como schema de mercado autónomo. En D1 remoto
        # se aplicará mediante las migraciones del Worker cuando se verifique.
        db.executescript((args.migrations_dir/"0004_market_intelligence.sql").read_text(encoding="utf-8"))
        result=import_market_report(db,data)
    print("RADAR_HISTORICO:",result["entities_seen"],"empresas,",result["interest_windows_upserted"],
          "series de 14 días; D1 remoto escrito:",result["remote_d1_write_performed"])


if __name__=="__main__":
    main()
