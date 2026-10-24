"""El apoyo del revisor amplía citas candidatas, nunca verifica hechos."""
import copy
from datetime import datetime, timezone
import json
import unittest

from test_ai_research_team import sources, candidate, configured, TEXT
from tools.ai_clients import FreeClients
from tools.ai_research_pipeline import analyze_sources, parse_review, assign_reviewed_support, validate_report_locally


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
            lambda r:r['source_assessments'][1].update(assessment='contradicted_by_excerpt'),
        ):
            row=review();mutate(row)
            with self.assertRaises(ValueError):
                parse_review(json.dumps({'reviews':[row]}),context()['evidence_manifest'],self.claims())

    def test_assignment_preserves_input_and_never_rewrites_statement(self):
        claims=self.claims();original=copy.deepcopy(claims)
        parsed=parse_review(json.dumps({'reviews':[review()]}),context()['evidence_manifest'],claims)
        result=assign_reviewed_support(claims,parsed)
        self.assertEqual(claims,original)
        self.assertEqual(result[0]['statement'],claims[0]['statement'])


if __name__=='__main__':unittest.main()
