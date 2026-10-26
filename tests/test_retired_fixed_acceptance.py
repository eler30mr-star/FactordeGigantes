"""A fixed company must not consume live providers as a stand-in for selection."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools import final_directed_acceptance as legacy


class RetiredFixedAcceptanceTests(unittest.TestCase):
    def test_even_old_confirmation_cannot_create_a_test_episode_or_call_providers(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'unexpected-output'
            with patch.dict(os.environ,{'CONFIRM_FINAL_ACCEPTANCE':'true','RESUME_DIRECTED_RUN':'40308206020'}), \
                 patch.object(legacy,'FOLDER',output), \
                 patch.object(legacy,'store',side_effect=AssertionError('No crear una selección ficticia')), \
                 patch('tools.ai_clients.FreeClients.generate',side_effect=AssertionError('No consumir IA')), \
                 patch('tools.ai_clients.FreeClients.search',side_effect=AssertionError('No consumir búsquedas')):
                with self.assertRaisesRegex(SystemExit,'Prueba fija de BlackBerry retirada'):
                    legacy.main()
            self.assertFalse(output.exists())

    def test_workflow_has_only_the_real_selected_episode_research_entry(self):
        root=Path(__file__).resolve().parents[1]
        workflow=(root/'.github/workflows/topic-discovery-smoke.yml').read_text()
        self.assertNotIn('episode-acceptance',workflow)
        self.assertNotIn('resume_directed_run:',workflow)
        self.assertNotIn('final-directed-acceptance:',workflow)
        self.assertNotIn('python -m tools.final_directed_acceptance',workflow)
        self.assertIn("inputs.phase == 'episode'",workflow)
        self.assertIn('python -m tools.channel_episode',workflow)


if __name__=='__main__':unittest.main()
