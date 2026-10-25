import json
import unittest
from datetime import date
from urllib.parse import urlsplit, parse_qs
from tools.youtube_opportunity_study import YoutubeMetadata, collect_study, identify_candidates, link_candidate_videos


class YoutubeOpportunityStudyTests(unittest.TestCase):
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
