import json
import unittest
from tools.ai_clients import FreeClients
from tools.editorial_search import plan_editorial_search, valid_search_plan

COMPANY='Empresa Ejemplo'
TOPIC='Por qué perdió liderazgo y cambió de negocio'
TERMS=['smartphone market leadership loss strategic decisions annual report',
       'smartphone competition software business transition independent analysis']

class EditorialSearchTests(unittest.TestCase):
    def client(self, value, allowed=True):
        return FreeClients(env={'GROQ_API_KEY':'fixture-not-a-real-key','GROQ_RESEARCH_FREE_CONFIRMED':'1'},
            reserve=lambda *_:allowed,transport=lambda *_:{'choices':[{'message':{'content':json.dumps(value)}}]})

    def test_plan_is_retrieval_only_and_bound_to_exact_company_and_topic(self):
        plan=plan_editorial_search(COMPANY,TOPIC,['¿Qué decisiones cambiaron el negocio?'],clients=self.client({'search_terms':TERMS}))
        self.assertTrue(valid_search_plan(plan,COMPANY,TOPIC))
        self.assertFalse(valid_search_plan(plan,'Otra empresa',TOPIC))
        self.assertFalse(valid_search_plan(plan,COMPANY,'Otra pregunta diferente'))
        self.assertFalse(plan['publication_authorized']);self.assertNotIn('candidate_claims',plan)
        self.assertEqual(plan['search_terms'],TERMS)
        self.assertEqual(plan_editorial_search(COMPANY,TOPIC,[],clients=None,previous=plan),plan)

    def test_bad_generated_urls_or_multiline_terms_are_not_used_as_searches(self):
        for terms in ([TERMS[0],'https://invented.example/source'], [TERMS[0],'query\nsecond command'], ['short'], 'not a list'):
            plan=plan_editorial_search(COMPANY,TOPIC,[],clients=self.client({'search_terms':terms}))
            self.assertEqual(plan['status'],'unavailable');self.assertEqual(plan['search_terms'],[])

    def test_denied_reservation_does_not_invoke_remote_planner(self):
        client=self.client({},allowed=False)
        client.transport=lambda *_:self.fail('No remote call after denied reservation')
        plan=plan_editorial_search(COMPANY,TOPIC,[],clients=client)
        self.assertEqual(plan['reason'],'budget_denied');self.assertFalse(plan['publication_authorized'])
