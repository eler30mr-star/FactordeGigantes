import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test_ai_research_team import candidate, configured
from test_review_support_assignment import context
from tools.ai_clients import FreeClients, ProviderError
from tools.ai_research_pipeline import analyze_sources, evidence_gaps, validate_report_locally
from tools.corroborate_research import continuation_selection, merge_passages, continue_corroboration, main
from tools.review_candidates import METHOD
from tools.review_research import review_existing

RUN = 'ai-'+'a'*28


def research():
    return analyze_sources(context(), clients=FreeClients(env={}, reserve=lambda *_:False),
                           local_generate=lambda _:candidate())


def discovered():
    e=copy.deepcopy(context()['evidence_manifest'][1])
    e.update(id='E001',url='https://fresh.example/independent-study',document_sha256='c'*64,
             excerpt=e['excerpt']+' La publicación conserva atribuciones y contexto.')
    return {'evidence_manifest':[e], 'source_documents':[{
        'url':e['url'],'resolved_url':e['url'],'status':'text_extracted','sha256':e['document_sha256']}],
        'stages':[{'provider':'tavily','role':'discover','status':'success'}],
        'discovery_plan':[], 'research_targets':[], 'retrieval_budget':{
            'max_documents':8,'attempted':1,'attempted_urls':[e['url']],
            'documents_with_relevant_text':1,'independent_domains_with_text':1,
            'public_authority_domains_with_text':0,'new_fragments':1,
            'budget_exhausted':False,'citation_scanned_urls':[]}}


class CorroborationTests(unittest.TestCase):
    def test_continuation_covers_three_pending_claims_and_rotates_without_rewriting_them(self):
        old=research()
        old['candidate_claims']=[{**copy.deepcopy(old['candidate_claims'][0]),
            'statement':f'Empresa Ejemplo anunció el cambio empresarial número {n} con fuentes pendientes.'} for n in range(6)]
        old['source_quality']=evidence_gaps(old['evidence_manifest'],old['candidate_claims'])
        before=copy.deepcopy(old)
        selection,progress=continuation_selection(old)
        self.assertEqual(progress['target_claim_indices'],[1,2,3])
        self.assertEqual(len(selection['prior_research_targets']),3)
        self.assertEqual(old,before)
        old['corroboration_continuation']={**progress,'visited_target_indices':progress['target_claim_indices']}
        self.assertEqual(continuation_selection(old)[1]['target_claim_indices'],[4,5,6])

    def client(self, calls, *, allowed=True, insufficient=False):
        def transport(url,body,headers):
            self.assertIn('api.groq.com',url)
            calls.append(url)
            data=json.loads(body['messages'][-1]['content'].split('\n')[-1])
            rows=[]
            for task in data['tasks']:
                refs=task['inspect_evidence_ids']
                assessments=[{'evidence_id':key,'assessment':
                    'insufficient_context' if insufficient and key==refs[-1] else 'supported_by_excerpt',
                    'reason':'El pasaje exige contraste documental independiente.'} for key in refs]
                rows.append({'claim_index':task['claim_index'],'assessment':'supported_by_excerpt',
                    'evidence_ids':[r['evidence_id'] for r in assessments if r['assessment']=='supported_by_excerpt'],
                    'reason':'Apoyo candidato; ninguna verificación humana.', 'source_assessments':assessments})
            return {'choices':[{'message':{'content':json.dumps({'reviews':rows})}}]}
        return FreeClients(env=configured('groq'),reserve=lambda *_:allowed,transport=transport)

    def test_new_sources_are_saved_when_quota_denied_and_review_resumes_without_downloads(self):
        old=research();before=copy.deepcopy(old);calls=[]
        result=continue_corroboration(old,source_run_id=RUN,clients=self.client(calls,allowed=False),
                                     discover=lambda *a,**k:discovered())
        self.assertEqual(result['status'],'sources_saved_pending_review')
        self.assertEqual(result['review_inference_calls'],0)
        self.assertEqual(calls,[])
        self.assertEqual(old,before)
        report=result['report']
        self.assertEqual(report['corroboration_continuation']['review_pending_reason'],'budget_denied')
        self.assertEqual(report['candidate_claims'][0]['evidence_ids'],['E001'])
        self.assertEqual(report['reviews'],[])
        retry=continue_corroboration(report,source_run_id=RUN,clients=self.client([]),
                                    discover=lambda *a,**k:self.fail('No descartar ni volver a buscar antes de revisión'))
        self.assertEqual(retry['status'],'awaiting_saved_passage_review')
        self.assertEqual(report['corroboration_continuation']['source_run_id'],RUN)
        resumed=review_existing(report,clients=self.client(calls),source_run_id=RUN)
        self.assertEqual(resumed['status'],'review_completed_candidate_only')
        self.assertEqual(resumed['source_downloads'],0)
        self.assertEqual(len(calls),1)
        validate_report_locally(resumed['report'])

    def test_only_review_can_add_support_and_partial_passages_remain_outside_active_citations(self):
        calls=[];client=self.client(calls,insufficient=True)
        result=continue_corroboration(research(),source_run_id=RUN,clients=client,
                                     discover=lambda *a,**k:discovered())
        self.assertEqual(result['status'],'review_completed_candidate_only')
        self.assertEqual(len(calls),1)
        self.assertEqual(client.calls['gemini'],0)
        self.assertEqual(client.calls['groq'],1)
        report=result['report']
        self.assertEqual(report['support_review_method'],METHOD)
        self.assertFalse(report['publication_authorized'])
        self.assertFalse(report['ready_for_script'])
        self.assertFalse(report['candidate_claims'][0]['human_verified'])
        self.assertNotIn(report['reviews'][0]['source_assessments'][-1]['evidence_id'],
                         report['candidate_claims'][0]['evidence_ids'])
        validate_report_locally(report)

    def test_unchanged_passages_never_call_reviewer_but_preserve_failed_attempt_history(self):
        found=discovered();found['evidence_manifest']=[]
        found['source_documents'][0]['status']='no_relevant_passages'
        found['retrieval_budget'].update(documents_with_relevant_text=0,independent_domains_with_text=0,new_fragments=0)
        client=FreeClients(env=configured('groq'),reserve=lambda *_:self.fail('No reservar sin novedades'))
        result=continue_corroboration(research(),source_run_id=RUN,clients=client,
                                     discover=lambda *a,**k:found)
        self.assertEqual(result['status'],'no_new_passages')
        self.assertIn(found['source_documents'][0]['url'],result['report']['corroboration_continuation']['attempted_urls'])
        validate_report_locally(result['report'])

    def test_merge_preserves_every_active_reference_and_avoids_relabeling_old_matrix(self):
        old=research();old['candidate_claims'][0]['evidence_ids']=['E002']
        old['candidate_claims'][0]['analysis_evidence_ids']=['E001','E002']
        old['candidate_claims'][0]['removed_support_evidence_ids']=['E001']
        evidence,claims,count=merge_passages(old,discovered())
        self.assertEqual(count,1)
        self.assertEqual(evidence[0]['url'],old['evidence_manifest'][1]['url'])
        self.assertEqual(claims[0]['evidence_ids'],['E001'])
        self.assertNotIn('analysis_evidence_ids',claims[0])
        self.assertEqual(old['candidate_claims'][0]['evidence_ids'],['E002'])
        duplicate=discovered();duplicate['evidence_manifest']=[{
            **old['evidence_manifest'][0],'document_sha256':'f'*64}]
        self.assertEqual(merge_passages(old,duplicate)[2],0)

    def test_next_run_rotates_target_and_capacity_gate_prevents_pointless_spending(self):
        old=research();old['candidate_claims']*=2
        old['candidate_claims'][1]=copy.deepcopy(old['candidate_claims'][1])
        old['candidate_claims'][1]['statement']='Otra afirmación específica de Empresa Ejemplo pendiente de contraste.'
        old['source_quality']=evidence_gaps(old['evidence_manifest'],old['candidate_claims'])
        selection,progress=continuation_selection(old)
        first=progress['target_claim_index']
        old['corroboration_continuation']={**progress,'visited_target_indices':[first]}
        self.assertNotEqual(continuation_selection(old)[1]['target_claim_index'],first)
        evidence=old['evidence_manifest'][0]
        old['evidence_manifest']=[{**evidence,'id':f'E{n:03d}', 'url':f'https://www.justice.gov/example/{n}'} for n in range(1,11)]
        old['candidate_claims'][0]['evidence_ids']=[f'E{n:03d}' for n in range(1,9)]
        old['candidate_claims'][1]['evidence_ids']=['E009','E010']
        old['source_quality']=evidence_gaps(old['evidence_manifest'],old['candidate_claims'])
        result=continue_corroboration(old,source_run_id=RUN,clients=self.client([]),
                                     discover=lambda *a,**k:self.fail('No buscar con capacidad llena'))
        self.assertEqual(result['status'],'blocked_evidence_capacity')

    def test_old_navigation_scan_can_be_reopened_once_and_new_scan_is_reused(self):
        from tools.ai_source_discovery import CITATION_SCAN_METHOD
        old=research();url=old['evidence_manifest'][0]['url']
        old['retrieval_budget']={'citation_scanned_urls':[url]}
        self.assertIn(url,continuation_selection(old)[0]['citation_expansion_urls'])
        old['retrieval_budget']['citation_scan_method']=CITATION_SCAN_METHOD
        self.assertNotIn(url,continuation_selection(old)[0]['citation_expansion_urls'])

    def test_cli_saves_new_sources_before_network_persistence_and_respects_human_review(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'contrast.json'
            ctx={'ok':True,'run_id':RUN,'research':research(),'selection':{'research_queue':{'state':'awaiting_sources'}}}
            with patch('sys.argv',['contrast','--out',str(output)]), \
                 patch('tools.corroborate_research.ControlClient') as control, \
                 patch('tools.corroborate_research.FreeClients',return_value=self.client([],allowed=False)), \
                 patch('tools.corroborate_research.discover_sources',return_value=discovered()):
                control.return_value.script_context.return_value=ctx
                control.return_value.persist.side_effect=ProviderError('persistence_unconfirmed')
                # Default callable is captured by Python; explicitly wrap for test isolation.
                from tools.corroborate_research import continue_corroboration as actual
                with patch('tools.corroborate_research.continue_corroboration',
                           side_effect=lambda r,**kw:actual(r,**kw,discover=lambda *a,**k:discovered())):
                    with self.assertRaises(ProviderError):main()
                self.assertEqual(json.loads(output.read_text())['status'],'sources_saved_pending_review')
                self.assertNotIn('receipt',json.loads(output.read_text()))
                ctx['selection']['research_queue']['state']='review'
                control.return_value.persist.reset_mock()
                main()
                control.return_value.persist.assert_not_called()
                self.assertEqual(json.loads(output.read_text())['status'],'skipped_no_research_work')

