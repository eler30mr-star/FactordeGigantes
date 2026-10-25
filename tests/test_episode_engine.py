import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import wave

from tools.episode_package import validate_episode,voice_plan,from_autonomous
from tools.episode_voice import generate_voice,collect_voice
from tools.episode_render import frame,render_episode
from tools.approved_voice import SHA,approved_reference,hash_file

FIXTURE=Path(__file__).resolve().parents[1]/'research/theranos-development/EPISODIO_DESARROLLO.json'


def episode():return json.loads(FIXTURE.read_text(encoding='utf-8'))


class TestEngine:
    kind='test_double'
    def __init__(self):self.calls=[]
    def generate(self,task,path,reference,metadata):
        self.calls.append(task['id'])
        with wave.open(str(path),'wb') as writer:
            writer.setparams((1,2,48000,0,'NONE','not compressed'))
            writer.writeframes(b'\x01\x00'*12_000)


class EpisodeEngineTests(unittest.TestCase):
    def test_directly_researched_fixture_and_every_character_reach_voice_plan(self):
        data=episode();summary=validate_episode(data);plan=voice_plan(data)
        self.assertEqual(summary['scene_count'],8)
        self.assertGreaterEqual(summary['narration_words'],1104)
        self.assertTrue(480<=summary['estimated_seconds']<=840)
        self.assertEqual(data['origin'],'codex_development_research')
        self.assertEqual(plan['canonical_voice_sha256'],SHA)
        for scene in data['scenes']:
            for number,p in enumerate(scene['paragraphs'],1):
                tasks=[t for t in plan['tasks'] if t['scene_id']==scene['id'] and t['paragraph_index']==number]
                self.assertEqual(''.join(t['text'] for t in tasks),p['text'])
                for task in tasks:
                    self.assertEqual(task['source_ids'],p['source_ids'])
                    self.assertEqual(task['text_sha256'],hashlib.sha256(task['text'].encode()).hexdigest())

    def test_invalid_sources_permissions_voice_identity_or_graph_values_block_production(self):
        for change in (lambda p:p.update(publication_authorized=True),
                       lambda p:p.update(canonical_voice_sha256='f'*64),
                       lambda p:p['scenes'][0]['paragraphs'][0].update(source_ids=['S99']),
                       lambda p:p['sources'][0].update(url='https://127.0.0.1/private'),
                       lambda p:p['scenes'][-1]['visual']['items'][0].update(value=float('nan')),
                       lambda p:p.update(scenes=p['scenes'][:1])):
            data=episode();change(data)
            with self.assertRaises(ValueError):voice_plan(data)

    def test_takes_resume_without_loading_models_and_corruption_regenerates_only_one(self):
        data=episode();engine=TestEngine();reference,_=approved_reference()
        with tempfile.TemporaryDirectory() as folder:
            a=generate_voice(data,folder,scene='SC01',max_new_takes=2,engine=engine)
            self.assertFalse(a['complete']);self.assertEqual(a['generated_now'],2)
            b=generate_voice(data,folder,scene='SC01',engine=engine)
            self.assertTrue(b['complete']);self.assertEqual(b['reused_now'],2)
            calls=len(engine.calls)
            c=generate_voice(data,folder,scene='SC01',engine=engine)
            self.assertEqual(c['generated_now'],0);self.assertEqual(len(engine.calls),calls)
            target=Path(folder)/c['takes'][0]['relative_file'];target.write_bytes(b'corrupted')
            d=generate_voice(data,folder,scene='SC01',engine=engine)
            self.assertEqual(d['generated_now'],1);self.assertEqual(len(engine.calls),calls+1)
            self.assertFalse(d['voice_identity_verified']);self.assertFalse(d['publication_authorized'])
            with self.assertRaises(ValueError):collect_voice(data,folder)
        self.assertEqual(hash_file(reference),SHA)

    def test_providers_are_never_loaded_without_final_test_switch(self):
        with tempfile.TemporaryDirectory() as folder, \
                patch('tools.episode_voice.QwenCanonicalEngine',side_effect=AssertionError('No cargar modelo')):
            with self.assertRaisesRegex(ValueError,'final-ai-test'):
                generate_voice(episode(),folder,scene='SC01')

    def test_visual_types_have_motion_and_distinct_scene_data(self):
        data=episode();seen=set()
        for scene in data['scenes']:
            a=frame(data,scene,1,1,.1,'Texto de prueba',technical=True)
            b=frame(data,scene,2,2,.2,'Texto de prueba',technical=True)
            self.assertEqual(a.size,(1280,720));self.assertNotEqual(a.tobytes(),b.tobytes())
            seen.add(scene['visual']['kind'])
        self.assertGreaterEqual(len(seen),5)

    def test_existing_autonomous_contract_uses_same_generic_production_engine(self):
        from test_documentary_blueprint import fixture
        from test_documentary_script import ScriptTests
        from tools.documentary_script import write_script
        research,selection=fixture()
        draft=write_script(research,selection,clients=ScriptTests().configured())
        converted=from_autonomous(draft,research)
        self.assertEqual(converted['origin'],'autonomous_script')
        self.assertEqual(validate_episode(converted)['narration_words'],1200)
        broken=copy.deepcopy(draft);broken['source_evidence_sha256']='0'*64
        with self.assertRaises(ValueError):from_autonomous(broken,research)

    @unittest.skipUnless(os.getenv('FDG_MEDIA_QA_INTEGRATION')=='1','Exportación FFmpeg explícita, sin proveedores')
    def test_real_mp4_subtitles_and_review_page_keep_signal_distinct_from_narration(self):
        with tempfile.TemporaryDirectory() as folder:
            report=render_episode(episode(),folder,technical_test=True,sample_seconds=4)
            self.assertTrue(report['technical_gate_passed'])
            self.assertFalse(report['contains_narration'])
            self.assertEqual(report['generated_voice_takes'],0)
            self.assertEqual(report['voice_kind'],'technical_test_signal')
            self.assertFalse(report['publication_authorized'])
            self.assertEqual(len(report['chapters']),8)
            path=Path(folder)
            self.assertTrue((path/'EPISODIO_PARA_REVISION.mp4').is_file())
            self.assertIn('no contiene locución',(path/'REVISAR.html').read_text())
            self.assertIn('-->',(path/'SUBTITULOS.srt').read_text())
            vtt=(path/'SUBTITULOS.vtt').read_text()
            self.assertTrue(vtt.startswith('WEBVTT'))
            self.assertIn('En dos mil tres,',vtt)
