"""Sube un informe de descubrimiento a la API administrativa dedicada de Factor.
No accede a YouTube ni usa credenciales de render/administrador.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

HOST = "factor-de-gigantes.martin30-eler.workers.dev"


def upload(report: dict, *, base_url: str, token: str, opener=urlopen) -> dict:
    url = urlsplit(base_url.strip().rstrip("/"))
    if (url.scheme != "https" or url.hostname != HOST or
            url.username or url.password or url.port or url.path not in ("", "/") or
            url.query or url.fragment):
        raise ValueError("API_BASE_URL no apunta al Worker de Factor")
    if not isinstance(token, str) or len(token) < 24:
        raise ValueError("MARKET_INGEST_TOKEN no configurado")
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
      token=os.environ.get("MARKET_INGEST_TOKEN", ""))
    print("D1_RADAR_CONFIRMED:",result["run_id"],"EMPRESAS:",result["entities_seen"],
          "SERIES:",result["windows_seen"],"ESTUDIO_COMPLETO:",result["market_study_complete"])


if __name__=="__main__":
    main()
