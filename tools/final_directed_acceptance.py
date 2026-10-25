"""Live chosen-episode acceptance; real providers, isolated editorial persistence."""
import json
import os
import shutil
import subprocess
import uuid
import hashlib
from urllib.parse import urlsplit
from pathlib import Path
from tools.ai_clients import FreeClients, ProviderError
from tools.ai_control import ControlClient
from tools.ai_source_discovery import discover_sources
from tools.channel_episode import run_episode

FOLDER = Path('dist/final-directed-acceptance')
COMPANY = 'BlackBerry'
TOPIC = 'Por qué perdió su liderazgo en el mercado de teléfonos y cómo cambió su negocio'


def store(action, **body):
    result = subprocess.run(['node', 'tools/episode_acceptance_store.mjs'],
        input=json.dumps({'action': action, **body}), text=True, capture_output=True, timeout=30)
    if result.returncode:
        raise ValueError('El contrato de persistencia editorial rechazó la prueba')
    return json.loads(result.stdout)


def main():
    if os.environ.get('CONFIRM_FINAL_ACCEPTANCE') != 'true':
        raise SystemExit('Prueba integrada no confirmada')
    FOLDER.mkdir(parents=True, exist_ok=True)
    audit = {'company': COMPANY, 'topic': TOPIC, 'providers': [], 'production_mode_changed': False,
             'production_episode_created': False, 'isolated_sqlite_only': True, 'publication_authorized': False,
             'phase': 'company_identity'}
    try:
        previous = os.environ.get('RESUME_DIRECTED_RUN', '')
        if previous:
            if not previous.isdigit():
                raise ValueError('Run previo inválido')
            names = ['IDENTIDAD.json', 'FUENTES.json', 'FUENTES_CONTINUACION.json', 'INVESTIGACION.json', 'GUION.json', 'ACEPTACION.sqlite']
            names += [f'RESPUESTA_{p}_{role}.json' for p in ('gemini', 'groq', 'mistral', 'openrouter') for role in ('analyze', 'review', 'script', 'editorial')]
            for name in names:
                source = Path('dist/previous-directed') / name
                if source.is_file():
                    shutil.copyfile(source, FOLDER / name)
            audit['resumed_from_run_id'] = previous
        identity_file = FOLDER / 'IDENTIDAD.json'
        identity = json.loads(identity_file.read_text()) if identity_file.exists() else {
            'episode_id': str(uuid.uuid4()), 'request_id': str(uuid.uuid4()), 'company': COMPANY, 'topic': TOPIC}
        if identity['company'] != COMPANY or identity['topic'] != TOPIC:
            raise ValueError('La prueba previa corresponde a otra elección')
        identity_file.write_text(json.dumps(identity, ensure_ascii=False, indent=2))
        old_report_file = FOLDER / 'INVESTIGACION.json'
        if old_report_file.exists():
            audit['previous_review_reason'] = json.loads(old_report_file.read_text()).get('corroboration_continuation', {}).get('review_pending_reason')
        store('init', identity=identity)
        budget = ControlClient()
        class Control:
            def reserve(self, provider, role):
                return budget.reserve(provider, role)
            def request(self, path, body):
                action = path.rsplit('/', 1)[-1]
                if action != 'context':
                    audit['phase'] = 'persist_' + action
                result = store(action, body=body)
                if action == 'research' and result.get('ok'):
                    (FOLDER / 'INVESTIGACION.json').write_text(json.dumps(body['report'], ensure_ascii=False, indent=2))
                if action == 'script' and result.get('ok'):
                    (FOLDER / 'GUION.json').write_text(json.dumps(body['script'], ensure_ascii=False, indent=2))
                return result
        class Clients(FreeClients):
            def generate(self, provider, prompt, **options):
                audit['phase'] = options.get('role') or ('review' if provider == 'groq' else 'analyze')
                signature = hashlib.sha256(prompt.encode()).hexdigest()
                cache_file = FOLDER / f"RESPUESTA_{provider}_{audit['phase']}.json"
                if cache_file.exists():
                    cached = json.loads(cache_file.read_text())
                    if cached.get('prompt_sha256') == signature and isinstance(cached.get('text'), str) and len(cached['text']) <= 24000:
                        audit['providers'].append({'provider': provider, 'state': 'reused_response'})
                        return cached['text'], cached['metadata']
                try:
                    text, metadata = super().generate(provider, prompt, **options)
                    cache_file.write_text(json.dumps({'prompt_sha256': signature, 'text': text, 'metadata': metadata}, ensure_ascii=False, indent=2))
                    audit['providers'].append({'provider': provider, 'state': 'success', **metadata})
                    return text, metadata
                except ProviderError as exc:
                    audit['providers'].append({'provider': provider, 'state': exc.code, 'http_status': exc.status})
                    raise
        def discover(selection, **options):
            audit['phase'] = 'source_discovery'
            continuing = bool(selection.get('prior_attempted_urls') or selection.get('prior_research_targets'))
            saved = FOLDER / ('FUENTES_CONTINUACION.json' if continuing else 'FUENTES.json')
            signature = hashlib.sha256(json.dumps(selection, sort_keys=True).encode()).hexdigest()
            cached = json.loads(saved.read_text()) if saved.exists() else None
            if cached and cached.get('_acceptance_selection_sha256') == signature:
                audit['source_checkpoint_reused'] = True
                return cached
            sources = discover_sources(selection, **options)
            sources['_acceptance_selection_sha256'] = signature
            saved.write_text(json.dumps(sources, ensure_ascii=False, indent=2))
            return sources
        result = run_episode(Control(), identity['request_id'], client_factory=Clients, discover=discover)
        if result.get('research', {}).get('editorial_focus_review', {}).get('status') == 'misaligned':
            # One bounded recovery in this explicit acceptance, not a provider loop.
            (FOLDER / 'ENFOQUE_ANTERIOR.json').write_text(json.dumps(result['research']['editorial_focus_review'], ensure_ascii=False, indent=2))
            audit['previous_editorial_focus'] = result['research']['editorial_focus_review']
            audit['editorial_replan_attempted'] = True
            result = run_episode(Control(), identity['request_id'], client_factory=Clients, discover=discover)
        (FOLDER / 'RESULTADO.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
        report = result.get('research', {})
        audit.update(state=result['state'], evidence_count=len(report.get('evidence_manifest', [])),
            claim_count=len(report.get('candidate_claims', [])), stages=report.get('stages', []),
            source_quality=report.get('source_quality'), script_status=result.get('draft', {}).get('status'),
            blocking_reasons=result.get('draft', {}).get('blocking_reasons', []), job_id=result.get('job_id'),
            pending_review_reason=report.get('corroboration_continuation', {}).get('review_pending_reason'))
        audit['documents'] = [{'host': urlsplit(d['url']).hostname,
                              'path': urlsplit(d['url']).path[:300],
                              'status': d['status'], 'error_type': d.get('error_type'), 'error_code': d.get('error_code')}
                             for d in report.get('source_documents', [])]
        audit['claims'] = [{'statement': claim['statement'], 'evidence_ids': claim['evidence_ids']}
                           for claim in report.get('candidate_claims', [])]
        audit['editorial_focus'] = report.get('editorial_focus_review')
        audit['source_classes'] = {kind: sum(e['source_class'] == kind for e in report.get('evidence_manifest', []))
            for kind in ('potential_official_primary', 'potential_official_pdf', 'public_document_candidate', 'public_authority_candidate')}
        print('ACEPTACION_EPISODIO:', json.dumps(audit, ensure_ascii=False))
    except (ValueError, RuntimeError, OSError, KeyError, TypeError) as exc:
        audit.update(state='blocked', error_type=type(exc).__name__)
        print('ACEPTACION_EPISODIO_BLOQUEADA:', json.dumps(audit, ensure_ascii=False))
        raise SystemExit('Aceptación detenida; diagnóstico y resultados conservados sin credenciales') from None
    finally:
        (FOLDER / 'DIAGNOSTICO.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
