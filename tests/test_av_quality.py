"""QA sobre contratos y archivos realmente codificados, no sólo mocks del FFmpeg."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from tools.av_quality import inspect_metadata,inspect_scan,inspect_file,file_hash


def media():
    return {'format':{'duration':'12'},'streams':[
        {'codec_type':'video','codec_name':'h264','width':1280,'height':720,
         'pix_fmt':'yuv420p','avg_frame_rate':'24/1','start_time':'0','duration':'12'},
        {'codec_type':'audio','codec_name':'aac','sample_rate':'48000','channels':1,
         'start_time':'0','duration':'12'}]}


class MediaContractTests(unittest.TestCase):
    def test_preview_and_documentary_are_distinct(self):
        self.assertEqual(inspect_metadata(media())['failures'],[])
        self.assertIn('duration_outside_profile',inspect_metadata(media(),profile='documentary')['failures'])
        with self.assertRaises(ValueError):inspect_metadata(media(),expected_seconds=float('nan'))

    def test_missing_audio_bad_format_and_real_track_skew_block(self):
        data=media();data['streams'].pop()
        self.assertIn('exactly_one_audio_track_required',inspect_metadata(data)['failures'])
        data=media();data['streams'][1]['duration']='10'
        self.assertIn('audio_video_timing_mismatch',inspect_metadata(data)['failures'])
        for change,expected in [({'codec_name':'hevc'},'h264_video_required'),
                                ({'width':640},'resolution_or_orientation_invalid'),
                                ({'avg_frame_rate':'0/0'},'frame_rate_invalid')]:
            data=media();data['streams'][0].update(change)
            self.assertIn(expected,inspect_metadata(data)['failures'])

    def test_eof_freeze_and_silence_are_not_lost(self):
        log='freeze_start: 5\nsilence_start: 6\nblack_start:1 black_end:2 black_duration:1\nmax_volume: -inf dB\n'
        scan=inspect_scan(log,12)
        self.assertEqual(scan['freeze_intervals'][0]['duration_seconds'],7)
        self.assertEqual(scan['silence_intervals'][0]['duration_seconds'],6)
        self.assertEqual(len(scan['failures']),4)

    def test_short_pauses_and_near_full_scale_are_not_automatic_audio_repair(self):
        result=inspect_scan('silence_start: 1\nsilence_end: 1.4\nmean_volume: -12 dB\nmax_volume: 0.0 dB',12)
        self.assertEqual(result['failures'],[])
        self.assertEqual(result['warnings'],['peak_near_full_scale_requires_listening'])


@unittest.skipUnless(os.getenv('FDG_MEDIA_QA_INTEGRATION')=='1','Prueba multimedia explícita; no requiere IA')
class RealMediaQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.encoder=os.getenv('FDG_FFMPEG','ffmpeg');cls.probe=os.getenv('FDG_FFPROBE','ffprobe')
        if not shutil.which(cls.encoder) or not shutil.which(cls.probe):
            raise RuntimeError('FFmpeg/ffprobe requeridos para integración audiovisual')
        cls.folder=tempfile.TemporaryDirectory();cls.root=Path(cls.folder.name)
        cls.good=cls.root/'movimiento_con_audio.mp4'
        cls.bad=cls.root/'congelado_sin_sonido.mp4'
        cls.black=cls.root/'negro_con_audio.mp4'
        for target,video,audio in [
                (cls.good,'testsrc2=size=1280x720:rate=12','sine=frequency=523:sample_rate=48000'),
                (cls.bad,'color=c=0x7a531c:size=1280x720:rate=12','anullsrc=r=48000:cl=mono'),
                (cls.black,'color=c=black:size=1280x720:rate=12','sine=frequency=523:sample_rate=48000')]:
            subprocess.run([cls.encoder,'-v','error','-nostdin','-y','-f','lavfi','-i',video,
                '-f','lavfi','-i',audio,'-t','3','-threads','2','-c:v','libx264',
                '-preset','ultrafast','-crf','28','-pix_fmt','yuv420p','-c:a','aac',
                '-movflags','+faststart',str(target)],check=True,capture_output=True,timeout=30)

    @classmethod
    def tearDownClass(cls):cls.folder.cleanup()

    def inspect(self,path,**kwargs):
        return inspect_file(path,ffmpeg=self.encoder,ffprobe=self.probe,**kwargs)

    def test_encoded_moving_video_passes_without_approving_voice_or_rights(self):
        before=file_hash(self.good)
        report=self.inspect(self.good,expected_seconds=3)
        self.assertTrue(report['technical_gate_passed'],report)
        self.assertTrue(report['full_decode_completed'])
        for key in ('voice_identity_verified','rights_verified','factual_approval','publication_authorized'):
            self.assertIs(report[key],False)
        self.assertEqual(file_hash(self.good),before)

    def test_encoded_frozen_silent_video_is_blocked(self):
        report=self.inspect(self.bad)
        self.assertFalse(report['technical_gate_passed'])
        self.assertIn('prolonged_frozen_video',report['failures'])
        self.assertIn('prolonged_audio_silence',report['failures'])

    def test_missing_audio_and_wrong_documentary_length_are_blocked(self):
        target=self.root/'sin_audio.mp4'
        subprocess.run([self.encoder,'-v','error','-nostdin','-y','-i',str(self.good),
                        '-an','-c:v','copy',str(target)],check=True,capture_output=True,timeout=15)
        self.assertIn('exactly_one_audio_track_required',self.inspect(target)['failures'])
        self.assertIn('duration_outside_profile',self.inspect(self.good,profile='documentary')['failures'])

    def test_black_frames_and_truncated_payload_are_blocked(self):
        self.assertIn('prolonged_black_video',self.inspect(self.black)['failures'])
        target=self.root/'truncado.mp4'
        raw=self.good.read_bytes();target.write_bytes(raw[:len(raw)//2])
        report=self.inspect(target)
        self.assertFalse(report['technical_gate_passed'])
        self.assertIn('full_decode_failed',report['failures'])


if __name__=='__main__':unittest.main()
