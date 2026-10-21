"""Contrato de investigador IA intercambiable, sin atribuir verificaciones falsas.

Gemini (API HTTP opt-in, solo con confirmación de free tier) y Qwen LLM
local (generador inyectado). Ninguna respuesta de IA es una fuente primaria.
No crea ni conecta servicios de pago ni genera contenido audiovisual.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
from urllib.request import Request, urlopen

ENDPOINT="https://generativelanguage.googleapis.com/v1beta/models/"
MODELS={"gemini-2.5-flash","gemini-2.5-flash-lite"}
MAX_EVIDENCE=24
MAX_RESPONSE=120_000
MAX_STATEMENT=650


def collect_evidence(report):
    if not isinstance(report,dict) or not isinstance(report.get("candidate_claims"),list):
        raise ValueError("Informe de fuentes inválido")
    records=[]
    for claim in report["candidate_claims"][:40]:
        if not isinstance(claim,dict):
            continue
        for p in (claim.get("candidate_passages") or [])[:5]:
            if not isinstance(p,dict):
                continue
            url=p.get("url","")
            excerpt=p.get("excerpt","")
            if not isinstance(url,str) or not url.startswith("https://") or not isinstance(excerpt,str) or not excerpt.strip():
                continue
            # Las citas originales llevan fuente, URL, página y un identificador
            # creado por el sistema; nunca aceptar referencias de IA no existentes.
            records.append({
                "id":f"E{len(records)+1:03d}",
                "source_id":str(p.get("source_id",""))[:60],
                "claim_id":str(claim.get("id",""))[:30],
                "url":url[:1200],
                "page":p.get("page") if isinstance(p.get("page"),int) and p.get("page")>0 else None,
                "excerpt":" ".join(excerpt.split())[:1400],
            })
            if len(records)>=MAX_EVIDENCE:
                break
        if len(records)>=MAX_EVIDENCE:
            break
    if not records:
        raise ValueError("No existe evidencia documental legible para investigar")
    return records


def request_document(topic,evidence):
    if not isinstance(topic,str) or not 3<=len(topic.strip())<=130:
        raise ValueError("Tema inválido")
    if not isinstance(evidence,list) or not 1<=len(evidence)<=MAX_EVIDENCE:
        raise ValueError("Se necesitan pasajes documentales")
    return (
        "Eres el módulo investigador de Factor de Gigantes. Lee SOLAMENTE "
        "los pasajes documentales listados, no uses conocimiento externo como prueba. "
        "No inventes URLs, años, cifras ni identificadores. Formula hasta 8 "
        "afirmaciones candidatas de una frase con evidence_ids de la lista; "
        "si faltan evidencias, proporciona nuevas preguntas en missing_questions. "
        "No declares ninguna afirmación verificada. Responde únicamente JSON "
        "con estructura {\"claims\":[{\"statement\":\"...\",\"evidence_ids\":[\"E001\"]}],"
        "\"missing_questions\":[\"...\"]}. Todos los datos son candidatos para revisión.\n"
        f"TEMA: {topic}\nPASAJES:\n"
        +json.dumps(evidence,ensure_ascii=False,separators=(",",":"))
    )


def parse_candidate_output(response_text,evidence,provider):
    if not isinstance(response_text,str) or len(response_text)>MAX_RESPONSE:
        raise ValueError("Respuesta de modelo inválida o excesiva")
    obj=json.loads(response_text)
    if not isinstance(obj,dict) or not isinstance(obj.get("claims"),list) or not isinstance(obj.get("missing_questions"),list):
        raise ValueError("El modelo no devolvió el contrato JSON")
    known={e["id"] for e in evidence}
    accepted=[]
    for item in obj["claims"][:8]:
        if not isinstance(item,dict) or not isinstance(item.get("statement"),str) or not isinstance(item.get("evidence_ids"),list):
            raise ValueError("Afirmación sin esquema válido")
        claim=item["statement"].strip()
        refs=item["evidence_ids"]
        if not 10<=len(claim)<=MAX_STATEMENT or not refs or any(not isinstance(ref,str) or ref not in known for ref in refs):
            raise ValueError("Una afirmación cita evidencia inexistente")
        if len(refs)>8:
            raise ValueError("Demasiados soportes para una afirmación")
        accepted.append({
            "statement":claim,"evidence_ids":list(dict.fromkeys(refs)),
            "status":"candidate_unverified",
            "human_verified":False
        })
    questions=[x.strip()[:220] for x in obj["missing_questions"][:8] if isinstance(x,str) and x.strip()]
    return {
        "provider":provider,"candidate_claims":accepted,
        "missing_questions":questions,
        "evidence_count":len(evidence),"facts_verified_automatically":0,
        "ready_for_script":False,"ready_for_youtube":False,
        "notice":"Citas apuntan a extractos existentes; su presencia NO prueba que la afirmación sea verdadera."
    }


def run_gemini_free(topic,evidence,*,api_key=None,model="gemini-2.5-flash",free_tier_confirmed=False,transport=None):
    if model not in MODELS:
        raise ValueError("Modelo Gemini no permitido en perfil sin costo")
    if not free_tier_confirmed:
        raise RuntimeError("No activar Gemini hasta comprobar la modalidad gratuita sin facturación")
    api_key=api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key or len(api_key)<15:
        raise RuntimeError("Falta GEMINI_API_KEY en secretos; no solicitarla por chat")
    prompt=request_document(topic,evidence)
    payload={
        "contents":[{"role":"user","parts":[{"text":prompt}]}],
        "generationConfig":{"responseMimeType":"application/json","maxOutputTokens":1800,"temperature":0.1}
    }
    if transport is None:
        def transport(url,body,headers):
            req=Request(url,data=json.dumps(body).encode("utf-8"),headers=headers,method="POST")
            with urlopen(req,timeout=45) as response:
                content=response.read(MAX_RESPONSE+1)
                if len(content)>MAX_RESPONSE:
                    raise ValueError("Respuesta Gemini demasiado grande")
            return json.loads(content.decode("utf-8"))
    reply=transport(
        ENDPOINT+model+":generateContent",
        payload,{"x-goog-api-key":api_key,"Content-Type":"application/json"}
    )
    try:
        generated="".join(part.get("text","") for part in reply["candidates"][0]["content"]["parts"])
    except (TypeError,IndexError,KeyError) as exc:
        raise ValueError("Gemini no devolvió respuesta de investigación utilizable") from exc
    result=parse_candidate_output(generated,evidence,"gemini_free")
    result["model"]=model
    result["prompt_sha256"]=hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    result["charged_api_calls_verified_free"]=False
    result["source_data_public_only_required"]=True
    return result


def run_qwen_local(topic,evidence,*,generate):
    """Adapter para el motor Qwen local; generate es un callback CPU, NO web."""
    if not callable(generate):
        raise ValueError("Falta función Qwen LLM local")
    prompt=request_document(topic,evidence)
    result=parse_candidate_output(generate(prompt),evidence,"qwen_local")
    result["model"]="qwen_local_configured_by_workflow"
    result["prompt_sha256"]=hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    return result
