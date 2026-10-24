"""Contratos del borrador documental: citas, duración, presupuestos y puertas."""
import copy
import json
import unittest
from unittest.mock import patch
from pathlib import Path
import tempfile

from test_documentary_blueprint import fixture
from tools.ai_clients import FreeClients, ProviderError
from tools.documentary_script import write_script,parse_script,revalidate_source_metadata
from tools.documentary_blueprint import inspect_episode


def narrative():
    return {"title":"Las decisiones de la empresa analizada",
            "central_question":"¿Qué decisiones explican la transformación de esta empresa?",
            "scenes":[{"scene_number":n,"paragraphs":[{
                "text":"contexto "*200,"claim_indices":[n],"evidence_ids":["E001","E002"]}]} for n in range(1,7)]}


class ScriptTests(unittest.TestCase):
    def test_existing_d1_draft_is_reused_without_reservation_or_generation(self):
        from tools.documentary_script import main
        research,selection=fixture()
        result=write_script(research,selection,clients=self.configured(),research_run_id='ai-'+'a'*28)
        context={'ok':True,'run_id':result['source_research_run_id'],'research':research,'selection':selection,
                 'existing_script_draft':{'job_id':'existing-job','script':result}}
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory)/'draft.json'
            with patch('sys.argv',['documentary_script','--run-id','latest','--out',str(out)]), \
                 patch('tools.ai_control.ControlClient') as client, \
                 patch('tools.documentary_script.FreeClients',side_effect=AssertionError('No regenerar')):
                client.return_value.script_context.return_value=context
                main()
                self.assertEqual(json.loads(out.read_text()),result)
                client.return_value.reserve.assert_not_called()

    def test_historical_metadata_is_revalidated_without_changing_original(self):
        research,selection=fixture()
        research['evidence_manifest'][0]['url']='https://pmc.ncbi.nlm.nih.gov/articles/example/'
        original=copy.deepcopy(research)
        normalized=revalidate_source_metadata(research)
        self.assertEqual(research,original)
        self.assertEqual(normalized['source_quality']['regulatory_primary_domains'],0)
        self.assertFalse(normalized['source_revalidation']['original_database_record_modified'])
        self.assertFalse(normalized['publication_authorized'])
        self.assertEqual(write_script(normalized,selection,clients=self.configured())['status'],'blocked_insufficient_research')

    def configured(self,*,reserve=None,transport=None):
        return FreeClients(env={"GEMINI_API_KEY":"fixture-not-a-real-key",
            "GEMINI_RESEARCH_FREE_CONFIRMED":"1"},reserve=reserve or (lambda *_:True),
            transport=transport or (lambda *_:{"candidates":[{"content":{"parts":[{"text":json.dumps(narrative())}]}}]}))

    def test_complete_draft_has_duration_citations_and_no_permissions(self):
        research,selection=fixture()
        calls=[]
        def transport(url,body,headers):
            calls.append(body)
            self.assertEqual(body['generationConfig']['maxOutputTokens'],6000)
            return {"candidates":[{"content":{"parts":[{"text":json.dumps(narrative())}]}}]}
        roles=[]
        result=write_script(research,selection,clients=self.configured(
            reserve=lambda p,role:roles.append((p,role)) or True,transport=transport))
        self.assertEqual(result['status'],'editorial_draft_unapproved')
        self.assertEqual(result['narration_word_count'],1200)
        self.assertTrue(480<=result['estimated_duration_seconds']<=840)
        self.assertEqual(len(result['scenes']),6)
        self.assertEqual(roles,[('gemini','script')])
        self.assertEqual(len(calls),1)
        self.assertTrue(result['duration_is_estimate'])
        self.assertTrue(result['factual_review_required'])
        self.assertFalse(result['ready_for_render'])
        self.assertFalse(result['publication_authorized'])

    def test_insufficient_research_does_not_reserve_or_call(self):
        research,selection=fixture(False)
        client=self.configured(reserve=lambda *_:self.fail('Reserva sin evidencia'),
                               transport=lambda *_:self.fail('Generación sin evidencia'))
        result=write_script(research,selection,clients=client)
        self.assertEqual(result['status'],'blocked_insufficient_research')
        self.assertEqual(result['scenes'],[])

    def test_quota_denied_is_a_resumable_block_and_never_retries(self):
        research,selection=fixture()
        result=write_script(research,selection,clients=self.configured(
            reserve=lambda *_:False,transport=lambda *_:self.fail('Superó cuota')))
        self.assertEqual(result['status'],'blocked_provider')
        self.assertEqual(result['blocking_reasons'],['budget_denied'])
        self.assertEqual(result['scenes'],[])

    def test_invalid_duration_citations_and_self_approval_are_rejected(self):
        research,selection=fixture()
        blueprint=inspect_episode(research,selection)
        for mutate in (
            lambda d:d['scenes'][0]['paragraphs'][0].update(evidence_ids=['E999']),
            lambda d:d['scenes'][0]['paragraphs'][0].update(evidence_ids=['E001']),
            lambda d:d['scenes'][0]['paragraphs'][0].update(claim_indices=[True]),
            lambda d:d['scenes'][0].update(facts_approved=True),
            lambda d:d.update(publication_authorized=True),
            lambda d:d.update(scenes=[]),
            lambda d:[s['paragraphs'][0].update(text='contexto '*10) for s in d['scenes']],
        ):
            data=narrative();mutate(data)
            with self.assertRaises(ValueError):parse_script(json.dumps(data),research,blueprint)

    def test_provider_failures_never_fall_back_to_unconfirmed_paid_services(self):
        research,selection=fixture()
        c=FreeClients(env={},reserve=lambda *_:self.fail('Sin proveedor confirmado'))
        self.assertEqual(write_script(research,selection,clients=c)['status'],'blocked_provider_configuration')
        c=self.configured()
        self.assertEqual(write_script(research,selection,clients=c)['status'],'editorial_draft_unapproved')
        self.assertEqual(write_script(research,selection,clients=c)['blocking_reasons'],['run_budget_exhausted'])

    def test_generation_profile_is_bounded_before_reservation(self):
        c=self.configured(reserve=lambda *_:self.fail('Perfil inválido reservó'))
        for kwargs in ({'max_output_tokens':6001},{'max_output_tokens':True},{'role':'publish'}):
            with self.assertRaises(ValueError):c.generate('gemini','Prueba',**kwargs)


if __name__=='__main__':unittest.main()
