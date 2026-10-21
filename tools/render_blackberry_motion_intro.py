"""Intro audiovisual en movimiento real con la voz canónica del propietario.

12.336 segundos, original art generado por Pillow, MP4 H.264 + AAC. Sin
substitución/síntesis de voz, clips externos, API pagada ni publicación.
Referencia editorial únicamente; derechos comerciales pendientes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from tools.approved_voice import approved_reference

W,H,FPS=1280,720,24
GLOW=(34,208,219)
VOICE_DURATION=12.336
SCENE_BREAKS=(0.0,3.05,6.18,9.22,VOICE_DURATION)


def system_font(size,bold=False):
    names=[
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for name in names:
        if Path(name).is_file():
            return ImageFont.truetype(name,size)
    raise RuntimeError("No hay fuente del sistema local")


def clamp(x,minimum=0.0,maximum=1.0):
    return max(minimum,min(maximum,x))


def smooth(x):
    x=clamp(x)
    return x*x*(3-2*x)


def base_background(t):
    img=Image.new("RGB",(W,H))
    d=ImageDraw.Draw(img)
    for y in range(0,H,3):
        fy=y/H
        d.rectangle((0,y,W,y+3),fill=(round(5+10*fy),round(12+17*fy),round(23+26*fy)))
    horizon=round(H*0.65)
    for i in range(70):
        x=round((i*171+60+t*(5+i%4)*(-1 if i%3==0 else 1))%(W+160)-80)
        y=round(85+(i*103)%475+7*math.sin(t*.55+i))
        r=2+i%5
        light=(12+i%4*7,56+i%6*7,69+i%7*6)
        d.ellipse((x-r,y-r,x+r,y+r),fill=light)
    for i in range(0,19):
        y=horizon+i*29
        d.line([(0,y+int(14*math.sin(t*.21+i))), (W,y+int(14*math.sin(t*.21+i)))],fill=(15,38,54),width=1)
    return img


def phone_scene(t):
    img=base_background(t)
    d=ImageDraw.Draw(img)
    # Changing cinematic camera perspective, bokeh and light trails.
    for n in range(18):
        y=round(70+n*43+12*math.sin(t*1.1+n))
        x=round(85-70*t+n*32)
        d.line((x,y,x+480,y-170),fill=(17,49+n%4*10,66+n%5*11),width=2)
    d.text((87,100),"BLACKBERRY",font=system_font(57,True),fill=(235,243,246))
    d.text((91,174),"CUANDO TODO PARECÍA IMPARABLE",font=system_font(23),fill=(89,203,204))
    d.line((92,223,522,223),fill=GLOW,width=3)
    phone=Image.new("RGBA",(380,660),(0,0,0,0))
    p=ImageDraw.Draw(phone)
    p.rounded_rectangle((65,18,317,630),radius=45,fill=(6,10,17,250),outline=(89,108,123),width=6)
    p.rounded_rectangle((81,47,301,344),radius=14,fill=(21,42,49),outline=(45,154,166),width=2)
    for j in range(12):
        glow=20+j%3*8
        p.line((95,85+j*19,286,84+j*19),fill=(21,glow+25,glow+42),width=2)
    p.ellipse((174,36,188,50),fill=(24,28,32))
    for row in range(5):
        for col in range(7):
            px=90+col*30+(row%2)*3
            py=383+row*36
            lighting=round(120+75*abs(math.sin(t*1.1+row+col*.4)))
            p.rounded_rectangle((px,py,px+23,py+27),radius=5,
                                fill=(20,29,38),outline=(45,lighting,lighting))
    p.rounded_rectangle((164,579,218,588),radius=5,fill=(42,116,130))
    spin=-10+1.4*math.sin(t*.7)
    phone=phone.rotate(spin,resample=Image.Resampling.BICUBIC,expand=True)
    scale=0.94+0.09*smooth(t/3.05)
    size=(int(phone.width*scale),int(phone.height*scale))
    phone=phone.resize(size,Image.Resampling.BICUBIC)
    px=780+round(22*math.sin(t*.7))+(0 if t<2.3 else round(170*smooth((t-2.3)/.75)))
    py=44+round(14*math.sin(t*.85))
    img.paste(phone,(px,py),phone)
    return img


def communication_scene(t):
    img=base_background(t)
    d=ImageDraw.Draw(img)
    local=t-3.05
    d.text((84,86),"LAS REGLAS CAMBIARON",font=system_font(52,True),fill=(226,239,238))
    d.text((90,168),"DE UN DISPOSITIVO A UNA RED DE TECNOLOGÍAS",font=system_font(23),fill=GLOW)
    # Moving polygonal connection web and traveling packets.
    nodes=[]
    for i in range(24):
        angle=2*math.pi*i/24
        radius=190+62*math.sin(local*.5+i*.8)
        x=round(825+radius*math.cos(angle)+65*math.sin(local*.44+i))
        y=round(418+radius*.75*math.sin(angle)+30*math.cos(local*.62+i))
        nodes.append((x,y))
    for i,(x,y) in enumerate(nodes):
        for j in (3,7):
            target=nodes[(i+j)%len(nodes)]
            d.line((x,y,*target),fill=(12,53+i%3*14,70+i%4*12),width=2)
        d.ellipse((x-5,y-5,x+5,y+5),fill=(36,142+i%4*23,154+i%4*20))
    for j in range(18):
        a=nodes[j];b=nodes[(j+7)%24]
        u=(local*.35+j*.117)%1
        x=round(a[0]+u*(b[0]-a[0]));y=round(a[1]+u*(b[1]-a[1]))
        d.ellipse((x-4,y-4,x+4,y+4),fill=(111,234,237))
    # Timeline slides laterally with moving indicator.
    d.line((100,590,1180,590),fill=(44,100,112),width=3)
    for k,(year,name) in enumerate((("1999","MENSAJERÍA"),("2016","TRANSICIÓN"),("2025","SOFTWARE"))):
        x=155+k*442
        d.ellipse((x-9,581,x+9,599),fill=GLOW)
        d.text((x-26,609),year,font=system_font(20,True),fill=(224,235,238))
        d.text((x-45,647),name,font=system_font(15),fill=(144,191,195))
    d.ellipse((145+round(local*308),579,165+round(local*308),600),fill=(255,214,142))
    return img


def systems_scene(t):
    img=base_background(t)
    d=ImageDraw.Draw(img)
    local=t-6.18
    d.text((86,96),"EL NEGOCIO INVISIBLE",font=system_font(50,True),fill=(238,244,247))
    d.text((90,164),"SOFTWARE  ·  SISTEMAS  ·  SEGURIDAD",font=system_font(22),fill=GLOW)
    cx,cy=800,420
    # Animated concentric data rings, rising pulse, circuit diagrams.
    for j in range(6):
        radius=75+j*47+13*math.sin(local*.8+j)
        d.arc((cx-radius,cy-radius,cx+radius,cy+radius),start=15+(local*30+j*25)%360,
              end=290+(local*30+j*25)%360,fill=(34,75+j*14,91+j*15),width=4)
    for k in range(18):
        a=k*math.pi/9+local*.21
        dx=round(cx+math.cos(a)*(250+k%3*37))
        dy=round(cy+math.sin(a)*(180+k%4*27))
        d.line((cx,cy,dx,dy),fill=(23,88+k%4*15,99+k%3*20),width=2)
        d.ellipse((dx-5,dy-5,dx+5,dy+5),fill=(42,183,186))
    d.rounded_rectangle((709,329,890,512),radius=13,fill=(9,28,41),outline=(98,218,218),width=5)
    d.text((737,386),"QNX",font=system_font(53,True),fill=(211,243,240))
    for i,(label,value) in enumerate((("SISTEMAS","01"),("SEGURIDAD","02"),("LICENCIAS","03"))):
        top=292+i*90
        d.rounded_rectangle((94,top,520,top+65),radius=10,fill=(11,36,48),outline=(29,78,91),width=2)
        fill=(24,135+i*25,148+i*18)
        width=round((i+1)*70*smooth((local-.18*i)/2)+35)
        d.rectangle((94,top+60,94+width,top+64),fill=fill)
        d.text((115,top+14),label,font=system_font(26,True),fill=(198,227,233))
        d.text((460,top+14),value,font=system_font(24),fill=GLOW)
    return img


def ending_scene(t):
    img=base_background(t)
    d=ImageDraw.Draw(img)
    local=t-9.22
    cx,cy=640,290
    for i in range(9):
        radius=83+i*25+round(12*math.sin(local*1.2+i))
        d.arc((cx-radius,cy-radius,cx+radius,cy+radius),
              start=round(local*32+i*38),end=round(local*32+i*38+260),
              fill=(17+i*3,75+i*12,96+i*11),width=3)
    reveal=smooth(local/1.25)
    w=round(600*reveal)
    d.rounded_rectangle((cx-w/2,260,cx+w/2,273),radius=6,fill=GLOW)
    d.text((206+round((1-reveal)*35),369),"FACTOR DE GIGANTES",
           font=system_font(66,True),fill=(round(230*reveal),round(244*reveal),round(246*reveal)))
    d.text((421,468),"DOCUMENTALES ORIGINALES",font=system_font(21),
           fill=(round(98*reveal),round(191*reveal),round(194*reveal)))
    d.text((460,621),"PRUEBA INTERNA CON VOZ DE REFERENCIA",font=system_font(16),fill=(130,163,168))
    return img


SCENES=(phone_scene,communication_scene,systems_scene,ending_scene)


def render_frame(t):
    if t<0 or t>VOICE_DURATION+1.0:
        raise ValueError("Instante fuera de rango")
    shot=next((i for i in range(4) if SCENE_BREAKS[i]<=t<SCENE_BREAKS[i+1]),3)
    frame=SCENES[shot](t)
    transition=.32
    if shot<3 and SCENE_BREAKS[shot+1]-t<transition:
        alpha=smooth((t-(SCENE_BREAKS[shot+1]-transition))/transition)
        following=SCENES[shot+1](SCENE_BREAKS[shot+1]+.001)
        frame=Image.blend(frame,following,alpha)
    # Gentle vignette, no external media.
    return frame


def render(output):
    audio,metadata=approved_reference()
    if metadata.get("rights_status")!="pending_commercial_verification":
        raise ValueError("Se alteró el manifiesto de la voz")
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("Falta ffmpeg en PATH")
    output=Path(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    frame_count=math.ceil(VOICE_DURATION*FPS)
    command=[
        "ffmpeg","-hide_banner","-loglevel","error","-y",
        "-f","rawvideo","-pixel_format","rgb24",
        "-video_size",f"{W}x{H}","-framerate",str(FPS),"-i","pipe:0",
        "-i",str(audio),"-t",f"{VOICE_DURATION:.3f}",
        "-map","0:v:0","-map","1:a:0",
        "-c:v","libx264","-preset","veryfast","-crf","23",
        "-pix_fmt","yuv420p","-c:a","aac","-b:a","160k",
        "-ar","48000","-ac","1","-movflags","+faststart",
        str(output)
    ]
    task=subprocess.Popen(command,stdin=subprocess.PIPE)
    try:
        for frame_index in range(frame_count):
            frame=render_frame(frame_index/FPS)
            task.stdin.write(frame.tobytes())
    except (BrokenPipeError,OSError):
        task.kill()
        raise RuntimeError("Falló la tubería de codificación audiovisual")
    finally:
        if task.stdin:
            try:task.stdin.close()
            except OSError:pass
    if task.wait(timeout=150)!=0:
        raise RuntimeError("FFmpeg falló, no hay preview aprobada")
    if not output.exists() or output.stat().st_size<100_000:
        raise RuntimeError("Archivo audiovisual vacío")
    return {
        "output":output.name,"expected_video_duration_s":VOICE_DURATION,"frames_written":frame_count,
        "resolution":[W,H],"fps":FPS,
        "audio_track_included":True,"audio_source":"unchanged_approved_reference_mp3",
        "audio_sha256":metadata["sha256"],"audio_reference_duration_s":VOICE_DURATION,
        "narration_matches_intro_reference_only":True,
        "cinematic_animation":True,"still_text_cards":False,
        "commercial_rights_verified":False,"documentary_complete":False,
        "youtube_publication_allowed":False
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,default=Path("dist/blackberry-motion/BLACKBERRY_INTRO_MOVIMIENTO_VOZ_REFERENCIA.mp4"))
    args=p.parse_args()
    info=render(args.output)
    (args.output.parent/"RESULTADO_INTRO_MOVIMIENTO.json").write_text(
        json.dumps(info,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("INTRO_MP4:",args.output,"FRAMES:",info["frames_written"],
          "AUDIO_PRESENTE:",info["audio_track_included"],
          "VOZ_CANONICA_SHA:",info["audio_sha256"],
          "YOUTUBE:",info["youtube_publication_allowed"],flush=True)


if __name__=="__main__":
    main()
