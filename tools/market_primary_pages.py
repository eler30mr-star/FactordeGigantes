"""Rastrea páginas corporativas de informes/inversionistas enlazadas en P856.

Amplía fuentes SIN usar LLM, sin adivinar rutas ni descargar páginas externas.
Descargador compartido valida HTTPS, DNS público y redirecciones; tras descargar
se exige el MISMO hostname que el sitio corporativo de origen.
Máximo tres páginas HTML en total. Solo extracto breve, URL y hash SHA-256.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

from tools.market_official_evidence import select_documentary_excerpt, documentary_excerpts
from tools.official_document_links import find_official_document_links
from tools.research_engine import fetch_public, extract_blocks, validate_url

MAX_PAGES = 3
MAX_SOURCE_LINKS = 4


def eligible_pages(report):
    if (not isinstance(report, dict) or
            report.get("provider") != "wikidata_p856_safe_official_fetch_v1" or
            report.get("primary_facts_verified") != 0 or
            report.get("ready_for_youtube") is not False):
        raise ValueError("Solo enlaces corporativos detectados por el radar")
    selected = []
    seen = set()
    for company in report.get("evidence", [])[:3]:
        if not isinstance(company, dict) or company.get("status") != "candidate_page_readable":
            continue
        origin = company.get("resolved_url")
        try:
            validate_url(origin)
            host = urlsplit(origin).hostname
        except (ValueError,TypeError):
            continue
        for candidate in company.get("document_link_candidates", [])[:MAX_SOURCE_LINKS]:
            if (not isinstance(candidate,dict) or
                    candidate.get("document_fetched") is not False or
                    candidate.get("ownership_verified") is not False):
                continue
            u = candidate.get("url")
            try:
                validate_url(u)
                parsed = urlsplit(u)
                if (parsed.hostname != host or parsed.path.lower().endswith(".pdf") or
                        not any(x in parsed.path.lower() for x in
                                ("invest", "financ", "result", "report", "informe", "annual")) or
                        u == origin or u in seen):
                    continue
            except (ValueError,TypeError):
                continue
            seen.add(u)
            selected.append({
                "wikidata_id":company["wikidata_id"],
                "company":company["company"],
                "origin_url":origin,
                "url":u,
            })
            if len(selected) >= MAX_PAGES:
                return selected
    return selected


def collect_primary_pages(report, *, fetcher=fetch_public):
    choices=eligible_pages(report)
    pages=[]
    for row in choices:
        result={**row,"status":"unreachable","resolved_url":None,
                "content_sha256":None,"short_excerpt":None,
                "excerpt_quality":None,
                "facts_verified":0,"rights_verified":False}
        try:
            body,resolved,mime=fetcher(row["url"],timeout=12)
            validate_url(resolved)
            if urlsplit(resolved).hostname != urlsplit(row["origin_url"]).hostname:
                raise ValueError("La redirección sale del dominio corporativo")
            if "html" not in mime.lower() or not isinstance(body,bytes) or len(body)>750_000:
                raise ValueError("Página corporativa sin HTML admitido")
            blocks=extract_blocks(body,mime)
            excerpt,quality=select_documentary_excerpt(blocks)
            result.update({
                "status":"excerpt_candidate" if quality=="documentary_candidate" else "low_information",
                "resolved_url":resolved,
                "content_sha256":hashlib.sha256(body).hexdigest(),
                "short_excerpt":excerpt,
                "excerpt_quality":quality,
                "excerpt_candidates":documentary_excerpts(blocks),
                "document_link_candidates":find_official_document_links(resolved,body,mime=mime),
            })
        except (OSError,TimeoutError,ValueError,TypeError,UnicodeError,KeyError) as exc:
            result["error_type"]=type(exc).__name__
        pages.append(result)
    return {
        "provider":"official_investor_pages_v1",
        "collected_on":report["collected_on"],
        "attempted":len(pages),
        "usable":sum(p["status"]=="excerpt_candidate" for p in pages),
        "pages":pages,
        "facts_verified":0,
        "rights_verified":False,
        "ready_for_script":False,
        "ready_for_youtube":False,
        "warning":"Páginas corporativas candidatas, sin corroboración independiente ni derechos audiovisuales."
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--official",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    report=collect_primary_pages(json.loads(args.official.read_text(encoding="utf-8")))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("PAGINAS_CORPORATIVAS_HIJAS:",report["attempted"],
          "EXTRACTOS_UTILES:",report["usable"],"HECHOS_VERIFICADOS:",report["facts_verified"])


if __name__=="__main__":
    main()

