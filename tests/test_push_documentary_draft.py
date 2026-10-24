import copy
import unittest
from tools.ai_clients import ProviderError
from tools.ai_control import ControlClient
from tools.push_documentary_draft import import_draft


class PushDraftTests(unittest.TestCase):
    def client(self, reply):
        return ControlClient(base_url='https://factor-de-gigantes.martin30-eler.workers.dev',
                             token='a'*30+'.'+'b'*30+'.signature',
                             transport=lambda *args: reply)

    def test_blocked_draft_needs_no_credentials_or_inference(self):
        for status in ('blocked_insufficient_research', 'blocked_provider', None):
            result = import_draft({'status': status}, control_factory=lambda: self.fail('No llamar control'))
            self.assertTrue(result['skipped'])

    def test_persistence_requires_matching_d1_receipt_without_approval(self):
        run_id = 'ai-'+'a'*28
        script = {'source_research_run_id': run_id, 'status': 'editorial_draft_unapproved'}
        receipt = {'ok': True, 'stored_in': 'd1', 'research_run_id': run_id,
                   'job_id': '12345678-1234-1234-1234-123456789abc',
                   'automatic_factual_approval': False, 'automatic_render_allowed': False,
                   'automatic_publication_allowed': False}
        self.assertEqual(import_draft(script, control_factory=lambda: self.client(receipt)), receipt)
        for key,value in (('ok',False),('stored_in','artifact'),('research_run_id','latest'),
                          ('job_id',None),('automatic_factual_approval',True),
                          ('automatic_render_allowed',True),('automatic_publication_allowed',True)):
            broken=copy.deepcopy(receipt);broken[key]=value
            with self.assertRaises(ProviderError):self.client(broken).persist_script(script)

    def test_failed_import_preserves_original_script_for_retry(self):
        script={'source_research_run_id':'ai-'+'a'*28, 'status':'editorial_draft_unapproved'}
        original=copy.deepcopy(script)
        with self.assertRaises(ProviderError):import_draft(script,control_factory=lambda:self.client({}))
        self.assertEqual(script,original)
        with self.assertRaises(ValueError):self.client({}).persist_script({'source_research_run_id':'latest'})
