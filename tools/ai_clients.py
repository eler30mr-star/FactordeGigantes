"""Clientes acotados para cuentas gratuitas. No activan planes ni facturación.

La confirmación de modalidad gratuita es una declaración del operador, no una
verificación de facturación. Toda llamada remota necesita una reserva D1 previa.
No hay reintentos automáticos, herramientas cobrables ni redirecciones con claves.
"""
from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

MAX_BODY = 180_000
MODELS = {
    # Gemini 3.5 Flash-Lite ofrece Free Tier en la tarifa oficial.
    # No usar Gemini 3.8 Flash ni modalidades Priority/Flex/Batches.
    "gemini": "gemini-3.5-flash-lite",
    "groq": "openai/gpt-oss-120b",
    "mistral": "mistral-small-latest",
    "openrouter": "openrouter/free",
}
KEYS = {p: p.upper() + "_API_KEY" for p in (*MODELS, "tavily", "exa")}
FLAGS = {p: p.upper() + "_RESEARCH_FREE_CONFIRMED" for p in KEYS}


class ProviderError(RuntimeError):
    def __init__(self, code, status=None):
        self.code, self.status = code, status
        super().__init__(code)  # Nunca cuerpo remoto, clave, URL o prompt.


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ProviderError("redirect_rejected")


def post_json(url, payload, headers):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    if len(body) > MAX_BODY:
        raise ProviderError("request_too_large")
    request = Request(url, data=body, method="POST", headers={
        "Content-Type": "application/json", "Accept": "application/json",
        "User-Agent": "FactorDeGigantesResearch/2.0", **headers})
    try:
        with build_opener(NoRedirects()).open(request, timeout=45) as response:
            raw = response.read(MAX_BODY + 1)
            if len(raw) > MAX_BODY:
                raise ProviderError("response_too_large")
            result = json.loads(raw)
            if not isinstance(result, dict):
                raise ProviderError("invalid_response")
            return result
    except HTTPError as exc:
        code = ("quota_exhausted" if exc.code in (402, 429, 432) else
                "credentials_rejected" if exc.code in (401, 403) else "http_failure")
        raise ProviderError(code, exc.code) from None
    except (URLError, TimeoutError, OSError):
        raise ProviderError("network_failure") from None
    except (ValueError, UnicodeError):
        raise ProviderError("invalid_response") from None


def readiness(provider, env=None):
    env = os.environ if env is None else env
    if provider not in KEYS:
        raise ValueError("Proveedor no admitido")
    if not env.get(KEYS[provider], "").strip():
        return "missing_key"
    if env.get(FLAGS[provider]) != "1":
        return "free_mode_unconfirmed"
    return "ready"


class FreeClients:
    def __init__(self, *, reserve, env=None, transport=post_json):
        self.env = dict(os.environ if env is None else env)
        self.reserve, self.transport = reserve, transport
        self.calls = {p: 0 for p in KEYS}
        self.blocked = set()

    def request(self, provider, role, url, body, headers):
        if self.env.get("RESEARCH_PROVIDER") == "disabled":
            raise ProviderError("disabled")
        status = readiness(provider, self.env)
        if status != "ready":
            raise ProviderError(status)
        if provider in self.blocked:
            raise ProviderError("provider_stopped")
        # Cuota local adicional: como máximo dos búsquedas o una inferencia.
        limit = 2 if provider in ("tavily", "exa") else 1
        if self.calls[provider] >= limit:
            raise ProviderError("run_budget_exhausted")
        if not callable(self.reserve) or not self.reserve(provider, role):
            raise ProviderError("budget_denied")
        self.calls[provider] += 1
        try:
            return self.transport(url, body, headers)
        except ProviderError:
            self.blocked.add(provider)
            raise

    def search(self, provider, query):
        key = self.env.get(KEYS[provider], "")
        if provider == "tavily":
            body = {"query": query, "search_depth": "basic", "max_results": 5,
                    "auto_parameters": False, "include_answer": False,
                    "include_raw_content": False, "include_images": False}
            reply = self.request(provider, "discover", "https://api.tavily.com/search",
                                 body, {"Authorization": "Bearer " + key})
        elif provider == "exa":
            # Sin Contents, Answer, Agent, Monitors ni búsquedas profundas.
            reply = self.request(provider, "discover", "https://api.exa.ai/search",
                                 {"query": query, "type": "auto", "numResults": 5},
                                 {"x-api-key": key})
        else:
            raise ValueError("No es un buscador")
        if not isinstance(reply.get("results"), list):
            raise ProviderError("invalid_response")
        return [{"url": r.get("url"), "title": str(r.get("title", ""))[:200],
                 "discovered_by": provider}
                for r in reply["results"][:5] if isinstance(r, dict)]

    def generate(self, provider, prompt):
        if self.env.get("RESEARCH_PROVIDER") == "qwen_local":
            raise ProviderError("not_selected")
        if provider not in MODELS or not isinstance(prompt, str) or len(prompt) > 24_000:
            raise ValueError("Solicitud de IA fuera del perfil permitido")
        key, model = self.env.get(KEYS[provider], ""), MODELS[provider]
        if provider == "gemini":
            body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
                    "generationConfig": {"responseMimeType": "application/json",
                                         "maxOutputTokens": 1800, "temperature": 0.1}}
            reply = self.request(provider, "analyze",
                "https://generativelanguage.googleapis.com/v1beta/models/" + model + ":generateContent",
                body, {"x-goog-api-key": key})
            try:
                parts = reply["candidates"][0]["content"]["parts"]
                if not isinstance(parts, list) or any(not isinstance(p, dict) for p in parts):
                    raise ProviderError("invalid_response")
                # Nunca incluir los bloques de pensamiento como JSON de salida.
                text = "".join(p.get("text", "") for p in parts
                               if not p.get("thought"))
            except (KeyError, TypeError, IndexError):
                raise ProviderError("invalid_response") from None
        else:
            endpoints = {"groq": "https://api.groq.com/openai/v1/chat/completions",
                         "mistral": "https://api.mistral.ai/v1/chat/completions",
                         "openrouter": "https://openrouter.ai/api/v1/chat/completions"}
            body = {"model": model, "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"}, "stream": False}
            body["max_completion_tokens" if provider == "groq" else "max_tokens"] = 1800
            if provider == "groq":
                body["reasoning_effort"] = "low"
            if provider == "openrouter":
                # Router exclusivamente gratuito, sin fallback pagado ni plugins.
                body["provider"] = {"max_price": {"prompt": 0, "completion": 0}}
            reply = self.request(provider, "review" if provider == "groq" else "analyze",
                                 endpoints[provider], body, {"Authorization": "Bearer " + key})
            try:
                text = reply["choices"][0]["message"]["content"]
            except (KeyError, IndexError, TypeError):
                raise ProviderError("invalid_response") from None
        if not isinstance(text, str) or len(text) > 24_000:
            raise ProviderError("invalid_response")
        usage = reply.get("usage") or reply.get("usageMetadata") or {}
        if not isinstance(usage, dict):
            raise ProviderError("invalid_response")
        # Lista cerrada: no guardar metadatos arbitrarios del proveedor.
        metrics = {k: v for k, v in usage.items() if k in {
            "prompt_tokens", "completion_tokens", "total_tokens",
            "promptTokenCount", "candidatesTokenCount", "totalTokenCount"}
                   and type(v) is int and 0 <= v <= 1_000_000}
        return text, {"model": model, "usage": metrics}
