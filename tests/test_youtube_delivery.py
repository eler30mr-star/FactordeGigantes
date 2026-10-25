import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from tools.youtube_delivery import DeliveryClient,transfer

JOB='00000000-0000-0000-0000-000000000001'
BASE='https://factor-de-gigantes.martin30-eler.workers.dev'

class DeliveryTests(unittest.TestCase):
    def test_transport_only_official_host_and_renderer_role_never_google_credentials(self):
        for base in ('http://'+BASE[8:],BASE+'.evil.test',BASE+'/path'):
            with self.assertRaises(ValueError):DeliveryClient(base=base,token='r'*32)
        seen=[]
        def opener(req,**kwargs):
            seen.append(req)
            return io.BytesIO(b'{"ok":true,"automatic_publication_allowed":false}')
        client=DeliveryClient(base=BASE,token='r'*32,opener=opener)
        client.request('uploads/'+JOB+'/chunk',method='PUT',data=b'123',headers={'Content-Range':'bytes 0-2/3'})
        self.assertEqual(seen[0].get_header('Authorization'),'Bearer '+'r'*32)
        self.assertEqual(seen[0].data,b'123')
        self.assertTrue(seen[0].full_url.startswith(BASE+'/api/renderer/youtube/'))
        with self.assertRaises(ValueError):client.request('../google')

    def test_http_errors_never_expose_server_body_or_secret_urls(self):
        def opener(*a,**k):raise HTTPError(BASE,502,'PRIVATE-SECRET',{},io.BytesIO(b'PRIVATE-SECRET'))
        client=DeliveryClient(base=BASE,token='r'*32,opener=opener)
        with self.assertRaises(RuntimeError) as ctx:client.request('exports')
        self.assertNotIn('PRIVATE-SECRET',str(ctx.exception))

    def test_resume_consults_offset_after_network_failure_and_never_opens_second_session(self):
        with tempfile.TemporaryDirectory() as folder:
            movie=Path(folder)/'movie.mp4';movie.write_bytes(b'0123456789')
            class Client:
                def __init__(self):self.started=0;self.probes=0;self.chunks=[];self.reports=[]
                def request(self,path,**opts):
                    if path.endswith('/start'):self.started+=1;return {'ok':True}
                    if path.endswith('/report'):self.reports.append(opts['body']);return {'ok':True}
                    if path.endswith('/chunk'):
                        if opts['data']==b'':
                            self.probes+=1;return {'next_offset':4 if self.probes==1 else 7}
                        self.chunks.append(opts['headers']['Content-Range'])
                        if len(self.chunks)==1:raise RuntimeError('Respuesta perdida; Google pudo recibir datos')
                        return {'complete':True,'video_id':'abcde123456'}
                    return {'state':'queued','source_run_id':'123','artifact_id':'456','archive_sha256':'b'*64,'export_id':'a'*64,'video_bytes':10}
            c=Client()
            with patch('tools.youtube_delivery.download_bundle',return_value=(None,{})),patch('tools.youtube_delivery.extract_bundle',return_value=({}, {'sha256':'a'*64},movie)):
                transfer(JOB,folder,client=c,sleep=lambda _:None)
            self.assertEqual(c.started,1)
            self.assertEqual(c.chunks,['bytes 4-9/10','bytes 7-9/10'])
            self.assertEqual(c.reports,[{'video_id':'abcde123456'}])

    def test_already_uploaded_or_different_file_never_restarts_transfer(self):
        class Done:
            def request(self,path,**kwargs):return {'state':'uploaded','video_id':'abcde123456'}
        with patch('tools.youtube_delivery.download_bundle',side_effect=AssertionError('No repetir descarga')):
            self.assertEqual(transfer(JOB,'unused',client=Done())['video_id'],'abcde123456')
