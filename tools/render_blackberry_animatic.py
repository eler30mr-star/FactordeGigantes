"""Generador de animática técnica BlackBerry sin material ajeno.

Renderiza un MP4 de ~30 segundos a partir de los títulos y tiempos de la EDL.
TODOS los fondos y gráficos son generados por código con Pillow. Sin música,
narrador, fotos de archivo, logotipos externos ni publicación automática.
No corresponde a un documental terminado o comercialmente aprobado.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from tools.blackberry_edl import make_edl, DEFAULT_SCRIPT, DEFAULT_SOURCES

WIDTH,HEIGHT=1280,720
DURATION_PER_SCENE=2.5
FPS=24


def font_file():
    candidates=(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
    )
    for path in candidates:
        if Path(path).is_file():
            return path
    raise RuntimeError("Se necesita fuente del sistema, no descargar fuentes ajenas")


def draw_slide(scene,index,total,destination,fontpath):
    from PIL import Image,ImageDraw,ImageFont
    img=Image.new("RGB",(WIDTH,HEIGHT),"#081522")
    d=ImageDraw.Draw(img)
    for y in range(0,HEIGHT,3):
        fraction=y/HEIGHT
        r=int(7+15*fraction)
        g=int(20+10*fraction)
        b=int(37+24*fraction)
        d.rectangle((0,y,WIDTH,y+2),fill=(r,g,b))
    # Solo elementos geométricos generados, no material audiovisual externo.
    for x in range(68,WIDTH,105):
        d.line((x,0,x,HEIGHT),fill="#162b3a",width=1)
    for y in range(58,HEIGHT,85):
        d.line((0,y,WIDTH,y),fill="#162b3a",width=1)
    cx,cy=990,320
    for rad in (235,194,152,112,72):
        d.ellipse((cx-rad,cy-rad,cx+rad,cy+rad),outline="#27515d",width=2)
    d.ellipse((cx-30,cy-30,cx+30,cy+30),fill="#31c8c5")
    titlefont=ImageFont.truetype(fontpath,62)
    small=ImageFont.truetype(fontpath,25)
    micro=ImageFont.truetype(fontpath,19)
    d.text((70,64),"FACTOR DE GIGANTES",font=small,fill="#e3f5f2")
    d.rectangle((70,116,360,119),fill="#31c8c5")
    d.text((70,157),f"BLACKBERRY  /  ESCENA {index:02d}",font=small,fill="#31c8c5")
    words=scene["title"].split()
    lines=[];line=""
    for word in words:
        candidate=(line+" "+word).strip()
        if d.textbbox((0,0),candidate,font=titlefont)[2]>750 and line:
            lines.append(line);line=word
        else:
            line=candidate
    if line:lines.append(line)
    y=242
    for line in lines[:3]:
        d.text((70,y),line,font=titlefont,fill="#ffffff",stroke_width=0)
        y+=82
    d.text((70,535),"DEMOSTRACIÓN DE MONTAJE · SIN VOZ",font=small,fill="#a6c0c9")
    d.text((70,581),"No autorizado para YouTube ni uso comercial",font=micro,fill="#91a8ad")
    d.text((70,625),f"Fuentes documentales: {', '.join(scene['source_ids'])}",font=micro,fill="#9ab0b5")
    d.rectangle((70,676,1210,680),fill="#294254")
    d.rectangle((70,676,70+round(1140*index/total),680),fill="#31c8c5")
    img.save(destination,optimize=False,compress_level=1)


def render_animation(script,registry,output,*,fps=FPS,seconds_per_scene=DURATION_PER_SCENE):
    if fps!=FPS or seconds_per_scene!=DURATION_PER_SCENE:
        raise ValueError("Animática de prueba solo admite 24 fps y 2,5 s por escena")
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("FFmpeg no está instalado")
    edl=make_edl(script,registry)
    output=Path(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="fdg-animatic-") as temp:
        folder=Path(temp)
        fontpath=font_file()
        paths=[]
        for i,scene in enumerate(edl["scenes"],1):
            path=folder/f"scene_{i:02d}.png"
            draw_slide(scene,i,len(edl["scenes"]),path,fontpath)
            paths.append(path)
        listing=folder/"slides.txt"
        # La última repetición cierra la duración del último frame.
        lines=[]
        for file in paths:
            lines.extend([f"file '{file.as_posix()}'",f"duration {seconds_per_scene}"])
        lines.append(f"file '{paths[-1].as_posix()}'")
        listing.write_text("\n".join(lines)+"\n",encoding="utf-8")
        args=["ffmpeg","-hide_banner","-loglevel","error","-y",
              "-f","concat","-safe","0","-i",str(listing),
              "-vf",f"fps={fps},format=yuv420p",
              "-c:v","libx264","-preset","veryfast","-crf","25",
              "-movflags","+faststart","-an",str(output)]
        subprocess.run(args,check=True,timeout=180)
    return {
        "file_name":output.name,"scenes":len(edl["scenes"]),
        "expected_seconds":len(edl["scenes"])*seconds_per_scene,
        "fps":fps,"format":"mp4","audio_present":False,
        "footage_origin":"procedural_vector_slides",
        "documentary_completed":False,"rights_verified":False,
        "youtube_publication_authorized":False
    }


def main():
    p=argparse.ArgumentParser(description="Generar animática sin voz ni material de terceros")
    p.add_argument("--out",type=Path,default=Path("dist/blackberry-animatic/BLACKBERRY_PREVISUAL_30S_SIN_VOZ.mp4"))
    p.add_argument("--script",type=Path,default=DEFAULT_SCRIPT)
    p.add_argument("--sources",type=Path,default=DEFAULT_SOURCES)
    args=p.parse_args()
    script=args.script.read_text(encoding="utf-8")
    sources=json.loads(args.sources.read_text(encoding="utf-8"))
    outcome=render_animation(script,sources,args.out)
    (args.out.parent/"ESTADO_PREVISUAL.json").write_text(
        json.dumps(outcome,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("MP4_PREVISUAL:",args.out,"ESCENAS:",outcome["scenes"],
          "AUDIO:",outcome["audio_present"],
          "YOUTUBE:",outcome["youtube_publication_authorized"])


if __name__=="__main__":
    main()
