"""Asistente de escritura IA local, limitado exclusivamente a pasajes de investigación.

Qwen3-0.6B se ejecuta en CPU; no envía datos de proyecto a una API LLM externa.
Las frases generadas NO son verificaciones ni guiones aprobados.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import time

from tools.research_engine import assemble_ai_evidence

DEFAULT_MODEL = "Qwen/Qwen3-0.6B"
MAX_INPUT = 12000
MAX_NEW_TOKENS = 360
PROMPT_RULES = """Eres el asistente de investigación para el canal español Factor de Gigantes.
Redacta un BORRADOR de desarrollo documental breve, original y cinematográfico en
español latinoamericano, solo a partir de los pasajes localizados a continuación.
REGLAS NO NEGOCIABLES:
- No inventes fechas, cifras, causas, diálogos, motivaciones internas ni resultados.
- No presentes coincidencias textuales como datos verificados.
- Cada afirmación factual propuesta debe citar explícitamente [S01], [S02], etc.,
  donde el identificador corresponda a uno de los pasajes presentados.
- Si el pasaje no prueba el dato, escribe "PENDIENTE DE CONTRASTAR" y una pregunta
  de investigación específica. No ocultes contradicciones.
- No afirmes que la voz, música, fotografías o clips pueden utilizarse comercialmente.
- No copies párrafos extensos de la fuente.
Entrega los apartados:
1) Pregunta poderosa de apertura.
2) Secuencia narrativa propuesta con citas [Sxx] y advertencias.
3) Qué necesitamos investigar para convertirla en un documental de 8-14 minutos.
4) Fuentes independientes que faltan y riesgos editoriales.
No declares listo el guion, no ordenes publicar ni renderizar."""


def build_messages(report: dict) -> list[dict]:
    if report.get("production_ready") is not False or report.get("facts_verified_automatically") != 0:
        raise ValueError("El asistente solo acepta reportes preliminares no verificados")
    passages = [e for claim in report.get("candidate_claims", [])
                for e in claim.get("candidate_passages", [])]
    if not passages:
        raise ValueError("Sin pasajes: no se permite inventar un guion basado en documentos")
    context = assemble_ai_evidence(report, MAX_INPUT)
    if len(context) < 70:
        raise ValueError("No hay evidencia suficiente para preparar un borrador")
    return [{"role": "system", "content": PROMPT_RULES},
            {"role": "user", "content": context}]


def result_metadata(report: dict, text: str, *, model_id: str, seconds: float):
    if not isinstance(text, str) or len(text.strip()) < 80:
        raise ValueError("El modelo no produjo una propuesta textual útil")
    used = sorted({p["source_id"] for c in report["candidate_claims"]
                   for p in c.get("candidate_passages", [])})
    cited = sorted(set(re.findall(r"\[S\d{2,3}\]", text)))
    unauthorized = [x for x in cited if x[1:-1] not in used]
    return {
        "model": model_id, "backend": "local_cpu_transformers",
        "no_paid_ai_api": True, "source_ids_available": used,
        "source_markers_in_output": cited,
        "unsupported_source_ids": unauthorized,
        "needs_editor_review": True,
        "claim_verification_automatic": False,
        "copyright_and_commercial_rights_verified": False,
        "narrator_reference_changed": False,
        "approved_for_render": False,
        "approved_for_youtube": False,
        "inference_seconds": round(seconds, 2),
        "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }


def create_draft(report: dict, output: Path, model_id: str = DEFAULT_MODEL,
                 max_new_tokens: int = 260):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    if not 80 <= max_new_tokens <= MAX_NEW_TOKENS:
        raise ValueError("La inferencia local debe tener límites CPU acotados")
    messages = build_messages(report)
    started = time.monotonic()
    torch.set_num_threads(4)
    torch.manual_seed(20261020)
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=False)
    model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float32)
    model.eval()
    encoded = tokenizer.apply_chat_template(
        messages, tokenize=True, add_generation_prompt=True,
        enable_thinking=False, return_tensors="pt"
    )
    if encoded.shape[-1] > 3900:
        raise ValueError("Contexto demasiado extenso para el ensayo gratuito")
    with torch.inference_mode():
        result = model.generate(
            encoded, max_new_tokens=max_new_tokens,
            do_sample=False, pad_token_id=tokenizer.eos_token_id
        )
    text = tokenizer.decode(result[0][encoded.shape[-1]:], skip_special_tokens=True).strip()
    metadata = result_metadata(report, text, model_id=model_id,
                               seconds=time.monotonic()-started)
    output.mkdir(parents=True, exist_ok=True)
    heading = (
        "# BORRADOR IA NO VERIFICADO — Factor de Gigantes\n\n"
        "**Uso interno exclusivamente. Ninguna afirmación aprobada automáticamente.**\n\n"
        f"**Modelo local:** {model_id}\n"
        f"**Asunto:** {report['topic']}\n\n"
        "---\n\n"
    )
    (output / "BORRADOR_IA_NO_VERIFICADO.md").write_text(
        heading + text + "\n\n---\n\n"
        "Revisión humana obligatoria de cada afirmación, fuente y material audiovisual.\n",
        encoding="utf-8"
    )
    (output / "metadatos_ia.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2)+"\n", encoding="utf-8"
    )
    print("IA_LOCAL:", len(text), "caracteres. Citas:", metadata["source_markers_in_output"],
          "referencias fuera del contexto:", metadata["unsupported_source_ids"], flush=True)
    return metadata


def main():
    parser = argparse.ArgumentParser(description="Qwen local sin servicios de pago ni publicación")
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("dist/research"))
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--max-new-tokens", type=int, default=260)
    args = parser.parse_args()
    report=json.loads(args.report.read_text(encoding="utf-8"))
    create_draft(report,args.out,args.model,args.max_new_tokens)


if __name__ == "__main__":
    main()
