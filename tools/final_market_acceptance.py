"""One explicitly invoked live acceptance run; no production-mode writes or video creation."""
import json
import os
import subprocess
from pathlib import Path
from tools.ai_clients import FreeClients, ProviderError, readiness
from tools.ai_control import ControlClient
from tools.youtube_opportunity_study import YoutubeMetadata, collect_study


def main():
    if os.environ.get('CONFIRM_FINAL_ACCEPTANCE') != 'true':
        raise SystemExit('Prueba final no autorizada')
    folder = Path('dist/final-acceptance'); folder.mkdir(parents=True, exist_ok=True)
    audit = {'youtube_calls': [], 'providers': [], 'production_mode_changed': False,
             'episode_created': False, 'publication_authorized': False}
    class Metadata(YoutubeMetadata):
        def call(self, method, params):
            try:
                rows = super().call(method, params)
                audit['youtube_calls'].append({'method': method, 'results': len(rows)})
                return rows
            except Exception as exc:
                audit['youtube_calls'].append({'method': method, 'error_type': type(exc).__name__})
                raise
    try:
        control = ControlClient()
        clients = FreeClients(reserve=control.reserve)
        chosen = {}
        def generate(prompt):
            for provider in ('gemini', 'groq', 'mistral', 'openrouter'):
                ready = readiness(provider)
                if ready != 'ready':
                    audit['providers'].append({'provider': provider, 'state': ready})
                    continue
                try:
                    text, metadata = clients.generate(provider, prompt, max_output_tokens=1800)
                    chosen.update(provider=provider, model=metadata['model'])
                    audit['providers'].append({'provider': provider, 'state': 'success', **metadata})
                    return text
                except ProviderError as exc:
                    audit['providers'].append({'provider': provider, 'state': exc.code, 'http_status': exc.status})
            raise RuntimeError('Analista no disponible')
        if os.environ.get('YOUTUBE_MARKET_BUDGET_ENABLED') != '1':
            raise RuntimeError('Cuota YouTube no habilitada')
        api = Metadata(os.environ.get('YOUTUBE_DATA_API_KEY', ''))
        report = collect_study(api, generate)
        report['extraction_provider'] = chosen['provider'] + '/' + chosen['model']
        (folder / 'ESTUDIO_REAL.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
        script = "import {assessOpportunityStudy} from './src/opportunity-study.mjs';let s='';for await(const c of process.stdin)s+=c;console.log(JSON.stringify(assessOpportunityStudy(JSON.parse(s))));"
        result = subprocess.run(['node', '--input-type=module', '-e', script], input=json.dumps(report), text=True, capture_output=True, timeout=30)
        if result.returncode:
            raise ValueError('El estudio real no cumple el contrato del selector')
        assessment = json.loads(result.stdout)
        (folder / 'EVALUACION_REAL.json').write_text(json.dumps(assessment, ensure_ascii=False, indent=2))
        audit['state'] = 'live_study_assessed'
        audit['candidate_count'] = len(assessment['rankings'])
        audit['qualified_count'] = sum(c['eligible'] for c in assessment['rankings'])
        audit['reason'] = assessment['reason']
        print('ACEPTACION_REAL:', json.dumps(audit, ensure_ascii=False))
    except (ValueError, RuntimeError, OSError, KeyError, TypeError) as exc:
        audit['state'] = 'blocked'
        audit['error_type'] = type(exc).__name__
        print('ACEPTACION_BLOQUEADA:', json.dumps(audit, ensure_ascii=False))
        raise SystemExit('Prueba real bloqueada; diagnóstico conservado sin credenciales') from None
    finally:
        (folder / 'DIAGNOSTICO.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
