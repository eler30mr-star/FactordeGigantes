"""Integración documental con fuentes sintéticas; no certifica mercado real."""
import copy
import hashlib
import json
import unittest
from tools.market_official_evidence import collect_official_evidence,documentary_excerpts
from tools.market_primary_pages import collect_primary_pages
from tools.market_pdf_evidence import select_pdf_candidates,extract_document_evidence
from tools.market_investigator import prepare_evidence,run_investigation
from tools.qwen_research_cpu import json_payload

DAY='2026-10-22'
TEXT=('In 2024 the manufacturing company published its annual report describing '
      'acquisition operations and revenue at production sites, pending independent review.')
OTHER=('The company was founded to develop manufacturing operations; its history '
       'and investment decisions require review against independent historical records.')


def documents():
    wiki={'method':'wikimedia_wikidata_company_discovery_v1','collected_on':DAY,
          'candidates':[{'wikidata_id':'Q12345','topic':'Empresa sintética',
                         'official_website_candidate':'https://example.org/'}]}
    news={'provider':'wikidata_news_company_resolution_v1','collected_on':DAY,'candidates':[]}
    def fetch(url,**kw):
        html=(f'<p>{TEXT}</p><a href="/investors/results">Financial results</a>' if url.endswith('/')
              else f'<p>{TEXT}</p><p>{OTHER}</p><a href="/report.pdf">Annual report</a>')
        return html.encode(),url,'text/html'
    official=collect_official_evidence(wiki,news,fetcher=fetch)
    primary=collect_primary_pages(official,fetcher=fetch)
    pdf=extract_document_evidence(official,primary_pages=primary,
            fetcher=lambda *a,**k:(_ for _ in ()).throw(TimeoutError('fixture')))
    return official,primary,pdf


class RadarResearchPipeline(unittest.TestCase):
    def test_homepage_to_investors_to_observed_pdf(self):
        official,primary,pdf=documents()
        self.assertEqual(primary['usable'],1)
        candidates=select_pdf_candidates(official,primary)
        self.assertEqual(len(candidates),1)
        self.assertEqual(candidates[0]['source_page'],'https://example.org/investors/results')
        self.assertEqual(candidates[0]['document_url'],'https://example.org/report.pdf')
        self.assertEqual(pdf['attempted'],1)
        self.assertEqual(pdf['text_extracted'],0)
        self.assertEqual(pdf['documents'][0]['state'],'fetch_failed')

    def test_multiple_passages_preserve_hash_and_are_deduplicated(self):
        official,primary,pdf=documents()
        evidence=prepare_evidence(pdf,official,primary)
        self.assertEqual(len(evidence),3)  # portada + dos párrafos de inversores
        self.assertEqual(len({(e['url'],e['excerpt']) for e in evidence}),3)
        self.assertEqual({e['wikidata_id'] for e in evidence},{'Q12345'})
        investors=[e for e in evidence if e['url'].endswith('/results')]
        self.assertEqual({e['document_sha256'] for e in investors},
                         {primary['pages'][0]['content_sha256']})
        self.assertEqual(investors[1]['locator'],'Bloque web 2')

    def test_local_provider_needs_no_external_api_and_cites_existing_evidence(self):
        official,primary,pdf=documents()
        calls=[]
        def generate(prompt):
            calls.append(prompt)
            return json.dumps({'claims':[{'statement':'La empresa describe sus operaciones industriales en un informe.',
                                         'evidence_ids':['E001']}],
                               'missing_questions':['¿Qué fuente independiente corrobora las operaciones?']})
        def gemini_forbidden(*a,**kw):self.fail('No API fallback allowed')
        out=run_investigation(pdf,official_report=official,primary_pages_report=primary,
              provider='qwen_local',local_generate=generate,runner=gemini_forbidden)
        self.assertEqual(len(calls),1)
        self.assertEqual(out['status'],'candidate_claims_generated')
        self.assertEqual(out['provider'],'qwen_local')
        self.assertEqual(out['model'],'Qwen/Qwen3-0.6B')
        self.assertEqual(out['prompt_sha256'],hashlib.sha256(calls[0].encode()).hexdigest())
        self.assertFalse(out['candidate_claims'][0]['human_verified'])
        self.assertFalse(out['ready_for_script'])
        self.assertFalse(out['publication_authorized'])

    def test_no_evidence_does_not_load_local_model(self):
        official,primary,pdf=documents()
        pdf['documents']=[]
        out=run_investigation(pdf,provider='qwen_local',local_generate=lambda p:self.fail('Model loaded'))
        self.assertEqual(out['status'],'skipped_no_documentary_evidence')

    def test_local_model_cannot_invent_citation(self):
        official,primary,pdf=documents()
        with self.assertRaises(ValueError):
            run_investigation(pdf,official_report=official,provider='qwen_local',
                local_generate=lambda p:json.dumps({'claims':[{'statement':'Esta es una afirmación inventada.',
                    'evidence_ids':['E999']}],'missing_questions':[]}))

    def test_child_pdf_does_not_trust_other_entity_date_or_host(self):
        official,primary,pdf=documents()
        for field,value in [('wikidata_id','Q99999'),('origin_url','https://other.example/'),
                            ('resolved_url','https://other.example/investors')]:
            changed=copy.deepcopy(primary)
            changed['pages'][0][field]=value
            self.assertEqual(select_pdf_candidates(official,changed),[])
        changed=copy.deepcopy(primary);changed['collected_on']='2026-10-21'
        with self.assertRaises(ValueError):select_pdf_candidates(official,changed)

    def test_generic_long_text_and_promotional_banner_not_documentary(self):
        self.assertEqual(documentary_excerpts(['A generic welcome message. '*30]),[])
        self.assertEqual(documentary_excerpts(['Accept cookies to read the annual report in 2024. '*4]),[])
        self.assertEqual(len(documentary_excerpts([TEXT,TEXT,OTHER])),2)

    def test_investor_links_use_observed_label_or_ir_path(self):
        from tools.market_primary_pages import eligible_pages
        official,_,_=documents()
        for candidate in [
            {'url':'https://example.org/en/ir/'},
            {'url':'https://example.org/corporate/library',
             'category':'financial_report_link_candidate'}]:
            candidate.update(document_fetched=False,ownership_verified=False)
            official['evidence'][0]['document_link_candidates']=[candidate]
            self.assertEqual(len(eligible_pages(official)),1)

    def test_annual_pdf_preserves_total_without_extracting_every_page(self):
        from io import BytesIO
        from pypdf import PdfWriter
        from tools.pdf_sources import pdf_page_blocks
        writer=PdfWriter()
        for i in range(40):writer.add_blank_page(width=200,height=200)
        stream=BytesIO();writer.write(stream)
        with self.assertRaisesRegex(ValueError,'páginas'):
            pdf_page_blocks(stream.getvalue())
        blocks,pages,total=pdf_page_blocks(stream.getvalue(),max_pages=350,scan_pages=12)
        self.assertEqual(total,40)
        self.assertEqual(blocks,[])
        self.assertEqual(pages,[])

    def test_fallback_tries_different_discovered_hosts_and_preserves_two_batches(self):
        from tools.market_official_evidence import combine_batches
        wiki={'method':'wikimedia_wikidata_company_discovery_v1','collected_on':DAY,
              'candidates':[{'wikidata_id':f'Q{i+100}','topic':f'Empresa sintética {i}',
                  'official_website_candidate':f'https://company{i}.example.org/'} for i in range(6)]}
        news={'provider':'wikidata_news_company_resolution_v1','collected_on':DAY,'candidates':[]}
        calls=[]
        def fetch(url,**kwargs):
            calls.append(url)
            if len(calls)<=3:raise TimeoutError('fixture')
            return f'<p>{TEXT}</p>'.encode(),url,'text/html'
        first=collect_official_evidence(wiki,news,fetcher=fetch)
        second=collect_official_evidence(wiki,news,fetcher=fetch,previous_report=first)
        self.assertEqual(len(calls),6)
        self.assertEqual(len(set(calls)),6)
        self.assertEqual(second['readable'],3)
        merged=combine_batches(first,second)
        self.assertEqual(merged['attempted'],6)
        self.assertTrue(merged['local_consolidation_only'])
        def forbidden(*args,**kwargs):self.fail('No further requests')
        skipped=collect_official_evidence(wiki,news,fetcher=forbidden,previous_report=second)
        self.assertEqual(skipped['skip_reason'],'initial_context_available')

    def test_fallback_never_revisits_a_shared_company_website(self):
        from tools.market_official_evidence import candidates_from_reports
        wiki={'method':'wikimedia_wikidata_company_discovery_v1','collected_on':DAY,
              'candidates':[{'wikidata_id':f'Q{i+100}','topic':f'Empresa sintética {i}',
                  'official_website_candidate':'https://same.example.org/'} for i in range(5)]}
        news={'provider':'wikidata_news_company_resolution_v1','collected_on':DAY,'candidates':[]}
        self.assertEqual(len(candidates_from_reports(wiki,news)),1)
        self.assertEqual(candidates_from_reports(wiki,news,exclude_hosts={'same.example.org'}),[])

    def test_json_cleanup_accepts_one_fence_but_rejects_prose_and_thought(self):
        obj={'claims':[],'missing_questions':[]}
        self.assertEqual(json.loads(json_payload('```json\n'+json.dumps(obj)+'\n```')),obj)
        for text in ['Intro '+json.dumps(obj),'<think>reason</think>'+json.dumps(obj),'[]']:
            with self.assertRaises(ValueError):json_payload(text)

    def test_provider_cannot_replace_source_manifest(self):
        official,primary,pdf=documents()
        def malicious(*a,**kw):
            return {'provider':'gemini_free','evidence_manifest':[],
                    'facts_verified_automatically':0,'ready_for_script':False,
                    'ready_for_youtube':False}
        out=run_investigation(pdf,official_report=official,runner=malicious,
                             api_key='x'*20,free_confirmed=True)
        self.assertTrue(out['evidence_manifest'])

    def test_market_choice_is_not_replaced_by_another_company_with_more_text(self):
        official,primary,pdf=documents()
        def no_model(prompt):self.fail('Selected company has no evidence')
        out=run_investigation(pdf,official_report=official,primary_pages_report=primary,
              provider='qwen_local',local_generate=no_model,selected_qid='Q99999')
        self.assertEqual(out['status'],'skipped_no_documentary_evidence')
        self.assertEqual(out['requested_wikidata_id'],'Q99999')
        self.assertEqual(out['evidence_manifest'],[])
        self.assertEqual(out['deferred_wikidata_ids'],['Q12345'])


if __name__=='__main__':unittest.main()
