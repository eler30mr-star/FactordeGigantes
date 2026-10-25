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
from tools.topic_discovery import property_ids, COMPANY_TYPES
from tools.market_sources import get_json
from tools.research_engine import fetch_public
from tools.pdf_sources import fetch_document_public


def normalized(value):
    return ''.join(c for c in unicodedata.normalize('NFKD', value.casefold()) if not unicodedata.combining(c)).strip()


def resolve_company(company, fetcher=get_json):
    base = 'https://www.wikidata.org/w/api.php?'
    search = fetcher(base + urlencode({'action': 'wbsearchentities', 'search': company, 'language': 'en', 'limit': 5, 'format': 'json'}))
    ids = [r['id'] for r in search.get('search', []) if re.fullmatch(r'Q[1-9][0-9]*', str(r.get('id', '')))]
    if not ids:
        raise ValueError('No unambiguous company identity')
    data = fetcher(base + urlencode({'action': 'wbgetentities', 'ids': '|'.join(ids), 'props': 'claims|labels|aliases', 'languages': 'en|es', 'format': 'json'}))
    matches = []
    for qid, entity in data.get('entities', {}).items():
        names = [r.get('value', '') for r in entity.get('labels', {}).values()]
        names += [r.get('value', '') for rows in entity.get('aliases', {}).values() for r in rows]
        if normalized(company) in {normalized(n) for n in names} and COMPANY_TYPES.intersection(property_ids(entity, 'P31')):
            matches.append(qid)
    if len(matches) != 1:
        raise ValueError('Company identity requires clarification')
    return matches[0]


def run_episode(control, request_id, *, resolver=resolve_company, discover=discover_sources, analyze=analyze_sources, scriptwriter=write_script, client_factory=FreeClients):
    path = '/api/market/channel-episode/'
    context = control.request(path + 'context', {'request_id': request_id})
    if context.get('allowed') is not True:
        return {'state': 'paused_or_finished'}
    episode = context['episode']
    def reserve(provider, role):
        current = control.request(path + 'context', {'request_id': request_id})
        return current.get('allowed') is True and control.reserve(provider, role)
    clients = client_factory(reserve=reserve)
    qid = resolver(episode['company'])
    selection = {'selected_wikidata_id': qid, 'selected_episode_id': episode['episode_id'],
        'editorial_topic': episode['topic'], 'research_queue': {'wikidata_id': qid,
        'title': episode['company'], 'topic': episode['topic'], 'origin': episode['origin']}}
    def checked(fetcher):
        def invoke(*args, **kwargs):
            current = control.request(path + 'context', {'request_id': request_id})
            if current.get('allowed') is not True:
                raise RuntimeError('Investigación pausada')
            return fetcher(*args, **kwargs)
        return invoke
    sources = discover(selection, clients=clients, wiki_fetcher=checked(fetch_public),
        gdelt_fetcher=checked(fetch_public), document_fetcher=checked(fetch_document_public))
    sources['editorial_topic'] = episode['topic']
    report = analyze(sources, clients=clients)
    report.update(editorial_topic=episode['topic'], selected_episode_id=episode['episode_id'])
    validate_report_locally(report)
    receipt = control.request(path + 'research', {'request_id': request_id, 'report': report})
    if not receipt.get('ok') or not receipt.get('run_id'):
        raise RuntimeError('Research persistence not confirmed')
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
