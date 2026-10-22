"""Control D1 por OIDC del radar: cuota, clasificación y auditoría de IA."""
from __future__ import annotations

import os
import re
from urllib.parse import urlsplit

from tools.ai_clients import ProviderError, post_json
from tools.push_market_radar import HOST, github_oidc_token


class ControlClient:
    def __init__(self, *, base_url=None, token=None, transport=post_json):
        self.base = (os.getenv("API_BASE_URL", "") if base_url is None else base_url).rstrip("/")
        u = urlsplit(self.base)
        if (u.scheme != "https" or u.hostname != HOST or u.path or u.query or u.fragment
                or u.username or u.password or u.port):
            raise ValueError("Solo control Factor de Gigantes permitido")
        self.token = github_oidc_token() if token is None else token
        if not isinstance(self.token, str) or self.token.count(".") != 2 or len(self.token) < 40:
            raise ValueError("OIDC requerido")
        run = os.getenv("GITHUB_RUN_ID", "local") + "-" + os.getenv("GITHUB_RUN_ATTEMPT", "1")
        if not re.fullmatch(r"[a-zA-Z0-9-]{1,70}", run):
            raise ValueError("Identidad de ejecución inválida")
        self.run, self.counter, self.transport = run, 0, transport

    def request(self, path, body):
        return self.transport(self.base + path, body, {"Authorization": "Bearer " + self.token})

    def request_id(self, provider, role):
        self.counter += 1
        return f"{self.run}-{provider}-{role}-{self.counter}"

    def reserve(self, provider, role):
        out = self.request("/api/market/ai-budget/reserve", {
            "provider": provider, "request_id": self.request_id(provider, role)})
        return out.get("ok") is True and out.get("allowed") is True

    def classify(self, evidence):
        return self.request("/api/market/ai-classify", {
            "request_id": self.request_id("cloudflare", "classify"),
            "evidence": [{"id": e["id"], "excerpt": e["excerpt"]} for e in evidence]})

    def persist(self, report):
        out = self.request("/api/market/ai-pipeline/ingest", report)
        if (out.get("ok") is not True or out.get("stored_in") != "d1"
                or out.get("automatic_publication_allowed") is not False):
            raise ProviderError("persistence_unconfirmed")
        return out

    def script_context(self, run_id="latest"):
        out = self.request("/api/market/ai-pipeline/script-context", {"run_id": run_id})
        if not isinstance(out.get("ok"), bool) or out.get("automatic_publication_allowed") is not False:
            raise ProviderError("script_context_unconfirmed")
        return out
