"""Smoke read-only de Factor de Gigantes desplegado en Cloudflare.

No usa ADMIN_TOKEN, no crea trabajos y no consume acciones del investigador.
Para usar: API_BASE_URL=https://factor-de-gigantes.martin30-eler.workers.dev
           python -m tools.production_smoke
"""
from __future__ import annotations

import json
import hashlib
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler

EXPECTED_HOST = "factor-de-gigantes.martin30-eler.workers.dev"
HEADERS = {"User-Agent": "FactorDeGigantes-ProductionSmoke/1.0",
           "Accept": "text/html,application/json,*/*"}
MAX_BYTES = 200_000

class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None

def read(base, path):
    request = Request(base + path, headers=HEADERS)
    try:
        with build_opener(NoRedirects()).open(request, timeout=15) as r:
            return r.status, r.headers.get("Content-Type", ""), r.read(MAX_BYTES + 1)
    except HTTPError as e:
        return e.code, e.headers.get("Content-Type", ""), e.read(1024)

def probe(base):
    parsed = urlsplit(base)
    if parsed.scheme != "https" or parsed.hostname != EXPECTED_HOST or parsed.username or parsed.password or parsed.port or parsed.path not in ("", "/") or parsed.query:
        raise ValueError("API_BASE_URL debe apuntar al Worker oficial sin rutas ni secretos")
    base = "https://" + EXPECTED_HOST
    report = {"product": "Factor de Gigantes", "worker": EXPECTED_HOST,
              "checks": {}, "production_ready": False}
    checks = [
        ("/health", 200, [b'Factor de Gigantes']),
        ("/", 200, [b'Investigar con IA', b'id="research-form"', b'id="dossier-panel"', b'id="production-detail"', b'id="youtube-connect"']),
        ("/app.js", 200, [b'loadResearch', b'/api/research', b'/api/jobs', b'retry-render', b'/api/production/runs', 'Abrir exportación'.encode()]),
        ("/api/research", 401, [b'Acceso no autorizado']),
        ("/api/production/runs", 401, [b'Acceso no autorizado']),
        ("/api/youtube/connection", 401, [b'Acceso no autorizado']),
        ("/oauth/youtube/callback?state=invalid", 303, []),
        ("/api/renderer/jobs/00000000-0000-0000-0000-000000000000/episode", 401, [b'Acceso no autorizado']),
    ]
    for path, expected_status, expected_text in checks:
        status, ctype, data = read(base, path)
        result = {"status": status, "pass": status == expected_status and len(data) <= MAX_BYTES and all(token in data for token in expected_text)}
        if path == '/app.js' and status == 200:
            result['sha256'] = hashlib.sha256(data).hexdigest()
        report["checks"][path] = result
    report["production_ready"] = all(item["pass"] for item in report["checks"].values())
    report["interpretation"] = (
        "Solo verifica archivos públicos, /health y barrera de autenticación. "
        "No confirma flujo autenticado, migraciones ni investigación completada."
    )
    return report

def main():
    url = os.environ.get("API_BASE_URL", "").strip()
    if not url:
        raise SystemExit("API_BASE_URL no está configurada")
    try:
        result = probe(url)
    except (ValueError, URLError, TimeoutError) as exc:
        raise SystemExit("Smoke de producción no disponible: " + type(exc).__name__)
    print(json.dumps(result, ensure_ascii=False))
    if not result["production_ready"]:
        raise SystemExit("El panel de producción no muestra todos los componentes esperados")

if __name__ == "__main__":
    main()

