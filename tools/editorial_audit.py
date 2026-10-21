"""Auditoría factual conservadora y escaleta de 10 min para Factor de Gigantes.

Analiza SOLO pasajes ya obtenidos y URLs trazables. Ninguna coincidencia de texto
se convierte en hecho verificado. No modifica guiones, D1 ni publicaciones.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

BEATS = (
    ("El enigma", 45, "Abrir una pregunta que merezca investigación, no anunciar una conclusión."),
    ("El origen", 50, "Identificar fundación, protagonistas y contexto con fechas documentadas."),
    ("El contexto", 55, "Explicar mercado y tecnología antes del punto de inflexión."),
    ("La primera ventaja", 55, "Mostrar qué diferenciaba al protagonista y citar su fuente."),
    ("La expansión", 50, "Exponer distribución, clientes o adopción sin exagerar cifras."),
    ("Las señales de cambio", 50, "Ordenar acontecimientos y separar fechas de interpretaciones."),
    ("La decisión difícil", 60, "Reconstruir decisiones solo cuando existan documentos o declaraciones."),
    ("La competencia", 50, "Comparar hitos y resultados sin inventar causalidad."),
    ("Las consecuencias", 55, "Vincular impactos con informes y métricas de años comparables."),
    ("La transformación", 50, "Distinguir cambios anunciados de resultados comprobados."),
    ("Lo que enseñan los datos", 50, "Exponer conclusiones prudentes y alternativas explicativas."),
    ("La pregunta final", 30, "Cerrar con una pregunta sustentable sin inventar moralejas."),
)
assert sum(seconds for _, seconds, _ in BEATS) == 600

YEAR = re.compile(r"(?<!\d)(?:18|19|20)\d{2}(?!\d)")
NUMBER = re.compile(r"(?<![\w])\d{1,3}(?:[.,]\d{3})+(?:[.,]\d+)?(?!\w)|(?<![\w])\d+(?:[.,]\d+)?(?!\w)")
ID = re.compile(r"^C\d{2,3}$")


def numbers_from_text(text):
    return sorted(set(NUMBER.findall(text)), key=lambda n: (len(n), n))


def domain_from_url(url):
    try:
        parsed = urlsplit(url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            return None
        host = parsed.hostname.lower().rstrip(".")
        return host[4:] if host.startswith("www.") else host
    except (ValueError, TypeError, AttributeError):
        return None


def audit_report(report):
    """Marcar carencias por afirmación; no resolver hechos automáticamente."""
    if not isinstance(report, dict) or not isinstance(report.get("candidate_claims"), list):
        raise ValueError("Informe no válido")
    source_types = {item.get("source_id"): item.get("source_class")
                    for item in report.get("sources", []) if isinstance(item, dict)}
    findings = []
    used_ids = set()
    for item in report["candidate_claims"][:50]:
        cid = item.get("id")
        if not isinstance(cid, str) or not ID.fullmatch(cid) or cid in used_ids:
            raise ValueError("ID de afirmación inválido o repetido")
        used_ids.add(cid)
        claim = str(item.get("proposition", ""))[:500]
        snippets = (item.get("candidate_passages") or [])[:8]
        evidence = [p for p in snippets if isinstance(p, dict)
                    and p.get("source_id") and domain_from_url(p.get("url"))]
        domains = sorted({domain_from_url(p["url"]) for p in evidence})
        claim_numbers = numbers_from_text(claim)
        claims_with_matching_numbers = [
            p for p in evidence
            if not claim_numbers or all(n in numbers_from_text(str(p.get("excerpt", ""))) for n in claim_numbers)
        ]
        candidate_years = sorted({y for p in evidence for y in YEAR.findall(str(p.get("excerpt", "")))})
        claim_years = sorted(set(YEAR.findall(claim)))
        flags = []
        if not evidence:
            flags.append("sin_pasaje_rastreable")
        if evidence and len(domains) < 2:
            flags.append("sin_contraste_de_dos_dominios")
        if any(source_types.get(p["source_id"]) == "secondary_discovery_not_primary"
               for p in evidence):
            flags.append("fuente_secundaria_requiere_primaria")
        if claim_numbers and not claims_with_matching_numbers:
            flags.append("numeros_no_coinciden_en_un_pasaje")
        if claim_years and candidate_years and not set(claim_years).intersection(candidate_years):
            flags.append("anos_de_fuentes_difieren_revisar_contexto")
        if not flags:
            flags.append("coincidencia_sin_validacion_humana")
        findings.append({
            "claim_id": cid,
            "segment_index": item.get("segment_index"),
            "evidence_source_ids": sorted({p["source_id"] for p in evidence}),
            "domains": domains, "claimed_numbers": claim_numbers[:12],
            "candidate_years": candidate_years[:12],
            "numeric_alignment_in_passage": bool(claims_with_matching_numbers) if claim_numbers else None,
            "possible_issue_flags": flags,
            "needs_human_review": True,
            "verified": False,
        })
    counts = dict(sorted(Counter(flag for item in findings for flag in item["possible_issue_flags"]).items()))
    return {
        "product": "Factor de Gigantes", "topic": report.get("topic", ""),
        "source_report_version": report.get("engine_version"),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "claim_count": len(findings), "findings": findings, "flag_counts": counts,
        "confirmed_contradictions": 0,
        "human_verified_claims": 0,
        "automatic_rights_clearance": False,
        "ready_for_render": False, "ready_for_youtube": False,
        "warning": "Los indicadores señalan posibles huecos, no contradicciones demostradas. Las coincidencias numéricas no prueban contexto ni veracidad."
    }


def build_documentary_beat_sheet(report, audit):
    """Escaleta de investigación, no guion narrativo autorizado."""
    claims = report.get("candidate_claims", [])[:50]
    assigned = [[] for _ in BEATS]
    for i, claim in enumerate(claims):
        # Distribuir evidencia por orden y mantener todos los ID presentes.
        ix = min(len(BEATS)-1, i * len(BEATS) // max(1, len(claims)))
        assigned[ix].append(claim.get("id", "?"))
    lines = [
        "# Factor de Gigantes · escaleta documental de trabajo (NO APROBADA)", "",
        f"**Tema:** {str(report.get('topic', 'Sin tema'))[:130]}",
        "**Duración objetivo:** 10:00 (dentro del formato de 8–14 min).",
        "**Estado:** preguntas de investigación, no narración final. No hay autorización de publicación.",
        "**Narrador y audiovisuales:** derechos pendientes de revisión independiente.", "",
        "## Estructura de escenas", "",
    ]
    for i, ((name, duration, brief), claim_ids) in enumerate(zip(BEATS, assigned), 1):
        lines.extend([
            f"### {i:02d}. {name} — {duration} s",
            brief,
            "Afirmaciones candidatas: " + (", ".join(claim_ids) if claim_ids else "SIN EVIDENCIA ASIGNADA."),
            "Narración: [PENDIENTE DE HECHOS CONTRASTADOS Y REDACCIÓN ORIGINAL].",
            "Visuales: [PENDIENTE DE CREACIÓN O LICENCIA DOCUMENTADA].",
            ""
        ])
    lines.extend([
        "## Condiciones para avanzar a guion", "",
        f"- {audit['claim_count']} afirmaciones candidatas, **0 verificadas por este motor**.",
        "- Obtener fuentes primarias y contrastar cifras, fechas y causalidad por afirmación.",
        "- Revisar derechos comerciales del narrador, imágenes, música y material externo.",
        "- No enviar a render ni a YouTube por el mero hecho de existir esta escaleta.", "",
    ])
    return "\n".join(lines)


def save_audit(report, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    audit = audit_report(report)
    (output / "AUDITORIA_EDITORIAL.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "ESCALETA_DOCUMENTAL_10MIN_NO_APROBADA.md").write_text(
        build_documentary_beat_sheet(report, audit), encoding="utf-8")
    return audit


def main():
    parser = argparse.ArgumentParser(description="Auditar posibles evidencias y preparar escaleta de 10 min")
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    result = save_audit(report, args.out)
    print("AUDITORIA:",result["claim_count"],"afirmaciones; potenciales brechas:",
          result["flag_counts"],"; hechos acreditados: 0",flush=True)


if __name__ == "__main__":
    main()
