"""Contratos de búsqueda dirigida, citas literales y presupuesto gratuito."""
import json
import unittest
from unittest.mock import patch

from tools.ai_clients import FreeClients
from tools.ai_source_discovery import discover_sources, REGULATORY_HOSTS
from tools.ai_research_pipeline import source_report, validate_report_locally
from tools.research_source_plan import search_plan, select_passages
from tools.research_diagnostics import research_summary

TITLE = 'Empresa Ejemplo'
TARGET = {'claim_index': 1, 'statement': 'Empresa Ejemplo acordó una restitución de 4.650.000 en 2017.',
          'cited_urls': ['https://reporter.example/story'],
          'gaps': ['only_one_document', 'no_regulatory_primary_document']}


class TargetedRetrievalTests(unittest.TestCase):
    def test_observed_citation_context_prioritizes_the_original_without_becoming_evidence(self):
        from tools.ai_clients import ProviderError
        root='https://corporate.example/company'
        document='https://corporate.example/z-quarterly-results'
        manual='https://corporate.example/a-device-manual'
        wiki_context='WIKI_ONLY_MARKER The company ended hardware development and shifted to software services.'
        text=wiki_context+'<ref>{{cite web|url='+document+'|title=Quarterly financial results}}</ref>'
        def wiki(url,**_):
            self.assertIn('wikitext',url)
            return json.dumps({'parse':{'externallinks':[manual,document],'wikitext':{'*':text}}}).encode(),url,'application/json'
        class Search:
            def search(self,*a,**k):raise ProviderError('missing_key')
        downloads=[]
        original=TITLE+' published its operations report and software development strategy, which still requires independent documentary corroboration.'
        def fetch(url,**_):
            downloads.append(url);return ('<p>'+original+'</p>').encode(),url,'text/html'
        result=discover_sources({'selected_wikidata_id':'Q100','research_queue':{'wikidata_id':'Q100','title':TITLE},
            'observed_official_websites':[root],'editorial_topic':'Su transformación del negocio',
            'editorial_search_terms':['hardware development software services original financial results',
                'hardware software transition independent market analysis']},
            clients=Search(),wiki_fetcher=wiki,document_fetcher=fetch)
        self.assertEqual(downloads[0],document)
        self.assertTrue(result['evidence_manifest'])
        self.assertTrue(all(e['excerpt'] in original for e in result['evidence_manifest']))
        self.assertTrue(all('WIKI_ONLY_MARKER' not in e['excerpt'] for e in result['evidence_manifest']))
        self.assertFalse(result['publication_authorized']);validate_report_locally(source_report(result))

    def test_english_retrieval_terms_reach_queries_and_literal_passage_ranking(self):
        from tools.ai_clients import ProviderError
        terms=['leadership loss smartphone market share annual report','hardware exit software transition independent analysis']
        queries=[]
        class Search:
            def search(self,provider,query,**filters):
                if provider!='tavily':raise ProviderError('missing_key')
                queries.append(query)
                return [{'url':'https://reporter.example/business','title':TITLE,'discovered_by':provider}]
        intro=TITLE+' announced a telephone with a keyboard and speakers, as described in technical specifications for this device.'
        focused=TITLE+' reported a loss of smartphone market share and a transition from hardware to software, requiring documentary verification.'
        raw=('<p>'+intro+'</p><p>'+focused+'</p>').encode()
        with patch('tools.ai_source_discovery.wikipedia_links',return_value=[]):
            sources=discover_sources({'selected_wikidata_id':'Q100','research_queue':{'wikidata_id':'Q100','title':TITLE},
                'editorial_topic':'Pérdida de liderazgo y transformación','editorial_search_terms':terms,
                'editorial_questions':['¿Qué decisiones cambiaron la posición competitiva de la empresa?']},
                clients=Search(),document_fetcher=lambda url,**_:(raw,url,'text/html'))
        self.assertEqual(queries,[f'"{TITLE}" '+term for term in terms])
        self.assertEqual(sources['evidence_manifest'][0]['excerpt'],focused)
        validate_report_locally(source_report(sources))

    def test_editorial_search_results_precede_unrelated_alphabetical_wiki_leads(self):
        from tools.ai_clients import ProviderError
        targeted=['https://z-context.example/z-business-shift', 'https://z-context.example/a-product-specs']
        downloads=[]
        class Search:
            def search(self,provider,*a,**k):
                if provider!='tavily':raise ProviderError('missing_key')
                return [{'url':url,'title':TITLE,'discovered_by':'tavily'} for url in targeted]
        def fetch(url,**_):
            downloads.append(url)
            return (('<p>'+TITLE+' cambió su posición en el mercado. '+
                'Información documental pública pendiente de contraste independiente. '*3+'</p>').encode(),url,'text/html')
        with patch('tools.ai_source_discovery.wikipedia_links',return_value=[
                {'url':'https://a-legacy.example/a-product-specs','discovered_by':'wikipedia'},
                {'url':targeted[0],'discovered_by':'wikipedia'}]):
            discover_sources({'selected_wikidata_id':'Q100','research_queue':{'wikidata_id':'Q100','title':TITLE},
                'editorial_topic':'Su pérdida de liderazgo','editorial_questions':['¿Qué cambió en el negocio de la empresa?']},
                clients=Search(),document_fetcher=fetch)
        self.assertEqual(downloads[0],targeted[0])
        self.assertNotIn(targeted[1],downloads)  # Same-host bound still applies.

    def test_editorial_questions_guide_queries_without_becoming_claims(self):
        questions=['¿Qué decisiones cambiaron la posición de la empresa?', '¿Cómo evolucionó su negocio de software?']
        plan=search_plan(TITLE,[],REGULATORY_HOSTS,editorial_questions=questions)
        self.assertEqual(len(plan),2)
        self.assertIn(questions[0],plan[0]['query'])
        self.assertIn(questions[1],plan[1]['query'])
        self.assertNotIn('target_claim_index',plan[0])

    def test_two_queries_cover_primary_and_another_pending_claim_with_its_own_exclusions(self):
        first={**TARGET,'gaps':['no_original_primary_document']}
        second={**TARGET,'claim_index':2,'statement':'Empresa Ejemplo cambió su negocio en 2018.',
            'cited_urls':['https://another.example/story'],'gaps':['no_independent_domain']}
        plan=search_plan(TITLE,[first,second],REGULATORY_HOSTS)
        self.assertEqual(len(plan),2)
        self.assertEqual([row['target_claim_index'] for row in plan],[1,2])
        self.assertIn(second['statement'],plan[1]['query'])
        self.assertIn('another.example',plan[1]['exclude_domains'])
        self.assertNotIn('reporter.example',plan[1]['exclude_domains'])

    def test_search_prioritizes_missing_authority_then_different_publisher(self):
        plan = search_plan(TITLE, [TARGET], REGULATORY_HOSTS)
        self.assertEqual(len(plan), 2)
        self.assertIn('justice.gov', plan[0]['include_domains'])
        self.assertNotIn('reporter.example', plan[0]['exclude_domains'])
        self.assertNotIn('include_domains', plan[1])
        self.assertIn('reporter.example', plan[1]['exclude_domains'])
        ordinary = {**TARGET, 'gaps': ['no_original_primary_document']}
        self.assertNotIn('include_domains', search_plan(TITLE, [ordinary], REGULATORY_HOSTS)[0])

    def test_filters_reach_tavily_without_raising_cost_profile_or_request_count(self):
        calls, reservations = [], []
        def transport(url, body, headers):
            calls.append(body)
            return {'results': []}
        client = FreeClients(env={'TAVILY_API_KEY': 'fixture-not-a-real-key',
                                  'TAVILY_RESEARCH_FREE_CONFIRMED': '1'},
            reserve=lambda p, r: reservations.append((p, r)) or True, transport=transport)
        with patch('tools.ai_source_discovery.wikipedia_links', return_value=[]):
            result = discover_sources({'selected_wikidata_id': 'Q100',
                'research_queue': {'wikidata_id': 'Q100', 'title': TITLE},
                'prior_research_targets': [TARGET]}, clients=client)
        self.assertEqual(len(calls), 2)
        self.assertEqual(len(reservations), 2)
        self.assertIn('justice.gov', calls[0]['include_domains'])
        self.assertIn('reporter.example', calls[1]['exclude_domains'])
        self.assertTrue(all(c['search_depth'] == 'basic' and not c['auto_parameters'] and
                            not c['include_raw_content'] and not c['include_answer'] for c in calls))
        validate_report_locally(source_report(result))

    def test_bad_filter_is_rejected_before_budget_reservation(self):
        client = FreeClients(env={}, reserve=lambda *_: self.fail('Reserva con filtro inválido'))
        for domain in ('localhost', 'https://justice.gov', 'sec.gov/private', 'a@justice.gov', '*.gov'):
            with self.assertRaises(ValueError):
                client.search('tavily', 'Tema', include_domains=[domain])

    def test_relevant_late_paragraph_survives_instead_of_three_introductory_mentions(self):
        introduction = TITLE + ' presentó información histórica general y comentarios sobre sus operaciones empresariales, sin abordar el acuerdo que debe contrastarse.'
        decisive = TITLE + ' acordó una restitución de 4.650.000 en 2017, según el documento original; el anuncio no demuestra que se haya ejecutado el pago.'
        analysis = {'blocks': [introduction + str(n) for n in range(5)] + [decisive],
                    'page_map': [None] * 6}
        passages = select_passages(analysis, TITLE, [TARGET])
        self.assertEqual(passages[0]['block_index'], 5)
        self.assertIn('4.650.000', passages[0]['excerpt'])
        self.assertTrue(all(p['excerpt'] in analysis['blocks'][p['block_index']] for p in passages))

    def test_window_captures_late_amount_and_does_not_rewrite_the_quote(self):
        text = TITLE + ': ' + 'Antecedentes documentales generales. ' * 16 + \
            'En 2017 acordó una restitución de 4.650.000 para los consumidores, sin acreditar todavía la ejecución efectiva del pago.'
        passage = select_passages({'blocks': [text], 'page_map': [4]}, TITLE, [TARGET])[0]
        self.assertIn('4.650.000', passage['excerpt'])
        self.assertIn('2017', passage['excerpt'])
        self.assertEqual(passage['page'], 4)
        self.assertLessEqual(len(passage['excerpt']), 320)
        self.assertIn(passage['excerpt'], text)

    def test_entity_context_may_use_nearby_text_but_never_another_pdf_page(self):
        heading = TITLE + ' comunicó un acuerdo que se explica a continuación con sus condiciones y fechas pendientes de revisión.'
        clause = 'El acuerdo de restitución fue anunciado en 2017 por un importe de 4.650.000, sin que ese anuncio pruebe que se ejecutó el desembolso.'
        for pages, expected in (([2, 2], True), ([2, 3], False)):
            passages = select_passages({'blocks': [heading, clause], 'page_map': pages}, TITLE, [TARGET])
            selected = [p for p in passages if p['block_index'] == 1]
            self.assertEqual(bool(selected), expected)
            if selected:
                self.assertEqual(selected[0]['entity_context_excerpt'], heading)

    def test_diagnostics_uses_only_public_allowlisted_fields(self):
        report = {'company': TITLE, 'candidate_claims': [], 'evidence_manifest': [],
                  'source_documents': [{'url': 'https://justice.gov/example', 'status': 'fetch_failed',
                                        'Authorization': 'must-not-appear', 'api_key': 'must-not-appear'}],
                  'private_token': 'must-not-appear'}
        summary = research_summary(report)
        self.assertNotIn('must-not-appear', json.dumps(summary))
        self.assertFalse(summary['facts_verified'])
        self.assertFalse(summary['publication_authorized'])

    def test_discovery_retains_targeted_quote_and_context_under_worker_contract(self):
        from tools.ai_clients import ProviderError
        text = TITLE + ': ' + 'Antecedentes documentales generales. ' * 16 + \
            'En 2017 acordó una restitución de 4.650.000 para los consumidores, sin acreditar todavía la ejecución efectiva del pago.'
        class Search:
            def search(self, provider, query, **filters):
                if provider != 'tavily':
                    raise ProviderError('missing_key')
                return [{'url': 'https://www.azag.gov/press-release/empresa-ejemplo', 'discovered_by': provider}]
        with patch('tools.ai_source_discovery.wikipedia_links', return_value=[]):
            sources = discover_sources({'selected_wikidata_id': 'Q100',
                'research_queue': {'wikidata_id': 'Q100', 'title': TITLE},
                'prior_research_targets': [TARGET]}, clients=Search(),
                document_fetcher=lambda url, **_: (('<p>'+text+'</p>').encode(), url, 'text/html'))
        quote = sources['evidence_manifest'][0]
        self.assertIn('4.650.000', quote['excerpt'])
        self.assertIn(quote['entity_context_excerpt'], text)
        self.assertIn(quote['excerpt'], text)
        self.assertEqual(sources['retrieval_budget']['attempted'], 1)
        self.assertEqual(sources['retrieval_budget']['public_authority_domains_with_text'], 1)
        validate_report_locally(source_report(sources))


if __name__ == '__main__':
    unittest.main()

