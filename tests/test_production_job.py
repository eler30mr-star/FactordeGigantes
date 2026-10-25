import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock
from urllib.error import HTTPError

from tools.production_job import ProductionClient,prepare_job,report_job

JOB='00000000-0000-0000-0000-000000000001'
BASE='https://factor-de-gigantes.martin30-eler.workers.dev'

class ProductionJobTests(unittest.TestCase):
    def test_only_official_https_host_and_bounded_routes_receive_renderer_token(self):
        for base in ('http://'+BASE[8:],BASE+'.evil.test',BASE+'/path',BASE+'?x=1'):
            with self.assertRaises(ValueError):ProductionClient(base=base,token='r'*32)
        opener=Mock(return_value=io.BytesIO(json.dumps({'ok':True,'automatic_publication_allowed':False}).encode()))
        client=ProductionClient(base=BASE,token='r'*32,opener=opener)
        self.assertTrue(client.request(JOB,'episode')['ok'])
        request=opener.call_args.args[0]
        self.assertEqual(request.get_header('Authorization'),'Bearer '+'r'*32)
        self.assertEqual(request.get_method(),'GET')
        for job,path in (('../other','episode'),(JOB,'anything')):
            with self.assertRaises(ValueError):client.request(job,path)
        self.assertEqual(opener.call_count,1)

    def test_rejects_unbounded_or_unconfirmed_response_and_never_logs_provider_body(self):
        for raw in (b'x'*260001,b'{"ok":true}',b'{"ok":true,"automatic_publication_allowed":true}'):
            client=ProductionClient(base=BASE,token='r'*32,opener=lambda *a,**k:io.BytesIO(raw))
            with self.assertRaises(ValueError):client.request(JOB,'episode')
        opener=Mock(side_effect=HTTPError(BASE,401,'SECRET-NOT-TO-LOG',{},None))
        with self.assertRaisesRegex(RuntimeError,'HTTP 401') as ctx:
            ProductionClient(base=BASE,token='r'*32,opener=opener).request(JOB,'episode')
        self.assertNotIn('SECRET',str(ctx.exception))

    def test_technical_or_failed_qa_never_reported_ready_and_failed_needs_no_model_or_files(self):
        client=Mock();client.request.return_value={'ok':True}
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/'PIPELINE_CONTEXT.json').write_text(json.dumps({'job_id':JOB,'approved_manifest_sha256':'a'*64}))
            for narration,qa in ((False,True),(True,False)):
                (root/'ESTADO_EXPORTACION.json').write_text(json.dumps({'contains_narration':narration,'technical_gate_passed':qa}))
                with self.assertRaises(ValueError):report_job(JOB,root,status='ready',run_id='12',client=client)
            client.request.assert_not_called()
            report_job(JOB,root,status='failed',run_id='123',client=client)
            client.request.assert_called_once_with(JOB,'episode-report',{'status':'failed','run_id':'123'})

    def test_ready_report_binds_approved_manifest_and_checks_job_and_run(self):
        client=Mock();client.request.return_value={'ok':True}
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/'PIPELINE_CONTEXT.json').write_text(json.dumps({'job_id':JOB,'approved_manifest_sha256':'a'*64}))
            (root/'ESTADO_EXPORTACION.json').write_text(json.dumps({'contains_narration':True,'technical_gate_passed':True}))
            report_job(JOB,root,status='ready',run_id='123',client=client)
            self.assertEqual(client.request.call_args.args[2]['export']['approved_manifest_sha256'],'a'*64)
            with self.assertRaises(ValueError):report_job(JOB,root,status='ready',run_id='bad',client=client)
            with self.assertRaises(ValueError):report_job(JOB[:-1]+'2',root,status='ready',run_id='123',client=client)
