"""Prueba acotada de Qwen3-TTS CPU local con voz sintética aprobada.

No es la voz de producción. Descarga pesos Apache-2.0 públicos y genera
solo una muestra corta; nunca sustituye el archivo aprobado ni publica video.
"""
import json
import time
from pathlib import Path
import subprocess
import tempfile

from tools.approved_voice import approved_reference,hash_file
from tools.documentary_pacing import run as pace

MODEL="Qwen/Qwen3-TTS-12Hz-0.6B-Base"
TEXT="Cuando una especie desaparece, su ausencia transforma el ecosistema. En los negocios ocurre algo parecido."

def run(output="dist/cpu-smoke-qwen"):
    import torch
    import soundfile as sf
    from qwen_tts import Qwen3TTSModel

    approved,manifest=approved_reference()
    torch.set_num_threads(4)
    target=Path(output)
    target.mkdir(parents=True,exist_ok=True)
    start=time.monotonic()
    print("Cargando modelo Qwen3-TTS Base 0.6B exclusivamente en CPU...",flush=True)
    model=Qwen3TTSModel.from_pretrained(
        MODEL,device_map="cpu",dtype=torch.float32,attn_implementation="sdpa"
    )
    model_seconds=round(time.monotonic()-start,2)
    with tempfile.TemporaryDirectory() as folder:
        ref=Path(folder)/"ref.wav"
        subprocess.run(["ffmpeg","-v","error","-y","-i",str(approved),
                        "-vn","-ac","1","-ar","24000","-c:a","pcm_s16le",str(ref)],
                       check=True,timeout=40)
        print("Modelo cargado; generando narración breve con referencia fija.",flush=True)
        with torch.inference_mode():
            audios,sr=model.generate_voice_clone(
                text=TEXT,language="Spanish",
                ref_audio=str(ref),ref_text=manifest["reference_text"])
        raw=Path(folder)/"raw.wav"
        sf.write(str(raw),audios[0],sr)
        final=target/"FactorDeGigantes_Qwen_Local_CPU.mp3"
        params=manifest["pacing"]
        pace_info=pace(raw,final,speed=params["atempo"],
                       pause_seconds=params["extra_pause_seconds"],
                       max_breaks=params["max_pauses"])
    if not 3 <= pace_info["duration"] <= 30 or final.stat().st_size<50000:
        raise RuntimeError("Audio de CPU inválido")
    report={
        "model":MODEL,"environment":"CPU 4 hilos GitHub Actions",
        "reference_sha256":hash_file(approved),
        "text":TEXT,"model_loading_seconds":model_seconds,
        "total_seconds":round(time.monotonic()-start,2),
        "pacing":pace_info,
        "voice_status":"prueba experimental no aprobada",
        "no_paid_api":True
    }
    (target/"cpu-metrics.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print("Prueba CPU terminada",json.dumps(report,ensure_ascii=False),flush=True)

if __name__=="__main__":
    run()
