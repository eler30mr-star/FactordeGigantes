import json
import unittest
from unittest.mock import patch
from tools.channel_episode import run_episode, run_episode_until_review, resolve_company, resolve_company_identity
from tools.editorial_focus import focus_sha


def focused(report):
    report['candidate_claims']=[{**row, 'statement':row.get('statement', 'La empresa perdió liderazgo frente al cambio del mercado.')} for row in report.get('candidate_claims', [{}])]
    if report['candidate_claims'] and len(report['candidate_claims'])<6:
        first=report['candidate_claims'][0]
        report['candidate_claims']=[{**first,'statement':first['statement']+f' Fixture {n}.'} for n in range(6)]
        report['reviews']=[{} for _ in report['candidate_claims']]
    topic=report.get('editorial_topic', 'Pérdida de liderazgo')
    report['editorial_focus_review']={'schema':'fdg_editorial_focus_v1','status':'aligned','topic':topic,
        'claims_sha256':focus_sha(topic,report['candidate_claims']),'publication_authorized':False,
        'judgments':[{'claim_index':n,'relevance':'central','reason':'Fixture simulado que responde a la pregunta.'} for n in range(1,len(report['candidate_claims'])+1)]}
    return report


class ChannelEpisodeTests(unittest.TestCase):
    def test_aligned_but_short_research_replans_instead_of_repeating_only_two_facts_forever(self):
        saved=focused({'company':'BlackBerry','editorial_topic':'Pérdida de liderazgo','selected_episode_id':'chosen',
            'selected_wikidata_id':'Q100','stages':[],'evidence_manifest':[]})
        saved['candidate_claims']=saved['candidate_claims'][:2]
        saved['editorial_focus_review']['claims_sha256']=focus_sha(saved['editorial_topic'],saved['candidate_claims'])
        saved['editorial_focus_review']['judgments']=saved['editorial_focus_review']['judgments'][:2]
        saved['editorial_focus_review']['research_questions']=['¿Qué otras decisiones explican la trayectoria de la empresa?']
        writes=[]
        class Control:
            def request(self,path,body):
                if path.endswith('/context'):return {'allowed':True,'episode':{'episode_id':'chosen','company':'BlackBerry',
                    'topic':'Pérdida de liderazgo','origin':'chat'},'checkpoint':{'run_id':'ai-'+'a'*28,'report':saved}}
                if path.endswith('/research'):writes.append(body['report'])
                return {'ok':True,'run_id':'ai-'+'b'*28,'job_id':'job'}
            def reserve(self,*_):return True
        forbidden=lambda *_a,**_k:self.fail('No descargar otra vez sin cambios de perfil')
        with patch('tools.channel_episode.validate_report_locally'):
            result=run_episode(Control(),'request',resolver=forbidden,discover=forbidden,
                analyze=lambda s,**_:focused({**s,'candidate_claims':[{}]}),
                scriptwriter=lambda *_a,**_k:{'status':'editorial_draft_unapproved'},client_factory=lambda **_:None)
        self.assertEqual(result['state'],'review')
        self.assertEqual(writes[0]['editorial_replanning']['reason'],'insufficient_relevant_facts')
        self.assertEqual(writes[0]['editorial_replanning']['parent_run_id'],'ai-'+'a'*28)
        self.assertTrue(writes[0]['editorial_replanning']['topic_unchanged'])

    def test_off_topic_facts_stop_before_more_downloads_or_scripting(self):
        saved={'company':'BlackBerry','selected_episode_id':'chosen','editorial_topic':'Pérdida de liderazgo',
            'selected_wikidata_id':'Q100','candidate_claims':[{'statement':'El teléfono tiene dos altavoces frontales.'}],
            'source_quality':{'claim_gaps':[{'gaps':['no_original_primary_document']}]}}
        class Control:
            def request(self,path,body):
                if path.endswith('/context'):return {'allowed':True,'episode':{'episode_id':'chosen','company':'BlackBerry',
                    'topic':'Pérdida de liderazgo','origin':'chat'},'checkpoint':{'run_id':'ai-'+'a'*28,'report':saved}}
                return {'ok':True,'run_id':'ai-'+'b'*28}
            def reserve(self,*_):return True
        def reviewer(report,topic,**_):
            return {'schema':'fdg_editorial_focus_v1','status':'misaligned','topic':topic,
                'claims_sha256':focus_sha(topic,report['candidate_claims']), 'publication_authorized':False,
                'judgments':[{'claim_index':1,'relevance':'off_topic','reason':'Es un detalle de producto y no explica el negocio.'}],
                'research_questions':['¿Qué decisiones afectaron su liderazgo?']}
        forbidden=lambda *_a,**_k:self.fail('No gastar en un enfoque ajeno')
        with patch('tools.channel_episode.validate_report_locally'):
            result=run_episode(Control(),'request',resolver=forbidden,discover=forbidden,analyze=forbidden,
                corroborate=forbidden,scriptwriter=forbidden,focus_reviewer=reviewer,client_factory=lambda **_:None)
        self.assertEqual(result['draft']['status'],'blocked_editorial_focus')
        self.assertEqual(result['research']['editorial_topic'],'Pérdida de liderazgo')

    def test_incomplete_checkpoint_corroborates_without_repeating_the_analyst(self):
        saved = {'company': 'BlackBerry', 'editorial_topic': 'Pérdida de liderazgo',
                 'selected_episode_id': 'chosen', 'selected_wikidata_id': 'Q100',
                 'candidate_claims': [{}], 'reviews': [{}],
                 'observed_official_websites': ['https://www.blackberry.com'],
                 'source_quality': {'claim_gaps': [{'claim_index': 1, 'gaps': ['no_independent_domain']}]}}
        focused(saved)
        class Control:
            def request(self, path, body):
                if path.endswith('/context'): return {'allowed': True, 'episode': {'episode_id': 'chosen', 'company': 'BlackBerry',
                    'topic': 'Pérdida de liderazgo', 'origin': 'chat'}, 'checkpoint': {'run_id': 'ai-' + 'b' * 28, 'report': saved}}
                if path.endswith('/research'):
                    self_test.assertEqual(body['report']['company'], 'BlackBerry')
                    self_test.assertEqual(body['report']['editorial_topic'], 'Pérdida de liderazgo')
                    return {'ok': True, 'run_id': 'ai-' + 'c' * 28}
                return {'ok': True, 'job_id': 'job'}
            def reserve(self, *_): return True
        self_test = self
        def corroborate(report, **options):
            selected = {'selected_wikidata_id': 'Q100', 'prior_research_targets': [{'statement': 'El cambio'}]}
            options['discover'](selected, clients=None)
            return {'report': {**report, 'source_quality': {'claim_gaps': []}}}
        def discover(selection, **_):
            self.assertEqual(selection['observed_official_websites'], ['https://www.blackberry.com'])
            self.assertEqual(selection['editorial_topic'], 'Pérdida de liderazgo')
            return {}
        def script(report, selection, **options):
            self.assertEqual(options['research_run_id'], 'ai-' + 'c' * 28)
            return {'status': 'editorial_draft_unapproved'}
        forbidden = lambda *_a, **_k: self.fail('No repetir identidad/analistas')
        with patch('tools.channel_episode.validate_report_locally'):
            result = run_episode(Control(), 'request', resolver=forbidden, analyze=forbidden, discover=discover,
                corroborate=corroborate, scriptwriter=script, client_factory=lambda **_: None)
        self.assertEqual(result['state'], 'review')

    def test_retry_continues_from_saved_research_without_resolver_sources_or_analysts(self):
        saved = {'company': 'BlackBerry', 'editorial_topic': 'Pérdida de liderazgo',
                 'selected_episode_id': 'chosen', 'selected_wikidata_id': 'Q100',
                 'candidate_claims': [{}], 'reviews': [{}]}
        focused(saved)
        run_id = 'ai-' + 'b' * 28
        calls = []
        class Control:
            def request(self, path, body):
                calls.append((path, body))
                if path.endswith('/context'):
                    return {'allowed': True, 'episode': {'episode_id': 'chosen', 'company': 'BlackBerry',
                        'topic': 'Pérdida de liderazgo', 'origin': 'chat'}, 'checkpoint': {'run_id': run_id, 'report': saved}}
                if path.endswith('/research'): raise AssertionError('No repetir persistencia/investigación')
                return {'ok': True, 'job_id': 'job'}
            def reserve(self, *_): return True
        def script(report, selection, **options):
            self.assertEqual(report, saved)
            self.assertEqual(options['research_run_id'], run_id)
            self.assertEqual(selection['selected_wikidata_id'], 'Q100')
            return {'status': 'editorial_draft_unapproved'}
        forbidden = lambda *_args, **_kwargs: self.fail('No repetir búsquedas ni analistas')
        with patch('tools.channel_episode.validate_report_locally'):
            result = run_episode(Control(), 'retry', resolver=forbidden, discover=forbidden, analyze=forbidden,
                scriptwriter=script, client_factory=lambda **_: None)
        self.assertEqual(result['state'], 'review')
        self.assertTrue(calls[0][1]['include_checkpoint'])
        saved['selected_episode_id'] = 'another'
        with patch('tools.channel_episode.validate_report_locally'), self.assertRaises(ValueError):
            run_episode(Control(), 'retry', resolver=forbidden, discover=forbidden, analyze=forbidden,
                scriptwriter=script, client_factory=lambda **_: None)

    def test_pause_does_not_resolve_or_investigate(self):
        class Control:
            def request(self, *args): return {'allowed': False}
        result = run_episode(Control(), 'unused', resolver=lambda _: self.fail('No resolver'))
        self.assertEqual(result['state'], 'paused_or_finished')

    def test_failed_analyst_reuses_sources_and_drops_old_failed_analysis_stages(self):
        saved = {'company': 'BlackBerry', 'editorial_topic': 'Pérdida de liderazgo', 'selected_episode_id': 'chosen',
            'selected_wikidata_id': 'Q100', 'candidate_claims': [], 'evidence_manifest': [{'id': 'E001'}],
            'stages': [{'provider': 'wikipedia', 'status': 'success'}, {'provider': 'gemini', 'status': 'quota_exhausted'}]}
        class Control:
            def request(self, path, body):
                if path.endswith('/context'): return {'allowed': True, 'episode': {'episode_id': 'chosen', 'company': 'BlackBerry',
                    'topic': 'Pérdida de liderazgo', 'origin': 'chat'}, 'checkpoint': {'run_id': 'ai-' + 'a' * 28, 'report': saved}}
                return {'ok': True, 'run_id': 'ai-' + 'b' * 28, 'job_id': 'job'}
            def reserve(self, *_): return True
        def analyze(sources, **_):
            self.assertEqual(sources['evidence_manifest'], saved['evidence_manifest'])
            self.assertEqual(sources['stages'], [{'provider': 'wikipedia', 'status': 'success'}])
            return focused({**sources, 'candidate_claims': [{}]})
        forbidden = lambda *_a, **_k: self.fail('No repetir identidad o fuentes')
        with patch('tools.channel_episode.validate_report_locally'):
            result = run_episode(Control(), 'retry', resolver=forbidden, discover=forbidden, analyze=analyze,
                scriptwriter=lambda *_a, **_k: {'status': 'editorial_draft_unapproved'}, client_factory=lambda **_: None)
        self.assertEqual(result['state'], 'review')

    def test_company_resolution_requires_exact_unambiguous_observed_company(self):
        entity = {'labels': {'en': {'value': 'BlackBerry'}}, 'claims': {'P31': [{'mainsnak': {'datavalue': {'value': {'id': 'Q783794'}}}}]}}
        def fetch(url):
            return {'search': [{'id': 'Q100'}]} if 'wbsearchentities' in url else {'entities': {'Q100': entity}}
        self.assertEqual(resolve_company('BlackBerry', fetch), 'Q100')
        entity['sitelinks'] = {'enwiki': {'title': 'BlackBerry Limited'}}
        entity['claims']['P856'] = [{'mainsnak': {'datavalue': {'value': url}}} for url in
            ['https://www.blackberry.com/en', 'https://127.0.0.1/private', 'http://invalid.example']]
        identity = resolve_company_identity('BlackBerry', fetch)
        self.assertEqual(identity['observed_official_websites'], ['https://www.blackberry.com/en'])
        self.assertEqual(identity['discovery_wikipedia_title'], 'BlackBerry Limited')
        entity['labels']['en']['value'] = 'Different company'
        with self.assertRaises(ValueError): resolve_company('BlackBerry', fetch)

    def test_selected_topic_is_preserved_and_only_its_sources_are_requested(self):
        class Control:
            def request(self, path, body):
                if path.endswith('/context'): return {'allowed': True, 'episode': {'episode_id': 'chosen', 'company': 'BlackBerry', 'topic': 'Pérdida de liderazgo', 'origin': 'chat'}}
                if path.endswith('/research'): return {'ok': True, 'run_id': 'ai-' + 'a' * 28}
                return {'ok': True, 'job_id': 'job'}
            def reserve(self, *_): return True
        def discover(selection, **_):
            self.assertEqual(selection['editorial_topic'], 'Pérdida de liderazgo')
            self.assertEqual(selection['research_queue']['origin'], 'chat')
            return {'company': 'BlackBerry'}
        def analyze(sources, **_): return focused({'company': sources['company']})
        def script(research, selection, **_):
            self.assertEqual(research['selected_episode_id'], 'chosen')
            self.assertEqual(research['editorial_topic'], 'Pérdida de liderazgo')
            return {'status': 'editorial_draft_unapproved'}
        with patch('tools.channel_episode.validate_report_locally'):
            result = run_episode(Control(), 'request', resolver=lambda _: 'Q100', discover=discover,
                analyze=analyze, scriptwriter=script, client_factory=lambda **_: None)
        self.assertEqual(result['state'], 'review')


class BoundedContinuationTests(unittest.TestCase):
    def setup_control(self, report):
        class Control:
            def __init__(self):
                self.report=report;self.writes=[];self.scripts=[];self.allowed=True;self.reservations=[]
            def request(self,path,body):
                if path.endswith('/context'):
                    return {'allowed':self.allowed,'episode':{'episode_id':'chosen','company':'BlackBerry',
                        'topic':'Pérdida de liderazgo','origin':'chat'},'checkpoint':{'run_id':'ai-'+'a'*28,'report':self.report}}
                if path.endswith('/research'):
                    self.report=body['report'];self.writes.append(self.report)
                    return {'ok':True,'run_id':'ai-'+'b'*28}
                self.scripts.append(body);return {'ok':True,'job_id':'job'}
            def reserve(self,provider,role):
                self.reservations.append((provider,role));return True
        return Control()

    def saved(self):
        return focused({'company':'BlackBerry','selected_episode_id':'chosen','editorial_topic':'Pérdida de liderazgo',
            'selected_wikidata_id':'Q100','candidate_claims':[{}],'evidence_manifest':[], 'stages':[],
            'observed_official_websites':['https://www.blackberry.com'],
            'source_quality':{'claim_gaps':[{'gaps':['no_independent_domain']}]}})

    def test_one_job_replans_then_corroborates_saved_facts_and_creates_only_one_draft(self):
        report=self.saved();report['editorial_focus_review']['status']='misaligned'
        control=self.setup_control(report);calls=[]
        def analyze(sources,**_):
            calls.append('analyze');return focused({**sources,'candidate_claims':[{}]})
        def corroborate(report,**_):
            calls.append('corroborate');return {'report':{**report,'source_quality':{'claim_gaps':[]}}}
        def script(report,*_,**kwargs):
            return {'status':'blocked_sources' if report['source_quality']['claim_gaps'] else 'editorial_draft_unapproved'}
        with patch('tools.channel_episode.validate_report_locally'):
            result=run_episode_until_review(control,'request',analyze=analyze,corroborate=corroborate,
                scriptwriter=script,client_factory=lambda **_:None)
        self.assertEqual(result['state'],'review');self.assertEqual(calls,['analyze','corroborate'])
        self.assertEqual(result['continuation']['rounds'],2);self.assertEqual(len(control.scripts),1)
        self.assertTrue(all(r['editorial_topic']=='Pérdida de liderazgo' for r in control.writes))

    def test_denied_budget_stops_even_after_new_evidence_has_been_saved(self):
        control=self.setup_control(self.saved());control.reserve=lambda *_:False;calls=[]
        def corroborate(report,**options):
            calls.append('corroborate');self.assertFalse(options['clients'].reserve('groq','review'))
            return {'report':{**report,'evidence_manifest':[{'id':'E001','excerpt':'New saved public text'}]}}
        with patch('tools.channel_episode.validate_report_locally'):
            result=run_episode_until_review(control,'request',corroborate=corroborate,
                scriptwriter=lambda *_a,**_k:{'status':'blocked_sources'})
        self.assertEqual(result['continuation'],{'rounds':1,'stop_reason':'budget_denied'})
        self.assertEqual(calls,['corroborate']);self.assertTrue(control.writes[0]['evidence_manifest'])
        self.assertEqual(control.scripts,[])

    def test_unchanged_checkpoint_does_not_repeatedly_invoke_providers(self):
        control=self.setup_control(self.saved());calls=[]
        def corroborate(report,**_):calls.append('once');return {'report':report}
        with patch('tools.channel_episode.validate_report_locally'):
            result=run_episode_until_review(control,'request',corroborate=corroborate,
                scriptwriter=lambda *_a,**_k:{'status':'blocked_sources'},client_factory=lambda **_:None)
        self.assertEqual(result['continuation']['stop_reason'],'no_material_progress')
        self.assertEqual(calls,['once'])

    def test_pause_between_rounds_prevents_another_source_or_model_call(self):
        control=self.setup_control(self.saved());calls=[]
        def corroborate(report,**_):
            calls.append('once');control.allowed=False
            return {'report':{**report,'evidence_manifest':[{'id':'E001'}]}}
        with patch('tools.channel_episode.validate_report_locally'):
            result=run_episode_until_review(control,'request',corroborate=corroborate,
                scriptwriter=lambda *_a,**_k:{'status':'blocked_sources'},client_factory=lambda **_:None)
        self.assertEqual(result['state'],'paused_or_finished');self.assertEqual(calls,['once'])
        self.assertFalse(control.scripts)

    def test_remote_quota_failure_is_not_retried_with_a_new_client_in_same_job(self):
        from tools.ai_clients import ProviderError
        control=self.setup_control(self.saved());calls=[]
        class Client:
            def generate(self,*a,**k):calls.append('remote');raise ProviderError('quota_exhausted',429)
        def corroborate(report,**options):
            for _ in range(2):
                with self.assertRaises(ProviderError):options['clients'].generate('groq','fixture')
            return {'report':{**report,'evidence_manifest':[{'id':'E001'}]}}
        with patch('tools.channel_episode.validate_report_locally'):
            result=run_episode_until_review(control,'request',corroborate=corroborate,
                scriptwriter=lambda *_a,**_k:{'status':'blocked_sources'},client_factory=lambda **_:Client())
        self.assertEqual(calls,['remote']);self.assertEqual(result['continuation']['stop_reason'],'provider_unavailable')

    def test_replanning_without_new_sources_preserves_claims_and_skips_analyst(self):
        import hashlib
        report=self.saved();report['editorial_focus_review']['status']='misaligned'
        report['focused_analysis_binding']=hashlib.sha256(json.dumps({'profile':'chosen_topic_v2',
            'topic':'Pérdida de liderazgo','evidence':[]},ensure_ascii=False,sort_keys=True).encode()).hexdigest()
        control=self.setup_control(report)
        with patch('tools.channel_episode.validate_report_locally'):
            result=run_episode_until_review(control,'request',discover=lambda *_a,**_k:{'evidence_manifest':[],
                'retrieval_budget':{'attempted_urls':['https://example.com/failed']}},
                analyze=lambda *_a,**_k:self.fail('No analizar otra vez los mismos documentos'),client_factory=lambda **_:None)
        self.assertEqual(result['draft']['status'],'blocked_editorial_sources')
        self.assertEqual(result['research']['candidate_claims'],report['candidate_claims'])
        self.assertIn('https://example.com/failed',result['research']['retrieval_history_urls'])
        self.assertEqual(result['continuation']['rounds'],1)
