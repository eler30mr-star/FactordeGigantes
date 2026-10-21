"""Primer montaje interno de BlackBerry con voz nueva en cuatro fragmentos.

Usa la narración del texto original de la Escena 01 y genera planos
animados propios a intervalos frecuentes. No usa imágenes ajenas, ni
música, ni voz robot alternativa, ni autoriza publicación.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
from PIL import Image,ImageDraw,ImageFont

from tools.render_blackberry_motion_intro import (
    SCENES, SCENE_BREAKS, W, H, GLOW,
    system_font, smooth,
)
from tools.approved_voice import approved_reference,hash_file
from tools.qwen_blackberry_scene01 import NAMES,get_cases,probe_mp3

FPS=12
SHOT_SECONDS=5.0
CROSSFADE_SECONDS=.42
MAX_AUDIO_SECONDS=165
MIN_AUDIO_SECONDS=35
OUTPUT_NAME="BLACKBERRY_ESCENA01_CON_VOZ_NUEVA_REVISAR.mp4"


def source_validation(audio_dir):
    audio_dir=Path(audio_dir)
    ref,meta=approved_reference()
    report=json.loads((audio_dir/"ESTADO_ESCENA01_VOZ.json").read_text(encoding="utf-8"))
    expected=get_cases()
    if report.get("canonical_reference_sha256") != meta["sha256"]:
        raise RuntimeError("Audio generado desde una referencia distinta")
    if report.get("owner_approved_new_takes") is not False or report.get("commercial_rights_verified") is not False:
        raise RuntimeError("Los audios nuevos no deben declararse aprobados")
    clips=report.get("clips",[])
    if len(clips)!=4 or len(expected)!=4:
        raise ValueError("La escena no tiene cuatro fragmentos")
    for given,(name,text) in zip(clips,expected):
        if given.get("id")!=name or given.get("text")!=text or given.get("auditory_approval")!="pending":
            raise ValueError("Texto o estado de la voz no coincide con el manuscrito")
        p=audio_dir/(name+".mp3")
        if given.get("sha256")!=hash_file(p):
            raise RuntimeError("Archivo de locución inesperado o modificado")
    audio=audio_dir/"05_escena01_unida.mp3"
    seconds=probe_mp3(audio)
    if not MIN_AUDIO_SECONDS<=seconds<=MAX_AUDIO_SECONDS:
        raise ValueError("Duración del bloque fuera del presupuesto")
    if abs(seconds-float(report["preview_mp3"]["duration_seconds"]))>.09:
        raise ValueError("Audio y manifiesto no corresponden")
    if hash_file(ref)!=meta["sha256"]:
        raise RuntimeError("Referencia canónica fue cambiada")
    return audio,seconds,report


def moving_frame(seconds,total_seconds):
    if not 0<=seconds<=total_seconds or total_seconds<MIN_AUDIO_SECONDS:
        raise ValueError("Tiempo de metraje inválido")
    count=min(4,max(0,math.floor(seconds/SHOT_SECONDS)))
    shot_number=min(int(seconds/SHOT_SECONDS),math.ceil(total_seconds/SHOT_SECONDS)-1)
    kind=shot_number%3  # Planos técnicos dinámicos; nunca sostener un título como escena.
    base_time=SCENE_BREAKS[kind]
    within=(seconds%SHOT_SECONDS)/SHOT_SECONDS
    raw_t=base_time+.05+2.80*within
    pic=SCENES[kind](raw_t)
    # Movimiento óptico de cámara: desplazamiento y escala suave dentro de cada toma.
    offset=round(8*math.sin(within*math.pi*2+shot_number))
    pic=pic.transform(pic.size,Image.Transform.AFFINE,
        (1,0,offset,0,1,round(4*math.cos(within*math.pi*2))),resample=Image.Resampling.BICUBIC)
    left=SHOT_SECONDS-(seconds%SHOT_SECONDS)
    if left<CROSSFADE_SECONDS and seconds+left<total_seconds:
        nxt=(shot_number+1)%3
        coming=SCENES[nxt](SCENE_BREAKS[nxt]+.07)
        alpha=smooth((CROSSFADE_SECONDS-left)/CROSSFADE_SECONDS)
        pic=Image.blend(pic,coming,alpha)
    d=ImageDraw.Draw(pic)
    d.rectangle((0,H-76,W,H),fill=(8,21,29))
    d.text((46,H-62),"BLACKBERRY    •    PRIMER CAPÍTULO",font=system_font(20,True),fill=(234,241,242))
    d.text((812,H-62),"AUDIO EN REVISIÓN EDITORIAL",font=system_font(16),fill=(106,194,202))
    d.rectangle((46,H-15,W-46,H-11),fill=(43,73,84))
    d.rectangle((46,H-15,46+round((W-92)*seconds/total_seconds),H-11),fill=GLOW)
    return pic


def render(audio_dir,output):
    audio,seconds,report=source_validation(audio_dir)
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("FFmpeg requerido")
    output=Path(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    frames=math.ceil(seconds*FPS)
    args=["ffmpeg","-hide_banner","-loglevel","error","-y",
          "-f","rawvideo","-pixel_format","rgb24","-video_size",f"{W}x{H}",
          "-framerate",str(FPS),"-i","pipe:0","-i",str(audio),
          "-map","0:v:0","-map","1:a:0","-t",f"{seconds:.3f}",
          "-c:v","libx264","-preset","veryfast","-crf","25","-threads","2",
          "-pix_fmt","yuv420p","-c:a","aac","-b:a","144k",
          "-ar","48000","-ac","1","-movflags","+faststart",str(output)]
    process=subprocess.Popen(args,stdin=subprocess.PIPE)
    try:
        for i in range(frames):
            process.stdin.write(moving_frame(i/FPS,seconds).tobytes())
    except (BrokenPipeError,OSError):
        process.kill()
        raise RuntimeError("La exportación de video se interrumpió")
    finally:
        if process.stdin:
            try:process.stdin.close()
            except OSError:pass
    if process.wait(timeout=180)!=0 or not output.exists() or output.stat().st_size<180_000:
        raise RuntimeError("MP4 de primer capítulo inválido")
    return {
        "file":output.name,"episode":"BlackBerry",
        "chapter":1,"video_seconds":seconds,
        "audio_seconds":seconds,"frames_written":frames,
        "fps":FPS,"resolution":[W,H],
        "camera_motion_verified_by_unit_tests":True,
        "voice_clips":4,"voice_clips_pending_human_review":4,
        "original_reference_untouched":True,
        "new_voice_approved":False,
        "rights_commercially_verified":False,
        "documentary_full_length_finished":False,
        "youtube_publication_allowed":False
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--audio-dir",type=Path,required=True)
    p.add_argument("--out",type=Path,
        default=Path("dist/blackberry-escena01-video/"+OUTPUT_NAME))
    args=p.parse_args()
    status=render(args.audio_dir,args.out)
    (args.out.parent/"ESTADO_ESCENA01_VIDEO.json").write_text(
        json.dumps(status,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("ESCENA01_MP4:",args.out,"AUDIO_S:",status["audio_seconds"],
          "FRAMES:",status["frames_written"],
          "APROBADO:",status["new_voice_approved"],flush=True)


if __name__=="__main__":
    main()
