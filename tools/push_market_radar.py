"""Sube un informe de descubrimiento a la API administrativa dedicada de Factor.
No accede a YouTube ni usa credenciales de render/administrador.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from urllib.parse import urlsplit, quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

HOST = "factor-de-gigantes.martin30-eler.workers.dev"
AUDIENCE = "factor-de-gigantes-market-v1"


def github_oidc_token(*, environ=os.environ, opener=urlopen) -> str:
    endpoint = environ.get("ACTIONS_ID_TOKEN_REQUEST_URL", "")
    bootstrap = environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN", "")
    u=urlsplit(endpoint)
    if (u.scheme != "https" or not u.hostname or
        not (u.hostname=="actions.githubusercontent.com" or
             u.hostname.endswith(".actions.githubusercontent.com")) or
        u.username or u.password or u.fragment or not u.query):
        raise ValueError("Emisor OIDC de GitHub Actions no disponible")
    if not bootstrap:
        raise ValueError("La ejecución no tiene permiso id-token: write")
    target=endpoint+("&" if u.query else "?")+"audience="+quote(AUDIENCE,safe="")
    req=Request(target,headers={"Authorization":"Bearer "+bootstrap,
                                "Accept":"application/json",
                                "User-Agent":"FactorDeGigantes-MarketRadar/1.0"})
    try:
        with opener(req,timeout=20) as response:
            body=json.load(response)
    except (URLError,HTTPError,TimeoutError):
        raise RuntimeError("GitHub no entregó una identidad OIDC temporal") from None
    value=body.get("value") if isinstance(body,dict) else None
    if not isinstance(value,str) or len(value)>12000 or value.count(".")!=2:
        raise RuntimeError("GitHub devolvió una identidad OIDC no válida")
    if environ.get("FDG_OIDC_DIAGNOSTIC") == "1":
        import base64
        encoded=value.split(".")[1]
        data=json.loads(base64.urlsafe_b64decode(encoded+"="*((4-len(encoded)%4)%4)))
        checks={
          "issuer": data.get("iss") == "https://token.actions.githubusercontent.com",
          "audience": data.get("aud") == AUDIENCE,
          "repository": data.get("repository") == "eler30mr-star/FactordeGigantes",
          "repository_id": str(data.get("repository_id")) == "1426522491",
          "ref": data.get("ref") == "refs/heads/main",
          "workflow_ref": data.get("workflow_ref") == "eler30mr-star/FactordeGigantes/.github/workflows/topic-discovery-smoke.yml@refs/heads/main",
          "event": data.get("event_name") in ("push","schedule","workflow_dispatch"),
          "runner": data.get("runner_environment") == "github-hosted",
          "time_fields": all(isinstance(data.get(n),int) for n in ("nbf","iat","exp")),
        }
        print("OIDC_DIAGNOSTICO_SOLO_BOOLEANOS:",checks)
    return value


def upload(report: dict, *, base_url: str, token: str, opener=urlopen) -> dict:
    url = urlsplit(base_url.strip().rstrip("/"))
    if (url.scheme != "https" or url.hostname != HOST or
            url.username or url.password or url.port or url.path not in ("", "/") or
            url.query or url.fragment):
        raise ValueError("API_BASE_URL no apunta al Worker de Factor")
    if not isinstance(token, str) or len(token) < 24:
        raise ValueError("Token OIDC no disponible")
    if not isinstance(report, dict) or report.get("market_study_complete") is not False or \
            report.get("ready_for_youtube") is not False:
        raise ValueError("Radar inválido: solo se admite descubrimiento preliminar")
    payload = json.dumps(report, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if len(payload)>250000:
        raise ValueError("Informe excede presupuesto de ingesta")
    req = Request(base_url.strip().rstrip("/") + "/api/market/ingest",
        data=payload, method="POST", headers={
          "Authorization": "Bearer " + token, "Content-Type": "application/json",
          "Accept": "application/json", "User-Agent": "FactorDeGigantes-MarketRadar/1.0"
        })
    try:
        with opener(req, timeout=25) as response:
            data=json.load(response)
            if response.status != 201 or not isinstance(data, dict) or data.get("stored_in") != "d1":
                raise RuntimeError("Servidor no confirmó persistencia D1")
            if data.get("market_study_complete") is not False or data.get("automatic_publication_allowed") is not False:
                raise RuntimeError("El servidor respondió con permisos inesperados")
            return data
    except HTTPError as exc:
        # No mostrar cuerpo de error ni cabeceras, pueden contener datos sensibles.
        raise RuntimeError("API de ingesta rechazó solicitud HTTP " + str(exc.code)) from None
    except (URLError, TimeoutError) as exc:
        raise RuntimeError("Error de comunicación con el Worker: " + type(exc).__name__) from None


def main():
    parser=argparse.ArgumentParser(description="Guardar radar Wikimedia diario en D1")
    parser.add_argument("--input", type=Path, required=True)
    args=parser.parse_args()
    report=json.loads(args.input.read_text(encoding="utf-8"))
    result=upload(report,base_url=os.environ.get("API_BASE_URL", ""),
      token=github_oidc_token())
    print("D1_RADAR_CONFIRMED:",result["run_id"],"EMPRESAS:",result["entities_seen"],
          "SERIES:",result["windows_seen"],"ESTUDIO_COMPLETO:",result["market_study_complete"])


if __name__=="__main__":
    main()
