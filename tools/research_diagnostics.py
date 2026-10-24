"""Resumen acotado de evidencia pública para explicar bloqueos sin secretos."""
from __future__ import annotations


def research_summary(report):
    quality = report.get("source_quality") or {}
    by_claim = {r["claim_index"]: r for r in quality.get("claim_gaps", [])}
    reviews = {r["claim_index"]: r["assessment"] for r in report.get("reviews", [])}
    return {
        "schema": "fdg_research_diagnostics_v1", "company": report.get("company"),
        "wikidata_id": report.get("selected_wikidata_id"),
        "unique_documents": quality.get("unique_documents", 0),
        "regulatory_primary_domains": quality.get("regulatory_primary_domains", 0),
        "original_primary_domains": quality.get("original_primary_domains", 0),
        "review_contract_failures": [s['contract_failure'] for s in report.get('stages',[]) if 'contract_failure' in s],
        "discovery_plan": report.get("discovery_plan", []),
        "retrieval_budget": report.get("retrieval_budget"),
        "source_documents": [{k: d[k] for k in (
            "url", "resolved_url", "status", "mime", "bytes_read", "readable_blocks",
            "entity_name_in_payload", "first_block_preview", "error_type", "discovered_by",
            "discovered_from", "discovered_from_page", "citation_links_scanned", "reference_urls") if k in d}
            for d in report.get("source_documents", [])[:8]],
        "evidence": [{k: e[k] for k in ("id", "url", "excerpt", "page", "source_class",
                     "document_sha256", "selection_method", "entity_context_excerpt") if k in e}
                     for e in report.get("evidence_manifest", [])[:10]],
        "claims": [{"claim_index": n, "statement": c["statement"], "evidence_ids": c["evidence_ids"],
                    "analysis_evidence_ids": c.get("analysis_evidence_ids", c["evidence_ids"]),
                    "source_assessments": next((r.get('source_assessments',[]) for r in report.get('reviews',[])
                                                if r['claim_index']==n),[]),
                    "gaps": by_claim.get(n, {}).get("gaps", []),
                    "review_assessment": reviews.get(n, "not_reviewed")}
                   for n, c in enumerate(report.get("candidate_claims", [])[:8], 1)],
        "facts_verified": False, "publication_authorized": False,
    }
