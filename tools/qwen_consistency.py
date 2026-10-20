"""Audición puntual de continuidad vocal con la muestra APROBADA en el repositorio.

El proveedor es la demo pública gratuita de Qwen; NO es proveedor final
de producción, ni garantía de derechos comerciales ni de cuota ilimitada.
"""
import json
from pathlib import Path
import subprocess
import tempfile

from tools.approved_voice import approved_reference, hash_file
from tools.documentary_pacing import run as pace
from tools.voice_lexicon import spoken_text

SPACE = "Qwen/Qwen3-TTS"
EDITORIAL_TEXT = (
    "Cuando una especie desaparece, su ausencia transforma el ecosistema. "
    "En los negocios ocurre algo parecido: una decisión puede cambiar el destino "
    "de una industria. Esto es Factor de Gigantes."
)

def validate_text(text):
    if not isinstance(text, str) or not 40 <= len(text.strip()) <= 230:
        raise ValueError("El ensayo requiere entre 40 y 230 caracteres")
    if "\n" in text or "\r" in text:
        raise ValueError("El ensayo requiere un solo párrafo")
    return spoken_text(text.strip())


def synthesize_once(text=EDITORIAL_TEXT, output_dir="dist/continuidad-qwen"):
    from gradio_client import Client, handle_file
    reference, meta = approved_reference()
    spoken = validate_text(text)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as folder:
        tmp = Path(folder)
        wav = tmp / "reference.wav"
        subprocess.run(["ffmpeg","-v","error","-y","-i",str(reference),
                        "-vn","-ac","1","-ar","24000","-c:a","pcm_s16le",str(wav)],
                       check=True, timeout=35)
        client = Client(SPACE, verbose=False)
        response = client.predict(
            handle_file(str(wav)), meta["reference_text"], spoken,
            "Spanish", False, "1.7B", api_name="/generate_voice_clone"
        )
        if not isinstance(response,(list,tuple)) or len(response)<2:
            raise RuntimeError("Qwen devolvió una respuesta incompleta")
        audio, status = response[:2]
        print("Qwen:",str(status)[:200],flush=True)
        if isinstance(audio,dict):
            audio = audio.get("path")
        if not isinstance(audio,str) or not Path(audio).is_file():
            raise RuntimeError("El modelo no entregó un audio reproducible")
        raw = tmp / "audio_original.mp3"
        subprocess.run(["ffmpeg","-v","error","-y","-i",audio,"-vn","-ac","1",
                        "-codec:a","libmp3lame","-b:a","160k",str(raw)],
                       check=True,timeout=30)
        final = out / "FactorDeGigantes_Prueba_Continuidad_Voz.mp3"
        details = pace(raw,final,speed=meta["pacing"]["atempo"],
                       pause_seconds=meta["pacing"]["extra_pause_seconds"],
                       max_breaks=meta["pacing"]["max_pauses"])
    if not 6 <= details["duration"] <= 50 or final.stat().st_size < 80000:
        raise RuntimeError("La muestra no pasó validación de duración y tamaño")
    report = {
        "origin":"Qwen3-TTS 1.7B Base con muestra fija aprobada",
        "voice_reference_sha256":hash_file(reference),
        "editorial_text":text,"tts_text":spoken,
        "duration_seconds":details["duration"],
        "pacing":details,"status":"pendiente_de_validacion_auditiva",
        "permission":"audicion_prueba_sin_uso_comercial_automatico",
        "paid_services":False
    }
    (out/"ficha.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print("Continuidad generada:",final,"duración",details["duration"],"seg",flush=True)
    return final,report


if __name__=="__main__":
    synthesize_once()
