"""Montaje genérico de episodio, audio real, escenas dinámicas, SRT y QA.

--technical-test usa una señal identificada, nunca la presenta como narración.
La locución real requiere todas las tomas Qwen canónicas. No publica ni concede
aprobación editorial, comercial o de identidad vocal.
"""
from __future__ import annotations
import argparse
from bisect import bisect_right
import html
import json
import math
from pathlib import Path
import re
import subprocess
import wave

from PIL import Image, ImageDraw, ImageFont
from tools.approved_voice import SHA, approved_reference, hash_file
from tools.av_quality import inspect_file
from tools.episode_package import validate_episode, voice_plan, write_manuscript
from tools.episode_voice import collect_voice, atomic_json
from tools.subtitles import split_lines, timestamp

W,H,FPS=1280,720,12
BG=(16,20,28);GOLD=(225,181,91);INK=(238,240,241);MUTED=(154,166,181)


def font(size,bold=False):
    path=Path('/usr/share/fonts/truetype/dejavu')/('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')
    if not path.is_file():raise ValueError('Fuente del sistema DejaVu requerida')
    return ImageFont.truetype(str(path),size)


FONTS={n:font(n,bold=n in (18,26,34)) for n in (16,18,22,26,34)}


def lines(draw,value,x,y,width,*,size=22,color=INK,max_lines=3):
    rows=[];active=''
    for word in value.split():
        proposed=(active+' '+word).strip()
        if draw.textlength(proposed,font=FONTS[size])>width and active:
            rows.append(active);active=word
        else:active=proposed
    if active:rows.append(active)
    for n,row in enumerate(rows[:max_lines]):draw.text((x,y+n*(size+8)),row,font=FONTS[size],fill=color)


def frame(episode,scene,seconds,local,progress,caption,*,technical=False):
    image=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(image)
    # Retícula y partículas en movimiento: gráfico editorial original, no metraje.
    for x in range(-40,W,64):
        xx=x+int(seconds*6)%64;d.line((xx,100,xx,H-110),fill=(27,34,44))
    for y in range(120,600,64):d.line((0,y,W,y),fill=(25,31,40))
    d.text((42,22),'FACTOR DE GIGANTES',font=FONTS[26],fill=GOLD)
    d.text((900,29),'DESARROLLO · REVISIÓN PENDIENTE',font=FONTS[16],fill=MUTED)
    lines(d,scene['headline'],42,72,1180,size=34,max_lines=2)
    items=scene['visual']['items'];kind=scene['visual']['kind'];n=len(items)
    phase=(local%8)/8;selected=min(n-1,int(phase*n))
    if kind in ('process','timeline'):
        left,right,cy=100,1180,310
        d.line((left,cy,right,cy),fill=(85,74,52),width=4)
        for i,item in enumerate(items):
            x=left+(right-left)*i/(n-1);on=i==selected
            rad=22+int(5*math.sin(local*2+i)) if on else 18
            d.ellipse((x-rad,cy-rad,x+rad,cy+rad),fill=GOLD if on else (58,67,79),outline=INK,width=2)
            lines(d,item['label'],max(38,min(1050,x-100)),365,205,size=22,max_lines=3)
            d.text((max(40,min(1080,x-65)),475),', '.join(item['source_ids']),font=FONTS[16],fill=GOLD)
        d.text((46,155),'SECUENCIA DEL RELATO · NO A ESCALA' if kind=='timeline' else 'PROCESO DOCUMENTADO',font=FONTS[18],fill=MUTED)
        x=left+(right-left)*phase;d.ellipse((x-6,cy-6,x+6,cy+6),fill=INK)
    elif kind=='network':
        cx,cy=640,320
        for i,item in enumerate(items):
            angle=2*math.pi*i/n-.6
            x=cx+350*math.cos(angle);y=cy+155*math.sin(angle)
            d.line((cx,cy,x,y),fill=GOLD if i==selected else (66,76,90),width=3)
            dot=(phase+i/n)%1;px=cx+(x-cx)*dot;py=cy+(y-cy)*dot
            d.ellipse((px-5,py-5,px+5,py+5),fill=GOLD)
            d.rounded_rectangle((x-135,y-44,x+135,y+48),radius=12,fill=(31,39,51),outline=GOLD if i==selected else (74,84,98),width=2)
            lines(d,item['label'],x-120,y-28,242,size=22,max_lines=2)
        d.ellipse((cx-68,cy-68,cx+68,cy+68),fill=BG,outline=GOLD,width=3)
        lines(d,'Decisión',cx-50,cy-14,110,size=22)
        d.text((46,155),'RELACIONES EDITORIALES ENTRE LAS AFIRMACIONES',font=FONTS[18],fill=MUTED)
    elif kind=='comparison':
        largest=max(x['value'] for x in items) or 1
        for i,item in enumerate(items):
            y=190+i*int(300/n)
            lines(d,item['label'],70,y,420,size=22,max_lines=2)
            length=650*item['value']/largest
            # El valor de la barra no cambia; se mueve el brillo, no el dato.
            d.rounded_rectangle((510,y,510+length,y+40),radius=8,fill=(111,87,45),outline=GOLD,width=2)
            glow=510+length*((phase+i/n)%1)
            d.line((glow,y+4,glow,y+36),fill=INK,width=3)
            d.text((1130,y+48),str(item['value']),font=FONTS[18],fill=INK)
        d.text((70,535),'Cantidades y alcance: '+', '.join(sorted({k for item in items for k in item['source_ids']})),font=FONTS[16],fill=GOLD)
    else:
        # Papeles/resultado procesal: no imitar una fotografía del documento.
        for i,item in enumerate(items):
            width=1120/n;x=70+i*width;y=190+int(6*math.sin(local+i))
            d.rounded_rectangle((x,y,x+width-20,485),radius=12,fill=(33,40,52),outline=GOLD if i==selected else (80,91,104),width=2)
            d.text((x+15,y+18),'EXPEDIENTE' if kind=='document' else 'RESULTADO',font=FONTS[16],fill=GOLD)
            lines(d,item['label'],x+15,y+80,width-50,size=22,max_lines=5)
            d.text((x+15,445),', '.join(item['source_ids']),font=FONTS[16],fill=MUTED)
            d.line((x+15,y+56,x+width-36,y+56),fill=(104,89,58),width=2)
        d.text((70,535),'REPRESENTACIÓN EDITORIAL · NO ES UNA IMAGEN DEL DOCUMENTO',font=FONTS[16],fill=MUTED)
    # Cámara sobre el gráfico completo, con desplazamiento subpíxel; mover sólo
    # una partícula pequeña podía desaparecer tras la compresión H.264.
    panel=image.crop((0,145,W,555))
    camera_x=14*math.sin(local*.48);camera_y=7*math.sin(local*.71)
    panel=panel.transform(panel.size,Image.Transform.AFFINE,(1,0,-camera_x,0,1,-camera_y),
                          resample=Image.Resampling.BICUBIC,fillcolor=BG)
    image.paste(panel,(0,145));d=ImageDraw.Draw(image)
    d.rectangle((0,570,W,H),fill=(20,25,34))
    if caption:
        for i,row in enumerate(caption.split('\n')):d.text((60,590+35*i),row,font=FONTS[26],fill=INK)
    label='SEÑAL TÉCNICA · ESTE ARCHIVO NO CONTIENE LOCUCIÓN' if technical else 'VOZ CANÓNICA · TOMAS NUEVAS PENDIENTES DE AUDICIÓN'
    d.text((42,675),label,font=FONTS[16],fill=GOLD)
    d.text((1075,675),scene['id'],font=FONTS[18],fill=MUTED)
    d.rectangle((0,H-6,int(W*progress),H),fill=GOLD)
    return image


def concatenate_audio(records,voice_root,target):
    with wave.open(str(target),'wb') as output:
        output.setparams((1,2,48000,0,'NONE','not compressed'))
        for record in records:
            path=Path(voice_root)/record['relative_file']
            if hash_file(path)!=record['sha256']:raise ValueError('La toma cambió antes del montaje')
            with wave.open(str(path),'rb') as source:
                while block:=source.readframes(48_000):output.writeframesraw(block)


def captions(records,durations):
    cues=[];offset=0
    for record,seconds in zip(records,durations):
        parts=split_lines(record['text']);weights=[len(p.replace('\n','')) for p in parts]
        total=sum(weights);elapsed=0
        for part,weight in zip(parts,weights):
            start=offset+seconds*elapsed/total;elapsed+=weight
            end=offset+seconds*elapsed/total
            cues.append((start,end,part))
        offset+=seconds
    return cues


def render_episode(episode,out,*,voice_root=None,technical_test=False,sample_seconds=None):
    summary=validate_episode(episode);plan=voice_plan(episode)
    reference,_=approved_reference()
    if not technical_test and sample_seconds is not None:raise ValueError('Muestras reducidas sólo para prueba técnica')
    if technical_test and voice_root is not None:raise ValueError('La señal técnica y la narración no se mezclan')
    out=Path(out).resolve()
    if out==reference.parent or reference.parent in out.parents:raise ValueError('No exportar en la referencia canónica')
    out.mkdir(parents=True,exist_ok=True)
    for name in ('EPISODIO_PARA_REVISION.mp4','EPISODIO.partial.mp4','MONTAJE_AUDIO.wav','SUBTITULOS.srt',
                 'SUBTITULOS.vtt','REVISAR.html','GUION.md','FUENTES_Y_CREDITOS.txt'):
        if (out/name).is_symlink():raise ValueError('Salida enlazada fuera del contrato')
    target=out/'EPISODIO_PARA_REVISION.mp4';audio=out/'MONTAJE_AUDIO.wav'
    if technical_test:
        seconds=summary['estimated_seconds'] if sample_seconds is None else sample_seconds
        if type(seconds) not in (int,float) or not math.isfinite(seconds) or not 1<=seconds<=840:
            raise ValueError('Duración de muestra inválida')
        records=plan['tasks'];weights=[len(r['text'].split()) for r in records]
        durations=[seconds*w/sum(weights) for w in weights]
        durations[-1]+=seconds-sum(durations)
        subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i',
                        f'sine=frequency=440:sample_rate=48000:duration={seconds}',
                        '-af','volume=0.5','-ac','1','-c:a','pcm_s16le',str(audio)],check=True,timeout=30)
    else:
        if voice_root is None:raise ValueError('Se requieren las tomas de la voz canónica')
        records=collect_voice(episode,voice_root);durations=[r['duration_seconds'] for r in records]
        seconds=sum(durations)
        if not 480<=seconds<=840:raise ValueError('La duración real de voz debe alcanzar ocho a catorce minutos')
        concatenate_audio(records,voice_root,audio)
    scenes=episode['scenes']
    scene_durations={s['id']:0 for s in scenes}
    for record,span in zip(records,durations):scene_durations[record['scene_id']]+=span
    ends=[];cursor=0;chapters=[]
    for scene in scenes:
        begin=cursor;cursor+=scene_durations[scene['id']];ends.append(cursor)
        chapters.append({'id':scene['id'],'title':scene['headline'],'start_seconds':begin,'end_seconds':cursor})
    cues=captions(records,durations);cue_starts=[x[0] for x in cues]
    srt='\n'.join(f'{n}\n{timestamp(a)} --> {timestamp(b)}\n{words}\n' for n,(a,b,words) in enumerate(cues,1))
    (out/'SUBTITULOS.srt').write_text(srt,encoding='utf-8')
    atomic_json(out/'EPISODIO.json',episode)
    write_manuscript(episode,out/'GUION.md')
    credits=['FACTOR DE GIGANTES',episode['title'],
             'Gráficos editoriales originales generados por código. No se usa metraje, música ni fotografías de terceros.',
             'Señal técnica sin locución.' if technical_test else 'Qwen3-TTS 1.7B Base, referencia canónica; tomas pendientes de audición.',
             'Subtítulos aproximados por toma, no alineación fonética verificada.',
             'Sin autorización de publicación ni acreditación comercial.','']
    credits += [f"{s['id']} · {s['publisher']} · {s['title']}\n{s['url']}\n{s['locator']}" for s in episode['sources']]
    (out/'FUENTES_Y_CREDITOS.txt').write_text('\n\n'.join(credits)+'\n',encoding='utf-8')
    temporary=out/'EPISODIO.partial.mp4'
    args=['ffmpeg','-hide_banner','-nostdin','-loglevel','error','-y','-f','rawvideo',
          '-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','pipe:0',
          '-i',str(audio),'-map','0:v:0','-map','1:a:0','-t',f'{seconds:.6f}',
          '-c:v','libx264','-preset','veryfast','-crf','26','-threads','2','-pix_fmt','yuv420p',
          '-c:a','aac','-b:a','128k','-ar','48000','-ac','1','-movflags','+faststart',str(temporary)]
    process=subprocess.Popen(args,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for n in range(math.ceil(seconds*FPS)):
            elapsed=n/FPS;index=min(bisect_right(ends,elapsed),len(scenes)-1)
            local=elapsed-(ends[index-1] if index else 0)
            ci=max(0,bisect_right(cue_starts,elapsed)-1)
            pic=frame(episode,scenes[index],elapsed,local,elapsed/seconds,cues[ci][2],technical=technical_test)
            process.stdin.write(pic.tobytes())
            if n%(FPS*30)==0:print('MONTAJE:',round(elapsed),'/',round(seconds),'s',flush=True)
    except BaseException:
        process.kill();process.wait(timeout=15)
        raise
    finally:
        process.stdin.close()
    code=process.wait(timeout=180)
    process.stderr.close()
    if code!=0:raise ValueError('FFmpeg no completó el montaje')
    profile='preview' if sample_seconds is not None else 'documentary'
    qa=inspect_file(temporary,profile=profile,expected_seconds=seconds)
    qa['file']=target.name;atomic_json(out/'QA_AUDIOVISUAL.json',qa)
    if not qa['technical_gate_passed']:raise ValueError('Exportación rechazada por QA: '+', '.join(qa['failures']))
    temporary.replace(target)
    if hash_file(reference)!=SHA:raise ValueError('La referencia canónica cambió')
    report={'schema':'fdg_episode_export_v1',**summary,'file':target.name,'actual_seconds':seconds,
            'sha256':hash_file(target),'fps':FPS,'resolution':[W,H],'chapters':chapters,
            'canonical_reference_sha256':SHA,
            'voice_kind':'technical_test_signal' if technical_test else 'canonical_qwen_pending_audition',
            'contains_narration':not technical_test,'canonical_reference_unchanged':True,
            'generated_voice_takes':0 if technical_test else len(records),
            'technical_gate_passed':True,'caption_alignment':'approximate_per_take',
            'human_factual_approval':False,'commercial_rights_verified':False,'publication_authorized':False}
    if (out/'PIPELINE_CONTEXT.json').is_file():
        context=json.loads((out/'PIPELINE_CONTEXT.json').read_text(encoding='utf-8'))
        if not re.fullmatch('[a-f0-9]{64}',context.get('approved_manifest_sha256','')):
            raise ValueError('Contexto de montaje inválido')
        report['approved_manifest_sha256']=context['approved_manifest_sha256']
    atomic_json(out/'ESTADO_EXPORTACION.json',report)
    body=''.join(f'<h2>{html.escape(s["headline"])}</h2>'+''.join(
        '<p>'+html.escape(p['text'])+'</p>' for p in s['paragraphs']) for s in scenes)
    page='<!doctype html><html lang="es"><meta charset="utf-8"><title>'+html.escape(episode['title'])+'</title>'
    page+='<style>body{background:#10141c;color:#eef0f1;font:18px system-ui;max-width:1050px;margin:40px auto;padding:20px}video{width:100%}a{color:#e1b55b}h1,h2{color:#e1b55b}</style>'
    page+='<h1>'+html.escape(episode['title'])+'</h1><p>Prueba de desarrollo. '+('Señal técnica: no contiene locución.' if technical_test else 'Tomas nuevas pendientes de audición.')+'</p>'
    page+='<video controls preload="metadata" src="'+target.name+'"><track kind="subtitles" srclang="es" label="Español" src="SUBTITULOS.vtt" default></video>'
    page+='<p><a href="SUBTITULOS.srt">Subtítulos SRT</a> · <a href="FUENTES_Y_CREDITOS.txt">Fuentes</a> · <a href="QA_AUDIOVISUAL.json">QA</a></p>'+body+'</html>'
    (out/'REVISAR.html').write_text(page,encoding='utf-8')
    vtt=re.sub(r'(\d{2}:\d{2}:\d{2}),(\d{3})',r'\1.\2',srt)
    (out/'SUBTITULOS.vtt').write_text('WEBVTT\n\n'+vtt,encoding='utf-8')
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--episode',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--voice-dir',type=Path);p.add_argument('--technical-test',action='store_true')
    p.add_argument('--sample-seconds',type=float);p.add_argument('--validate-only',action='store_true')
    a=p.parse_args();episode=json.loads(a.episode.read_text(encoding='utf-8'))
    if a.validate_only:print(json.dumps(voice_plan(episode),ensure_ascii=False));return
    result=render_episode(episode,a.out,voice_root=a.voice_dir,technical_test=a.technical_test,sample_seconds=a.sample_seconds)
    print('EPISODIO_EXPORTADO:',result['file'],'SEGUNDOS:',result['actual_seconds'],
          'LOCUCION:',result['contains_narration'],'PUBLICACION:',result['publication_authorized'])


if __name__=='__main__':main()
