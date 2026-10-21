"""Radar de mercado de Factor de Gigantes: clasificación con datos verificables.

NO inventa tendencias ni genera listas de temas por ocurrencia. Recibe
observaciones REALES de colectores externos; si faltan, declara "insuficiente".
La fórmula es una heurística explicable, NO una predicción de visitas.
"""
from __future__ import annotations

import argparse
from datetime import date
from decimal import Decimal
import json
import math
from pathlib import Path
import re
from statistics import median
from urllib.parse import urlsplit

CATEGORIES = {
    "historia_empresarial", "innovacion", "disrupcion",
    "transformacion_empresarial", "industria_tecnologica",
}
VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
MAX_CANDIDATES = 30
MAX_VIDEO_SAMPLES = 30
MAX_OBSERVATION_AGE_DAYS = 7


def verified_https(url, allowed_hosts=None):
    if not isinstance(url, str) or len(url) > 1700:
        raise ValueError("URL de fuente ausente o excesiva")
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Las fuentes deben ser HTTPS sin credenciales")
    host = parsed.hostname.lower()
    if allowed_hosts and host not in allowed_hosts:
        raise ValueError("Dominio de señal de mercado inesperado")
    return url


def observed_within(date_string, now):
    if not isinstance(date_string, str):
        raise ValueError("Fecha de observación faltante")
    day = date.fromisoformat(date_string)
    age = (now - day).days
    if age < 0 or age > MAX_OBSERVATION_AGE_DAYS:
        raise ValueError("Señal de mercado futura o caducada")
    return day


def positive_int(value, *, minimum=0, maximum=10**12):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError("Estadística fuera de intervalo o no numérica")
    return value


def youtube_signal(value, now):
    if not isinstance(value, dict):
        raise ValueError("Falta observación real de YouTube")
    observed_within(value.get("observed_at"), now)
    samples = value.get("videos")
    if not isinstance(samples, list) or not 3 <= len(samples) <= MAX_VIDEO_SAMPLES:
        raise ValueError("YouTube requiere entre 3 y 30 videos medidos")
    velocities = []
    seen = set()
    for video in samples:
        if not isinstance(video, dict) or not VIDEO_ID.fullmatch(str(video.get("video_id", ""))):
            raise ValueError("Video de YouTube inválido")
        key = video["video_id"]
        if key in seen:
            raise ValueError("No duplicar videos en la muestra")
        seen.add(key)
        verified_https(video.get("url"), {"www.youtube.com", "youtube.com", "youtu.be"})
        views = positive_int(video.get("view_count"))
        published = date.fromisoformat(video["published_at"])
        elapsed = (now - published).days
        if elapsed < 0 or elapsed > 90:
            raise ValueError("La muestra requiere videos de los últimos 90 días")
        velocities.append(views / max(1, elapsed))
    # uploads_recent es el número observado por la búsqueda, no el mercado completo.
    uploads = positive_int(value.get("sampled_recent_uploads"), maximum=100)
    return {
        "median_daily_views": round(median(velocities), 2),
        "sample_size": len(samples),
        "sampled_recent_uploads": uploads,
        "observed_at": value["observed_at"],
        "interpretation": "Muestra observada, no demanda total ni alcance garantizado.",
    }


def pageview_signal(value, now):
    if not isinstance(value, dict):
        raise ValueError("Falta señal independiente de interés")
    observed_within(value.get("observed_at"), now)
    verified_https(value.get("url"), {"en.wikipedia.org", "es.wikipedia.org"})
    current = positive_int(value.get("views_last_7d"))
    previous = positive_int(value.get("views_previous_7d"))
    if previous == 0:
        trend_ratio = None
    else:
        trend_ratio = round(current / previous, 4)
    return {
        "views_last_7d": current,
        "views_previous_7d": previous,
        "growth_ratio": trend_ratio,
        "observed_at": value["observed_at"],
        "interpretation": "Interés en Wikipedia como proxy, NO volumen de búsquedas ni demanda en YouTube.",
    }


def rank_market(candidates, *, today, previously_published=()):
    if isinstance(today, str):
        today = date.fromisoformat(today)
    if not isinstance(today, date):
        raise ValueError("Fecha de análisis obligatoria")
    if not isinstance(candidates, list) or len(candidates) > MAX_CANDIDATES:
        raise ValueError("Máximo 30 candidatos con procedencia")
    published = {str(p).casefold().strip() for p in previously_published}
    results = []
    for item in candidates:
        topic = item.get("topic") if isinstance(item, dict) else None
        if not isinstance(topic, str) or not 4 <= len(topic.strip()) <= 130:
            raise ValueError("Nombre de candidato inválido")
        topic = topic.strip()
        category = item.get("category")
        if category not in CATEGORIES:
            raise ValueError("Tema fuera de las categorías del canal")
        if not isinstance(item.get("story_angle"), str) or len(item["story_angle"].strip()) < 24:
            raise ValueError("Falta ángulo documental")
        reasons = []
        yt = None
        wiki = None
        try:
            yt = youtube_signal(item.get("youtube_market"), today)
        except (ValueError, KeyError, TypeError) as exc:
            reasons.append("youtube_no_comparable: " + type(exc).__name__)
        try:
            wiki = pageview_signal(item.get("wikipedia_interest"), today)
        except (ValueError, KeyError, TypeError) as exc:
            reasons.append("independent_interest_unavailable: " + type(exc).__name__)
        documents = item.get("primary_documents", [])
        hosts = set()
        if not isinstance(documents, list) or len(documents) > 12:
            raise ValueError("Fuentes documentales de formato inválido")
        for doc in documents:
            if not isinstance(doc, dict):
                continue
            try:
                link = verified_https(doc.get("url"))
                if doc.get("document_type") not in {"report", "filing", "primary_press_release", "academic", "government"}:
                    continue
                hosts.add(urlsplit(link).hostname.lower())
            except ValueError:
                continue
        if not hosts:
            reasons.append("sin_fuente_primaria_identificada")
        if topic.casefold() in published:
            reasons.append("tema_ya_publicado")
        if yt is None or wiki is None or not hosts or topic.casefold() in published:
            results.append({
                "topic": topic, "category": category,
                "eligible_for_investigation": False,
                "market_score": None,
                "reasons": reasons,
                "youtube": yt, "wikipedia": wiki,
                "primary_host_count": len(hosts),
            })
            continue
        # Ponderación HEURÍSTICA, auditable; no equivale a previsión de reproducciones.
        demand = min(100.0, 25 * math.log10(1 + yt["median_daily_views"]))
        ratio = wiki["growth_ratio"]
        momentum = 20.0 if ratio is None else max(0., min(100., 50 + 35 * math.log2(max(.01, ratio))))
        # Más competencia reciente puede dificultar diferenciar un documental nuevo.
        scarcity = max(0., 100.0 - 4.0 * yt["sampled_recent_uploads"])
        traceability = min(100., 40.0 + 30.0 * len(hosts))
        novelty = 75.0  # Punto neutro: requiere métricas del propio canal para ajustarlo.
        score = round(.35 * demand + .25 * momentum + .15 * scarcity +
                      .15 * traceability + .10 * novelty, 2)
        results.append({
            "topic": topic,
            "category": category,
            "story_angle": item["story_angle"].strip(),
            "eligible_for_investigation": True,
            "market_score": score,
            "score_components": {
                "youtube_velocity": round(demand, 2),
                "wikipedia_momentum": round(momentum, 2),
                "competition_proxy": round(scarcity, 2),
                "primary_document_availability": round(traceability, 2),
                "novelty_neutral_pending_channel_analytics": novelty,
            },
            "youtube": yt, "wikipedia": wiki,
            "primary_host_count": len(hosts),
            "reasons": [
                "Candidato para investigación, NO afirmación factual aprobada.",
                "Los datos de una muestra no predicen visitas ni viralidad.",
            ],
        })
    results.sort(key=lambda r: (not r["eligible_for_investigation"],
                                -(r["market_score"] or 0), r["topic"].casefold()))
    return {
        "project": "Factor de Gigantes",
        "evaluated_at": today.isoformat(),
        "method": "market_radar_heuristic_v1",
        "candidate_count": len(candidates),
        "qualified_count": sum(x["eligible_for_investigation"] for x in results),
        "ranking": results,
        "selected_for_research": next((x["topic"] for x in results if x["eligible_for_investigation"]), None),
        "realtime_verified": False,
        "data_quality_note": "Clasificación solo sobre datos suministrados por colectores. Su origen debe quedar auditado.",
        "research_automatic": False,
        "script_automatic": False,
        "video_completed": False,
        "youtube_publication_authorized": False,
    }


def main():
    p = argparse.ArgumentParser(description="Priorizar temas por datos, nunca por imaginación del modelo")
    p.add_argument("--input", required=True, type=Path,
                   help="Candidatos reunidos por colectores con estadísticas fechadas")
    p.add_argument("--out", type=Path, default=Path("dist/radar/ESTUDIO_MERCADO.json"))
    args = p.parse_args()
    source = json.loads(args.input.read_text(encoding="utf-8"))
    result = rank_market(source["candidates"], today=source["observed_at"],
                         previously_published=source.get("previously_published", []))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("RADAR:", result["candidate_count"], "evaluados,", result["qualified_count"],
          "elegibles; seleccionado:", result["selected_for_research"] or "ninguno")
    if result["selected_for_research"] is None:
        raise SystemExit("Mercado sin datos suficientes: se requiere recopilar señales reales.")


if __name__ == "__main__":
    main()
