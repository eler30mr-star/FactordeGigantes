import json
import unittest
from unittest.mock import patch
from tools.channel_episode import run_episode, resolve_company


class ChannelEpisodeTests(unittest.TestCase):
    def test_pause_does_not_resolve_or_investigate(self):
        class Control:
            def request(self, *args): return {'allowed': False}
        result = run_episode(Control(), 'unused', resolver=lambda _: self.fail('No resolver'))
        self.assertEqual(result['state'], 'paused_or_finished')

    def test_company_resolution_requires_exact_unambiguous_observed_company(self):
        entity = {'labels': {'en': {'value': 'BlackBerry'}}, 'claims': {'P31': [{'mainsnak': {'datavalue': {'value': {'id': 'Q783794'}}}}]}}
        def fetch(url):
            return {'search': [{'id': 'Q100'}]} if 'wbsearchentities' in url else {'entities': {'Q100': entity}}
        self.assertEqual(resolve_company('BlackBerry', fetch), 'Q100')
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
