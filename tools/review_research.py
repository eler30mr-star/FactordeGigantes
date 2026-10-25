"""Reanudar sólo la revisión de un expediente D1; sin radar, búsquedas ni Qwen."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re

from tools.ai_clients import FreeClients, ProviderError
from tools.ai_control import ControlClient
from tools.ai_research_pipeline import (
    parse_review, review_prompt, assign_reviewed_support, evidence_gaps, validate_report_locally, ReviewContractError,
)
from tools.documentary_script import revalidate_source_metadata
from tools.documentary_blueprint import inspect_episode
from tools.research_diagnostics import research_summary
from tools.review_candidates import review_tasks, METHOD

def review_existing(research, *, clients, source_run_id):
    if not isinstance(source_run_id,str) or not re.fullmatch(r'ai-[a-f0-9]{28}',source_run_id):
        raise ValueError('Se requiere el identificador D1 original')
    report=revalidate_source_metadata(research)
    validate_report_locally(report)
    base={'schema':'fdg_review_resumption_v1','source_run_id':source_run_id,
          'research_inference_repeated':False,'source_downloads':0,
          'review_inference_calls':0,'publication_authorized':False,'report':None}
    if not report['candidate_claims']:
        return {**base,'status':'blocked_no_candidate_claims'}
    if (report.get('support_review_method')==METHOD and
            len(report['reviews'])==len(report['candidate_claims']) and
            all('source_assessments' in row for row in report['reviews'])):
        parse_review(json.dumps({'reviews':report['reviews']}),
                     report['evidence_manifest'],report['candidate_claims'])
        reconciled=assign_reviewed_support(report['candidate_claims'],report['reviews'])
        if reconciled!=report['candidate_claims']:
            report['candidate_claims']=reconciled
            report['source_quality']=evidence_gaps(report['evidence_manifest'],reconciled)
            report['support_assignment_reconciliation']={'method':'active_support_from_matrix_v1',
                'source_run_id':source_run_id,'review_inference_calls':0}
            validate_report_locally(report)
            return {**base,'status':'support_reconciled_without_inference','report':report}
        return {**base,'status':'skipped_already_reviewed'}
    prompt=review_prompt(report['evidence_manifest'],report['candidate_claims'])
    previous_calls=clients.calls['groq']
    try:
        text,metadata=clients.generate('groq',prompt,max_output_tokens=3200)
        reviews=parse_review(text,report['evidence_manifest'],report['candidate_claims'],
            expected_tasks=review_tasks(report['evidence_manifest'],report['candidate_claims']))
        if not all('source_assessments' in row for row in reviews):
            raise ValueError('Falta matriz por pasaje')
    except ProviderError as exc:
        return {**base,'status':'blocked_provider','reason':exc.code,
                'review_inference_calls':clients.calls['groq']-previous_calls}
    except ReviewContractError as exc:
        return {**base,'status':'blocked_invalid_review','reason':exc.code,
                'review_inference_calls':clients.calls['groq']-previous_calls}
    except (ValueError,TypeError,KeyError):
        return {**base,'status':'blocked_invalid_review','reason':'per_excerpt_contract_failed',
                'review_inference_calls':clients.calls['groq']-previous_calls}
    old_stage=next((s for s in report['stages'] if s['provider']=='groq'),{})
    report['stages']=[s for s in report['stages'] if s['provider']!='groq']+[{
        'provider':'groq','role':'review','status':'success',
        'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),**metadata}]
    report['reviews']=reviews
    report['candidate_claims']=assign_reviewed_support(report['candidate_claims'],reviews)
    report['source_quality']=evidence_gaps(report['evidence_manifest'],report['candidate_claims'])
    report['support_review_method']=METHOD
    if isinstance(report.get('corroboration_continuation'), dict):
        report['corroboration_continuation'].pop('review_pending_reason', None)
    report['review_resumption']={'method':METHOD,'source_run_id':source_run_id,
        'source_report_sha256':hashlib.sha256(json.dumps(research,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),
        'reviewed_on':datetime.now(timezone.utc).date().isoformat(),
        'source_collected_on':research['collected_on'],
        'previous_review_prompt_sha256':old_stage.get('prompt_sha256')}
    validate_report_locally(report)
    return {**base,'status':'review_completed_candidate_only','review_inference_calls':1,'report':report}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--run-id',default='latest')
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    control=ControlClient()
    context=control.script_context(args.run_id)
    if context.get('ok') is not True:
        result={'schema':'fdg_review_resumption_v1','status':'blocked_no_active_research',
                'publication_authorized':False,'report':None}
    else:
        source_id=context.get('run_id') or args.run_id
        result=review_existing(context['research'],
            clients=FreeClients(reserve=control.reserve),source_run_id=source_id)
        # Conservar el cálculo antes de la escritura de red, como el analizador.
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        if result['report'] is not None:
            receipt=control.persist(result['report']);result['receipt']=receipt
            plan=inspect_episode(result['report'],context['selection']);result['blueprint']=plan
            print('EQUIPO_IA_D1:',receipt['run_id'])
            print('INVESTIGACION_DIAGNOSTICO:',json.dumps(research_summary(result['report']),ensure_ascii=False))
            if (plan['status']=='source_grounded_outline_unapproved' and
                    re.fullmatch(r'ai-[a-f0-9]{28}',receipt['run_id']) and os.getenv('GITHUB_OUTPUT')):
                with open(os.environ['GITHUB_OUTPUT'],'a') as output:
                    output.write('run_id='+receipt['run_id']+'\n')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('REVISION_REANUDADA:',result['status'],'MOTIVO:',result.get('reason','none'),
          'GROQ_SOLICITUDES:',result.get('review_inference_calls',0),'DESCARGAS: 0','QWEN_GEMINI_REPETIDOS: NO')


if __name__=='__main__':main()

