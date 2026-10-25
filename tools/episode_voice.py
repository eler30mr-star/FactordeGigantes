"""Narración genérica y reanudable con la referencia canónica, nunca otra voz.

Los modelos sólo se cargan con --final-ai-test. Las pruebas de desarrollo usan
dobles explícitos; esos archivos no pasan como narración Qwen al renderizador.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import wave

from tools.approved_voice import SHA, approved_reference, hash_file
from tools.documentary_pacing import run as pace
from tools.episode_package import voice_plan, digest

MODEL = 'Qwen/Qwen3-TTS-12Hz-1.7B-Base'


def pcm_info(path):
    path=Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size>20_000_000:
        raise ValueError('Toma local inválida')
    with wave.open(str(path),'rb') as reader:
        if (reader.getframerate(),reader.getnchannels(),reader.getsampwidth()) != (48000,1,2):
            raise ValueError('La toma requiere PCM mono de 48 kHz y 16 bits')
        seconds=reader.getnframes()/reader.getframerate()
    if not .2 <= seconds <= 90:
        raise ValueError('Duración de toma fuera de presupuesto')
    return {'duration_seconds':seconds,'sha256':hash_file(path),'bytes':path.stat().st_size}


def atomic_json(path,value):
    path=Path(path)
    if path.is_symlink():raise ValueError('Checkpoint enlazado no permitido')
    tmp=path.with_suffix('.json.tmp')
    if tmp.is_symlink():raise ValueError('Checkpoint temporal enlazado no permitido')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    tmp.replace(path)


class QwenCanonicalEngine:
    kind='qwen_cpu'
    def __init__(self):
        self.model=None

    def generate(self,task,target,reference,metadata):
        import torch
        import soundfile as sf
        from qwen_tts import Qwen3TTSModel
        import subprocess
        if metadata['model'] != MODEL.split('/')[-1]:
            raise ValueError('Modelo canónico incompatible')
        torch.set_num_threads(4)
        if self.model is None:
            self.model=Qwen3TTSModel.from_pretrained(MODEL,device_map='cpu',dtype=torch.float32,
                                                    attn_implementation='sdpa')
        torch.manual_seed(int(task['text_sha256'][:8],16))
        with tempfile.TemporaryDirectory() as folder:
            ref=Path(folder)/'reference.wav';raw=Path(folder)/'raw.wav'
            subprocess.run(['ffmpeg','-v','error','-y','-i',str(reference),'-ac','1','-ar','24000',
                            '-c:a','pcm_s16le',str(ref)],check=True,timeout=45)
            with torch.inference_mode():
                audio,rate=self.model.generate_voice_clone(text=task['text'],language='Spanish',
                    ref_audio=str(ref),ref_text=metadata['reference_text'])
            if len(audio)!=1:raise ValueError('El motor debe entregar una sola toma')
            sf.write(str(raw),audio[0],rate)
            p=metadata['pacing']
            pace(raw,Path(target),speed=p['atempo'],pause_seconds=p['extra_pause_seconds'],max_breaks=p['max_pauses'])


def checked_take(task,root,*,engine_kind,pacing_sha):
    directory=Path(root)/task['scene_id']
    path=directory/(task['id']+'.wav');checkpoint=directory/(task['id']+'.json')
    try:
        if checkpoint.is_symlink():return None
        record=json.loads(checkpoint.read_text(encoding='utf-8'))
        if (record.get('id')!=task['id'] or record.get('text_sha256')!=task['text_sha256'] or
                record.get('canonical_reference_sha256')!=SHA or record.get('model')!=MODEL or
                record.get('engine_kind')!=engine_kind or record.get('pacing_sha256')!=pacing_sha or
                record.get('auditory_approval')!='pending' or record.get('publication_authorized') is not False):
            return None
        actual=pcm_info(path)
        if actual['sha256']!=record.get('sha256') or abs(actual['duration_seconds']-record.get('duration_seconds',0))>.001:
            return None
        return {**record,'relative_file':task['scene_id']+'/'+task['id']+'.wav'}
    except (OSError,ValueError,TypeError,wave.Error):
        return None


def generate_voice(episode,root,*,scene=None,max_new_takes=128,engine=None,final_ai_test=False):
    plan=voice_plan(episode)
    if type(max_new_takes) is not int or not 1<=max_new_takes<=128:
        raise ValueError('Límite de tomas inválido')
    scenes={s['id'] for s in episode['scenes']}
    if scene is not None and scene not in scenes:raise ValueError('Escena inexistente')
    root=Path(root).resolve()
    reference,metadata=approved_reference()
    if root==reference.parent or reference.parent in root.parents:
        raise ValueError('No escribir tomas en la carpeta de referencia aprobada')
    kind=engine.kind if engine else 'qwen_cpu'
    if kind not in ('qwen_cpu','test_double'):raise ValueError('Motor no permitido')
    pacing_sha=digest(metadata['pacing'])
    tasks=[t for t in plan['tasks'] if scene is None or t['scene_id']==scene]
    root.mkdir(parents=True,exist_ok=True)
    records=[];generated=0;reused=0
    def report():
        result={'schema':'fdg_episode_voice_v1','episode_sha256':plan['episode_sha256'],
                'model':MODEL,'engine_kind':kind,'canonical_reference_sha256':SHA,
                'pacing_sha256':pacing_sha,'scene':scene,'planned_takes':len(tasks),
                'complete':len(records)==len(tasks),'generated_now':generated,'reused_now':reused,
                'takes':records,'voice_identity_verified':False,'human_listening_required':True,
                'commercial_rights_verified':False,'publication_authorized':False}
        location=root/scene if scene else root
        location.mkdir(parents=True,exist_ok=True)
        atomic_json(location/'VOICE_REPORT.json',result)
        return result
    for task in tasks:
        existing=checked_take(task,root,engine_kind=kind,pacing_sha=pacing_sha)
        if existing:
            reused+=1;records.append(existing);continue
        if generated>=max_new_takes:continue
        if engine is None:
            if not final_ai_test:raise ValueError('Carga de Qwen reservada a --final-ai-test')
            engine=QwenCanonicalEngine()
        if hash_file(reference)!=SHA:raise ValueError('La referencia canónica cambió')
        directory=root/task['scene_id'];directory.mkdir(parents=True,exist_ok=True)
        if directory.resolve().parent!=root:raise ValueError('Ruta de escena fuera de destino')
        temporary=directory/(task['id']+'.partial.wav')
        if temporary.is_symlink():raise ValueError('Toma temporal enlazada no permitida')
        print('TOMA:',task['id'],'CARACTERES:',len(task['text']),flush=True)
        engine.generate(task,temporary,reference,metadata)
        actual=pcm_info(temporary)
        target=directory/(task['id']+'.wav');temporary.replace(target)
        record={'id':task['id'],'text_sha256':task['text_sha256'],'canonical_reference_sha256':SHA,
                'model':MODEL,'engine_kind':kind,'pacing_sha256':pacing_sha,**actual,
                'auditory_approval':'pending','publication_authorized':False}
        atomic_json(directory/(task['id']+'.json'),record)
        generated+=1;records.append({**record,'relative_file':task['scene_id']+'/'+target.name})
        report()
    if hash_file(reference)!=SHA:raise ValueError('La referencia canónica fue modificada')
    return report()


def collect_voice(episode,root):
    plan=voice_plan(episode);reference,metadata=approved_reference()
    records=[]
    for task in plan['tasks']:
        record=checked_take(task,root,engine_kind='qwen_cpu',pacing_sha=digest(metadata['pacing']))
        if record is None:raise ValueError('Narración Qwen incompleta o alterada: '+task['id'])
        records.append({**record,'text':task['text'],'scene_id':task['scene_id'],'source_ids':task['source_ids']})
    return records


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--episode',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--scene');p.add_argument('--max-new-takes',type=int,default=128)
    p.add_argument('--final-ai-test',action='store_true')
    a=p.parse_args()
    result=generate_voice(json.loads(a.episode.read_text(encoding='utf-8')),a.out,scene=a.scene,
                          max_new_takes=a.max_new_takes,final_ai_test=a.final_ai_test)
    print('NARRACION:', 'completa pendiente de audición' if result['complete'] else 'parcial reanudable',
          'NUEVAS:',result['generated_now'],'REUTILIZADAS:',result['reused_now'])


if __name__=='__main__':main()
