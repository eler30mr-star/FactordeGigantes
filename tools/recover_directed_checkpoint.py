"""Recover the isolated acceptance's saved lineage without any provider call."""
import json
import sqlite3
from tools.final_directed_acceptance import FOLDER, COMPANY, TOPIC, store


def main():
    identity = json.loads((FOLDER / 'IDENTIDAD.json').read_text())
    if identity.get('company') != COMPANY or identity.get('topic') != TOPIC:
        raise SystemExit('Checkpoint de otra elección')
    context = store('context', body={'request_id': identity['request_id'], 'include_checkpoint': True})
    report = context.get('checkpoint', {}).get('report')
    if not context.get('allowed') or not report or not report.get('pending_editorial_analysis'):
        raise SystemExit('No hay una recuperación pendiente de análisis en esta aceptación')
    receipt = store('research', body={'request_id': identity['request_id'], 'report': report})
    if receipt.get('ok') is not True: raise SystemExit('No se confirmó la persistencia recuperada')
    (FOLDER / 'INVESTIGACION.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    pending = report['pending_editorial_analysis']
    with sqlite3.connect(FOLDER / 'ACEPTACION.sqlite') as db:
        rows = db.execute('SELECT id,report_json FROM market_ai_pipeline_runs ORDER BY rowid DESC LIMIT 8').fetchall()
    history = []
    for run_id, body in rows:
        saved = json.loads(body)
        history.append({'run_id': run_id, 'claims': saved['candidate_claims'],
            'focus_status': (saved.get('editorial_focus_review') or {}).get('status'),
            'focus_reason': (saved.get('editorial_focus_review') or {}).get('reason'),
            'pending_analysis': bool(saved.get('pending_editorial_analysis'))})
    summary = {'state': 'saved_sources_await_analysis', 'company': COMPANY, 'topic': TOPIC,
        'run_id': receipt['run_id'], 'recovery': report.get('editorial_checkpoint_recovery'),
        'candidate_claim_count': len(report['candidate_claims']),
        'pending_passage_count': len(pending['sources']['evidence_manifest']),
        'provider_calls': 0, 'production_episode_created': False, 'publication_authorized': False,
        'history': history}
    (FOLDER / 'RECUPERACION.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print('CHECKPOINT_RECUPERADO:', json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
