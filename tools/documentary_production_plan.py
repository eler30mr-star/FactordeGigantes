"""Guion autónomo -> tareas trazables de voz y visuales, todavía sin producir.

No carga modelos, no descarga recursos y no concede aprobaciones. Cada toma
conserva texto, posición y citas del borrador; la voz requerida es la canónica.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re

from tools.approved_voice import FILE_NAME, SHA
from tools.documentary_blueprint import WPM

MAX_TAKE_CHARS = 260
MAX_TAKES = 128
WORD = re.compile(r"\b[\wÁÉÍÓÚÜÑáéíóúüñ]+\b")
HASH = re.compile(r"^[a-f0-9]{64}$")


def segment_text(text):
    """Cortes acotados entre palabras; concatenarlos recupera el texto exacto."""
    parts, start = [], 0
    while start < len(text):
        end = min(start + MAX_TAKE_CHARS, len(text))
        if end < len(text):
            boundaries = [m.end() for m in re.finditer(r"[.!?;:]\s+", text[start:end])
                          if m.end() >= 90]
            if not boundaries:
                boundaries = [m.end() for m in re.finditer(r"\s+", text[start:end])]
            if not boundaries:
                raise ValueError("La narración contiene una palabra fuera del límite de toma")
            end = start + boundaries[-1]
        parts.append((start, end, text[start:end]))
        start = end
    return parts


def prepare_production(script):
    if not isinstance(script, dict) or script.get("schema") != "fdg_documentary_script_v1":
        raise ValueError("Se requiere el borrador original del guionista")
    for flag in ("publication_authorized", "ready_for_render"):
        if script.get(flag) is not False:
            raise ValueError("El planificador no admite permisos de producción")
    digest = hashlib.sha256(json.dumps(script, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    base = {"schema": "fdg_documentary_production_plan_v1", "project": "Factor de Gigantes",
            "wikidata_id": script.get("wikidata_id"), "company": script.get("company"),
            "source_script_sha256": digest, "source_research_sha256": script.get("source_research_sha256"),
            "canonical_voice": {"file": FILE_NAME, "sha256": SHA,
                                "reference_file_checked": False, "substitution_allowed": False},
            "scenes": [], "planned_voice_takes": 0, "generated_voice_takes": 0,
            "downloaded_visual_assets": 0, "factual_approval": False,
            "voice_license_verified": False, "visual_rights_verified": False,
            "ready_for_render": False, "publication_authorized": False}
    status = script.get("status")
    if isinstance(status, str) and status.startswith("blocked_"):
        if script.get("scenes") != []:
            raise ValueError("Un guion bloqueado no puede contener escenas producibles")
        return {**base, "status": "blocked_script_unavailable",
                "blocking_reasons": script.get("blocking_reasons", ["script_unavailable"])}
    if (status != "editorial_draft_unapproved" or
            any(script.get(k) is not False for k in
                ("factual_approval", "voice_license_verified", "visual_rights_verified")) or
            script.get("factual_review_required") is not True or
            not isinstance(script.get("source_research_sha256"), str) or
            not HASH.fullmatch(script["source_research_sha256"]) or
            not isinstance(script.get("wikidata_id"), str) or
            not re.fullmatch(r"Q[1-9][0-9]*", script["wikidata_id"]) or
            not isinstance(script.get("company"), str) or not 3 <= len(script["company"]) <= 130):
        raise ValueError("Borrador sin procedencia o revisión pendiente explícita")
    scenes = script.get("scenes")
    if not isinstance(scenes, list) or not 6 <= len(scenes) <= 8:
        raise ValueError("Plan de escenas documental incompleto")
    planned, total_words, total_takes = [], 0, 0
    for number, scene in enumerate(scenes, 1):
        if (not isinstance(scene, dict) or type(scene.get("scene_number")) is not int or
                scene["scene_number"] != number or scene.get("facts_approved") is not False or
                scene.get("rights_verified") is not False):
            raise ValueError("Escena alterada o aprobaciones ajenas al borrador")
        paragraphs = scene.get("paragraphs")
        if not isinstance(paragraphs, list) or not 1 <= len(paragraphs) <= 8:
            raise ValueError("Escena sin párrafos citados")
        tasks, visuals = [], []
        scene_start = math.ceil(total_words * 60 / WPM)
        for pnum, paragraph in enumerate(paragraphs, 1):
            if not isinstance(paragraph, dict):
                raise ValueError("Párrafo inválido")
            text, refs, claims = (paragraph.get(k) for k in ("text", "evidence_ids", "claim_indices"))
            if (not isinstance(text, str) or not 40 <= len(text) <= 3500 or
                    paragraph.get("human_verified") is not False or
                    not isinstance(refs, list) or not 1 <= len(refs) <= 8 or
                    any(not isinstance(x, str) or not re.fullmatch(r"E00[1-9]|E010", x) for x in refs) or
                    len(set(refs)) != len(refs) or
                    not isinstance(claims, list) or not 1 <= len(claims) <= 8 or
                    any(type(x) is not int or not 1 <= x <= 8 for x in claims) or
                    len(set(claims)) != len(claims)):
                raise ValueError("Narración sin citas o identidad de afirmación")
            paragraph_id = f"S{number:02d}_P{pnum:02d}"
            for part, (start, end, exact_text) in enumerate(segment_text(text), 1):
                tasks.append({"id": f"{paragraph_id}_T{part:02d}", "paragraph_id": paragraph_id,
                              "text": exact_text, "character_start": start, "character_end": end,
                              "text_sha256": hashlib.sha256(exact_text.encode()).hexdigest(),
                              "claim_indices": list(claims), "evidence_ids": list(refs),
                              "state": "blocked_pending_editorial_and_voice_rights",
                              "requires_segmentation_review": len(exact_text.strip()) < 90})
            visuals.append({"paragraph_id": paragraph_id, "narration_text": text,
                            "claim_indices": list(claims), "evidence_ids": list(refs),
                            "state": "awaiting_original_or_licensed_visuals", "assets": [],
                            "rights_verified": False})
            total_words += len(WORD.findall(text))
        if scene.get("narration_text") != "\n\n".join(p["text"] for p in paragraphs):
            raise ValueError("Narración de escena distinta de los párrafos citados")
        end = math.ceil(total_words * 60 / WPM)
        if (type(scene.get("start_seconds_estimated")) is not int or
                scene["start_seconds_estimated"] != scene_start or
                type(scene.get("end_seconds_estimated")) is not int or
                scene["end_seconds_estimated"] != end):
            raise ValueError("La estimación de escena no corresponde a su texto")
        total_takes += len(tasks)
        planned.append({"scene_number": number, "voice_takes": tasks, "visual_requests": visuals,
                        "start_seconds_estimated": scene_start, "end_seconds_estimated": end,
                        "actual_audio_duration_seconds": None, "ready_for_render": False})
    seconds = math.ceil(total_words * 60 / WPM)
    if (not 480 <= seconds <= 840 or total_takes > MAX_TAKES or
            script.get("narration_word_count") != total_words or
            script.get("estimated_duration_seconds") != seconds or
            script.get("duration_is_estimate") is not True or script.get("narration_wpm") != WPM):
        raise ValueError("Duración o presupuesto de producción incompatible")
    return {**base, "status": "production_plan_unapproved", "scenes": planned,
            "planned_voice_takes": total_takes, "narration_word_count": total_words,
            "estimated_duration_seconds": seconds, "duration_is_estimate": True,
            "blocking_reasons": ["human_factual_review_required", "canonical_voice_rights_required",
                                 "licensed_scene_assets_required", "human_render_approval_required"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = prepare_production(json.loads(args.script.read_text(encoding="utf-8-sig")))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PLAN_PRODUCCION:", result["status"], "TOMAS_PLANIFICADAS:", result["planned_voice_takes"],
          "TOMAS_GENERADAS:", result["generated_voice_takes"])


if __name__ == "__main__":
    main()
