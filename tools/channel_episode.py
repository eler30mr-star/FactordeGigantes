"""Investigate only the persisted chosen episode, then prepare a cited draft."""
import json
import os
import re
import unicodedata
from pathlib import Path
from urllib.parse import urlencode
from tools.ai_control import ControlClient
from tools.ai_clients import FreeClients
from tools.ai_source_discovery import discover_sources
from tools.ai_research_pipeline import analyze_sources, validate_report_locally
from tools.documentary_script import write_script
from tools.corroborate_research import continue_corroboration
from tools.review_research import review_existing
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


def run_episode(control, request_id, *, resolver=resolve_company_identity, discover=discover_sources, analyze=analyze_sources, scriptwriter=write_script, client_factory=FreeClients, corroborate=continue_corroboration):
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
    if not checkpoint:
        sources = focused_discover(selection, clients=clients)
        sources['editorial_topic'] = episode['topic']
        report = analyze(sources, clients=clients)
        report.update(editorial_topic=episode['topic'], selected_episode_id=episode['episode_id'], **metadata)
        validate_report_locally(report)
        receipt = control.request(path + 'research', {'request_id': request_id, 'report': report})
        if not receipt.get('ok') or not receipt.get('run_id'):
            raise RuntimeError('Research persistence not confirmed')
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
    draft = scriptwriter(report, selection, clients=client_factory(reserve=reserve), research_run_id=receipt['run_id'])
    if draft.get('status') != 'editorial_draft_unapproved':
        return {'state': 'blocked', 'research': report, 'draft': draft}
    result = control.request(path + 'script', {'request_id': request_id, 'script': draft})
    if result.get('ok') is not True:
        raise RuntimeError('Draft persistence not confirmed')
    return {'state': 'review', 'research': report, 'draft': draft, 'job_id': result['job_id']}


def main():
    request_id = os.environ.get('EPISODE_REQUEST_ID', '')
    if not re.fullmatch(r'[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}', request_id):
        raise SystemExit('Identificador de episodio inválido')
    control = ControlClient()
    folder = Path('dist/channel-episode'); folder.mkdir(parents=True, exist_ok=True)
    try:
        result = run_episode(control, request_id)
        (folder / 'RESULTADO.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
        if result['state'] == 'blocked':
            control.request('/api/market/channel-episode/research', {'request_id': request_id, 'blocked': True})
        print('EPISODIO:', result['state'])
    except (ValueError, RuntimeError, OSError, KeyError, TypeError):
        control.request('/api/market/channel-episode/research', {'request_id': request_id, 'blocked': True})
        raise SystemExit('Investigación detenida: revisar identidad, fuentes o cuota. Sin render ni publicación.') from None


if __name__ == '__main__':
    main()
