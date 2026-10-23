"""Referencias regulatorias observadas en PDF: sin rutas adivinadas ni red."""
from io import BytesIO
import unittest
from unittest.mock import patch

from pypdf import PdfWriter
from pypdf.annotations import Link

from tools.ai_clients import FreeClients
from tools.ai_source_discovery import discover_sources, document_references
from tools.ai_research_pipeline import source_report, validate_report_locally
from tools.pdf_sources import pdf_link_annotations
from tools.pdf_sources import clean_pdf_layout
from tools.research_source_plan import search_plan, select_passages

TEXT = 'Empresa Ejemplo comunicó en 2018 una investigación de sus operaciones; el documento necesita contraste independiente y revisión del contexto legal antes de narrarlo.'


def pdf_with_links(urls):
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    for url in urls:
        writer.add_annotation(0, Link(rect=(10, 10, 100, 30), url=url))
    stream = BytesIO(); writer.write(stream)
    return stream.getvalue()


class PdfReferencesTests(unittest.TestCase):
    def test_legal_margin_sequence_is_removed_but_fact_numbers_are_retained(self):
        text='\n'.join(['Instrucciones al jurado',*map(str,range(1,29)),
                        'El periodo investigado fue de 2010 a 2015.',
                        '2018','4','Importe mencionado: 452 millones.',
                        'Case 5:18-cr-00258-EJD Document 1006 Filed 09/07/21 Page 2 of 4'])
        result=clean_pdf_layout(text)
        self.assertNotIn('1\n2\n3',result)
        self.assertIn('2010 a 2015',result)
        self.assertIn('2018\n4',result)
        self.assertIn('452 millones',result)
        self.assertNotIn('Document 1006',result)

    def test_identical_candidate_statements_merge_citations_without_approval(self):
        import json
        from tools.research_providers import parse_candidate_output
        parsed=parse_candidate_output(json.dumps({'claims':[
            {'statement':'La empresa presentó un documento en 2018.', 'evidence_ids':['E001']},
            {'statement':'La empresa presentó un documento en 2018!', 'evidence_ids':['E002']}],
            'missing_questions':[]}),[{'id':'E001'},{'id':'E002'}],'fixture')
        self.assertEqual(len(parsed['candidate_claims']),1)
        self.assertEqual(parsed['candidate_claims'][0]['evidence_ids'],['E001','E002'])
        self.assertFalse(parsed['candidate_claims'][0]['human_verified'])

    def test_annotations_keep_literal_url_and_page_and_reject_untrusted_hosts(self):
        original = 'https://www.justice.gov/company-original'
        raw = pdf_with_links([original, 'https://sec.gov.attacker.example/bad',
                              'https://127.0.0.1/private', 'http://www.sec.gov/no-tls'])
        refs = document_references(raw, 'https://university.example/study.pdf', mime='application/pdf')
        self.assertEqual([r['url'] for r in refs], [original])
        self.assertEqual(refs[0]['discovered_from_page'], 1)
        self.assertEqual(refs[0]['discovered_from'], 'https://university.example/study.pdf')
        self.assertEqual(pdf_link_annotations(raw)[0]['url'], original)

    def test_plain_pdf_bibliography_supplies_leads_but_never_becomes_factual_passage(self):
        text = ('Referencias de Empresa Ejemplo: https://www.sec.gov/original ' +
                'https://www.justice.gov/second. Consultar los documentos originales antes de usar los títulos como respaldo.')
        analysis = {'blocks': [text], 'page_map': [1]}
        raw = pdf_with_links([])
        refs = document_references(raw, 'https://university.example/study.pdf',
                                   mime='application/pdf', analysis=analysis)
        self.assertEqual([r['url'] for r in refs],
                         ['https://www.sec.gov/original', 'https://www.justice.gov/second'])
        self.assertEqual(select_passages(analysis, 'Empresa Ejemplo', []), [])

    def test_pdf_original_is_followed_within_same_eight_document_budget(self):
        study, original = 'https://university.example/study.pdf', 'https://www.justice.gov/company-original'
        raw = pdf_with_links([original])
        calls = []
        def download(url, **_):
            calls.append(url)
            return (raw, url, 'application/pdf') if url == study else (('<p>'+TEXT+'</p>').encode(), url, 'text/html')
        clients = FreeClients(env={}, reserve=lambda *_: self.fail('No hay IA configurada'))
        with patch('tools.ai_source_discovery.wikipedia_links', return_value=[{'url': study}]), \
             patch('tools.ai_source_discovery.analyze_document', return_value={
                 'blocks': [TEXT], 'page_map': [1], 'total_pages': 1, 'type': 'pdf'}):
            result = discover_sources({'selected_wikidata_id': 'Q100',
                'research_queue': {'wikidata_id': 'Q100', 'title': 'Empresa Ejemplo'}},
                clients=clients, document_fetcher=download)
        self.assertEqual(calls, [study, original])
        self.assertEqual(result['retrieval_budget']['attempted'], 2)
        self.assertIn(study, result['retrieval_budget']['citation_scanned_urls'])
        self.assertEqual(result['retrieval_budget']['public_authority_domains_with_text'], 1)
        validate_report_locally(source_report(result))

    def test_second_observed_authority_url_is_allowed_only_after_unreadable_first(self):
        urls = ['https://www.justice.gov/a', 'https://www.justice.gov/b', 'https://www.justice.gov/c']
        calls = []
        def download(url, **_):
            calls.append(url)
            text = 'Información institucional general sin relación con la entidad investigada, cuya lectura no contiene respaldo documental útil para el episodio.' if url == urls[0] else TEXT
            return ('<p>'+text+'</p>').encode(), url, 'text/html'
        with patch('tools.ai_source_discovery.wikipedia_links', return_value=[{'url': u} for u in urls]):
            result = discover_sources({'selected_wikidata_id': 'Q100',
                'research_queue': {'wikidata_id': 'Q100', 'title': 'Empresa Ejemplo'}},
                clients=FreeClients(env={}, reserve=lambda *_: False), document_fetcher=download)
        self.assertEqual(calls, urls[:2])
        self.assertEqual(result['retrieval_budget']['attempted'], 2)
        validate_report_locally(source_report(result))

    def test_official_query_uses_legal_terms_and_observed_year_without_spanish_boilerplate(self):
        target = {'claim_index': 2, 'statement': 'En junio de 2018, dos directivos fueron imputados por cargos de fraude.',
                  'gaps': ['no_regulatory_primary_document'], 'cited_urls': []}
        query = search_plan('Empresa Ejemplo', [target], ['justice.gov'])[0]['query']
        self.assertIn('"Empresa Ejemplo"', query)
        self.assertIn('2018', query)
        self.assertIn('indictment', query)
        self.assertNotIn('fueron imputados', query)


if __name__ == '__main__':
    unittest.main()
