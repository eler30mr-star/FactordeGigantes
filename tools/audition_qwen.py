#!/usr/bin/env python3
"""Audición puntual y gratuita con Space oficial Qwen3-TTS Voice Design.

No llama APIs de facturación, no usa credenciales, no clona personas reales.
Resultado sujeto a colas y límites de Hugging Face ZeroGPU.
"""
import json
from pathlib import Path
import shutil
import subprocess

from gradio_client import Client

TEXT = (
    "Durante años, BlackBerry parecía invencible. "
    "Sus decisiones definían el futuro de la comunicación. "
    "Hasta que una nueva generación cambió las reglas. "
    "Esto es Factor de Gigantes."
)
DESCRIPTION = (
    "An energetic yet sophisticated Latin American Spanish male documentary storyteller, "
    "with the naturally resonant, warm and full-bodied voice of a mature professional host. "
    "Deliver this narration with captivating forward momentum and strong presence, not slow or sleepy. "
    "Medium-brisk conversational pace, vivid human intonation, compelling rising suspense, "
    "expressive emphasis on 'BlackBerry', 'invencible', 'cambió las reglas' and 'Factor de Gigantes'. "
    "Dynamic rhythm and audible enthusiasm for a remarkable business story. "
    "Crisp articulation and clear Latin American Spanish vowels; confident, intriguing, alive, "
    "engaging and credible without shouting or imitating a movie trailer. "
    "Authentically masculine adult voice, not robotic, not artificially lowered."
)
SPACE = "Qwen/Qwen3-TTS"

def run(output="dist/audicion-qwen"):
    directory = Path(output)
    directory.mkdir(parents=True, exist_ok=True)
    print("Usando Space oficial público, sin token ni servicios facturables.", flush=True)
    client = Client(SPACE, verbose=False)
    result = client.predict(TEXT, "Spanish", DESCRIPTION, api_name="/generate_voice_design")
    if not isinstance(result, (tuple, list)) or len(result) < 2:
        raise RuntimeError("Respuesta de demo Qwen distinta de la esperada")
    audio, status = result[0], result[1]
    print("Estado Qwen: " + str(status)[:260], flush=True)
    if audio is None:
        raise RuntimeError("El Space no entregó un archivo de audio")
    if isinstance(audio, str):
        source = Path(audio)
    elif isinstance(audio, dict) and audio.get("path"):
        source = Path(audio["path"])
    elif isinstance(audio, (tuple, list)) and audio and isinstance(audio[0], str):
        source = Path(audio[0])
    else:
        raise RuntimeError("El Space devolvió formato de audio desconocido: " + str(type(audio)))
    if not source.is_file() or source.stat().st_size < 12000:
        raise RuntimeError("El archivo recibido no existe o está incompleto")
    final = directory / "Qwen3_FactorDeGigantes_MasEnergia.mp3"
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(source), "-vn", "-ac", "1", "-codec:a", "libmp3lame", "-b:a", "160k", str(final)
    ], check=True, timeout=35)
    analysis = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries",
        "stream=codec_type,codec_name,sample_rate:format=duration",
        "-of", "json", str(final)
    ], text=True, timeout=20)
    info = json.loads(analysis)
    seconds = float(info["format"]["duration"])
    if not 4 <= seconds <= 90 or final.stat().st_size < 20000:
        raise RuntimeError("Audio no válido por tamaño o duración")
    (directory / "audicion.json").write_text(
        json.dumps({
            "engine": "Qwen3-TTS-12Hz-1.7B-VoiceDesign",
            "space": SPACE,
            "text": TEXT,
            "voice_description": DESCRIPTION,
            "language": "Spanish",
            "seconds": seconds,
            "status": "demo_not_official_voice",
            "voice_decision": "PENDING_HUMAN_REVIEW",
            "revision_reason": "El propietario considera la primera muestra demasiado calmada; solicita más energía manteniendo madurez y naturalidad.",
            "same_text_as_previous": True,
            "distribution": "test_only_not_for_youtube",
            "cost": "public_demo_no_payment",
        }, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Archivo real: {final}; duración {seconds:.1f} segundos", flush=True)

if __name__ == "__main__":
    run()
