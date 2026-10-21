"""Motor de investigación de Factor de Gigantes: fuentes -> evidencias -> borrador.

Servicios sin pago. Una similitud textual NO acredita verdad ni derechos.
No guarda páginas completas, no publica y jamás altera los estados de aprobación.
"""
from __future__ import annotations

import argparse
import hashlib
import html
from html.parser import HTMLParser
import ipaddress
import json
from pathlib import Path
import re
import socket
import ssl
from datetime import date, datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import HTTPSHandler, HTTPRedirectHandler, Request, build_opener

USER_AGENT = "FactorDeGigantesResearch/0.1 (https://github.com/eler30mr-star/FactordeGigantes)"
MAX_BYTES = 750_000
MAX_REQUESTS = 12
MAX_REDIRECTS = 3
TIMEOUT = 14
STOPWORDS = {
    "para", "como", "sobre", "entre", "desde", "hasta", "esta", "este", "estos",
    "estas", "cuando", "donde", "despues", "antes", "fueron", "habia", "tiene",
    "tenia", "tambien", "empresa", "compania", "informacion", "documental",
    "fuente", "que", "con", "una", "del", "los", "las", "por", "sus", "and", "the",
    "this", "that", "with", "from", "for", "its", "have", "was", "are", "were"
}
MAX_EXCERPT_CHARS = 270
MAX_EXCERPTS_PER_CLAIM = 2


def validate_url(value: str) -> str:
    if not isinstance(value, str) or not 12 <= len(value) <= 1000:
        raise ValueError("URL inexistente o demasiado larga")
    p = urlsplit(value)
    if (p.scheme != "https" or not p.hostname or p.username or p.password
            or p.port not in (None, 443)):
        raise ValueError("Solo HTTPS público en puerto 443, sin credenciales")
    host = p.hostname.lower().rstrip(".")
    if (host in {"localhost", "localtest.me"} or host.endswith((".local", ".internal", ".invalid"))
            or host.startswith(("127.", "0.", "169.254."))):
        raise ValueError("Host interno o reservado")
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        if "." not in host:
            raise ValueError("El dominio requiere al menos un punto")
    else:
        if not ip.is_global:
            raise ValueError("Dirección IP no pública")
    return value


def check_public_dns(host: str) -> None:
    """Proteger las consultas iniciadas por el usuario frente a destinos privados."""
    try:
        addresses = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError("El dominio no se pudo resolver") from exc
    if not addresses:
        raise ValueError("El dominio no tiene direcciones IP")
    for record in addresses:
        try:
            address = ipaddress.ip_address(record[4][0])
        except ValueError as exc:
            raise ValueError("DNS inválido") from exc
        if not address.is_global:
            raise ValueError("DNS devuelve una dirección privada/reservada")


class PublicRedirects(HTTPRedirectHandler):
    def __init__(self):
        self.count = 0

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.count += 1
        if self.count > MAX_REDIRECTS:
            raise ValueError("Demasiadas redirecciones")
        validate_url(newurl)
        check_public_dns(urlsplit(newurl).hostname)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_public(url: str, *, timeout: int = TIMEOUT) -> tuple[bytes, str, str]:
    validate_url(url)
    check_public_dns(urlsplit(url).hostname)
    opener = build_opener(HTTPSHandler(context=ssl.create_default_context()), PublicRedirects())
    request = Request(url, headers={
        "User-Agent": USER_AGENT, "Accept": "text/html,application/json;q=0.9",
        "Accept-Encoding": "identity"
    })
    with opener.open(request, timeout=timeout) as response:
        final_url = response.geturl()
        validate_url(final_url)
        content_type = response.headers.get("Content-Type", "").lower()
        if not any(kind in content_type for kind in ("text/html", "application/json", "text/plain")):
            raise ValueError("Tipo de contenido no analizable; PDF y binarios se excluyen")
        declared_length = response.headers.get("Content-Length")
        if declared_length and int(declared_length) > MAX_BYTES:
            raise ValueError("Contenido remoto demasiado grande")
        raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("Contenido remoto excede el límite")
        return raw, final_url, content_type


class ExtractText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.invisible = 0
        self.current: list[str] | None = None
        self.blocks: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript", "svg", "nav", "footer"}:
            self.invisible += 1
        if not self.invisible and tag in {"p", "li", "h1", "h2", "h3"}:
            if self.current is not None:
                self._flush()
            self.current = []

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript", "svg", "nav", "footer"}:
            self.invisible = max(0, self.invisible - 1)
        if not self.invisible and tag in {"p", "li", "h1", "h2", "h3"}:
            self._flush()

    def handle_data(self, data):
        if not self.invisible and self.current is not None:
            self.current.append(data)

    def _flush(self):
        if self.current is None:
            return
        text = re.sub(r"\s+", " ", html.unescape(" ".join(self.current))).strip()
        if 42 <= len(text) <= 5000:
            self.blocks.append(text[:3000])
        self.current = None


def extract_blocks(payload: bytes, content_type: str) -> list[str]:
    if "json" in content_type:
        data = json.loads(payload.decode("utf-8"))
        if isinstance(data, dict):
            text = data.get("extract") or data.get("description") or ""
            return [text] if isinstance(text, str) and len(text) > 42 else []
        return []
    parser = ExtractText()
    parser.feed(payload.decode("utf-8", errors="replace"))
    parser.close()
    return list(dict.fromkeys(parser.blocks))[:450]


def tokens(text: str) -> set[str]:
    import unicodedata
    normalized = unicodedata.normalize("NFKD", text.lower())
    simplified = "".join(c for c in normalized if not unicodedata.combining(c))
    return {x for x in re.findall(r"[a-z0-9]{3,}", simplified) if x not in STOPWORDS}


def excerpts_for_claim(claim: str, blocks: list[str], limit: int = MAX_EXCERPTS_PER_CLAIM) -> list[dict]:
    wanted = tokens(claim)
    if not wanted:
        return []
    rankings = []
    for index, block in enumerate(blocks):
        words = tokens(block)
        overlap = wanted & words
        # Evitar un resultado por coincidencia casual de 1 nombre o palabra común.
        score = len(overlap) / max(1, len(wanted))
        if len(overlap) >= 2 and score >= 0.18:
            rankings.append((score, len(overlap), index, block))
    rankings.sort(key=lambda value: (-value[0], -value[1], value[2]))
    return [{
        "excerpt": block[:MAX_EXCERPT_CHARS].strip(),
        "similarity": round(score, 3),
        "block_index": index,
        "verification_status": "candidate_unchecked",
    } for score, _, index, block in rankings[:limit]]


def research_dossier(dossier: dict, fetcher=fetch_public, max_requests: int = MAX_REQUESTS) -> dict:
    if dossier.get("publication_authorized") is not False:
        raise ValueError("El motor solo acepta expedientes no publicables")
    sources = dossier.get("sources", [])
    claims = dossier.get("claims", [])
    if not 2 <= len(sources) <= 30 or not 1 <= len(claims) <= 50:
        raise ValueError("El expediente requiere fuentes y afirmaciones acotadas")
    max_requests = max(1, min(MAX_REQUESTS, int(max_requests)))
    by_id = {}
    retrieval = []
    for source in sources[:max_requests]:
        sid, url = source["id"], source["url"]
        validate_url(url)
        if sid in by_id:
            raise ValueError("ID de fuente duplicado")
        by_id[sid] = None
        try:
            raw, final_url, content_type = fetcher(url)
            blocks = extract_blocks(raw, content_type)
            retrieval.append({
                "source_id": sid, "requested_url": url, "resolved_url": final_url,
                "publisher_declared": source["publisher"], "status": "fetched" if blocks else "no_readable_text",
                "content_sha256": hashlib.sha256(raw).hexdigest(),
                "readable_blocks": len(blocks),
                "limited_extracts": [
                    {"claim_id": claim["id"], "matches": excerpts_for_claim(claim["text"], blocks)}
                    for claim in claims
                    if any(ev["source_id"] == sid for ev in claim["evidence"])
                ],
            })
        except (ValueError, HTTPError, URLError, TimeoutError, OSError, UnicodeError, json.JSONDecodeError) as exc:
            retrieval.append({
                "source_id": sid, "requested_url": url, "status": "blocked_or_unavailable",
                "reason_category": type(exc).__name__,
            })
    sourced = {r["source_id"]: r for r in retrieval if r["status"] == "fetched"}
    candidates = []
    for claim in claims:
        evidence = []
        for ev in claim["evidence"]:
            record = sourced.get(ev["source_id"])
            if not record:
                continue
            found = next((x for x in record["limited_extracts"]
                          if x["claim_id"] == claim["id"]), None)
            if found:
                evidence.extend([{
                    "source_id": ev["source_id"], "url": record["resolved_url"],
                    "excerpt": x["excerpt"], "similarity": x["similarity"],
                    "block_index": x["block_index"]
                } for x in found["matches"]])
        evidence.sort(key=lambda x: x["similarity"], reverse=True)
        candidates.append({
            "id": claim["id"], "segment_index": claim.get("segment_index"),
            "proposition": claim["text"], "candidate_passages": evidence[:3],
            "verification_status": "pending_human",
            "claim_confirmed": False
        })
    return {
        "product": "Factor de Gigantes", "engine_version": "0.1",
        "topic": dossier["title"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "request_count": len(retrieval), "requested_max": max_requests,
        "fetched_count": len(sourced),
        "sources": retrieval,
        "candidate_claims": candidates,
        "facts_verified_automatically": 0,
        "rights_verified_automatically": 0,
        "original_dossier_changed": False,
        "production_ready": False, "youtube_publication_authorized": False,
        "editorial_warning": "Una coincidencia de texto NO prueba verdad, contexto, causalidad ni licencia. Revisión humana obligatoria."
    }


def discover_wikipedia(topic: str, fetcher=fetch_public) -> list[dict]:
    """Punto de entrada genérico: busca temas sin inventar fuentes primarias."""
    if not 3 <= len(topic.strip()) <= 130:
        raise ValueError("Tema fuera de límite")
    url = "https://es.wikipedia.org/w/api.php?" + urlencode({
        "action": "query", "list": "search", "srsearch": topic,
        "srlimit": "5", "format": "json", "formatversion": "2"
    })
    payload, _, _ = fetcher(url)
    data = json.loads(payload)
    results = data.get("query", {}).get("search", [])
    return [{
        "title": r["title"],
        "url": "https://es.wikipedia.org/wiki/" + quote(r["title"].replace(" ", "_")),
        "type": "secundaria", "verification_status": "discovery_only",
        "publisher": "Wikipedia (punto de partida, NO fuente primaria)"
    } for r in results[:5] if r.get("title")]


def assemble_ai_evidence(report: dict, max_chars: int = 10500) -> str:
    """Solo pasar al LLM pasajes explícitamente enlazados a las fuentes consultadas."""
    chunks = [f"TEMA: {report['topic']}", "EVIDENCIA DOCUMENTAL SIN VERIFICAR:"]
    for candidate in report["candidate_claims"]:
        chunks.append(f"AFIRMACION {candidate['id']}: {candidate['proposition']}")
        if not candidate["candidate_passages"]:
            chunks.append("  SIN PASAJES ENCONTRADOS; investigar más y NO completar inventando.")
        for x in candidate["candidate_passages"][:2]:
            chunks.append(f"  [{x['source_id']}] {x['url']} | TEXTO: {x['excerpt']}")
    return "\n".join(chunks)[:max_chars]


def save_report(report: dict, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    file = output_dir / "reporte_investigacion.json"
    file.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Factor de Gigantes — investigación automática preliminar",
        "", f"**Tema:** {report['topic']}", "",
        f"**Fuentes consultadas:** {report['fetched_count']}/{report['request_count']}.",
        "**Ningún hecho ni derecho se da por verificado automáticamente.**", "",
        "## Afirmaciones y pasajes localizados", ""
    ]
    for candidate in report["candidate_claims"]:
        lines.append(f"### {candidate['id']} · Escena {candidate['segment_index'] or 'por decidir'}")
        lines.append(candidate["proposition"])
        for x in candidate["candidate_passages"]:
            lines.append(f"- Candidato [{x['source_id']}]({x['url']}), similitud {x['similarity']}: {x['excerpt']}")
        if not candidate["candidate_passages"]:
            lines.append("- Sin fragmento coincidente. Requiere una nueva búsqueda.")
        lines.append("")
    lines.extend(["## Advertencia obligatoria", report["editorial_warning"], "",
                  "No se modifica el expediente aprobado ni se produce video o publicación.", ""])
    (output_dir / "LECTURA_PRELIMINAR.md").write_text("\n".join(lines), encoding="utf-8")
    (output_dir / "evidencia_para_ia.txt").write_text(assemble_ai_evidence(report), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Investigar sin pagos, sin publicación y con trazabilidad")
    parser.add_argument("--dossier", type=Path)
    parser.add_argument("--topic")
    parser.add_argument("--out", type=Path, default=Path("dist/research"))
    parser.add_argument("--max-requests", type=int, default=6)
    args = parser.parse_args()
    if bool(args.dossier) == bool(args.topic):
        parser.error("Indica exactamente --dossier o --topic")
    if args.topic:
        try:
            discoveries = discover_wikipedia(args.topic)
        except (ValueError, HTTPError, URLError, OSError) as e:
            raise SystemExit("No hay acceso a la búsqueda enciclopédica: " + type(e).__name__)
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / "descubrimiento.json").write_text(json.dumps({
            "topic": args.topic, "results": discoveries,
            "automatic_fact_verification": False, "primary_sources_required": True,
            "publication_authorized": False,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("DESCUBRIMIENTO:", len(discoveries), "entradas secundarias; buscar fuentes primarias.")
        return
    dossier = json.loads(args.dossier.read_text(encoding="utf-8"))
    result = research_dossier(dossier, max_requests=args.max_requests)
    save_report(result, args.out)
    print("RESULTADO:", result["fetched_count"], "/", result["request_count"], "fuentes legibles,",
          len(result["candidate_claims"]), "afirmaciones aún pendientes.")


if __name__ == "__main__":
    main()
