"""Expediente editorial consolidado: evidencias, SEC, diferencias y bloqueos.

El paquete organiza lo que ya se extrajo. No evalúa licencias ni convierte
metadatos SEC/XBRL en afirmaciones periodísticas verificadas.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

MAX_CLAIMS=50
MAX_SOURCES=30


def safe_line(value,limit=220):
    return " ".join(str(value or "").replace("[","(").replace("]",")").split())[:limit]


def summarize(research, audit, edgar=None, finance=None, blackberry=None):
    if not isinstance(research,dict) or not isinstance(audit,dict):
        raise ValueError("Informe y auditoría requeridos")
    claims=research.get("candidate_claims",[])
    findings=audit.get("findings",[])
    if not isinstance(claims,list) or len(claims)>MAX_CLAIMS or not isinstance(findings,list):
        raise ValueError("Afirmaciones fuera de presupuesto")
    by_id={x["claim_id"]:x for x in findings if isinstance(x,dict) and isinstance(x.get("claim_id"),str)}
    tasks=[]
    for claim in claims:
        if not isinstance(claim,dict) or claim.get("id") not in by_id:
            raise ValueError("Cada afirmación debe contar con diagnóstico")
        row=by_id[claim["id"]]
        evidence=[{
            "source_id":p.get("source_id"),
            "url":p.get("url"),
            "page":p.get("page"),
            "locator":p.get("locator") or "Ubicación textual sin página confirmada",
            "verification_status":"candidate_unchecked"
        } for p in claim.get("candidate_passages",[])[:3] if isinstance(p,dict)]
        tasks.append({
            "claim_id":claim["id"],
            "question_or_claim":safe_line(claim.get("proposition"),380),
            "issues":list(row.get("possible_issue_flags",[])),
            "candidate_evidence":evidence,
            "editor_action":"Contrastar autoría, fecha, contenido y licencia; aprobar solo tras leer originales.",
            "editorial_verification":"pending_human"
        })
    entities=(edgar or {}).get("entities",[]) if isinstance(edgar,dict) else []
    sec_files=sum(len(x.get("filing_candidates",[])) for x in entities if isinstance(x,dict))
    fin=(finance or {}) if isinstance(finance,dict) else {}
    xbrl=fin.get("analysis")
    discrepancies=(xbrl or {}).get("comparison",{}).get("comparisons",[]) if isinstance(xbrl,dict) else []
    financial_status=fin.get("status","not_queried")
    original_pdf_report=blackberry if isinstance(blackberry,dict) else {}
    original_pdf_facts=[]
    for fact in original_pdf_report.get("facts",[])[:12]:
        if not isinstance(fact,dict) or fact.get("machine_matched_original_pdf") is not True:
            continue
        if fact.get("human_verified") is not False:
            continue
        original_pdf_facts.append({
            "id":fact.get("id"),"metric":fact.get("metric"),
            "period_end":fact.get("period_end"),"accounting_scope":fact.get("accounting_scope"),
            "value_millions_usd":fact.get("value_millions_usd"),
            "url":fact.get("source_url"),"pdf_page":fact.get("pdf_page"),
            "verification_status":"located_in_original_pdf_not_human_approved"
        })
    blockers=[]
    if research.get("fetched_count",0)==0:
        blockers.append("No se obtuvo contenido documental legible.")
    if any(not t["candidate_evidence"] for t in tasks):
        blockers.append("Existen escenas o afirmaciones sin pasajes rastreables.")
    if not entities or not sec_files:
        blockers.append("No se han acreditado documentos regulatorios originales para este tema.")
    if financial_status!="retrieved_structured_candidates":
        blockers.append("Cifras XBRL no recuperadas o no consultadas.")
    if discrepancies:
        blockers.append("Hay diferencias XBRL del mismo periodo que requieren evaluación editorial.")
    if original_pdf_facts:
        blockers.append("Las cifras localizadas en PDF requieren control humano de contexto y comparabilidad.")
    blockers.append("Licencias comerciales de voz, imágenes, música y material externo no comprobadas.")
    return {
        "product":"Factor de Gigantes",
        "topic":safe_line(research.get("topic"),130),
        "claim_count":len(tasks),
        "source_count":min(MAX_SOURCES,len(research.get("sources",[]))),
        "fetched_count":research.get("fetched_count",0),
        "sec_candidate_documents":sec_files,
        "sec_issuer_identity_confirmed":False,
        "xbrl_status":financial_status,
        "xbrl_observation_count":(xbrl or {}).get("observation_count",0) if isinstance(xbrl,dict) else 0,
        "same_period_discrepancy_candidates":len(discrepancies),
        "claims":tasks,
        "corporate_pdf_facts_located":original_pdf_facts,
        "corporate_pdf_facts_human_verified":0,
        "corporate_reporting_scope_warning":original_pdf_report.get("comparability_warning") if original_pdf_facts else None,
        "blockers":blockers,
        "verified_claims":0,
        "voice_rights_verified":False,
        "visual_rights_verified":False,
        "ready_for_narration":False,
        "ready_for_render":False,
        "ready_for_youtube":False,
        "warning":"Expediente para revisión humana, no un documental ni una certificación de hechos."
    }


def to_markdown(result):
    lines=[
        "# FACTOR DE GIGANTES · Dossier para revisión (NO APROBADO)","",
        "**Tema:** "+result["topic"],
        f"**Afirmaciones candidatas:** {result['claim_count']}",
        f"**Fuentes legibles:** {result['fetched_count']}/{result['source_count']}",
        f"**Documentos SEC candidatos:** {result['sec_candidate_documents']}",
        f"**Hechos XBRL extraídos:** {result['xbrl_observation_count']}",
        f"**Diferencias XBRL por revisar:** {result['same_period_discrepancy_candidates']}",
        "**Autorización:** ninguna; revisión humana obligatoria.","",
        "## Lista de decisiones pendientes","",
    ]
    for item in result["claims"]:
        lines.append("### "+item["claim_id"]+" · "+item["question_or_claim"])
        lines.append("Alertas: "+(", ".join(item["issues"]) if item["issues"] else "Sin alertas automáticas, pero NO verificado"))
        if not item["candidate_evidence"]:
            lines.append("No hay evidencia documental vinculada.")
        for ev in item["candidate_evidence"]:
            lines.append("Pasaje candidato: "+safe_line(ev["source_id"],20)+" · "+safe_line(ev["locator"],120))
            lines.append("URL original candidata: "+safe_line(ev["url"],300))
        lines.append("Decisión humana: [PENDIENTE].")
        lines.append("")
    if result.get("corporate_pdf_facts_located"):
        lines.extend(["## Extractos financieros de documentos originales (AÚN SIN APROBAR)",""])
        for fact in result["corporate_pdf_facts_located"]:
            lines.append(
                "- "+safe_line(fact["id"],60)+": "+safe_line(fact["metric"],90)
                +" = US$ "+safe_line(fact["value_millions_usd"],30)+" millones;"
                +" cierre "+safe_line(fact["period_end"],20)
                +"; PDF página "+str(fact["pdf_page"])
                +"; alcance "+safe_line(fact["accounting_scope"],100)
            )
            lines.append("  Documento original: "+safe_line(fact["url"],300))
        lines.extend(["","ADVERTENCIA DE COMPARABILIDAD: "+
                      safe_line(result["corporate_reporting_scope_warning"],440),""])
    lines.extend(["## Bloqueos",""])
    lines.extend("- "+safe_line(b,240) for b in result["blockers"])
    lines.extend(["","**No enviar a render, ni locución comercial, ni YouTube.**",""])
    return "\n".join(lines)


def consolidate(directory):
    directory=Path(directory)
    def read(name,required=False):
        path=directory/name
        if not path.is_file():
            if required:
                raise FileNotFoundError(name)
            return None
        return json.loads(path.read_text(encoding="utf-8"))
    output=summarize(
        read("reporte_investigacion.json",True),
        read("AUDITORIA_EDITORIAL.json",True),
        read("sec_edgar_documentos_candidatos.json"),
        read("METRICAS_SEC_CANDIDATAS_NO_VERIFICADAS.json"),
        read("HECHOS_BLACKBERRY_2024_2025_CON_PAGINAS.json")
    )
    (directory/"EXPEDIENTE_EDITORIAL_PENDIENTE.json").write_text(
        json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (directory/"EXPEDIENTE_PARA_REVISOR.md").write_text(
        to_markdown(output),encoding="utf-8")
    return output


def main():
    parser=argparse.ArgumentParser(description="Consolidar expediente documental con bloqueos editoriales")
    parser.add_argument("--dir",required=True,type=Path)
    args=parser.parse_args()
    obj=consolidate(args.dir)
    print("EXPEDIENTE:",obj["claim_count"],"afirmaciones;",
          obj["sec_candidate_documents"],"documentos SEC candidatos;",
          obj["xbrl_observation_count"],"hechos XBRL;",
          "LISTO: NO",flush=True)


if __name__=="__main__":
    main()
