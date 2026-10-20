#!/usr/bin/env python3
"""Notify Worker of a completed or failed render; do not leak tokens."""
import json
import os
import re
import sys
import urllib.request

def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ("ready","failed"):
        sys.exit("Uso: report.py ready|failed <job_id>")
    status, job_id = sys.argv[1:]
    if not re.fullmatch(r"[0-9a-f-]{36}", job_id):
        sys.exit("job_id inválido")
    base = os.environ.get("API_BASE_URL", "").rstrip("/")
    key = os.environ.get("RENDERER_TOKEN", "")
    if not base.startswith("https://") or len(key) < 24:
        sys.exit("Faltan API_BASE_URL / RENDERER_TOKEN")
    url = base + "/api/renderer/jobs/" + job_id + "/report"
    payload = {"status":status,"detail":"Revisar ejecución en GitHub Actions" if status=="failed" else ""}
    req = urllib.request.Request(url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization":"Bearer "+key,"Content-Type":"application/json",
                 "User-Agent":"FactorDeGigantes-Renderer/1.0","Accept":"application/json"},
        method="POST")
    with urllib.request.urlopen(req,timeout=30) as response:
        print("Estado reportado:",status,response.status)

if __name__ == "__main__":
    main()
