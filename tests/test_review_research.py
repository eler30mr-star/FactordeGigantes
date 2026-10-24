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
from tools.review_research import review_existing, main

RUN='ai-'+'a'*28


class ReviewResumeTests(unittest.TestCase):
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
        research=self.research();original=copy.deepcopy(research);calls=[]
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
