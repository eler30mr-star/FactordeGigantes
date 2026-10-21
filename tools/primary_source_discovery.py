"""Descubrimiento acotado de posibles fuentes oficiales a partir de un tema.

MediaWiki -> Wikidata P856 (sitio oficial) -> URL HTTPS pública.
El sitio de la organización es una fuente PRIMARIA potencial, pero P856
ni un extracto de su portada prueba automáticamente un hecho empresarial.
No se consulta ninguna API de pago ni se descarga contenido audiovisual.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlencode

from tools.research_engine import (
    MAX_EXCERPT_CHARS, discover_wikipedia, extract_blocks,
    fetch_public, validate_url,
)

WIKIPEDIA_API = "https://es.wikipedia.org/w/api.php"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
QID = re.compile(r"^Q[1-9][0-9]{0,12}$")


def lookup_wikidata_id(title, fetcher=fetch_public):
    if not isinstance(title, str) or not 1 <= len(title) <= 140:
        raise ValueError("Título de la enciclopedia inválido")
    url = WIKIPEDIA_API + "?" + urlencode({
        "action": "query", "prop": "pageprops", "ppprop": "wikibase_item",
        "titles": title, "format": "json", "formatversion": "2"
    })
    raw, _, _ = fetcher(url)
    data = json.loads(raw.decode("utf-8"))
    pages = data.get("query", {}).get("pages", [])
    if not isinstance(pages, list) or len(pages) != 1:
        return None
    qid = pages[0].get("pageprops", {}).get("wikibase_item")
    return qid if isinstance(qid, str) and QID.fullmatch(qid) else None


def wikidata_official_url(qid, fetcher=fetch_public):
    if not isinstance(qid, str) or not QID.fullmatch(qid):
        raise ValueError("Wikidata ID inválido")
    url = WIKIDATA_API + "?" + urlencode({
        "action": "wbgetentities", "ids": qid, "props": "claims",
        "format": "json", "formatversion": "2",
    })
    raw, _, _ = fetcher(url)
    item = json.loads(raw.decode("utf-8")).get("entities", {}).get(qid, {})
    claims = item.get("claims", {}).get("P856", [])
    urls = []
    for claim in claims[:4]:
        snak = claim.get("mainsnak", {})
        val = snak.get("datavalue", {}).get("value")
        if not isinstance(val, str):
            continue
        try:
            url = validate_url(val)
        except (ValueError, OverflowError):
            continue
        if url not in urls:
            urls.append(url)
    return urls[:2]


def discover_official(topic, fetcher=fetch_public, *, max_entities=2):
    if not isinstance(topic, str) or not 3 <= len(topic.strip()) <= 130:
        raise ValueError("Tema inválido")
    max_entities = max(1, min(3, int(max_entities)))
    suggestions = discover_wikipedia(topic, fetcher=fetcher)
    results = []
    seen_sites = set()
    # Un tema puede remitir primero a un producto y luego a su empresa.
    # Analizar hasta cinco entidades para hallar hasta max_entities sitios distintos.
    for suggestion in suggestions[:min(5, max_entities * 3)]:
        title = suggestion["title"]
        record = {
            "title": title, "encyclopedia_url": suggestion["url"],
            "wikidata_item": None, "site_url": None,
            "status": "no_official_link_found", "source_class": "potential_official_primary",
            "confirmed_primary": False, "facts_verified": 0,
        }
        try:
            qid = lookup_wikidata_id(title, fetcher=fetcher)
            if qid:
                record["wikidata_item"] = qid
                official = wikidata_official_url(qid, fetcher=fetcher)
                for official_url in official:
                    if official_url in seen_sites:
                        continue
                    seen_sites.add(official_url)
                    record["site_url"] = official_url
                    record["status"] = "official_url_candidate"
                    try:
                        body, resolved, mime = fetcher(official_url)
                        # Fetchers used in tests and public provider must return HTTPS.
                        validate_url(resolved)
                        blocks = extract_blocks(body, mime)
                        record.update({
                            "status": "official_page_fetched" if blocks else "official_page_unreadable",
                            "resolved_url": resolved,
                            "content_sha256": hashlib.sha256(body).hexdigest(),
                            "readable_blocks": len(blocks),
                            "short_excerpt": blocks[0][:MAX_EXCERPT_CHARS] if blocks else "",
                        })
                    except (OSError, ValueError, TimeoutError, UnicodeError, json.JSONDecodeError) as exc:
                        record["fetch_error_type"] = type(exc).__name__
                    break
        except (OSError, ValueError, TimeoutError, UnicodeError, json.JSONDecodeError) as exc:
            record["status"] = "discovery_unavailable"
            record["error_type"] = type(exc).__name__
        results.append(record)
        if len(seen_sites) >= max_entities:
            break
    return {
        "product": "Factor de Gigantes",
        "topic": topic,
        "method": "mediawiki_to_wikidata_p856",
        "sources": results,
        "official_candidates": sum(r["site_url"] is not None for r in results),
        "automatic_fact_verification": False,
        "automatic_rights_verification": False,
        "needs_independent_sources": True,
        "publication_authorized": False,
        "warning": (
            "El campo P856 es una pista de un sitio corporativo o de otra entidad; "
            "puede estar desactualizado o representar a otra organización. "
            "Confirmar entidad, autoría, hechos, fechas, contexto y licencias."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description="Encontrar posibles fuentes corporativas oficiales")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--out", type=Path, default=Path("dist/investigacion"))
    parser.add_argument("--max-entities", type=int, default=2)
    opts = parser.parse_args()
    result = discover_official(opts.topic, max_entities=opts.max_entities)
    opts.out.mkdir(parents=True, exist_ok=True)
    dest = opts.out / "fuentes_oficiales_candidatas.json"
    dest.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("FUENTES_OFICIALES:", result["official_candidates"], "/",
          len(result["sources"]), "candidatas, 0 hechos aprobados", flush=True)


if __name__ == "__main__":
    main()
