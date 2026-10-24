"""El apoyo del revisor amplía citas candidatas, nunca verifica hechos."""
import copy
from datetime import datetime, timezone
import json
import unittest

from test_ai_research_team import sources, candidate, configured, TEXT
from tools.ai_clients import FreeClients
from tools.ai_research_pipeline import analyze_sources, parse_review, assign_reviewed_support, validate_report_locally
from tools.review_candidates import review_tasks


def context():
    result=sources()
    result['collected_on']=datetime.now(timezone.utc).date().isoformat()
    result['evidence_manifest'].append({**result['evidence_manifest'][0], 'id':'E002',
        'url':'https://reporter.example/company-report', 'document_sha256':'b'*64,
        'source_class':'public_document_candidate'})
    return result


def review(*, assessment='supported_by_excerpt', ids=('E001','E002')):
    return {'claim_index':1,'assessment':assessment,'evidence_ids':list(ids),
            'reason':'Los pasajes deben contrastarse antes de aprobar hechos.',
            'source_assessments':[{'evidence_id':ref,'assessment':assessment,
                'reason':'El pasaje describe el mismo hecho y conserva su contexto.'} for ref in ids]}


class SupportAssignmentTests(unittest.TestCase):
    def test_reviewer_cannot_omit_selected_independent_comparison(self):
        evidence=context()['evidence_manifest']
        row=review(ids=('E001',))
        with self.assertRaises(ValueError):
            parse_review(json.dumps({'reviews':[row]}),evidence,self.claims(),
                         expected_tasks=review_tasks(evidence,self.claims()))

    def test_insufficient_alternative_is_evaluated_but_never_added_as_support(self):
        evidence=context()['evidence_manifest']
        evidence.append({**evidence[1],'id':'E003','url':'https://other.example/unrelated',
                         'document_sha256':'c'*64})
        row=review()
        row['source_assessments'].append({'evidence_id':'E003','assessment':'insufficient_context',
                                         'reason':'No describe el hecho completo.'})
        parsed=parse_review(json.dumps({'reviews':[row]}),evidence,self.claims(),
                            expected_tasks=review_tasks(evidence,self.claims()))
        self.assertEqual(assign_reviewed_support(self.claims(),parsed)[0]['evidence_ids'],['E001','E002'])

    def test_comparison_candidates_remain_bounded_when_original_has_eight_citations(self):
        evidence=[{**context()['evidence_manifest'][0],'id':f'E{i:03d}',
                   'url':f'https://source{i}.example/report','document_sha256':str(i)*64} for i in range(1,10)]
        claim={**self.claims()[0],'evidence_ids':[e['id'] for e in evidence[:8]]}
        self.assertEqual(review_tasks(evidence,[claim])[0]['inspect_evidence_ids'],claim['evidence_ids'])

    def claims(self):
        return [{'statement':TEXT,'evidence_ids':['E001'],'status':'candidate_unverified','human_verified':False}]

    def test_complete_pipeline_reuses_reviewed_support_and_passes_real_worker_contract(self):
        calls=[];reservations=[]
        def transport(url,body,headers):
            calls.append(url)
            if 'googleapis' in url:
                return {'candidates':[{'content':{'parts':[{'text':candidate()}]}}]}
            self.assertEqual(body['max_completion_tokens'],3200)
            return {'choices':[{'message':{'content':json.dumps({'reviews':[review()]})}}]}
        clients=FreeClients(env=configured('gemini','groq'),
            reserve=lambda p,r:reservations.append((p,r)) or True,transport=transport)
        report=analyze_sources(context(),clients=clients,local_generate=lambda _:candidate())
        self.assertEqual(len(calls),2)
        self.assertEqual(reservations,[('gemini','analyze'),('groq','review')])
        claim=report['candidate_claims'][0]
        self.assertEqual(claim['analysis_evidence_ids'],['E001'])
        self.assertEqual(claim['evidence_ids'],['E001','E002'])
        self.assertEqual(report['source_quality']['claim_gaps'][0]['gaps'],[])
        self.assertFalse(claim['human_verified'])
        self.assertFalse(report['source_quality']['all_claims_verified'])
        self.assertFalse(report['ready_for_script'])
        self.assertFalse(report['publication_authorized'])
        validate_report_locally(report)

    def test_legacy_review_without_per_quote_assessment_cannot_expand_claim(self):
        row=review();del row['source_assessments']
        parsed=parse_review(json.dumps({'reviews':[row]}),context()['evidence_manifest'],self.claims())
        self.assertEqual(assign_reviewed_support(self.claims(),parsed)[0]['evidence_ids'],['E001'])

    def test_contradiction_or_insufficient_context_never_expands_citations(self):
        for assessment in ('contradicted_by_excerpt','insufficient_context'):
            parsed=parse_review(json.dumps({'reviews':[review(assessment=assessment)]}),
                context()['evidence_manifest'],self.claims())
            self.assertEqual(assign_reviewed_support(self.claims(),parsed)[0]['evidence_ids'],['E001'])

    def test_missing_original_support_is_not_silently_replaced(self):
        parsed=parse_review(json.dumps({'reviews':[review(ids=('E002',))]}),
            context()['evidence_manifest'],self.claims())
        self.assertEqual(assign_reviewed_support(self.claims(),parsed)[0]['evidence_ids'],['E001'])

    def test_invalid_matrix_missing_invented_duplicate_or_self_verified_is_rejected(self):
        for mutate in (
            lambda r:r['source_assessments'].pop(),
            lambda r:r['source_assessments'][1].update(evidence_id='E999'),
            lambda r:r['source_assessments'][1].update(evidence_id='E001'),
            lambda r:r['source_assessments'][1].update(human_verified=True),
        ):
            row=review();mutate(row)
            with self.assertRaises(ValueError):
                parse_review(json.dumps({'reviews':[row]}),context()['evidence_manifest'],self.claims())

    def test_positive_summary_cannot_override_a_contradictory_passage(self):
        row=review();row['source_assessments'][1]['assessment']='contradicted_by_excerpt'
        parsed=parse_review(json.dumps({'reviews':[row]}),context()['evidence_manifest'],self.claims())
        self.assertEqual(parsed[0]['assessment'],'contradicted_by_excerpt')
        self.assertEqual(assign_reviewed_support(self.claims(),parsed)[0]['evidence_ids'],['E001'])

    def test_unclear_passage_is_removed_from_support_ids_without_erasing_assessment(self):
        row=review();row['source_assessments'][1]['assessment']='insufficient_context'
        parsed=parse_review(json.dumps({'reviews':[row]}),context()['evidence_manifest'],self.claims())
        self.assertEqual(parsed[0]['evidence_ids'],['E001'])
        self.assertEqual(len(parsed[0]['source_assessments']),2)
        self.assertEqual(assign_reviewed_support(self.claims(),parsed)[0]['evidence_ids'],['E001'])

    def test_assignment_preserves_input_and_never_rewrites_statement(self):
        claims=self.claims();original=copy.deepcopy(claims)
        parsed=parse_review(json.dumps({'reviews':[review()]}),context()['evidence_manifest'],claims)
        result=assign_reviewed_support(claims,parsed)
        self.assertEqual(claims,original)
        self.assertEqual(result[0]['statement'],claims[0]['statement'])


if __name__=='__main__':unittest.main()
