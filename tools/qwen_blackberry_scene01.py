"""Primera escena narrada REAL de BlackBerry, Qwen Base 1.7B CPU.

Cuatro fragmentos exactos del guion completo (Escena 01), sin cambiar
la identidad canónica ni habilitar publicación. Cada clip requiere audición.
"""
from __future__ import annotations
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time

from tools.approved_voice import approved_reference, hash_file
from tools.documentary_pacing import run as pace
from tools.qwen_longform_probe import probe_mp3, build_preview

ROOT = Path("research/blackberry/GUION_DOCUMENTAL_11MIN_NO_APROBADO.md")
OUTPUT = Path("dist/blackberry-escena01-voz")
MODEL = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
NAMES = ("01_teclado", "02_segunda_historia", "03_pregunta", "04_seguiremos")
MAX_CHARS = 260
MIN_CHARS = 150
MAX_LENGTH_SECONDS = 42
MAX_TOTAL_SECONDS = 165
SEED = 20261021


def scene_one(text):
    match = re.search(
        r"^## Escena 01[^\n]*\n(?P<section>.*?)(?=^## Escena 02)",
        text, re.S | re.M,
    )
    if match is None:
        raise ValueError("No se encontraron las escenas 01 y 02")
    narrator = re.search(
        r"\*\*NARRADOR\*\*\s*(.*?)\s*\*\*FUENTES POR COMPROBAR:\*\*",
        match.group("section"), re.S,
    )
    if not narrator:
        raise ValueError("El texto del narrador no tiene cierre")
    return " ".join(narrator.group(1).split())


def split_for_speech(narration):
    # Conserva las frases originales; no resume ni inventa texto.
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚ¿])", narration)
    groups = []
    active = ""
    for sentence in sentences:
        proposed = (active + " " + sentence).strip()
        if len(proposed) > MAX_CHARS and active:
            groups.append(active)
            active = sentence
        else:
            active = proposed
    if active:
        groups.append(active)
    if len(groups) != len(NAMES) or any(not MIN_CHARS <= len(x) <= MAX_CHARS for x in groups):
        raise ValueError("La escena 01 cambió: la segmentación debe revisarse manualmente")
    if " ".join(groups) != narration:
        raise RuntimeError("La segmentación perdió palabras del guion original")
    return list(zip(NAMES, groups))


def get_cases():
    return split_for_speech(scene_one(ROOT.read_text(encoding="utf-8")))


def report_for_review(clips,reference_hash,joined,elapsed):
    if len(clips)!=4 or any(x.get("auditory_approval")!="pending" for x in clips):
        raise ValueError("No se declara aprobado un lote incompleto")
    return {
        "product":"Factor de Gigantes",
        "episode":"BlackBerry",
        "chapter":1,
        "source_manuscript":str(ROOT),
        "purpose":"first_scene_experimental_voice",
        "model":MODEL,
        "cpu_only":True,"paid_api":False,
        "source_text_matches_manuscript":True,
        "canonical_reference_sha256":reference_hash,
        "canonical_reference_changed":False,
        "clips":clips,
        "preview_mp3":{"file":"05_escena01_unida.mp3","duration_seconds":joined},
        "elapsed_generation_seconds":round(elapsed,2),
        "owner_approved_new_takes":False,
        "human_listening_review":"pending",
        "commercial_rights_verified":False,
        "documentary_render_approved":False,
        "youtube_publication_enabled":False,
    }


def run(out=OUTPUT):
    import torch
    import soundfile as sf
    from qwen_tts import Qwen3TTSModel

    reference,metadata=approved_reference()
    cases=get_cases()
    initial_sha=hash_file(reference)
    target=Path(out)
    target.mkdir(parents=True,exist_ok=True)
    torch.set_num_threads(4)
    torch.manual_seed(SEED)
    clock=time.monotonic()
    model=Qwen3TTSModel.from_pretrained(
        MODEL,device_map="cpu",dtype=torch.float32,attn_implementation="sdpa"
    )
    clips=[]
    with tempfile.TemporaryDirectory() as dirname:
        temp=Path(dirname)
        reference_wav=temp/"reference_24khz.wav"
        subprocess.run(["ffmpeg","-v","error","-y","-i",str(reference),
                        "-vn","-ac","1","-ar","24000","-c:a","pcm_s16le",str(reference_wav)],
                       check=True,timeout=45)
        for name,text in cases:
            if hash_file(reference)!=initial_sha:
                raise RuntimeError("La referencia aprobada ha cambiado")
            started=time.monotonic()
            print("GENERANDO:",name,"caracteres:",len(text),flush=True)
            with torch.inference_mode():
                samples,sample_rate=model.generate_voice_clone(
                    text=text,language="Spanish",ref_audio=str(reference_wav),
                    ref_text=metadata["reference_text"]
                )
            raw=temp/(name+".wav")
            sf.write(str(raw),samples[0],sample_rate)
            output=target/(name+".mp3")
            pacing=metadata["pacing"]
            pace(raw,output,speed=pacing["atempo"],
                 pause_seconds=pacing["extra_pause_seconds"],
                 max_breaks=pacing["max_pauses"])
            seconds=probe_mp3(output)
            if not 7<=seconds<=MAX_LENGTH_SECONDS or output.stat().st_size<60_000:
                raise RuntimeError("Audio fuera de límites: "+name)
            clips.append({
                "id":name,"file":output.name,
                "text":text,"length_s":seconds,
                "sha256":hash_file(output),
                "processing_seconds":round(time.monotonic()-started,2),
                "auditory_approval":"pending"
            })
            print("CLIP:",name,seconds,"segundos",flush=True)
        joinfile=target/"05_escena01_unida.mp3"
        seconds=build_preview([target/(name+".mp3") for name,_ in cases],joinfile,temp)
    if seconds>MAX_TOTAL_SECONDS or seconds<sum(c["length_s"] for c in clips)-.5:
        raise RuntimeError("Duración inesperada del bloque montado")
    if hash_file(reference)!=initial_sha:
        raise RuntimeError("La voz canónica fue modificada")
    original_copy=target/"00_referencia_original.mp3"
    shutil.copyfile(reference,original_copy)
    if hash_file(original_copy)!=initial_sha:
        raise RuntimeError("La copia no coincide con la referencia")
    report=report_for_review(clips,initial_sha,seconds,time.monotonic()-clock)
    (target/"ESTADO_ESCENA01_VOZ.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (target/"GUIA_AUDICION.txt").write_text(
        "FACTOR DE GIGANTES · ESCENA 01 BLACKBERRY\n"
        "Escuchar la voz canónica 00, los 4 fragmentos y el montaje 05.\n"
        "Comparar timbre, naturalidad, pronunciación de BlackBerry, fluidez y pausas.\n"
        "No sustituir el audio aprobado, ni asumir licencia comercial ni publicar.\n",
        encoding="utf-8"
    )
    print("ESCENA01_AUDIO_REAL:",round(seconds,3),
          "segundos; clips:4; nuevo audio humano aprobado:NO",flush=True)
    return report


if __name__=="__main__":
    run()
