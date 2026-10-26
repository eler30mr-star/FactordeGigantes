import json
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit, parse_qs
from tools.youtube_opportunity_study import YoutubeMetadata, collect_study, identify_candidates, link_candidate_videos, main


def proposal(*companies):
    return json.dumps({'candidates': [{'company': name, 'topic': 'Su transformación empresarial',
        'rationale': 'Hipótesis de oportunidad pendiente de comparación.',
        'niche_reason': 'Una historia de innovación dentro del nicho.'} for name in companies]})


class SampleMetadata:
    """In-memory metadata only; no transport or provider can be invoked."""
    def __init__(self, *, broad_count=0, focused_count=0, channels=3):
        self.calls = self.searches = self.baseline_calls = 0
        self.broad_count, self.focused_count, self.channels = broad_count, focused_count, channels

    def search(self, query, today):
        self.calls += 1
        self.searches += 1
        count = self.broad_count if self.searches <= 3 else self.focused_count
        return ['v' + str(i).zfill(10) for i in range(count)]

    def videos(self, ids):
        self.calls += bool(ids)
        return [{'id': identity, 'title': 'Empresa Alfa y Empresa Beta: decisiones e innovación',
            'channel_id': 'UC' + str(int(identity[1:]) % self.channels).zfill(22),
            'views': 1000, 'duration_seconds': 600, 'published_on': '2026-10-15'} for identity in ids]

    def baselines(self, channels):
        self.baseline_calls += 1
        return []


class YoutubeOpportunityStudyTests(unittest.TestCase):
    def test_empty_observations_do_not_invoke_ai_or_channel_baselines(self):
        api = SampleMetadata()
        report = collect_study(api, lambda _: self.fail('No titles: no AI call'), date(2026, 10, 25))
        self.assertEqual(api.searches, 3)
        self.assertEqual(api.baseline_calls, 0)
        self.assertEqual(report['candidates'], [])
        self.assertEqual(report['extraction_provider'], 'not_invoked_insufficient_evidence')
        self.assertEqual(report['sample_summary']['observed_videos'], 0)
        self.assertIn('need_four_comparable_long_videos', report['early_stop_reasons'])

    def test_small_broad_sample_can_grow_before_sufficiency_is_checked(self):
        api = SampleMetadata(broad_count=1, focused_count=8)
        proposals = []
        def generate(prompt):
            self.assertEqual(api.searches, 3)
            proposals.append(prompt)
            return proposal('Empresa Alfa', 'Empresa Beta')
        report = collect_study(api, generate, date(2026, 10, 25))
        self.assertEqual(len(proposals), 1)
        self.assertEqual(api.searches, 5)
        self.assertEqual(len(report['videos']), 8)
        self.assertEqual(api.baseline_calls, 1)
        self.assertNotIn('early_stop_reasons', report)

    def test_final_insufficient_pool_skips_baselines_without_repeating_ai(self):
        api = SampleMetadata(broad_count=4, focused_count=8, channels=1)
        with patch('tools.youtube_opportunity_study.identify_candidates', wraps=identify_candidates) as identify:
            report = collect_study(api, lambda _: proposal('Empresa Alfa', 'Empresa Beta'), date(2026, 10, 25))
        self.assertEqual(identify.call_count, 1)
        self.assertEqual(api.searches, 5)
        self.assertEqual(api.baseline_calls, 0)
        self.assertEqual(report['early_stop_reasons'], ['need_three_observed_channels'])
        self.assertEqual(report['sample_summary']['comparable_long_videos'], 8)
        self.assertEqual(report['baselines'], [])
        self.assertEqual(len(report['candidates']), 2)

    def test_main_records_empty_study_instead_of_failing_or_spending_a_model_call(self):
        calls = []
        def control_request(path, body):
            calls.append((path, body))
            if path.endswith('/finish'):
                return {'ok': True, 'state': 'insufficient'}
            self.assertNotIn('/fail', path)
            return {'allowed': True}
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            with patch.dict('os.environ', {'YOUTUBE_MARKET_BUDGET_ENABLED': '1'}), \
                    patch('tools.youtube_opportunity_study.Path', return_value=folder), \
                    patch('tools.youtube_opportunity_study.ControlClient') as control, \
                    patch('tools.youtube_opportunity_study.FreeClients') as clients, \
                    patch('tools.youtube_opportunity_study.YoutubeMetadata', return_value=SampleMetadata()), \
                    redirect_stdout(io.StringIO()):
                control.return_value.request.side_effect = control_request
                main()
                clients.return_value.generate.assert_not_called()
                control.return_value.reserve.assert_not_called()
            self.assertEqual(json.loads((folder / 'DECISION.json').read_text())['state'], 'insufficient')
            self.assertEqual(json.loads((folder / 'ESTUDIO_YOUTUBE.json').read_text())['candidates'], [])
            self.assertFalse((folder / 'BLOQUEO.json').exists())
        self.assertEqual([p for p, _ in calls], ['/api/market/opportunity-study/start', '/api/market/opportunity-study/finish'])

    def test_company_identity_is_a_whole_name_and_accent_variants_are_duplicates(self):
        videos = [{'id': 'v0000000001', 'title': 'Palmolive y Citroën cambian el mercado'},
                  {'id': 'v0000000002', 'title': 'Empresa Beta y su innovación'}]
        with self.assertRaises(ValueError):
            identify_candidates(videos, lambda _: proposal('Palm', 'Empresa Beta'))
        with self.assertRaises(ValueError):
            identify_candidates(videos, lambda _: proposal('Citroën', 'Citroen'))
        self.assertEqual(identify_candidates(videos, lambda _: proposal('Citroen', 'Empresa Beta'))[0]['company'], 'Citroen')

    def test_broad_search_evidence_is_retained_and_company_names_are_not_substrings(self):
        candidates = [{'company': 'Palm', 'video_ids': ['focused']}, {'company': 'Nokia', 'video_ids': []}]
        videos = [{'id': 'broad', 'title': 'La historia de Palm y Nokia'},
                  {'id': 'focused', 'title': 'Palm: su transformación'},
                  {'id': 'unrelated', 'title': 'Palmolive y sus productos'}]
        link_candidate_videos(videos, candidates)
        self.assertEqual(candidates[0]['video_ids'], ['broad', 'focused'])
        self.assertEqual(candidates[1]['video_ids'], ['broad'])

    def test_guard_stops_before_any_youtube_request(self):
        api = YoutubeMetadata('fake-key-for-unit-tests-only', guard=lambda: False,
            transport=lambda _: self.fail('No debe realizar red'))
        with self.assertRaises(ValueError):
            api.search('historia empresas', date(2026, 10, 25))
        self.assertEqual(api.calls, 0)

    def test_api_budget_and_format_are_explicit(self):
        calls = []
        def transport(url):
            query = parse_qs(urlsplit(url).query)
            calls.append(query)
            self.assertEqual(query['videoDuration'], ['medium'])
            self.assertEqual(query['maxResults'], ['12'])
            return {'items': []}
        api = YoutubeMetadata('fake-key-for-unit-tests-only', transport=transport)
        for _ in range(7):
            api.search('historia empresas', date(2026, 10, 25))
        with self.assertRaises(ValueError):
            api.search('una consulta de más', date(2026, 10, 25))
        self.assertEqual(len(calls), 7)

    def test_llm_cannot_introduce_unobserved_or_duplicate_companies(self):
        videos = [{'id': 'v0000000001', 'title': 'Empresa Alfa cambia el mercado'},
                  {'id': 'v0000000002', 'title': 'Empresa Beta cambia el mercado'}]
        def candidate(name):
            return {'company': name, 'topic': 'Su transformación empresarial',
                'rationale': 'Una oportunidad que debe compararse con evidencia.',
                'niche_reason': 'La innovación empresarial encaja con el canal.'}
        result = identify_candidates(videos, lambda _: json.dumps({'candidates': [candidate('Empresa Alfa'), candidate('Empresa Beta')]}))
        self.assertEqual(len(result), 2)
        for names in [('Empresa Alfa', 'Empresa Inventada'), ('Empresa Alfa', 'Empresa Alfa')]:
            with self.assertRaises(ValueError):
                identify_candidates(videos, lambda _: json.dumps({'candidates': [candidate(n) for n in names]}))

    def test_search_precedes_candidate_extraction_and_only_metadata_is_collected(self):
        events = []
        class Metadata:
            calls = 0
            searches = 0
            def search(self, query, today):
                events.append(('search', query)); self.calls += 1; self.searches += 1
                return ['v0000000001', 'v0000000002']
            def videos(self, ids):
                events.append(('metadata', list(ids))); self.calls += 1
                return [{'id': i, 'title': ('Empresa Alfa' if i.endswith('1') else 'Empresa Beta') + ' y su historia',
                    'channel_id': 'UC' + i[-1] * 22, 'views': 1000, 'duration_seconds': 600,
                    'published_on': '2026-10-15'} for i in ids]
            def baselines(self, channels):
                events.append(('baselines', channels)); return []
        def generate(prompt):
            events.append(('llm', None))
            return json.dumps({'candidates': [{'company': name, 'topic': 'Su transformación empresarial',
                'rationale': 'Hipótesis basada en los títulos, pendiente de comparación.',
                'niche_reason': 'Es una historia de innovación de una empresa.'} for name in ['Empresa Alfa', 'Empresa Beta']]})
        result = collect_study(Metadata(), generate, date(2026, 10, 25))
        self.assertEqual(len(result['queries']), 5)
        self.assertEqual(len(result['videos']), 2)
        self.assertLess(next(i for i, event in enumerate(events) if event[0] == 'search'),
                        next(i for i, event in enumerate(events) if event[0] == 'llm'))
        self.assertNotIn('sources', result)
        self.assertNotIn('research', result)


if __name__ == '__main__':
    unittest.main()
