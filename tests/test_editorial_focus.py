import copy
import json
import subprocess
import unittest
from tools.ai_clients import FreeClients
from tools.editorial_focus import review_editorial_focus, valid_focus, filter_editorial_claims, focus_sha

TOPIC='Por qué perdió su liderazgo y cómo cambió su negocio'


class EditorialFocusTests(unittest.TestCase):
    def test_filter_keeps_exact_relevant_facts_and_remaps_reviews_without_new_inference(self):
        from test_review_support_assignment import context
        report={**context(),'selected_episode_id':'chosen','editorial_topic':TOPIC,
            'candidate_claims':[{'statement':f'La empresa cambió su estrategia comercial en la etapa {n}.',
                'evidence_ids':['E001','E002'],'status':'candidate_unverified','human_verified':False} for n in range(7)],
            'reviews':[{'claim_index':n,'assessment':'supported_by_excerpt','evidence_ids':['E001','E002'],
                'reason':'Fixture de apoyo documental sin verificación humana.','human_verified':False} for n in range(1,8)]}
        review={'schema':'fdg_editorial_focus_v1','status':'misaligned','topic':TOPIC,
            'claims_sha256':focus_sha(TOPIC,report['candidate_claims']),'publication_authorized':False,
            'judgments':[{'claim_index':n,'relevance':'off_topic' if n==3 else 'central',
                'reason':'Juicio previo vinculado a esta afirmación concreta.'} for n in range(1,8)]}
        report['editorial_focus_review']=review;before=copy.deepcopy(report)
        result=filter_editorial_claims(report,TOPIC,parent_run_id='ai-'+'a'*28)
        self.assertEqual(report,before)
        self.assertEqual(result['candidate_claims'],[c for n,c in enumerate(before['candidate_claims'],1) if n!=3])
        self.assertEqual([r['claim_index'] for r in result['reviews']],list(range(1,7)))
        self.assertTrue(valid_focus(result['editorial_focus_review'],TOPIC,result['candidate_claims']))
        self.assertFalse(result['source_quality']['all_claims_verified'])
        self.assertEqual(result['editorial_filter']['removed_judgments'][0]['claim_index'],3)
        review['claims_sha256']='f'*64
        self.assertIsNone(filter_editorial_claims(report,TOPIC,parent_run_id='ai-'+'a'*28))

    def test_gemini_handles_editorial_work_with_its_own_reserved_role(self):
        calls=[]
        value={'judgments':[{'claim_index':n,'relevance':'central','reason':'Responde directamente a la pregunta elegida.'} for n in range(1,7)],
            'research_questions':[],'reason':'Las afirmaciones corresponden al enfoque empresarial seleccionado.'}
        def transport(url,body,headers):
            calls.append(url);return {'candidates':[{'content':{'parts':[{'text':json.dumps(value)}]}}]}
        env={p.upper()+'_API_KEY':'fixture-not-a-real-key' for p in ('gemini','groq')}
        env.update({p.upper()+'_RESEARCH_FREE_CONFIRMED':'1' for p in ('gemini','groq')})
        reservations=[]
        client=FreeClients(env=env,reserve=lambda p,r:reservations.append((p,r)) or True,transport=transport)
        review=review_editorial_focus(self.report(),TOPIC,clients=client)
        self.assertEqual(review['provider'],'gemini');self.assertEqual(reservations,[('gemini','editorial')])
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

