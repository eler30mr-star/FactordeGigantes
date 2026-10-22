"""QA técnico del archivo audiovisual real de Factor de Gigantes.

Sólo lee medios locales. No corrige audio, no sustituye voz, no acredita
veracidad/licencias y nunca concede aprobación editorial o publicación.
Filtros: https://ffmpeg.org/ffmpeg-filters.html
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess


def number(value):
    try:
        result=float(value)
    except (ValueError,TypeError):
        return None
    return result if math.isfinite(result) else None


def file_hash(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda:source.read(1024*1024),b''):
            digest.update(block)
    return digest.hexdigest()


def inspect_metadata(data,*,profile='preview',expected_seconds=None):
    if not isinstance(data,dict) or not isinstance(data.get('format'),dict):
        raise ValueError('Inspección del contenedor inválida')
    if profile not in ('preview','documentary','short'):
        raise ValueError('Perfil audiovisual inválido')
    if expected_seconds is not None and (type(expected_seconds) not in (int,float) or
            not math.isfinite(expected_seconds) or not 0<expected_seconds<=900):
        raise ValueError('Duración esperada inválida')
    streams=data.get('streams',[]) if isinstance(data,dict) else []
    if not isinstance(streams,list) or any(not isinstance(s,dict) for s in streams):
        raise ValueError('Inspección de pistas inválida')
    videos=[s for s in streams if s.get('codec_type')=='video']
    audios=[s for s in streams if s.get('codec_type')=='audio']
    duration=number((data.get('format') or {}).get('duration'))
    failures=[]
    if len(videos)!=1:failures.append('exactly_one_video_track_required')
    if len(audios)!=1:failures.append('exactly_one_audio_track_required')
    minimum,maximum={'preview':(.5,900),'documentary':(480,840),'short':(.5,180)}[profile]
    if duration is None or not minimum<=duration<=maximum:failures.append('duration_outside_profile')
    if expected_seconds is not None and (duration is None or abs(duration-expected_seconds)>.25):
        failures.append('duration_does_not_match_expected')
    video=videos[0] if len(videos)==1 else {}
    audio=audios[0] if len(audios)==1 else {}
    if video:
        if video.get('codec_name')!='h264':failures.append('h264_video_required')
        if video.get('pix_fmt')!='yuv420p':failures.append('yuv420p_required')
        width,height=number(video.get('width')),number(video.get('height'))
        if width is None or height is None or (
                (width<720 or height<1280 or width>=height) if profile=='short'
                else (width<1280 or height<720 or width<=height)):
            failures.append('resolution_or_orientation_invalid')
        try:
            numerator,denominator=video.get('avg_frame_rate','').split('/')
            fps=float(numerator)/float(denominator)
        except (ValueError,ZeroDivisionError,AttributeError):fps=0
        if not math.isfinite(fps) or not 12<=fps<=60:failures.append('frame_rate_invalid')
    if audio:
        if audio.get('codec_name')!='aac':failures.append('aac_audio_required')
        if number(audio.get('sample_rate')) not in (44100,48000):failures.append('audio_sample_rate_invalid')
        if number(audio.get('channels')) not in (1,2):failures.append('audio_channels_invalid')
    if video and audio:
        spans=[]
        for stream in (video,audio):
            start=number(stream.get('start_time'))
            length=number(stream.get('duration'))
            if start is None or length is None or length<=0:
                failures.append('stream_timing_unavailable');break
            spans.append((start,start+length))
        if len(spans)==2 and (abs(spans[0][0]-spans[1][0])>.15 or abs(spans[0][1]-spans[1][1])>.3):
            failures.append('audio_video_timing_mismatch')
    return {'duration_seconds':duration,'profile':profile,'failures':failures,
            'video':{k:video.get(k) for k in ('codec_name','width','height','pix_fmt','avg_frame_rate')},
            'audio':{k:audio.get(k) for k in ('codec_name','sample_rate','channels')}}


def scan_intervals(log,kind,duration):
    """Emparejar eventos, incluyendo congelamiento/silencio abiertos al EOF."""
    prefix={'freeze':'freeze','silence':'silence'}[kind]
    events=re.findall(r'\b'+prefix+r'_(start|end):\s*([0-9]+(?:\.[0-9]+)?)',log)
    pending=None;intervals=[]
    for action,value in events:
        value=min(duration,float(value))
        if action=='start':
            if pending is None:pending=value
        elif pending is not None:
            if value>pending:intervals.append({'start_seconds':pending,'end_seconds':value,'duration_seconds':round(value-pending,3)})
            pending=None
    if pending is not None and duration>pending:
        intervals.append({'start_seconds':pending,'end_seconds':duration,'duration_seconds':round(duration-pending,3)})
    return intervals


def inspect_scan(log,duration):
    freeze=scan_intervals(log,'freeze',duration)
    silence=scan_intervals(log,'silence',duration)
    black=[{'start_seconds':float(a),'end_seconds':float(b),'duration_seconds':float(c)}
           for a,b,c in re.findall(r'black_start:([0-9.]+)\s+black_end:([0-9.]+)\s+black_duration:([0-9.]+)',log)]
    failures=[]
    if any(x['duration_seconds']>=2 for x in freeze):failures.append('prolonged_frozen_video')
    if any(x['duration_seconds']>=2 for x in silence):failures.append('prolonged_audio_silence')
    if any(x['duration_seconds']>=.8 for x in black):failures.append('prolonged_black_video')
    levels={}
    for label in ('mean_volume','max_volume'):
        matches=re.findall(r'\b'+label+r':\s*(-?inf|[-+0-9.]+) dB',log)
        levels[label+'_dbfs']=number(matches[-1]) if matches else None
    if levels['max_volume_dbfs'] is None or levels['max_volume_dbfs']<-45:
        failures.append('audible_audio_not_detected')
    warnings=['peak_near_full_scale_requires_listening'] if levels['max_volume_dbfs'] is not None and levels['max_volume_dbfs']>=-.1 else []
    return {'failures':failures,'warnings':warnings,'freeze_intervals':freeze,
            'silence_intervals':silence,'black_intervals':black,'audio_levels':levels}


def inspect_file(source,*,profile='preview',expected_seconds=None,ffmpeg='ffmpeg',ffprobe='ffprobe'):
    path=Path(source).resolve()
    if not path.is_file() or not 0<path.stat().st_size<=4_000_000_000:
        raise ValueError('Se requiere un archivo audiovisual local de hasta 4 GB')
    sha=file_hash(path)
    try:
        probe=subprocess.run([str(ffprobe),'-v','error','-protocol_whitelist','file,pipe',
                              '-show_format','-show_streams','-of','json',str(path)],
                             capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=25)
        if probe.returncode or len(probe.stdout)>250_000:raise ValueError('No se pudo inspeccionar el archivo')
        metadata=inspect_metadata(json.loads(probe.stdout),profile=profile,expected_seconds=expected_seconds)
    except (OSError,subprocess.TimeoutExpired,json.JSONDecodeError):
        raise ValueError('Inspector multimedia no disponible o archivo ilegible') from None
    result={'schema':'fdg_av_quality_v1','product':'Factor de Gigantes','file':path.name,
            'sha256':sha,'bytes':path.stat().st_size,'metadata':metadata,
            'full_decode_completed':False,'technical_gate_passed':False,
            'human_listening_required':True,'human_visual_review_required':True,
            'voice_identity_verified':False,'rights_verified':False,'factual_approval':False,
            'publication_authorized':False,'failures':list(metadata['failures'])}
    if metadata['failures']:
        result['status']='blocked_metadata';return result
    try:
        decoded=subprocess.run([str(ffmpeg),'-hide_banner','-nostdin','-nostats','-v','info',
            '-xerror','-err_detect','explode','-protocol_whitelist','file,pipe','-threads','2',
            '-i',str(path),'-map','0:v:0','-map','0:a:0','-filter_threads','1',
            '-vf','freezedetect=n=-60dB:d=2,blackdetect=d=0.8:pix_th=0.05:pic_th=0.98',
            '-af','silencedetect=noise=-45dB:d=2,volumedetect','-f','null','-'],
            capture_output=True,text=True,encoding='utf-8',errors='replace',
            timeout=min(360,max(30,metadata['duration_seconds']*2+20)))
        if decoded.returncode or len(decoded.stderr)>2_000_000:
            result['failures'].append('full_decode_failed')
        else:
            result['full_decode_completed']=True
            result['scan']=inspect_scan(decoded.stderr,metadata['duration_seconds'])
            result['failures'].extend(result['scan']['failures'])
    except (OSError,subprocess.TimeoutExpired):result['failures'].append('decoder_unavailable_or_timeout')
    if file_hash(path)!=sha:result['failures'].append('source_changed_during_inspection')
    result['technical_gate_passed']=not result['failures']
    result['status']='technical_pass_human_review_pending' if result['technical_gate_passed'] else 'blocked_technical_quality'
    return result


def main():
    parser=argparse.ArgumentParser(description='QA técnico local de Factor de Gigantes, sin modificar el medio')
    parser.add_argument('source',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--profile',choices=('preview','documentary','short'),default='preview')
    parser.add_argument('--expected-seconds',type=float)
    parser.add_argument('--ffmpeg',default='ffmpeg');parser.add_argument('--ffprobe',default='ffprobe')
    args=parser.parse_args()
    if args.out.resolve()==args.source.resolve():parser.error('El informe no puede sobrescribir el medio')
    result=inspect_file(args.source,profile=args.profile,expected_seconds=args.expected_seconds,
                        ffmpeg=args.ffmpeg,ffprobe=args.ffprobe)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print('QA_AUDIOVISUAL:',result['status'],'FALLOS:',','.join(result['failures']) or 'ninguno')
    raise SystemExit(0 if result['technical_gate_passed'] else 1)


if __name__=='__main__':main()
