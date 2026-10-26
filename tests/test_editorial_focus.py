import copy
import json
import subprocess
import unittest
from tools.ai_clients import FreeClients
from tools.editorial_focus import review_editorial_focus, valid_focus

TOPIC='Por qué perdió su liderazgo y cómo cambió su negocio'


class EditorialFocusTests(unittest.TestCase):
    def test_independent_editorial_reviewer_preserves_analyst_allowance(self):
        calls=[]
        value={'judgments':[{'claim_index':n,'relevance':'central','reason':'Responde directamente a la pregunta elegida.'} for n in range(1,7)],
            'research_questions':[],'reason':'Las afirmaciones corresponden al enfoque empresarial seleccionado.'}
        def transport(url,body,headers):
            calls.append(url);return {'choices':[{'message':{'content':json.dumps(value)}}]}
        env={p.upper()+'_API_KEY':'fixture-not-a-real-key' for p in ('gemini','groq')}
        env.update({p.upper()+'_RESEARCH_FREE_CONFIRMED':'1' for p in ('gemini','groq')})
        reservations=[]
        client=FreeClients(env=env,reserve=lambda p,r:reservations.append((p,r)) or True,transport=transport)
        review=review_editorial_focus(self.report(),TOPIC,clients=client)
        self.assertEqual(review['provider'],'groq');self.assertEqual(reservations,[('groq','editorial')])
        self.assertEqual(len(calls),1);self.assertTrue(valid_focus(review,TOPIC,self.report()['candidate_claims']))

    def report(self):
        return {'company':'Empresa Ejemplo','selected_episode_id':'chosen','editorial_topic':TOPIC,
            'candidate_claims':[{'statement':f'El teléfono modelo {n} incluye una pantalla y altavoces.'} for n in range(6)]}

    def client(self, relevance='off_topic', allowed=True):
        def transport(url, body, headers):
            value={'judgments':[{'claim_index':n,'relevance':relevance,
                'reason':'Describe un producto y no explica la trayectoria empresarial.'} for n in range(1,7)],
                'research_questions':['¿Qué decisiones cambiaron la posición competitiva de la empresa?'],
                'reason':'Los detalles del producto no cubren la pregunta empresarial elegida.'}
            return {'candidates':[{'content':{'parts':[{'text':json.dumps(value)}]}}]}
        return FreeClients(env={'GEMINI_API_KEY':'fixture-not-a-real-key','GEMINI_RESEARCH_FREE_CONFIRMED':'1'},
            reserve=lambda *_:allowed,transport=transport)

    def test_product_details_do_not_unlock_a_different_business_topic(self):
        report=self.report();before=copy.deepcopy(report)
        review=review_editorial_focus(report,TOPIC,clients=self.client())
        self.assertEqual(review['status'],'misaligned')
        self.assertFalse(valid_focus(review,TOPIC,report['candidate_claims']))
        self.assertEqual(report,before)
        self.assertFalse(review['publication_authorized'])

    def test_binding_matches_worker_and_changed_claim_or_topic_invalidates_review(self):
        report=self.report();review=review_editorial_focus(report,TOPIC,clients=self.client('central'))
        self.assertTrue(valid_focus(review,TOPIC,report['candidate_claims']))
        report['editorial_focus_review']=review
        code="import {editorialFocusReady} from './src/editorial-focus.mjs';let s='';for await(const c of process.stdin)s+=c;console.log(await editorialFocusReady(JSON.parse(s)));"
        def worker(value):
            r=subprocess.run(['node','--input-type=module','-e',code],input=json.dumps(value),text=True,capture_output=True,timeout=20)
            self.assertEqual(r.returncode,0,r.stderr)
            return r.stdout.strip()=='true'
        self.assertTrue(worker(report))
        report['candidate_claims'][0]['statement']='Otra afirmación distinta con otro enfoque.'
        self.assertFalse(worker(report))
        self.assertFalse(valid_focus(review,TOPIC,report['candidate_claims']))
        report=self.report();report['editorial_focus_review']=review;report['editorial_topic']='Un tema diferente del elegido anteriormente'
        self.assertFalse(worker(report))
        review['judgments'][0]['claim_index']=2
        self.assertFalse(valid_focus(review,TOPIC,self.report()['candidate_claims']))

    def test_budget_denied_blocks_without_discovery_or_script_authorization(self):
        review=review_editorial_focus(self.report(),TOPIC,clients=self.client(allowed=False))
        self.assertEqual(review['status'],'unavailable')
        self.assertEqual(review['reason'],'budget_denied')
        self.assertFalse(review['publication_authorized'])

