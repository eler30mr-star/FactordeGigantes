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
    "Native Latin American Spanish male broadcast journalist, mature professional narrator for a factual business documentary. "
    "Clear, clean, focused, front-of-microphone studio speech with broadcast-standard diction and articulate delivery. "
    "Every word fully pronounced; crisp consonants, precise syllables, well-formed vowels and clear word boundaries. "
    "Firm well-supported voice, medium-low natural male register, direct confident projection, attentive and present. "
    "Measured medium conversational pace, controlled energy and purposeful emphasis. "
    "Smooth but decisive phrasing; short natural pauses at sentence boundaries. "
    "High intelligibility and authority, without slurring, trailing off, lazy mumbling, breathiness, hoarseness, "
    "nasal tone or radio-drama overacting. Professional news-documentary studio voice, neutral Latin American accent."
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
    final = directory / "Qwen3_FactorDeGigantes_DiccionProfesional.mp3"
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(source), "-vn", "-ac", "1",
        "-af", "highpass=f=70,loudnorm=I=-17:TP=-1.5:LRA=9",
        "-codec:a", "libmp3lame", "-b:a", "160k", str(final)
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
            "revision_reason": "El propietario considera v2 una voz vaga y poco profesional; exige dicción limpia, clara, entendible, sílabas y consonantes bien pronunciadas.",
            "same_text_as_previous": True,
            "audio_processing": "High-pass 70Hz; loudness normalization EBU R128 at -17 LUFS. No pitch-shifting or speech time-stretch.",
            "distribution": "test_only_not_for_youtube",
            "cost": "public_demo_no_payment",
        }, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Archivo real: {final}; duración {seconds:.1f} segundos", flush=True)

if __name__ == "__main__":
    run()
