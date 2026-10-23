"""Continuación factual: mismos objetivos, nuevas fuentes observadas, cuotas fijas."""
import json
import unittest
from unittest.mock import patch

from tools.ai_clients import FreeClients,ProviderError
from tools.ai_source_discovery import discover_sources,document_references,research_targets
from tools.ai_research_pipeline import source_report,validate_report_locally,analyze_sources,gate_duplicate_research

TEXT = "Empresa Ejemplo acordó en 2017 pagar una restitución a los consumidores, según un documento público que todavía necesita contraste independiente."
SELECTION = {"selected_wikidata_id":"Q100","research_queue":{"wikidata_id":"Q100","title":"Empresa Ejemplo"}}


class ContinuationTests(unittest.TestCase):
    def test_reopening_an_article_for_links_does_not_count_dynamic_html_as_new_evidence(self):
        old={'url':'https://reporter.example/original','document_sha256':'a'*64}
        changed={**old,'document_sha256':'b'*64,'excerpt':TEXT}
        selection={'prior_evidence_manifest':[old],'citation_expansion_urls':[old['url']]}
        evidence,audit=gate_duplicate_research(selection,[changed])
        self.assertEqual(evidence,[])
        self.assertEqual(audit['reason'],'unchanged_documentary_sources')
        new={**changed,'url':'https://www.azag.gov/document'}
        self.assertEqual(len(gate_duplicate_research(selection,[changed,new])[0]),2)

    def clients(self):
        return FreeClients(env={}, reserve=lambda *_: self.fail("Consumo IA inesperado"))

    def test_article_link_discovers_original_authority_without_extra_budget(self):
        article="https://reporter.example/empresa-ejemplo"
        original="https://www.azag.gov/press-release/empresa-ejemplo"
        calls=[]
        def fetch(url,**_):
            calls.append(url)
            text="<p>"+TEXT+"</p>"
            if url==article:
                text+='<a href="'+original+'">Acuerdo original</a>'
            return text.encode(),url,"text/html"
        with patch('tools.ai_source_discovery.wikipedia_links',return_value=[{
                "url":article,"title":"Empresa Ejemplo","discovered_by":"wikipedia_external_links"}]):
            result=discover_sources(SELECTION,clients=self.clients(),document_fetcher=fetch)
        self.assertEqual(calls,[article,original])
        self.assertEqual(result['retrieval_budget']['attempted'],2)
        self.assertEqual(result['retrieval_budget']['public_authority_domains_with_text'],1)
        linked=next(d for d in result['source_documents'] if d['url']==original)
        self.assertEqual(linked['discovered_from'],article)
        self.assertEqual(linked['discovered_by'],'document_citations')
        self.assertFalse(result['ready_for_script'])
        validate_report_locally(source_report(result))

    def test_link_graph_is_bounded_and_cannot_follow_private_or_fake_authorities(self):
        raw=('''<a href="https://127.0.0.1/private">bad</a>
          <a href="http://www.justice.gov/no-tls">bad</a>
          <a href="https://sec.gov.attacker.example/a">bad</a>
          <a href="https://www.justice.gov/a#section">one</a>
          <a href="https://www.justice.gov/a">duplicate</a>'''+
          ''.join(f'<a href="https://www.sec.gov/doc/{i}">doc</a>' for i in range(30))).encode()
        refs=document_references(raw,'https://reporter.example/news')
        self.assertEqual(len(refs),12)
        self.assertEqual(refs[0]['url'],'https://www.justice.gov/a')
        self.assertTrue(all(r['discovered_from']=='https://reporter.example/news' for r in refs))

    def test_targets_and_forty_attempts_survive_without_new_search_spending(self):
        targets=[{"claim_index":1,"statement":TEXT,
                  "cited_urls":["https://reporter.example/original"],
                  "gaps":["no_independent_domain"]}]
        selection={**SELECTION,"prior_research_targets":targets,
                   "prior_attempted_urls":[f'https://old.example/doc/{i}' for i in range(40)]}
        with patch('tools.ai_source_discovery.wikipedia_links',return_value=[]):
            result=discover_sources(selection,clients=self.clients(),
                                    document_fetcher=lambda *_:self.fail('No hay fuentes nuevas'))
        self.assertEqual(result['research_targets'],targets)
        self.assertEqual(result['retrieval_budget']['attempted'],0)
        report=analyze_sources(result,clients=self.clients(),local_generate=lambda _:self.fail('No contexto'))
        self.assertEqual(report['research_targets'],targets)
        validate_report_locally(report)
        with self.assertRaises(ValueError):
            research_targets({"prior_research_targets":[{**targets[0],"cited_urls":["https://localhost/private"]}]})

    def test_prompt_continues_existing_claims_without_treating_them_as_verified(self):
        from tools.research_providers import request_document
        targets=[{'claim_index':1,'statement':TEXT,'cited_urls':[],'gaps':['only_one_document']}]
        prompt=request_document('Empresa Ejemplo',[{'id':'E001','excerpt':TEXT}],targets=targets)
        self.assertIn(TEXT,prompt)
        self.assertIn('no hechos aprobados',prompt)
        self.assertIn('dos documentos de emisores distintos',prompt)
        self.assertIn('un acuerdo de pago con un pago ya ejecutado',prompt)

    def test_targeted_search_precedes_general_links_even_when_wikipedia_has_same_url(self):
        target='https://z-target.example/empresa-ejemplo'
        targets=[{'claim_index':1,'statement':TEXT,'cited_urls':[], 'gaps':['only_one_document']}]
        class Search:
            def search(self,provider,query,**filters):
                if provider!='tavily':raise ProviderError('missing_key')
                return [{'url':target,'title':'Documento dirigido','discovered_by':'tavily'}]
        wiki=[{'url':f'https://a{i}.example/empresa-ejemplo','discovered_by':'wikipedia_external_links'} for i in range(12)]
        wiki.append({'url':target,'discovered_by':'wikipedia_external_links'})
        calls=[]
        def fetch(url,**_):
            calls.append(url)
            return ('<p>'+TEXT+'</p>').encode(),url,'text/html'
        with patch('tools.ai_source_discovery.wikipedia_links',return_value=wiki):
            result=discover_sources({**SELECTION,'prior_research_targets':targets},clients=Search(),document_fetcher=fetch)
        self.assertEqual(calls[0],target)
        self.assertEqual(len(calls),5)  # Límite de documentos secundarios intacto.
        self.assertEqual(len(set(calls)),5)
        self.assertEqual(next(d for d in result['source_documents'] if d['url']==target)['discovered_by'],'tavily')
        validate_report_locally(source_report(result))

    def test_wikipedia_from_search_history_or_redirect_never_becomes_evidence(self):
        class Search:
            def search(self,provider,query,**filters):
                if provider!='tavily':raise ProviderError('missing_key')
                return [{'url':u,'discovered_by':'tavily'} for u in
                        ['https://es.wikipedia.org/wiki/Empresa','https://reporter.example/redirect']]
        old={'wikidata_id':'Q100','company':'Empresa Ejemplo','url':'https://en.wikipedia.org/wiki/Empresa',
             'document_sha256':'a'*64,'excerpt':TEXT,'source_class':'public_document_candidate','page':None}
        calls=[]
        def fetch(url,**_):
            calls.append(url)
            return ('<p>'+TEXT+'</p>').encode(),'https://es.wikipedia.org/wiki/Empresa','text/html'
        with patch('tools.ai_source_discovery.wikipedia_links',return_value=[]):
            result=discover_sources({**SELECTION,'prior_evidence_manifest':[old]},clients=Search(),document_fetcher=fetch)
        self.assertEqual(calls,['https://reporter.example/redirect'])
        self.assertEqual(result['evidence_manifest'],[])
        validate_report_locally(source_report(result))

    def test_ten_passage_cap_keeps_history_and_represents_all_new_documents(self):
        old=[{'wikidata_id':'Q100','company':'Empresa Ejemplo','url':f'https://old{i}.example/article',
              'document_sha256':'a'*64,'excerpt':TEXT,'source_class':'public_document_candidate','page':None}
             for i in range(4)]
        urls=[f'https://new{i}.example/article' for i in range(4)]
        def fetch(url,**_):
            return ''.join('<p>'+TEXT+f' Pasaje {i}.</p>' for i in range(3)).encode(),url,'text/html'
        with patch('tools.ai_source_discovery.wikipedia_links',return_value=[{'url':u} for u in urls]):
            result=discover_sources({**SELECTION,'prior_evidence_manifest':old},clients=self.clients(),document_fetcher=fetch)
        self.assertEqual(result['retrieval_budget']['new_fragments'],12)
        self.assertEqual(len(result['evidence_manifest']),10)
        self.assertEqual({e['url'] for e in result['evidence_manifest']},set(urls+[e['url'] for e in old]))
        validate_report_locally(source_report(result))


if __name__=='__main__':unittest.main()
