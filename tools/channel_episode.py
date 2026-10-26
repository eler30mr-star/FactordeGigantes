"""Investigate only the persisted chosen episode, then prepare a cited draft."""
import json
import os
import re
import unicodedata
import hashlib
from pathlib import Path
from urllib.parse import urlencode
from tools.ai_control import ControlClient
from tools.ai_clients import FreeClients, ProviderError
from tools.ai_source_discovery import discover_sources
from tools.ai_research_pipeline import analyze_sources, validate_report_locally, source_report
from tools.documentary_script import write_script
from tools.corroborate_research import continue_corroboration
from tools.review_research import review_existing
from tools.editorial_focus import review_editorial_focus, valid_focus, focus_sha
from tools.editorial_search import plan_editorial_search, valid_search_plan
from tools.topic_discovery import property_ids, COMPANY_TYPES
from tools.market_sources import get_json
from tools.research_engine import fetch_public, validate_url
from tools.pdf_sources import fetch_document_public


def normalized(value):
    return ''.join(c for c in unicodedata.normalize('NFKD', value.casefold()) if not unicodedata.combining(c)).strip()


def resolve_company_identity(company, fetcher=get_json):
    base = 'https://www.wikidata.org/w/api.php?'
    search = fetcher(base + urlencode({'action': 'wbsearchentities', 'search': company, 'language': 'en', 'limit': 5, 'format': 'json'}))
    ids = [r['id'] for r in search.get('search', []) if re.fullmatch(r'Q[1-9][0-9]*', str(r.get('id', '')))]
    if not ids:
        raise ValueError('No unambiguous company identity')
    data = fetcher(base + urlencode({'action': 'wbgetentities', 'ids': '|'.join(ids), 'props': 'claims|labels|aliases|sitelinks', 'languages': 'en|es', 'format': 'json'}))
    matches = []
    for qid, entity in data.get('entities', {}).items():
        names = [r.get('value', '') for r in entity.get('labels', {}).values()]
        names += [r.get('value', '') for rows in entity.get('aliases', {}).values() for r in rows]
        if normalized(company) in {normalized(n) for n in names} and COMPANY_TYPES.intersection(property_ids(entity, 'P31')):
            matches.append(qid)
    if len(matches) != 1:
        raise ValueError('Company identity requires clarification')
    qid = matches[0]
    entity = data['entities'][qid]
    websites = []
    for claim in entity.get('claims', {}).get('P856', [])[:4]:
        try:
            url = validate_url(claim['mainsnak']['datavalue']['value']).split('#', 1)[0]
            if url not in websites: websites.append(url)
        except (KeyError, TypeError, ValueError):
            continue
    article = entity.get('sitelinks', {}).get('enwiki', {}).get('title')
    return {'wikidata_id': qid, 'observed_official_websites': websites[:2],
            'discovery_wikipedia_title': article if isinstance(article, str) and 1 <= len(article) <= 200 else company}


def resolve_company(company, fetcher=get_json):
    return resolve_company_identity(company, fetcher)['wikidata_id']


def run_episode(control, request_id, *, resolver=resolve_company_identity, discover=discover_sources, analyze=analyze_sources, scriptwriter=write_script, client_factory=FreeClients, corroborate=continue_corroboration, focus_reviewer=review_editorial_focus, search_planner=plan_editorial_search):
    path = '/api/market/channel-episode/'
    context = control.request(path + 'context', {'request_id': request_id, 'include_checkpoint': True})
    if context.get('allowed') is not True:
        return {'state': 'paused_or_finished'}
    episode = context['episode']
    def reserve(provider, role):
        current = control.request(path + 'context', {'request_id': request_id})
        return current.get('allowed') is True and control.reserve(provider, role)
    clients = client_factory(reserve=reserve)
    metadata = {}
    checkpoint = context.get('checkpoint')
    if checkpoint:
        report = checkpoint['report']
        if (report.get('selected_episode_id') != episode['episode_id'] or
                report.get('company') != episode['company'] or report.get('editorial_topic') != episode['topic']):
            raise ValueError('Stored research belongs to another episode')
        validate_report_locally(report)
        qid = report['selected_wikidata_id']
        receipt = {'run_id': checkpoint['run_id']}
        metadata = {k: report[k] for k in ('observed_official_websites', 'discovery_wikipedia_title') if k in report}
    else:
        resolved = resolver(episode['company'])
        qid = resolved['wikidata_id'] if isinstance(resolved, dict) else resolved
        if isinstance(resolved, dict): metadata = {k: v for k, v in resolved.items() if k != 'wikidata_id'}
    selection = {'selected_wikidata_id': qid, 'selected_episode_id': episode['episode_id'],
        'editorial_topic': episode['topic'], 'research_queue': {'wikidata_id': qid,
        'title': episode['company'], 'topic': episode['topic'], 'origin': episode['origin']}, **metadata}
    def checked(fetcher):
        def invoke(*args, **kwargs):
            current = control.request(path + 'context', {'request_id': request_id})
            if current.get('allowed') is not True:
                raise RuntimeError('Investigación pausada')
            return fetcher(*args, **kwargs)
        return invoke
    def focused_discover(chosen, **options):
        return discover({**chosen, **metadata, 'editorial_topic': episode['topic']}, **{
            **options, 'wiki_fetcher': checked(fetch_public), 'gdelt_fetcher': checked(fetch_public),
            'document_fetcher': checked(fetch_document_public)})
    def persist(report):
        validate_report_locally(report)
        receipt = control.request(path + 'research', {'request_id': request_id, 'report': report})
        if not receipt.get('ok') or not receipt.get('run_id'):
            raise RuntimeError('Focused research persistence not confirmed')
        return receipt
    def analysis_binding(report):
        return hashlib.sha256(json.dumps({'profile': 'chosen_topic_v2', 'topic': episode['topic'],
            'evidence': report.get('evidence_manifest', [])}, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    old_focus = (report.get('editorial_focus_review') or {}) if checkpoint else {}
    pending = report.get('pending_editorial_analysis') if checkpoint else None
    replanning = bool(checkpoint and (pending or (old_focus.get('status') in {'misaligned', 'aligned'}
        and (old_focus.get('status') == 'misaligned' or len(report.get('candidate_claims', [])) < 6) and old_focus.get('topic') == episode['topic']
        and old_focus.get('claims_sha256') == focus_sha(episode['topic'], report.get('candidate_claims', [])))))
    if replanning:
        prior = report
        questions = old_focus.get('research_questions') or prior.get('editorial_research_questions') or prior.get('missing_questions', [])
        questions = [q for q in questions if isinstance(q, str) and 10 <= len(q) <= 220][:4]
        if not questions: questions = [f"¿Qué documentos responden a: {episode['topic'][:180]}?"]
        history=list(dict.fromkeys([*prior.get('retrieval_history_urls', []),
            *prior.get('corroboration_continuation', {}).get('attempted_urls', []),
            *(prior.get('retrieval_budget') or {}).get('attempted_urls', [])]))[-40:]
        parent_run_id = pending.get('parent_run_id') if pending else receipt['run_id']
        if pending:
            sources = pending['sources']
            if (sources.get('company') != episode['company'] or sources.get('selected_wikidata_id') != qid
                    or sources.get('editorial_topic') != episode['topic']):
                raise ValueError('Pending sources belong to another choice')
            validate_report_locally(source_report(sources))
        elif prior.get('focused_analysis_binding') == analysis_binding(prior):
            plan = prior.get('editorial_retrieval_plan')
            if prior.get('editorial_source_attempt') or plan:
                plan = search_planner(episode['company'], episode['topic'], questions,
                    clients=client_factory(reserve=reserve), previous=plan)
                if not valid_search_plan(plan, episode['company'], episode['topic']):
                    report = {**prior, 'editorial_retrieval_plan': plan}
                    persist(report)
                    return {'state': 'blocked', 'research': report, 'draft': {'status': 'blocked_editorial_search_plan',
                        'blocking_reasons': [plan.get('reason', 'invalid_search_plan')], 'publication_authorized': False}}
            sources = focused_discover({**selection, 'editorial_questions': questions,
                **({'editorial_search_terms': plan['search_terms']} if plan else {}),
                'prior_attempted_urls': history}, clients=clients)
            # The parent retains every old claim and citation. Prefer fresh focused
            # evidence; the analyst may select new facts under the SAME topic.
            fresh = sources['evidence_manifest']
            if not fresh:
                report = {**prior, **({'editorial_retrieval_plan': plan} if plan else {}), 'retrieval_history_urls': list(dict.fromkeys([
                    *history, *(sources.get('retrieval_budget') or {}).get('attempted_urls', [])]))[-40:],
                    'editorial_source_attempt': {'status': 'no_new_documentary_evidence',
                        'stages': sources.get('stages', []), 'retrieval_budget': sources.get('retrieval_budget', {}),
                        'discovery_plan': sources.get('discovery_plan', [])}}
                persist(report)
                return {'state': 'blocked', 'research': report, 'draft': {'status': 'blocked_editorial_sources',
                    'blocking_reasons': ['need_new_relevant_documents'], 'publication_authorized': False}}
            keys = {(e['url'], e.get('page'), e['excerpt']) for e in fresh}
            kept = fresh + [e for e in prior['evidence_manifest'] if (e['url'], e.get('page'), e['excerpt']) not in keys]
            sources['evidence_manifest'] = [{**e, 'id': f'E{n:03d}'} for n, e in enumerate(kept[:10], 1)]
            if plan: sources['editorial_retrieval_plan'] = plan
        else:
            sources = {**prior, 'stages': [s for s in prior['stages']
                if s['provider'] in {'wikipedia', 'gdelt', 'tavily', 'exa', 'd1_history', 'document_citations'}]}
        sources['editorial_topic'] = episode['topic']
        # Persist the new source bundle before any model request. A failed
        # analyst must not replace the last candidate facts with an empty set.
        pending = {'parent_run_id': parent_run_id, 'sources': {k: sources[k] for k in (
            'schema', 'collected_on', 'selected_wikidata_id', 'company', 'evidence_manifest', 'source_documents',
            'stages', 'retrieval_budget', 'research_targets', 'discovery_plan', 'editorial_topic', 'editorial_retrieval_plan')
            if k in sources}}
        persist({**prior, 'pending_editorial_analysis': pending})
        report = analyze(sources, clients=clients)
        if not report.get('candidate_claims'):
            pending['last_attempt_stages'] = report.get('stages', [])
            report = {**prior, 'pending_editorial_analysis': pending}
            persist(report)
            return {'state': 'blocked', 'research': report, 'draft': {'status': 'blocked_editorial_analysis',
                'blocking_reasons': ['saved_sources_await_analysis'], 'publication_authorized': False}}
        report.pop('pending_editorial_analysis', None)
        if sources.get('editorial_retrieval_plan'): report['editorial_retrieval_plan'] = sources['editorial_retrieval_plan']
        report.update(editorial_topic=episode['topic'], selected_episode_id=episode['episode_id'], **metadata)
        report['focused_analysis_binding'] = analysis_binding(report)
        report['editorial_research_questions'] = questions
        report['retrieval_history_urls'] = history
        report['editorial_replanning'] = {'parent_run_id': parent_run_id,
            'previous_claims_sha256': focus_sha(episode['topic'], prior['candidate_claims']), 'topic_unchanged': True,
            'reason': 'scope_mismatch' if old_focus.get('status')=='misaligned' else 'insufficient_relevant_facts'}
        receipt = persist(report)
    # Check relevance before spending more searches on a legacy set of unrelated facts.
    if checkpoint and not replanning and report.get('candidate_claims') and not valid_focus(
            report.get('editorial_focus_review'), episode['topic'], report['candidate_claims']):
        report['editorial_focus_review'] = focus_reviewer(report, episode['topic'], clients=client_factory(reserve=reserve))
        receipt = persist(report)
        if report['editorial_focus_review']['status'] != 'aligned':
            return {'state': 'blocked', 'research': report, 'draft': {'status': 'blocked_editorial_focus',
                'blocking_reasons': ['editorial_review_unavailable' if report['editorial_focus_review']['status']=='unavailable' else 'chosen_topic_not_covered'], 'publication_authorized': False}}
        if len(report['candidate_claims']) < 6:
            return {'state': 'blocked', 'research': report, 'draft': {'status': 'blocked_editorial_coverage',
                'blocking_reasons': ['need_more_relevant_facts'], 'publication_authorized': False}}
    if replanning:
        pass
    elif not checkpoint:
        sources = focused_discover(selection, clients=clients)
        sources['editorial_topic'] = episode['topic']
        report = analyze(sources, clients=clients)
        report.update(editorial_topic=episode['topic'], selected_episode_id=episode['episode_id'], **metadata)
        report['focused_analysis_binding'] = analysis_binding(report)
        validate_report_locally(report)
        receipt = control.request(path + 'research', {'request_id': request_id, 'report': report})
        if not receipt.get('ok') or not receipt.get('run_id'):
            raise RuntimeError('Research persistence not confirmed')
    elif not report.get('candidate_claims'):
        # A failed analyst can reuse the observed sources; empty discovery may
        # continue within the same selection while avoiding earlier failed URLs.
        if report.get('evidence_manifest'):
            sources = {**report, 'editorial_topic': episode['topic'], 'stages': [s for s in report['stages']
                if s['provider'] in {'wikipedia', 'gdelt', 'tavily', 'exa', 'd1_history', 'document_citations'}]}
        else:
            sources = focused_discover({**selection, 'prior_attempted_urls':
                (report.get('retrieval_budget') or {}).get('attempted_urls', [])[-40:]}, clients=clients)
        report = analyze(sources, clients=clients)
        report.update(editorial_topic=episode['topic'], selected_episode_id=episode['episode_id'], **metadata)
        validate_report_locally(report)
        receipt = control.request(path + 'research', {'request_id': request_id, 'report': report})
        if not receipt.get('ok') or not receipt.get('run_id'):
            raise RuntimeError('Resumed analysis persistence not confirmed')
    elif any(row.get('gaps') for row in report.get('source_quality', {}).get('claim_gaps', [])):
        # An incomplete checkpoint needs new corroboration, not another analyst.
        if not metadata.get('observed_official_websites'):
            resolved = resolver(episode['company'])
            if isinstance(resolved, dict):
                if resolved['wikidata_id'] != qid: raise ValueError('Company identity changed')
                metadata = {k: v for k, v in resolved.items() if k != 'wikidata_id'}
        continued = corroborate(report, source_run_id=receipt['run_id'], clients=clients, discover=focused_discover)
        if continued.get('status') == 'awaiting_saved_passage_review':
            continued = review_existing(report, source_run_id=receipt['run_id'], clients=clients)
        if continued.get('report') is not None:
            report = continued['report']
            report.update(editorial_topic=episode['topic'], selected_episode_id=episode['episode_id'], **metadata)
            validate_report_locally(report)
            receipt = control.request(path + 'research', {'request_id': request_id, 'report': report})
            if not receipt.get('ok') or not receipt.get('run_id'):
                raise RuntimeError('Corroboration persistence not confirmed')
    elif checkpoint and len(report.get('reviews', [])) < len(report.get('candidate_claims', [])):
        reviewed = review_existing(report, source_run_id=receipt['run_id'], clients=clients)
        if reviewed.get('report') is not None:
            report = reviewed['report']
            receipt = control.request(path + 'research', {'request_id': request_id, 'report': report})
            if not receipt.get('ok') or not receipt.get('run_id'):
                raise RuntimeError('Review persistence not confirmed')
    if report.get('candidate_claims') and not valid_focus(report.get('editorial_focus_review'), episode['topic'], report['candidate_claims']):
        report['editorial_focus_review'] = focus_reviewer(report, episode['topic'], clients=client_factory(reserve=reserve))
        receipt = persist(report)
    if not valid_focus(report.get('editorial_focus_review'), episode['topic'], report.get('candidate_claims', [])):
        return {'state': 'blocked', 'research': report, 'draft': {'status': 'blocked_editorial_focus',
            'blocking_reasons': ['editorial_review_unavailable' if report.get('editorial_focus_review', {}).get('status')=='unavailable' else 'chosen_topic_not_covered'], 'publication_authorized': False}}
    if len(report['candidate_claims']) < 6:
        return {'state': 'blocked', 'research': report, 'draft': {'status': 'blocked_editorial_coverage',
            'blocking_reasons': ['need_more_relevant_facts'], 'publication_authorized': False}}
    draft = scriptwriter(report, selection, clients=client_factory(reserve=reserve), research_run_id=receipt['run_id'])
    if draft.get('status') != 'editorial_draft_unapproved':
        return {'state': 'blocked', 'research': report, 'draft': draft}
    result = control.request(path + 'script', {'request_id': request_id, 'script': draft})
    if result.get('ok') is not True:
        raise RuntimeError('Draft persistence not confirmed')
    return {'state': 'review', 'research': report, 'draft': draft, 'job_id': result['job_id']}


def run_episode_until_review(control, request_id, *, max_rounds=3, **options):
    """Advance saved stages in one job; never retry a denied reservation.

    Every round still uses the production checkpoint contract and pause guards.
    Three rounds is a ceiling, not a new provider or download allowance.
    """
    if type(max_rounds) is not int or not 1 <= max_rounds <= 3:
        raise ValueError('Continuación fuera del presupuesto')
    denied = False
    stopped_providers = set()
    factory = options.pop('client_factory', FreeClients)
    def guarded_factory(**kwargs):
        client = factory(**kwargs)
        class Client:
            def __getattr__(self, name): return getattr(client, name)
            def invoke(self, method, provider, *args, **kwargs):
                if provider in stopped_providers: raise ProviderError('provider_stopped')
                try:
                    return getattr(client, method)(provider, *args, **kwargs)
                except ProviderError as exc:
                    if exc.code in {'quota_exhausted', 'credentials_rejected', 'network_failure'}:
                        stopped_providers.add(provider)
                    raise
            def generate(self, provider, *args, **kwargs):
                return self.invoke('generate', provider, *args, **kwargs)
            def search(self, provider, *args, **kwargs):
                return self.invoke('search', provider, *args, **kwargs)
        return Client()
    class GuardedControl:
        def request(self, *args, **kwargs):
            return control.request(*args, **kwargs)
        def reserve(self, *args, **kwargs):
            nonlocal denied
            accepted = control.reserve(*args, **kwargs)
            if not accepted: denied = True
            return accepted
    def material(report):
        return hashlib.sha256(json.dumps({k: report.get(k) for k in (
            'selected_episode_id', 'editorial_topic', 'evidence_manifest', 'candidate_claims',
            'reviews', 'editorial_focus_review', 'focused_analysis_binding')},
            sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    initial = control.request('/api/market/channel-episode/context',
        {'request_id': request_id, 'include_checkpoint': True})
    if initial.get('allowed') is not True:
        return {'state': 'paused_or_finished', 'continuation': {'rounds': 0, 'stop_reason': 'paused_or_finished'}}
    previous = material(initial['checkpoint']['report']) if initial.get('checkpoint') else None
    seen = {previous} if previous else set()
    for round_number in range(1, max_rounds + 1):
        result = run_episode(GuardedControl(), request_id, client_factory=guarded_factory, **options)
        reason = 'round_limit'
        if result['state'] != 'blocked': reason = result['state']
        elif denied: reason = 'budget_denied'
        elif stopped_providers: reason = 'provider_unavailable'
        elif result.get('draft', {}).get('status') == 'blocked_editorial_analysis': reason = 'saved_sources_await_analysis'
        elif not result.get('research'): reason = 'no_saved_research'
        else:
            current = material(result['research'])
            if current in seen: reason = 'no_material_progress'
            seen.add(current)
        result['continuation'] = {'rounds': round_number, 'stop_reason': reason}
        if reason != 'round_limit': return result
    return result


def main():
    request_id = os.environ.get('EPISODE_REQUEST_ID', '')
    if not re.fullmatch(r'[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}', request_id):
        raise SystemExit('Identificador de episodio inválido')
    control = ControlClient()
    folder = Path('dist/channel-episode'); folder.mkdir(parents=True, exist_ok=True)
    try:
        result = run_episode_until_review(control, request_id)
        (folder / 'RESULTADO.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
        if result['state'] == 'blocked':
            control.request('/api/market/channel-episode/research', {'request_id': request_id, 'blocked': True})
        print('EPISODIO:', result['state'])
    except (ValueError, RuntimeError, OSError, KeyError, TypeError):
        control.request('/api/market/channel-episode/research', {'request_id': request_id, 'blocked': True})
        raise SystemExit('Investigación detenida: revisar identidad, fuentes o cuota. Sin render ni publicación.') from None


if __name__ == '__main__':
    main()
