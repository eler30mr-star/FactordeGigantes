"""Revisión reanudable: una llamada Groq, no volver a investigar ni descargar."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test_ai_research_team import candidate, configured
from test_review_support_assignment import context, review
from tools.ai_clients import FreeClients, ProviderError
from tools.ai_research_pipeline import analyze_sources, validate_report_locally
from tools.ai_research_pipeline import parse_review,evidence_gaps
from tools.review_candidates import METHOD
from tools.review_research import review_existing, main

RUN='ai-'+'a'*28


class ReviewResumeTests(unittest.TestCase):
    def test_gemini_reviews_when_groq_budget_is_denied_without_claiming_independent_verification(self):
        calls=[];reservations=[]
        def reserve(provider,role):
            reservations.append((provider,role));return provider=='gemini'
        def transport(url,body,headers):
            calls.append(url);self.assertIn('googleapis',url)
            return {'candidates':[{'content':{'parts':[{'text':json.dumps({'reviews':[review()]})}]}}]}
        client=FreeClients(env=configured('groq','gemini'),reserve=reserve,transport=transport)
        research=self.research();before=copy.deepcopy(research)
        result=review_existing(research,clients=client,source_run_id=RUN)
        self.assertEqual(reservations,[('groq','review'),('gemini','review')])
        self.assertEqual(len(calls),1);self.assertEqual(result['review_inference_calls'],1)
        self.assertEqual(result['report']['review_resumption']['review_provider'],'gemini')
        self.assertFalse(result['report']['source_quality']['all_claims_verified'])
        self.assertTrue(all(not row['human_verified'] for row in result['report']['reviews']))
        self.assertEqual(research,before);validate_report_locally(result['report'])

    def test_gemini_fallback_cannot_invent_a_citation_or_omit_the_source_matrix(self):
        for row in ({**review(),'evidence_ids':['E999']},{k:v for k,v in review().items() if k!='source_assessments'}):
            client=FreeClients(env=configured('gemini'),reserve=lambda *_:True,
                transport=lambda *_:{'candidates':[{'content':{'parts':[{'text':json.dumps({'reviews':[row]})}]}}]})
            result=review_existing(self.research(),clients=client,source_run_id=RUN)
            self.assertEqual(result['status'],'blocked_invalid_review');self.assertIsNone(result['report'])

    def test_old_active_citations_are_reconciled_without_any_inference(self):
        report=self.research()
        report['candidate_claims'][0]['evidence_ids']=['E001','E002']
        row=review(ids=('E001','E002'))
        row['source_assessments'][1]['assessment']='insufficient_context'
        report['reviews']=parse_review(json.dumps({'reviews':[row]}),
            report['evidence_manifest'],report['candidate_claims'])
        next(s for s in report['stages'] if s['provider']=='groq')['status']='success'
        report['source_quality']=evidence_gaps(report['evidence_manifest'],report['candidate_claims'])
        report['support_review_method']=METHOD
        client=FreeClients(env=configured('groq'),reserve=lambda *_:self.fail('No debe invocar IA'))
        result=review_existing(report,clients=client,source_run_id=RUN)
        self.assertEqual(result['status'],'support_reconciled_without_inference')
        self.assertEqual(result['review_inference_calls'],0)
        corrected=result['report']
        self.assertEqual(corrected['candidate_claims'][0]['evidence_ids'],['E001'])
        self.assertEqual(corrected['candidate_claims'][0]['analysis_evidence_ids'],['E001','E002'])
        self.assertIn('only_one_document',corrected['source_quality']['claim_gaps'][0]['gaps'])
        self.assertEqual(review_existing(corrected,clients=client,source_run_id=RUN)['status'],
                         'skipped_already_reviewed')

    def research(self):
        return analyze_sources(context(),clients=FreeClients(env={},reserve=lambda *_:False),
                               local_generate=lambda _:candidate())

    def client(self,calls):
        def transport(url,body,headers):
            calls.append(url)
            self.assertIn('api.groq.com',url)
            return {'choices':[{'message':{'content':json.dumps({'reviews':[review()]})}}]}
        return FreeClients(env=configured('groq'),reserve=lambda *_:True,transport=transport)

    def test_one_groq_call_updates_candidate_support_without_research_or_input_mutation(self):
        research=self.research()
        research['corroboration_continuation']={'review_pending_reason':'comparison_passages_omitted'}
        original=copy.deepcopy(research);calls=[]
        result=review_existing(research,clients=self.client(calls),source_run_id=RUN)
        report=result['report']
        self.assertEqual(result['status'],'review_completed_candidate_only')
        self.assertEqual(len(calls),1)
        self.assertEqual(research,original)
        self.assertEqual(report['collected_on'],research['collected_on'])
        self.assertEqual(report['review_resumption']['source_run_id'],RUN)
        self.assertEqual(report['candidate_claims'][0]['evidence_ids'],['E001','E002'])
        self.assertEqual(len([s for s in report['stages'] if s['provider']=='groq']),1)
        self.assertEqual(result['source_downloads'],0)
        self.assertFalse(report['publication_authorized'])
        self.assertNotIn('review_pending_reason', report['corroboration_continuation'])
        validate_report_locally(report)

    def test_repeating_same_review_contract_does_not_reserve_or_persist_again(self):
        report=review_existing(self.research(),clients=self.client([]),source_run_id=RUN)['report']
        client=FreeClients(env=configured('groq'),reserve=lambda *_:self.fail('Revisión duplicada'))
        result=review_existing(report,clients=client,source_run_id=RUN)
        self.assertEqual(result['status'],'skipped_already_reviewed')
        self.assertIsNone(result['report'])

    def test_budget_denied_never_uses_another_provider_or_retries(self):
        client=FreeClients(env=configured('groq'),reserve=lambda *_:False,
                           transport=lambda *_:self.fail('Superó cuota'))
        result=review_existing(self.research(),clients=client,source_run_id=RUN)
        self.assertEqual(result['status'],'blocked_provider')
        self.assertEqual(result['reason'],'budget_denied')

    def test_legacy_review_response_is_not_falsely_marked_as_per_quote_review(self):
        row=review();del row['source_assessments']
        client=FreeClients(env=configured('groq'),reserve=lambda *_:True,
            transport=lambda *_:{'choices':[{'message':{'content':json.dumps({'reviews':[row]})}}]})
        result=review_existing(self.research(),clients=client,source_run_id=RUN)
        self.assertEqual(result['status'],'blocked_invalid_review')
        self.assertIsNone(result['report'])

    def test_cli_saves_calculation_even_if_d1_persistence_fails(self):
        research=self.research()
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'review.json'
            with patch('sys.argv',['review','--out',str(output)]), \
                 patch('tools.review_research.ControlClient') as control, \
                 patch('tools.review_research.FreeClients',return_value=self.client([])):
                control.return_value.script_context.return_value={'ok':True,'run_id':RUN,'research':research}
                control.return_value.persist.side_effect=ProviderError('persistence_unconfirmed')
                with self.assertRaises(ProviderError):main()
            self.assertEqual(json.loads(output.read_text())['status'],'review_completed_candidate_only')
            self.assertNotIn('receipt',json.loads(output.read_text()))


if __name__=='__main__':unittest.main()

