"""Importación reanudable de un guion existente: no llama a ninguna IA."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from tools.ai_control import ControlClient
from tools.ai_clients import ProviderError


def import_draft(script, *, control_factory=ControlClient):
    if script.get('status') != 'editorial_draft_unapproved':
        return {'ok': False, 'skipped': True, 'reason': 'no_acceptable_draft',
                'automatic_publication_allowed': False}
    return control_factory().persist_script(script)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--script', type=Path, required=True)
    p.add_argument('--receipt', type=Path, required=True)
    p.add_argument('--probe-rejection', action='store_true',
                   help='Comprobar con OIDC que producción rechaza este expediente bloqueado, sin crear trabajos')
    a = p.parse_args()
    script = json.loads(a.script.read_text(encoding='utf-8-sig'))
    result = import_draft(script)
    if result.get('skipped') and a.probe_rejection:
        control = ControlClient()
        context = control.script_context(script.get('source_research_run_id') or 'latest')
        if context.get('ok') is True:
            try:
                control.request('/api/market/ai-pipeline/script-ingest', {
                    'research_run_id': context['run_id'], 'script': script})
            except ProviderError as exc:
                if exc.status != 400:
                    raise
                result['production_rejection_confirmed'] = True
                print('GUION_PANEL_OIDC: rechazo 400 confirmado; sin guion aceptable')
            else:
                raise RuntimeError('Producción aceptó un borrador bloqueado')
    a.receipt.parent.mkdir(parents=True, exist_ok=True)
    a.receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('GUION_PANEL:', 'omitido' if result.get('skipped') else result['job_id'])


if __name__ == '__main__':
    main()
