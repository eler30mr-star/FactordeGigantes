import json
import unittest
from unittest.mock import patch
from tools.channel_episode import run_episode, resolve_company, resolve_company_identity


class ChannelEpisodeTests(unittest.TestCase):
    def test_incomplete_checkpoint_corroborates_without_repeating_the_analyst(self):
        saved = {'company': 'BlackBerry', 'editorial_topic': 'Pérdida de liderazgo',
                 'selected_episode_id': 'chosen', 'selected_wikidata_id': 'Q100',
                 'candidate_claims': [{}], 'reviews': [{}],
                 'observed_official_websites': ['https://www.blackberry.com'],
                 'source_quality': {'claim_gaps': [{'claim_index': 1, 'gaps': ['no_independent_domain']}]}}
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
            return {**sources, 'candidate_claims': [{}]}
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
        def analyze(sources, **_): return {'company': sources['company']}
        def script(research, selection, **_):
            self.assertEqual(research['selected_episode_id'], 'chosen')
            self.assertEqual(research['editorial_topic'], 'Pérdida de liderazgo')
            return {'status': 'editorial_draft_unapproved'}
        with patch('tools.channel_episode.validate_report_locally'):
            result = run_episode(Control(), 'request', resolver=lambda _: 'Q100', discover=discover,
                analyze=analyze, scriptwriter=script, client_factory=lambda **_: None)
        self.assertEqual(result['state'], 'review')
