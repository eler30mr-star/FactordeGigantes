"""Ampliar y contrastar un expediente D1 sin repetir radar, Qwen ni Gemini.

Las afirmaciones permanecen candidatas. Sólo el revisor puede asignar nuevos
pasajes de apoyo; descubrir una URL o una coincidencia no verifica el hecho.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re

from tools.ai_clients import FreeClients
from tools.ai_control import ControlClient
from tools.ai_source_discovery import discover_sources, CITATION_SCAN_METHOD
from tools.ai_research_pipeline import evidence_gaps, validate_report_locally
from tools.documentary_script import revalidate_source_metadata
from tools.documentary_blueprint import inspect_episode
from tools.research_source_plan import prioritized_targets
from tools.research_diagnostics import research_summary
from tools.review_research import review_existing
from tools.review_candidates import METHOD as REVIEW_METHOD
from tools.research_engine import fetch_public

METHOD = 'corroboration_continuation_v1'


def passage_key(p):
    # No considerar el HTML dinámico como texto nuevo si conserva el pasaje.
    return p['url'], p.get('page'), p['excerpt']


def continuation_selection(research):
    by_id = {e['id']: e for e in research['evidence_manifest']}
    targets = []
    for row in research['source_quality']['claim_gaps']:
        if not row['gaps']:
            continue
        claim = research['candidate_claims'][row['claim_index']-1]
        targets.append({'claim_index': row['claim_index'], 'statement': claim['statement'],
                        'cited_urls': list(dict.fromkeys(by_id[k]['url'] for k in claim['evidence_ids'])),
                        'gaps': row['gaps']})
    previous = research.get('corroboration_continuation') or {}
    # Un cambio de afirmaciones reinicia la rotación; nunca reutilizar índices
    # pertenecientes a otra versión del analista.
    claim_digest = hashlib.sha256(json.dumps(
        [c['statement'] for c in research['candidate_claims']], ensure_ascii=False).encode()).hexdigest()
    visited = previous.get('visited_target_indices', []) if previous.get('claims_sha256') == claim_digest else []
    available = [t for t in prioritized_targets(targets) if t['claim_index'] not in visited]
    if not available:
        visited = []
        available = prioritized_targets(targets)
    batch = available[:3]
    target = batch[0] if batch else None
    attempted = list(dict.fromkeys([
        *research.get('retrieval_history_urls', []),
        *previous.get('attempted_urls', []),
        *(research.get('retrieval_budget') or {}).get('attempted_urls', []),
        *(e['url'] for e in research['evidence_manifest']),
    ]))[-40:]
    scanned = set(previous.get('ranked_citation_scanned_urls', []))
    budget=research.get('retrieval_budget') or {}
    if budget.get('citation_scan_method') == CITATION_SCAN_METHOD:
        scanned.update(budget.get('citation_scanned_urls', []))
    scanned.update(d.get('url') for d in research.get('source_documents', [])
                   if d.get('citation_scan_method') == CITATION_SCAN_METHOD)
    expansions = [u for u in (target or {}).get('cited_urls', []) if u not in scanned][:2]
    return {'selected_wikidata_id': research['selected_wikidata_id'],
            'research_queue': {'wikidata_id': research['selected_wikidata_id'], 'title': research['company']},
            'prior_attempted_urls': attempted, 'prior_evidence_manifest': [],
            'prior_research_targets': batch, 'citation_expansion_urls': expansions}, \
        {'claims_sha256': claim_digest, 'visited_target_indices': visited,
         'target_claim_index': target['claim_index'] if target else None,
         'target_claim_indices': [row['claim_index'] for row in batch]}


def merge_passages(research, discovered):
    """Conservar TODAS las citas activas y añadir documentos antes de repetirlos."""
    old = research['evidence_manifest']
    active = {key for c in research['candidate_claims'] for key in c['evidence_ids']}
    required = [e for e in old if e['id'] in active]
    old_keys = {passage_key(e) for e in old}
    fresh, seen = [], set()
    buckets = {}
    for e in discovered['evidence_manifest']:
        key = passage_key(e)
        if key not in old_keys and key not in seen:
            seen.add(key)
            buckets.setdefault(e['url'], []).append(e)
    while any(buckets.values()):
        for values in buckets.values():
            if values:
                fresh.append(values.pop(0))
    additions = fresh[:max(0, 10-len(required))]
    if not additions:
        return copy.deepcopy(old), copy.deepcopy(research['candidate_claims']), 0
    picked = required + additions
    # Usar espacios sobrantes para contexto histórico, sin desplazar citas activas.
    picked += [e for e in old if e['id'] not in active][:10-len(picked)]
    out = [{**copy.deepcopy(e), 'id': f'E{n:03d}'} for n,e in enumerate(picked, 1)]
    remap = {e['id']: out[i]['id'] for i,e in enumerate(required)}
    claims = []
    for c in research['candidate_claims']:
        # La atribución histórica completa permanece en el expediente padre.
        # No arrastrar IDs numéricos de su matriz hacia un manifiesto diferente.
        clean = {k:copy.deepcopy(v) for k,v in c.items()
                 if k not in ('analysis_evidence_ids', 'removed_support_evidence_ids')}
        clean['evidence_ids'] = [remap[key] for key in c['evidence_ids']]
        claims.append(clean)
    return out, claims, len(additions)


def continue_corroboration(research, *, source_run_id, clients, discover=discover_sources):
    if not isinstance(source_run_id, str) or not re.fullmatch(r'ai-[a-f0-9]{28}', source_run_id):
        raise ValueError('Se requiere expediente D1 original')
    report = revalidate_source_metadata(research)
    validate_report_locally(report)
    base = {'schema': 'fdg_corroboration_resumption_v1', 'source_run_id': source_run_id,
            'radar_repeated': False, 'research_inference_repeated': False,
            'new_passages': 0, 'source_downloads': 0, 'review_inference_calls': 0,
            'publication_authorized': False, 'report': None}
    if not report['candidate_claims']:
        return {**base, 'status': 'blocked_no_candidate_claims'}
    previous = report.get('corroboration_continuation') or {}
    if previous.get('new_passages', 0) and report.get('support_review_method') != REVIEW_METHOD:
        return {**base, 'status': 'awaiting_saved_passage_review'}
    selection, progress = continuation_selection(report)
    if progress['target_claim_index'] is None:
        return {**base, 'status': 'skipped_no_source_gaps'}
    # Si todas las ranuras contienen citas activas, ninguna fuente nueva cabría.
    # No descargar ni gastar buscadores cuando no se puede ampliar el manifiesto.
    active = {key for c in report['candidate_claims'] for key in c['evidence_ids']}
    if len(active) >= 10:
        return {**base, 'status': 'blocked_evidence_capacity'}
    discovered = discover(selection, clients=clients, gdelt_fetcher=fetch_public)
    evidence, claims, count = merge_passages(report, discovered)
    budget = discovered['retrieval_budget']
    progress.update(method=METHOD, source_run_id=source_run_id,
        source_collected_on=research['collected_on'], research_inference_repeated=False,
        source_report_sha256=hashlib.sha256(json.dumps(research, ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
        visited_target_indices=list(dict.fromkeys(progress['visited_target_indices']+progress['target_claim_indices'])),
        attempted_urls=list(dict.fromkeys([
            *previous.get('attempted_urls', []), *selection['prior_attempted_urls'], *budget['attempted_urls']]))[-40:],
        ranked_citation_scanned_urls=list(dict.fromkeys([
            *previous.get('ranked_citation_scanned_urls', []),
            *(budget.get('citation_scanned_urls', []) if budget.get('citation_scan_method') == CITATION_SCAN_METHOD else []),
            *(d['url'] for d in discovered['source_documents']
              if d.get('citation_scan_method') == CITATION_SCAN_METHOD)]))[-40:],
        new_passages=count)
    report.update(evidence_manifest=evidence, candidate_claims=claims,
        collected_on=datetime.now(timezone.utc).date().isoformat(),
        source_documents=discovered['source_documents'], retrieval_budget=budget,
        discovery_plan=discovered['discovery_plan'], research_targets=discovered['research_targets'],
        corroboration_continuation=progress, source_quality=evidence_gaps(evidence, claims))
    # Clasificación y preliminares antiguos tienen otros IDs. La versión padre
    # los conserva; no se presentan como un nuevo trabajo Qwen/Gemini.
    report['classification'] = []
    report['preliminary_claims'] = []
    report.pop('research_freshness', None)
    discovery_providers = {'wikipedia', 'gdelt', 'tavily', 'exa', 'd1_history', 'document_citations'}
    report['stages'] = [s for s in report['stages'] if s['provider'] not in discovery_providers] + discovered['stages']
    result = {**base, 'new_passages': count, 'source_downloads': budget['attempted'],
              'target_claim_index': progress['target_claim_index']}
    if not count:
        validate_report_locally(report)
        return {**result, 'status': 'no_new_passages', 'report': report}
    report['reviews'] = []
    report.pop('support_review_method', None)
    report['stages'] = [s for s in report['stages'] if s['provider'] != 'groq'] + [
        {'provider': 'groq', 'role': 'review', 'status': 'pending_new_passages'}]
    validate_report_locally(report)
    reviewed = review_existing(report, clients=clients, source_run_id=source_run_id)
    if reviewed['report'] is not None:
        report = reviewed['report']
    else:
        # Guardar las lecturas nuevas antes de que caduque el artefacto; el cron
        # de revisión puede continuar sin repetir descarga ni investigadores.
        report['corroboration_continuation']['review_pending_reason'] = reviewed.get('reason', reviewed['status'])
    validate_report_locally(report)
    return {**result, 'status': 'review_completed_candidate_only' if reviewed['report'] else 'sources_saved_pending_review',
            'review_inference_calls': reviewed['review_inference_calls'], 'report': report}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run-id', default='latest')
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    control = ControlClient()
    context = control.script_context(a.run_id)
    if not context.get('ok') or context.get('existing_script_draft') or \
            context.get('selection', {}).get('research_queue', {}).get('state') == 'review':
        result = {'schema': 'fdg_corroboration_resumption_v1', 'status': 'skipped_no_research_work',
                  'report': None, 'publication_authorized': False}
    else:
        result = continue_corroboration(context['research'], source_run_id=context['run_id'],
                                       clients=FreeClients(reserve=control.reserve))
    def save():
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    save()
    if result['report'] is not None:
        receipt = control.persist(result['report'])
        result['receipt'] = receipt
        print('EQUIPO_IA_D1:', receipt['run_id'])
        print('INVESTIGACION_DIAGNOSTICO:', json.dumps(research_summary(result['report']), ensure_ascii=False))
        plan = inspect_episode(result['report'], context['selection'])
        if plan['status'] == 'source_grounded_outline_unapproved' and os.getenv('GITHUB_OUTPUT'):
            with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
                output.write('run_id='+receipt['run_id']+'\n')
        save()
    print('CONTRASTE_REANUDADO:', result['status'], 'PASAJES_NUEVOS:', result.get('new_passages',0),
          'DESCARGAS:', result.get('source_downloads',0), 'GROQ_SOLICITUDES:', result.get('review_inference_calls',0),
          'RADAR_QWEN_GEMINI_REPETIDOS: NO')


if __name__ == '__main__':
    main()

