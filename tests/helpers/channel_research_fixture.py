
import sys,json
from datetime import datetime,timezone
sys.path.insert(0,'.');sys.path.insert(0,'tests')
from test_documentary_blueprint import fixture
from test_documentary_script import narrative,ScriptTests
from tools.documentary_script import write_script
from tools.ai_research_pipeline import evidence_gaps
r,selection=fixture()
r.update(collected_on=datetime.now(timezone.utc).date().isoformat(),status='candidate_claims_generated',
 analysis_provider='gemini',source_documents=[],classification=[],missing_questions=[],preliminary_claims=[],
 ready_for_youtube=False,stages=[{'provider':'gemini','role':'analyze','status':'success'},
 {'provider':'groq','role':'review','status':'success'}])
for e in r['evidence_manifest']:
 e.update(page=None,excerpt='La Empresa analizada presentó públicamente su informe sobre las operaciones y decisiones empresariales, sujeto a revisión independiente y contraste documental.')
for review in r['reviews']:review.update(reason='Pasajes candidatos con apoyo documental suficiente para revisión.',human_verified=False)
r['source_quality']=evidence_gaps(r['evidence_manifest'],r['candidate_claims'])
s=write_script(r,selection,clients=ScriptTests().configured(),research_run_id='ai-'+'a'*28)
print(json.dumps({'research':r,'script':s},ensure_ascii=False))
