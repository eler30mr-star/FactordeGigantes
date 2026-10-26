"""Production and CI must not reintroduce the retired company collectors."""
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]


def jobs(text):
    return set(re.findall(r'^  ([a-z][a-z0-9-]*):$',text.split('jobs:\n',1)[1],re.M))


class ChannelWorkflowPolicyTests(unittest.TestCase):
    def test_daily_workflow_studies_youtube_and_only_processes_a_selected_episode(self):
        workflow=(ROOT/'.github/workflows/topic-discovery-smoke.yml').read_text()
        self.assertEqual(jobs(workflow),{'final-market-acceptance','chosen-episode','youtube-opportunity-study','search-provider-profile'})
        self.assertEqual(re.findall(r"cron: '([^']+)'",workflow),['17 10 * * *'])
        self.assertIn('options: [opportunity, episode, acceptance, profile]',workflow)
        self.assertIn('default: opportunity',workflow)
        self.assertIn('python -m tools.youtube_opportunity_study',workflow)
        self.assertIn('python -m tools.channel_episode',workflow)
        for retired in ('tools.topic_discovery','tools.news_discovery','tools.market_official_evidence',
                        'tools.market_pdf_evidence','tools.ai_research_pipeline','tools.review_research',
                        'tools.corroborate_research','tools.documentary_script','research_run_id:'):
            self.assertNotIn(retired,workflow)

    def test_ci_cannot_dispatch_provider_runs_or_development_episodes_from_commit_markers(self):
        workflow=(ROOT/'.github/workflows/check.yml').read_text()
        self.assertEqual(jobs(workflow),{'checks','audiovisual-quality','production-smoke'})
        for retired in ('gh workflow run','actions: write','run_radar:','run_script:',
                        'GEMINI_API_KEY','TAVILY_API_KEY'):
            self.assertNotIn(retired,workflow)

    def test_provider_workflow_keeps_the_operational_pause_and_main_branch_guards(self):
        workflow=(ROOT/'.github/workflows/topic-discovery-smoke.yml').read_text()
        blocks=re.split(r'(?=^  [a-z][a-z0-9-]*:\n)',workflow.split('jobs:\n',1)[1],flags=re.M)
        for block in blocks:
            if not block.strip() or block.startswith('  final-market-acceptance:'):continue
            conditions=block.split('runs-on:',1)[0]
            self.assertIn("vars.FINAL_AI_INTEGRATION_ENABLED == '1'",conditions)
            self.assertIn("github.ref == 'refs/heads/main'",conditions)


if __name__=='__main__':unittest.main()
