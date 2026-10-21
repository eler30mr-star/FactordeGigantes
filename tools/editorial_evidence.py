"""Auditoría documental de Factor de Gigantes: trazabilidad por afirmación.

NO verifica remotamente la veracidad. Comprueba la estructura de evidencias,
su revisión editorial y ausencia de aprobación/publicación automática.
No sustituye el examen de enlaces, citas y derechos por un humano.
"""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

SOURCE_TYPES = {"primaria", "secundaria"}
VERIFICATION_STATES = {"pendiente", "verificada", "rechazada"}
ASSET_TYPES = {"imagen", "video", "musica", "voz", "grafico"}


def _text(value, field, low=1, high=500):
    if not isinstance(value, str) or not low <= len(value.strip()) <= high:
        raise ValueError(f"{field} inválido (entre {low} y {high} caracteres)")
    return value.strip()


def _url(value):
    if not isinstance(value, str) or len(value) > 1000:
        raise ValueError("URL inválida")
    try:
        parsed = urlsplit(value)
    except ValueError as exc:
        raise ValueError("URL inválida") from exc
    if parsed.scheme != "https" or not parsed.netloc or not parsed.hostname:
        raise ValueError("Solo URLs HTTPS absolutas de fuentes identificables")
    host = parsed.hostname.casefold()
    if host in {"localhost", "127.0.0.1", "::1"} or host.endswith((".local", ".invalid")):
        raise ValueError("No admitir destinos locales como fuente")
    if parsed.username or parsed.password:
        raise ValueError("Una fuente no debe contener credenciales")
    return value


def validate_dossier(data):
    """Devuelve resumen, NUNCA permiso automático de publicación."""
    if not isinstance(data, dict):
        raise ValueError("El expediente editorial debe ser un objeto JSON")
    title = _text(data.get("title"), "Título editorial", 8, 150)
    thesis = _text(data.get("thesis"), "Tesis", 25, 550)
    if data.get("publication_authorized") is not False:
        raise ValueError("El expediente de investigación no puede publicar automáticamente")
    sources = data.get("sources")
    claims = data.get("claims")
    assets = data.get("assets", [])
    if not isinstance(sources, list) or not 2 <= len(sources) <= 30:
        raise ValueError("Se requieren 2-30 fuentes documentales")
    if not isinstance(claims, list) or not 1 <= len(claims) <= 50:
        raise ValueError("Se requiere al menos una afirmación verificable")
    if not isinstance(assets, list) or len(assets) > 40:
        raise ValueError("Demasiados activos declarados")
    by_id = {}
    for src in sources:
        if not isinstance(src, dict):
            raise ValueError("Fuente debe ser objeto")
        sid = _text(src.get("id"), "ID fuente", 2, 12)
        if not re.fullmatch(r"S[0-9]{2,3}", sid) or sid in by_id:
            raise ValueError("Identificador de fuente duplicado o incorrecto")
        _url(src.get("url"))
        _text(src.get("publisher"), "Publicador", 3, 130)
        _text(src.get("accessed_on"), "Fecha acceso", 10, 10)
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", src["accessed_on"]):
            raise ValueError("Fecha debe ser ISO AAAA-MM-DD")
        if src.get("type") not in SOURCE_TYPES:
            raise ValueError("Tipo de fuente no reconocido")
        by_id[sid] = src

    identifiers = set()
    pending = 0
    verified = 0
    for claim in claims:
        if not isinstance(claim, dict):
            raise ValueError("Afirmación no válida")
        cid = _text(claim.get("id"), "ID afirmación", 2, 12)
        if not re.fullmatch(r"C[0-9]{2,3}", cid) or cid in identifiers:
            raise ValueError("Identificador de afirmación duplicado o incorrecto")
        identifiers.add(cid)
        _text(claim.get("text"), "Afirmación", 20, 900)
        evidence = claim.get("evidence")
        if not isinstance(evidence, list) or not 1 <= len(evidence) <= 5:
            raise ValueError("Cada afirmación requiere evidencia vinculada")
        seen = set()
        for item in evidence:
            if not isinstance(item, dict) or item.get("source_id") not in by_id:
                raise ValueError("Evidencia con fuente inexistente")
            sid = item["source_id"]
            if sid in seen:
                raise ValueError("Evidencia duplicada para la misma fuente")
            seen.add(sid)
            _text(item.get("locator"), "Ubicación exacta en fuente", 4, 220)
            if item.get("status") not in VERIFICATION_STATES:
                raise ValueError("Estado de verificación inexistente")
        if claim.get("reviewed_by") and not isinstance(claim["reviewed_by"], str):
            raise ValueError("Revisor inválido")
        if all(x["status"] == "verificada" for x in evidence) and claim.get("reviewed_by"):
            verified += 1
        else:
            pending += 1
    pending_assets = 0
    for asset in assets:
        if not isinstance(asset, dict) or asset.get("kind") not in ASSET_TYPES:
            raise ValueError("Recurso audiovisual desconocido")
        _text(asset.get("description"), "Descripción de recurso", 5, 250)
        if asset.get("rights_status") not in {"pendiente", "verificado", "rechazado"}:
            raise ValueError("Estado de derechos inválido")
        if asset["rights_status"] != "verificado":
            pending_assets += 1
    return {
        "project": "Factor de Gigantes",
        "title": title, "thesis": thesis,
        "sources_count": len(sources), "claims_count": len(claims),
        "claims_reviewed_with_sources": verified,
        "claims_pending_or_rejected": pending,
        "assets_pending_rights": pending_assets,
        "human_fact_check_required": True,
        "automated_publication_authorized": False,
        "can_release_documentary": False,
    }


def main():
    parser = argparse.ArgumentParser(description="Validar expediente documental sin publicar")
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    report = validate_dossier(json.loads(args.file.read_text(encoding="utf-8")))
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
