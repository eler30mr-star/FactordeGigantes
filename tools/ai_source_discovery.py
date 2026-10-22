"""Descubrimiento observado -> descarga original -> pasajes, sin hechos aprobados.

Wikipedia aporta enlaces, nunca evidencia sustitutiva. Tavily/Exa aportan URLs,
nunca sus resúmenes como prueba. No se adivinan rutas ni nombres de compañías.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import re
import unicodedata
from urllib.parse import urlencode, urlsplit

from tools.ai_clients import ProviderError
from tools.pdf_sources import analyze_document, fetch_document_public
from tools.research_engine import fetch_public, validate_url

MAX_DOCUMENTS = 4
MAX_EVIDENCE = 10


def normalized(text):
    return "".join(c for c in unicodedata.normalize("NFKD", text.lower())
                   if not unicodedata.combining(c))


def primary_host(host):
    host = host.lower().rstrip(".")
    return host.endswith((".gov", ".gov.uk", ".gob.mx", ".gob.es")) or host in {
        "sec.gov", "justice.gov", "fda.gov", "govinfo.gov", "boe.es",
        "cnmv.es", "ftc.gov", "eur-lex.europa.eu", "curia.europa.eu"}


def selection_identity(selection):
    if not isinstance(selection, dict):
        raise ValueError("Selección D1 requerida")
    qid = selection.get("selected_wikidata_id")
    queue = selection.get("research_queue") or {}
    if qid is None:
        return None, None
    if not re.fullmatch(r"Q[1-9][0-9]*", str(qid)) or queue.get("wikidata_id") != qid:
        raise ValueError("Identidad de investigación no coincide con D1")
    title = queue.get("title") or queue.get("company")
    if not isinstance(title, str) or not 3 <= len(title.strip()) <= 130:
        raise ValueError("Falta nombre canónico en selección D1")
    return qid, title.strip()


def wikipedia_links(title, *, fetcher=fetch_public):
    url = "https://en.wikipedia.org/w/api.php?" + urlencode({
        "action": "parse", "page": title, "prop": "externallinks",
        "format": "json", "redirects": "1"})
    raw, resolved, mime = fetcher(url, timeout=12)
    if urlsplit(resolved).hostname != "en.wikipedia.org" or "json" not in mime:
        raise ValueError("Respuesta de descubrimiento inesperada")
    data = json.loads(raw)
    if not isinstance(data, dict) or not isinstance(data.get("parse"), dict):
        raise ValueError("Descubrimiento sin artículo")
    links = (data.get("parse") or {}).get("externallinks", [])
    if not isinstance(links, list):
        raise ValueError("Lista de enlaces inválida")
    return [{"url": link if isinstance(link, str) else link.get("*"),
             "title": "Referencia externa observada en Wikipedia",
             "discovered_by": "wikipedia_external_links"}
            # Parse devuelve enlaces ordenados por URL. Cortar antes de ordenar
            # por relevancia puede excluir autoridades situadas al final.
            for link in links[:800] if isinstance(link, (str, dict))]


def discover_sources(selection, *, clients, wiki_fetcher=fetch_public,
                     document_fetcher=fetch_document_public):
    qid, title = selection_identity(selection)
    day = datetime.now(timezone.utc).date().isoformat()
    out = {"schema": "fdg_ai_sources_v1", "collected_on": day,
           "selected_wikidata_id": qid, "company": title, "evidence_manifest": [],
           "source_documents": [], "stages": [], "facts_verified_automatically": 0,
           "ready_for_script": False, "ready_for_youtube": False,
           "publication_authorized": False}
    if not qid:
        out["status"] = "skipped_no_selection"
        return out
    leads = []
    try:
        leads.extend(wikipedia_links(title, fetcher=wiki_fetcher))
        out["stages"].append({"provider": "wikipedia", "role": "discover",
                              "status": "success", "result_count": len(leads)})
    except (OSError, ValueError, TypeError, KeyError):
        out["stages"].append({"provider": "wikipedia", "role": "discover",
                              "status": "source_unavailable"})
    queries = [f'"{title}" regulator court complaint financial statements',
               f'"{title}" history annual report investigation original documents']
    for provider in ("tavily", "exa"):
        found = []
        try:
            for query in queries:
                found.extend(clients.search(provider, query))
            state = {"status": "success", "result_count": len(found)}
        except ProviderError as exc:
            state = {"status": exc.code}
        leads.extend(found)  # Conservar primera consulta aunque falle la segunda.
        out["stages"].append({"provider": provider, "role": "discover", **state})
    seen, eligible = set(), []
    for lead in leads:
        try:
            url = lead.get("url")
            validate_url(url)
            # URL completa observada, sin fragmentos y sin credenciales.
            url = url.split("#", 1)[0]
            if url in seen:
                continue
            seen.add(url)
            eligible.append({**lead, "url": url})
        except (ValueError, TypeError):
            continue
    # Priorizar autoridades y documentos del tema. No usar la posición del buscador
    # como verdad; se conserva el proveedor que descubrió cada URL.
    generic = {"the", "and", "company", "corporation", "group", "holding", "holdings",
               "inc", "limited", "ltd", "llc", "empresa", "compania", "grupo", "sociedad"}
    words = [w for w in re.findall(r"\w+", normalized(title)) if len(w) >= 3 and w not in generic]
    def mentions(text):
        tokens = set(re.findall(r"\w+", normalized(text)))
        return normalized(title) in normalized(text) or any(w in tokens for w in words)
    def rank(lead):
        parsed = urlsplit(lead["url"])
        relevant = any(w in normalized(parsed.path) for w in words)
        return (-int(primary_host(parsed.hostname)), -int(relevant),
                -int(parsed.path.lower().endswith(".pdf")), lead["url"])
    per_host = Counter()
    for lead in sorted(eligible, key=rank):
        if len(out["source_documents"]) >= MAX_DOCUMENTS:
            break
        host = urlsplit(lead["url"]).hostname
        if per_host[host] >= 2:
            continue
        per_host[host] += 1
        record = {**lead, "status": "fetch_failed"}
        try:
            raw, resolved, mime = document_fetcher(lead["url"], timeout=12)
            validate_url(resolved)
            if primary_host(host) and not primary_host(urlsplit(resolved).hostname):
                raise ValueError("Redirección fuera de autoridad pública")
            analysis = analyze_document(raw, mime, pdf_max_pages=350, pdf_scan_pages=12)
            record.update({"bytes_read": len(raw), "mime": mime,
                           "readable_blocks": len(analysis["blocks"]),
                           "raw_prefix_hex": raw[:4].hex(),
                           "entity_name_in_payload": normalized(title) in normalized(raw.decode("utf-8", errors="ignore")),
                           "first_block_preview": str(next(iter(analysis["blocks"]), ""))[:160]})
            digest = hashlib.sha256(raw).hexdigest()
            fragments = []
            for index, block in enumerate(analysis["blocks"]):
                text = " ".join(block.split())
                if len(text) < 90 or not mentions(text):
                    continue
                # Mantener el nombre en el fragmento, incluso si aparece al final.
                start = next((m.start() for m in re.finditer(r"\b\w+", text)
                              if any(normalized(m.group()).startswith(w) for w in words)), 0)
                excerpt = text[max(0, start - 80):max(0, start - 80) + 320]
                if len(excerpt) < 90:
                    excerpt = text[-320:]
                fragments.append({"id": "", "wikidata_id": qid, "company": title,
                    "url": resolved, "document_sha256": digest,
                    "page": analysis["page_map"][index], "block_index": index,
                    "excerpt": excerpt, "source_id": qid + "-observed-document",
                    "claim_id": "documentary_candidate",
                    "source_class": "public_authority_candidate" if primary_host(urlsplit(resolved).hostname)
                                    else "public_document_candidate"})
                if len(fragments) >= 3:
                    break
            record.update({"status": "text_extracted" if fragments else "no_relevant_passages",
                           "resolved_url": resolved, "sha256": digest,
                           "pages_total": analysis["total_pages"],
                           "full_document_text_read": analysis["type"] != "pdf" or analysis["total_pages"] <= 12})
            out["evidence_manifest"].extend(fragments)
        except (OSError, ValueError, TypeError, KeyError, ImportError, RuntimeError) as exc:
            record["status"] = "fetch_failed"
            record["error_type"] = type(exc).__name__
        out["source_documents"].append(record)
    out["evidence_manifest"] = [{**e, "id": f"E{i+1:03d}"}
                                for i, e in enumerate(out["evidence_manifest"][:MAX_EVIDENCE])]
    out["status"] = "sources_collected" if out["evidence_manifest"] else "skipped_no_documentary_evidence"
    return out
