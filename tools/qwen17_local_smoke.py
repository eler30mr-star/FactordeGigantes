"""Audición breve de Qwen3-TTS Base 1.7B en CPU, comparada con 0.6B.

Usar exclusivamente la referencia sintética aprobada. Solo experimento,
cero API pagada ni publicación. No sobreescribe ni modifica narrador aprobado.
"""
import json
import time
from pathlib import Path
import subprocess
import tempfile

from tools.approved_voice import approved_reference, hash_file
from tools.documentary_pacing import run as pacing

MODEL = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
TEXT = "Cuando una especie desaparece, su ausencia transforma el ecosistema. En los negocios ocurre algo parecido."
OUT = Path("dist/qwen17-cpu")

def run():
    import torch
    import soundfile as sf
    from qwen_tts import Qwen3TTSModel
    approved, manifest = approved_reference()
    assert manifest["model"] == "Qwen3-TTS-12Hz-1.7B-Base"
    torch.set_num_threads(4)
    OUT.mkdir(parents=True, exist_ok=True)
    t0=time.monotonic()
    print("Prueba local 1.7B iniciada: solo CPU, sin servicios de pago.",flush=True)
    model=Qwen3TTSModel.from_pretrained(
        MODEL, device_map="cpu", dtype=torch.float32, attn_implementation="sdpa"
    )
    loading=round(time.monotonic()-t0,2)
    print(f"1.7B cargado en CPU ({loading:.2f}s).",flush=True)
    with tempfile.TemporaryDirectory() as d:
        d=Path(d)
        ref=d/"ref.wav"
        subprocess.run(["ffmpeg","-v","error","-y","-i",str(approved),
                        "-vn","-ac","1","-ar","24000","-c:a","pcm_s16le",str(ref)],
                       check=True,timeout=40)
        with torch.inference_mode():
            clips, rate=model.generate_voice_clone(text=TEXT, language="Spanish",
                ref_audio=str(ref), ref_text=manifest["reference_text"])
        raw=d/"raw.wav"
        sf.write(str(raw),clips[0],rate)
        final=OUT/"FactorDeGigantes_Qwen_17B_CPU_Voz.mp3"
        profile=manifest["pacing"]
        result=pacing(raw,final,speed=profile["atempo"],
            pause_seconds=profile["extra_pause_seconds"],
            max_breaks=profile["max_pauses"])
    if not 3 <= result["duration"] <= 35 or final.stat().st_size < 50000:
        raise RuntimeError("La muestra no cumple duración/tamaño mínimos")
    report={
       "model":MODEL, "cpu_only":True, "paid_api":False,
       "voice_reference_sha256":hash_file(approved),
       "reference_status":"owner_approved_editorial_reference",
       "text":TEXT, "loading_seconds":loading,
       "total_execution_seconds":round(time.monotonic()-t0,2),
       "output_duration_seconds":result["duration"],"pacing":result,
       "owner_approval":"pending_audio_comparison",
       "production_ready":False
    }
    (OUT/"cpu-metrics.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    print("RESULT:",json.dumps(report,ensure_ascii=False),flush=True)

if __name__=="__main__":
    run()
