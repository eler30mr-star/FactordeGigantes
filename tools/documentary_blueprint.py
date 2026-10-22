"""Puerta P1 -> P2: estructura documental atribuida a fuentes, nunca escritura manual.

Consume el expediente generado por Qwen/Gemini/Groq y la selección real D1.
Exige diversidad de documentos, contraste regulatorio y reviews completas.
Hasta superar las puertas devuelve bloqueo SIN escenas ficticias o narración.
La salida aprobable sigue requiriendo guion, derechos, TTS y edición posteriores.
"""
from __future__ import annotations
import argparse,json,math,re
from pathlib import Path
from urllib.parse import urlsplit

QID=re.compile(r"^Q[1-9][0-9]*$")
TARGET_SECONDS=660
WPM=138
MIN_CLAIMS=6
MAX_CLAIMS=8

def inspect_episode(ai,selection):
    if not isinstance(ai,dict) or not isinstance(selection,dict) or \
       ai.get("schema")!="fdg_ai_pipeline_v1":
        raise ValueError("Se requiere expediente original de Factor de Gigantes")
    qid=ai.get("selected_wikidata_id")
    queue=selection.get("research_queue") or {}
    if (ai.get("publication_authorized") is not False or
        ai.get("ready_for_script") is not False or
        ai.get("facts_verified_automatically")!=0):
        raise ValueError("Informe IA declaró autorizaciones incompatibles")
    if qid is None and selection.get("selected_wikidata_id") is None:
        return {"schema":"fdg_documentary_blueprint_v1",
                "status":"blocked_no_market_selection","wikidata_id":None,
                "company":None,"selected_from_real_market":False,
                "source_document_count":0,"independent_domains":0,
                "regulatory_domains":0,"candidate_claim_count":0,"review_count":0,
                "target_duration_seconds":TARGET_SECONDS,"target_narration_wpm":WPM,
                "estimated_narration_words":0,"scenes":[],
                "blocking_reasons":["no_market_candidate_with_real_evidence"],
                "verified_claim_count":0,"factual_approval":False,
                "voice_license_verified":False,"visual_rights_verified":False,
                "ready_for_render":False,"publication_authorized":False}
    if (not isinstance(qid,str) or not QID.fullmatch(qid) or
        qid!=selection.get("selected_wikidata_id") or
        queue.get("wikidata_id")!=qid):
        raise ValueError("La selección del radar no coincide con la investigación")
    company=ai.get("company")
    if not isinstance(company,str) or not 3<=len(company.strip())<=130:
        raise ValueError("Empresa sin título canónico")
    evidence=ai.get("evidence_manifest",[])
    claims=ai.get("candidate_claims",[])
    reviews=ai.get("reviews",[])
    if not all(isinstance(x,list) for x in (evidence,claims,reviews)):
        raise ValueError("El manifiesto documental no tiene forma válida")
    if len(evidence)>10 or len(claims)>MAX_CLAIMS:
        raise ValueError("Exceso de citas o afirmaciones")
    index={e.get("id"):e for e in evidence if isinstance(e,dict)}
    if len(index)!=len(evidence):raise ValueError("Citas repetidas")
    sources=set();domains=set();regulators=set();primary_sources=set()
    for e in evidence:
        if e.get("wikidata_id")!=qid or e.get("company")!=company or \
            not isinstance(e.get("url"),str) or not e["url"].startswith("https://") or \
            not isinstance(e.get("document_sha256"),str) or \
            not re.fullmatch(r"[a-f0-9]{64}",e["document_sha256"]):
            raise ValueError("Cita sin identidad documental")
        host=urlsplit(e["url"]).hostname
        if not host or host=="localhost":raise ValueError("Dominio inválido")
        sources.add((e["url"],e["document_sha256"]))
        domains.add(host)
        if e.get("source_class")=="public_authority_candidate":
            regulators.add(host)
        if e.get("source_class") in (
                "public_authority_candidate","potential_official_pdf",
                "potential_official_primary"):
            primary_sources.add(host)
    by_claim={r.get("claim_index"):r for r in reviews if isinstance(r,dict)}
    if len(by_claim)!=len(reviews):raise ValueError("Revisión duplicada")
    gaps=[]
    if len(sources)<2:gaps.append("at_least_two_original_documents_required")
    if len(domains)<2:gaps.append("at_least_two_independent_domains_required")
    if not primary_sources:gaps.append("original_primary_document_required")
    if len(claims)<MIN_CLAIMS:gaps.append("insufficient_distinct_claims")
    if len(reviews)!=len(claims):gaps.append("review_missing_or_incomplete")
    quality=ai.get("source_quality") or {}
    if quality.get("all_claims_verified") is not False or quality.get("ready_for_script") is not False:
        gaps.append("source_quality_untrusted")
    claim_to_refs=[]
    for pos,c in enumerate(claims,1):
        if (not isinstance(c,dict) or c.get("status")!="candidate_unverified" or
            c.get("human_verified") is not False or
            not isinstance(c.get("statement"),str) or
            not isinstance(c.get("evidence_ids"),list) or not c["evidence_ids"]):
            raise ValueError("Afirmación sin naturaleza candidata")
        refs=c["evidence_ids"]
        if any(ref not in index for ref in refs):
            raise ValueError("La afirmación cita evidencias inexistentes")
        review=by_claim.get(pos)
        if review is None or review.get("assessment")!="supported_by_excerpt":
            gaps.append("claim_"+str(pos)+"_lacks_supported_review")
        cited={index[key]["url"] for key in refs}
        cited_hosts={urlsplit(u).hostname for u in cited}
        if len(cited)<2 or len(cited_hosts)<2:
            gaps.append("claim_"+str(pos)+"_not_independently_corroborated")
        claim_to_refs.append(list(refs))
    for row in quality.get("claim_gaps",[]):
        if isinstance(row,dict) and row.get("gaps"):
            gaps.append("claim_"+str(row.get("claim_index","?"))+"_source_gaps")

    reasons=sorted(set(gaps))
    base={"schema":"fdg_documentary_blueprint_v1","company":company,
          "wikidata_id":qid,"selected_from_real_market":True,
          "source_document_count":len(sources),"independent_domains":len(domains),
          "regulatory_domains":len(regulators),"original_primary_domains":len(primary_sources),
          "candidate_claim_count":len(claims),"review_count":len(reviews),
          "target_duration_seconds":TARGET_SECONDS,"target_narration_wpm":WPM,
          "verified_claim_count":0,"factual_approval":False,
          "voice_license_verified":False,"visual_rights_verified":False,
          "ready_for_render":False,"publication_authorized":False}
    if reasons:
        return {**base,"status":"blocked_insufficient_corroboration",
                "blocking_reasons":reasons,"scenes":[],"estimated_narration_words":0}
    # Estructura derivada de afirmaciones CITADAS, no diálogo fabricado ni
    # escenas BlackBerry prefijadas. Son objetivos de escenas aún sin guion.
    scenes=[]
    prev=0
    for i,c in enumerate(claims):
        end=round(TARGET_SECONDS*(i+1)/len(claims))
        scenes.append({"scene_number":i+1,"start_seconds":prev,"end_seconds":end,
           "source_claim_index":i+1,"citation_ids":claim_to_refs[i],
           "story_beat_candidate":c["statement"][:240],
           "narration_words_target":round((end-prev)*WPM/60),
           "narration_text":None,"scene_visuals":[],
           "facts_approved":False,"rights_verified":False})
        prev=end
    return {**base,"status":"source_grounded_outline_unapproved",
       "blocking_reasons":["human_factual_review_required","scene_assets_licenses_required"],
       "scenes":scenes,
       "estimated_narration_words":sum(x["narration_words_target"] for x in scenes)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--research",type=Path,required=True)
    ap.add_argument("--selection",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    result=inspect_episode(json.loads(args.research.read_text(encoding="utf-8")),
                           json.loads(args.selection.read_text(encoding="utf-8")))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("PLAN_DOCUMENTAL:",result["status"],
          "FUENTES_DISTINTAS:",result["source_document_count"],
          "ESCENAS_PLANIFICADAS:",len(result["scenes"]),
          "PERMISO_PUBLICAR:",result["publication_authorized"])

if __name__=="__main__":main()
