"""Descubrimiento observado -> descarga original -> pasajes, sin hechos aprobados.

Wikipedia aporta enlaces, nunca evidencia sustitutiva. Tavily/Exa aportan URLs,
nunca sus resúmenes como prueba. No se adivinan rutas ni nombres de compañías.
"""
from __future__ import annotations

from collections import Counter, deque
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import urlencode, urlsplit, urljoin

from tools.ai_clients import ProviderError
from tools.pdf_sources import analyze_document, fetch_document_public
from tools.research_engine import fetch_public, validate_url

MAX_DOCUMENTS = 8
MAX_PRIMARY_ATTEMPTS = 5
MAX_SECONDARY_ATTEMPTS = 5
MAX_PER_HOST = 1
MAX_EVIDENCE = 10
REGULATORY_HOSTS = frozenset(json.loads(
    (Path(__file__).resolve().parents[1] / "src/regulatory-authorities.json").read_text(encoding="utf-8")))


def discovery_only_host(host):
    host=(host or '').lower().rstrip('.')
    return any(host==domain or host.endswith('.'+domain)
               for domain in ('wikipedia.org','wikimedia.org','wikidata.org'))


def regulatory_host(host):
    """Autoridad candidata conocida; un repositorio .gov no es un regulador."""
    host = (host or "").lower().rstrip(".")
    return any(host == domain or host.endswith("." + domain) for domain in REGULATORY_HOSTS)


def research_targets(selection):
    targets = selection.get("prior_research_targets", [])
    allowed = {"only_one_document", "no_independent_domain", "no_regulatory_primary_document",
               "no_original_primary_document"}
    if not isinstance(targets, list) or len(targets) > 8:
        raise ValueError("Objetivos de contraste fuera del presupuesto")
    for target in targets:
        if (not isinstance(target, dict) or type(target.get("claim_index")) is not int or
                not 1 <= target["claim_index"] <= 8 or
                not isinstance(target.get("statement"), str) or not 10 <= len(target["statement"]) <= 650 or
                not isinstance(target.get("cited_urls"), list) or len(target["cited_urls"]) > 8 or
                not isinstance(target.get("gaps"), list) or any(g not in allowed for g in target["gaps"])):
            raise ValueError("Objetivo factual inválido")
        for url in target["cited_urls"]:
            validate_url(url)
    return targets


def document_references(raw, base):
    """Seguir sólo URLs de autoridades observadas en el documento descargado.

    El enlace aporta una pista, nunca prueba de un hecho. El lector público
    valida DNS y redirecciones al descargar; todo cuenta en el límite de ocho.
    """
    class Links(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.urls = []
        def handle_starttag(self, tag, attrs):
            if tag != "a" or len(self.urls) >= 12:
                return
            href = dict(attrs).get("href")
            if not href:
                return
            try:
                url = urljoin(base, href).split("#", 1)[0]
                validate_url(url)
            except (ValueError, TypeError):
                return
            if regulatory_host(urlsplit(url).hostname) and url not in self.urls:
                self.urls.append(url)
    parser = Links()
    parser.feed(raw.decode("utf-8", errors="replace"))
    return [{"url": url, "title": "Referencia original enlazada por el documento",
             "discovered_by": "document_citations", "discovered_from": base}
            for url in parser.urls]


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



def gdelt_articles(title, *, fetcher=fetch_public):
    """Una búsqueda pública sin clave para localizar medios realmente distintos.

    GDELT devuelve URL y titular, NO evidencia factual. No se conserva
    cobertura como prueba hasta descargar el artículo y comprobar su texto.
    Una petición por corrida; sin reintentos ni scraping de motores privados.
    """
    if not isinstance(title,str) or not 3<=len(title.strip())<=130:
        raise ValueError("Empresa canónica necesaria")
    phrase=" ".join(title.strip().split())
    if any(c in phrase for c in '"\\\n\r'):
        raise ValueError("Consulta de noticias no válida")
    query='"'+phrase+'"'
    endpoint="https://api.gdeltproject.org/api/v2/doc/doc?"+urlencode({
        "query":query,"mode":"artlist","format":"json",
        "maxrecords":"20","timespan":"1y","sort":"datedesc"})
    raw,resolved,mime=fetcher(endpoint,timeout=12)
    if urlsplit(resolved).hostname!="api.gdeltproject.org" or "json" not in mime.lower() or len(raw)>150_000:
        raise ValueError("Índice GDELT rechazado")
    data=json.loads(raw)
    articles=data.get("articles") if isinstance(data,dict) else None
    if not isinstance(articles,list) or len(articles)>20:
        raise ValueError("Respuesta GDELT sin artículos verificables")
    results=[]
    for row in articles:
        if not isinstance(row,dict):continue
        url=row.get("url")
        label=row.get("title")
        if not isinstance(url,str) or not isinstance(label,str):continue
        try:
            validate_url(url)
        except (ValueError,TypeError):
            continue
        results.append({"url":url,"title":label[:200],"discovered_by":"gdelt_doc_artlist",
                        "seendate":str(row.get("seendate",""))[:20]})
    return results


def discover_sources(selection, *, clients, wiki_fetcher=fetch_public,
                     document_fetcher=fetch_document_public,gdelt_fetcher=None):
    qid, title = selection_identity(selection)
    targets = research_targets(selection)
    day = datetime.now(timezone.utc).date().isoformat()
    out = {"schema": "fdg_ai_sources_v1", "collected_on": day,
           "selected_wikidata_id": qid, "company": title, "evidence_manifest": [],
           "source_documents": [], "stages": [], "facts_verified_automatically": 0,
           "ready_for_script": False, "ready_for_youtube": False,
           "publication_authorized": False}
    out["research_targets"] = targets
    if not qid:
        out["status"] = "skipped_no_selection"
        return out
    # La selección D1 informa qué enlaces ya fallaron y qué pasajes se
    # observaron anteriormente. Sólo usarlos para ampliar el dossier cuando
    # se consiga al menos UNA fuente nueva. Así evitamos gasto IA redundante.
    previous_urls = selection.get("prior_attempted_urls", [])
    expand_urls = selection.get("citation_expansion_urls", [])
    if not isinstance(expand_urls, list) or len(expand_urls) > 2:
        raise ValueError("Ampliación de referencias fuera del presupuesto")
    for url in expand_urls:
        validate_url(url)
    previous_passages = selection.get("prior_evidence_manifest", [])
    if (not isinstance(previous_urls,list) or len(previous_urls)>40 or
            not isinstance(previous_passages,list) or len(previous_passages)>4):
        raise ValueError("Historial de fuentes excede el presupuesto")
    for url in previous_urls:
        validate_url(url)
    previous_urls = set(previous_urls)
    preserved = []
    for passage in previous_passages:
        if (not isinstance(passage,dict) or passage.get("wikidata_id")!=qid or
                not isinstance(passage.get("url"),str) or
                not isinstance(passage.get("excerpt"),str) or
                len(passage["excerpt"])<90 or len(passage["excerpt"])>320 or
                not isinstance(passage.get("document_sha256"),str) or
                not re.fullmatch(r"[0-9a-f]{64}",passage["document_sha256"]) or
                passage.get("source_class") not in
                    {"potential_official_primary","potential_official_pdf",
                     "public_authority_candidate","public_document_candidate"}):
            raise ValueError("Fuente histórica D1 sin procedencia admitida")
        validate_url(passage["url"])
        if discovery_only_host(urlsplit(passage['url']).hostname):
            continue  # Históricos intactos; no reutilizar enciclopedias como prueba.
        if passage["source_class"] == "public_authority_candidate" and not regulatory_host(urlsplit(passage["url"]).hostname):
            passage = {**passage, "source_class": "public_document_candidate"}
        preserved.append(passage)
    leads = []
    leads.extend({"url": u, "title": "Extraer referencias originales del documento ya citado",
                  "discovered_by": "d1_document_citation_expansion"} for u in expand_urls)
    try:
        wiki_leads = wikipedia_links(title, fetcher=wiki_fetcher)
        leads.extend(wiki_leads)
        out["stages"].append({"provider": "wikipedia", "role": "discover",
                              "status": "success", "result_count": len(wiki_leads)})
    except (OSError, ValueError, TypeError, KeyError):
        out["stages"].append({"provider": "wikipedia", "role": "discover",
                              "status": "source_unavailable"})
    # Fuente abierta adicional; ninguna solicitud en fixtures aislados.
    if gdelt_fetcher is not None:
        try:
            fresh=gdelt_articles(title,fetcher=gdelt_fetcher)
            leads.extend(fresh)
            out["stages"].append({"provider":"gdelt","role":"discover",
                                  "status":"success","result_count":len(fresh)})
        except (OSError,ValueError,TypeError,KeyError,TimeoutError):
            out["stages"].append({"provider":"gdelt","role":"discover",
                                  "status":"source_unavailable"})
    queries = [f'"{title}" regulator court complaint financial statements',
               f'"{title}" history annual report investigation original documents']
    if targets:
        # Siguen siendo dos búsquedas por proveedor: sustituir, no multiplicar.
        queries = [f'"{title}" ' + t["statement"][:220] for t in targets[:2]]
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
    out["stages"].append({"provider":"d1_history","role":"avoid_duplicate_sources",
                          "status":"success" if previous_urls else "empty",
                          "result_count":len(previous_urls)})
    seen, eligible = set(), []
    for lead in leads:
        try:
            url = lead.get("url")
            validate_url(url)
            # URL completa observada, sin fragmentos y sin credenciales.
            url = url.split("#", 1)[0]
            if discovery_only_host(urlsplit(url).hostname):
                continue
            if url in seen:
                # La misma URL puede aparecer antes en Wikipedia. Conservar la
                # pista dirigida para que no pierda prioridad por deduplicación.
                if targets and lead.get('discovered_by') in ('tavily','exa'):
                    for i,existing in enumerate(eligible):
                        if existing['url']==url and url not in expand_urls:
                            eligible[i]={**lead,'url':url}
                            break
                continue
            if url in previous_urls and url not in expand_urls:
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
        path = normalized(parsed.path + " " + (lead.get("title") if isinstance(lead.get("title"), str) else ""))
        relevant = any(w in path for w in words)
        # La URL archivada puede terminar en CAPTCHA/HTML y consumir presupuesto
        # sin poder abrir el documento original. Probar primero el editor original.
        archive = parsed.hostname in {"web.archive.org", "archive.today",
                                     "archive.ph", "wayback.archive-it.org"}
        targeted=bool(targets) and lead.get('discovered_by') in ('tavily','exa')
        return (-int(lead["url"] in expand_urls), -int(targeted), -int(regulatory_host(parsed.hostname)), int(archive), -int(relevant),
                -int(parsed.path.lower().endswith(".pdf")), lead["url"])

    # Intercalar gobierno/justicia con publicaciones independientes. El orden
    # alfabético de Wikipedia enviaba cuatro solicitudes y se detenía aunque
    # tres de ellas no entregaran extractos. Nunca rellenar con texto simulado.
    authorities = sorted((x for x in eligible
                          if primary_host(urlsplit(x["url"]).hostname)), key=rank)
    independent = sorted((x for x in eligible
                          if not primary_host(urlsplit(x["url"]).hostname)), key=rank)
    ordered = deque()
    while authorities or independent:
        if authorities:
            ordered.append(authorities.pop(0))
        if independent:
            ordered.append(independent.pop(0))
    # Una expansión documental deliberada va antes del barrido general; su
    # lectura cuenta en los mismos ocho intentos y no justifica por sí sola IA.
    ordered = deque(sorted(ordered, key=lambda x: x["url"] not in expand_urls))
    per_host, per_kind = Counter(), Counter()
    useful_urls, useful_hosts, regulatory_hits = set(), set(), set()
    attempted_urls = set(previous_urls) - set(expand_urls)
    followed = set()
    while ordered and len(out["source_documents"]) < MAX_DOCUMENTS:
        lead = ordered.popleft()
        if lead["url"] in attempted_urls:
            continue
        host = urlsplit(lead["url"]).hostname
        kind = "primary" if primary_host(host) else "secondary"
        if per_host[host] >= MAX_PER_HOST or per_kind[kind] >= (
                MAX_PRIMARY_ATTEMPTS if kind == "primary" else MAX_SECONDARY_ATTEMPTS):
            continue
        per_host[host] += 1
        per_kind[kind] += 1
        attempted_urls.add(lead["url"])
        record = {**lead, "status": "fetch_failed"}
        try:
            raw, resolved, mime = document_fetcher(lead["url"], timeout=12)
            validate_url(resolved)
            if discovery_only_host(urlsplit(resolved).hostname):
                raise ValueError('Enciclopedia reservada a descubrimiento')
            if primary_host(host) and not primary_host(urlsplit(resolved).hostname):
                raise ValueError("Redirección fuera de autoridad pública")
            analysis = analyze_document(raw, mime, pdf_max_pages=350, pdf_scan_pages=12)
            if "html" in mime:
                references = document_references(raw, resolved)
                record.update({"citation_links_scanned": True,
                               "reference_urls": [r["url"] for r in references]})
                for reference in reversed(references):
                    if reference["url"] not in attempted_urls and reference["url"] not in followed and len(followed) < 16:
                        followed.add(reference["url"])
                        ordered.appendleft(reference)
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
                    "source_class": "public_authority_candidate" if regulatory_host(urlsplit(resolved).hostname)
                                    else "public_document_candidate"})
                if len(fragments) >= 3:
                    break
            record.update({"status": "text_extracted" if fragments else "no_relevant_passages",
                           "resolved_url": resolved, "sha256": digest,
                           "pages_total": analysis["total_pages"],
                           "full_document_text_read": bool(fragments) and
                               (analysis["type"] != "pdf" or analysis["total_pages"] <= 12)})
            out["evidence_manifest"].extend(fragments)
            if fragments:
                useful_urls.add(resolved)
                useful_hosts.add(urlsplit(resolved).hostname)
                if regulatory_host(urlsplit(resolved).hostname):
                    regulatory_hits.add(urlsplit(resolved).hostname)
        except (OSError, ValueError, TypeError, KeyError, ImportError, RuntimeError) as exc:
            record["status"] = "fetch_failed"
            record["error_type"] = type(exc).__name__
        out["source_documents"].append(record)
        # Dos dominios con texto y al menos un regulador ofrecen un punto de
        # partida para contraste. No los declaramos hechos verificados.
        if len(useful_urls) >= 2 and len(useful_hosts) >= 2 and regulatory_hits:
            break
    # El Worker publicado acepta cuatro filas de descarga por informe.
    # Mantener compatibilidad mientras se despliega el nuevo validador:
    # conservar preferentemente documentos con texto y transmitir todas las
    # URLs intentadas en metadata acotada; no perder los pasajes observados.
    attempted_documents=list(out["source_documents"])
    out["source_documents"]=sorted(
        attempted_documents,key=lambda r: (r.get("status")!="text_extracted",
                                           -int(bool(targets) and r.get('discovered_by') in ('tavily','exa')),
                                           r.get("url","")))[:4]
    out["retrieval_budget"] = {
        "max_documents": MAX_DOCUMENTS,
        "attempted": len(attempted_documents),
        "attempted_urls": [row["url"] for row in attempted_documents],
        "documents_with_relevant_text": len(useful_urls),
        "independent_domains_with_text": len(useful_hosts),
        "public_authority_domains_with_text": len(regulatory_hits),
        "budget_exhausted": len(attempted_documents) >= MAX_DOCUMENTS,
        "citation_scanned_urls": [d["url"] for d in attempted_documents if d.get("citation_links_scanned")],
    }
    new_fragments=out["evidence_manifest"]
    new_count=len(new_fragments)
    # Conservar citas viejas para comparar sólo si una nueva lectura real
    # amplió la base informativa. Nunca recircular el mismo dossier a Gemini.
    if new_fragments:
        # Reservar espacio a las citas anteriores: sin ellas la continuación
        # pierde precisamente el documento que debe contrastar. Evitar duplicar
        # un mismo texto por hashes de HTML dinámico y repartir los nuevos
        # pasajes entre documentos antes de tomar su segundo/tercer fragmento.
        new_urls={e['url'] for e in new_fragments}
        historical=[];old_keys=set()
        for old in preserved:
            key=(old['url'],old.get('page'),old['excerpt'])
            if old['url'] not in new_urls and key not in old_keys:
                old_keys.add(key);historical.append(old)
        buckets={}
        for e in new_fragments:
            buckets.setdefault(e['url'],deque()).append(e)
        balanced=[]
        while any(buckets.values()) and len(balanced)<MAX_EVIDENCE-len(historical):
            for bucket in buckets.values():
                if bucket and len(balanced)<MAX_EVIDENCE-len(historical):
                    balanced.append(bucket.popleft())
        new_fragments=balanced+historical
    out["retrieval_budget"]["new_fragments"]=new_count
    out["stages"].append({"provider":"document_citations","role":"discover",
                          "status":"success" if followed else "empty","result_count":len(followed)})
    out["evidence_manifest"] = [{**e, "id": f"E{i+1:03d}"}
                                for i, e in enumerate(new_fragments[:MAX_EVIDENCE])]
    out["status"] = "sources_collected" if out["retrieval_budget"]["documents_with_relevant_text"] else "skipped_no_documentary_evidence"
    return out
