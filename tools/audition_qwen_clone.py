#!/usr/bin/env python3
"""Prueba de lectura con el MISMO timbre Qwen v3 mediante Voice Clone Base.

Origen: muestra sintética propia creada anteriormente en la demo pública Qwen3.
No se clona un ser humano ajeno, no hay API de pago ni modificación de render.
"""
import hashlib
import json
from pathlib import Path
import subprocess

from gradio_client import Client, handle_file

from tools.voice_lexicon import spoken_text

SPACE = "Qwen/Qwen3-TTS"
REFERENCE_NAME = "Qwen3_FactorDeGigantes_DiccionProfesional.mp3"
REFERENCE_SHA256 = "e03ee9359a0323d958279ea22ccb37f07aafd681dcd36667a0d318214c06e675"
REFERENCE_TEXT = (
    "Durante años, BlackBerry parecía invencible. "
    "Sus decisiones definían el futuro de la comunicación. "
    "Hasta que una nueva generación cambió las reglas. "
    "Esto es Factor de Gigantes."
)
EDITORIAL_TEXT = (
    "Durante años, BlackBerry parecía invencible. "
    "Sus decisiones definían el futuro de la comunicación. "
    "Hasta que una nueva generación cambió las reglas. "
    "Esto es Factor de Gigantes."
)


def run(reference_dir="dist/referencia-qwen", output_dir="dist/audicion-blackberry"):
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    original = Path(reference_dir) / REFERENCE_NAME
    if not original.is_file():
        raise FileNotFoundError("Falta la muestra aprobada de Qwen v3")
    digest = hashlib.sha256(original.read_bytes()).hexdigest()
    if digest != REFERENCE_SHA256:
        raise RuntimeError("La muestra de referencia cambió de contenido")
    reference = directory / "voz_referencia_24000.wav"
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
         "-i", str(original), "-vn", "-ac", "1", "-ar", "24000",
         "-c:a", "pcm_s16le", str(reference)],
        check=True, timeout=30,
    )

    phrase = spoken_text(EDITORIAL_TEXT)
    assert "BlackBerry" not in phrase and phrase.count("Blákberri") == 1
    print("Control de nombre: BlackBerry (original) -> Blákberri (solo para el sintetizador)", flush=True)

    demo = Client(SPACE, verbose=False)
    result = demo.predict(
        handle_file(str(reference)), REFERENCE_TEXT, phrase,
        "Spanish", False, "1.7B", api_name="/generate_voice_clone"
    )
    if not isinstance(result, (tuple, list)) or len(result) < 2:
        raise RuntimeError("Formato de respuesta de Qwen Base inesperado")
    audio, status = result[:2]
    print("Respuesta de Qwen Voice Clone: " + str(status)[:280], flush=True)
    if audio is None:
        raise RuntimeError("Qwen no entregó audio de clonación")
    if isinstance(audio, dict) and "path" in audio:
        path = Path(audio["path"])
    elif isinstance(audio, str):
        path = Path(audio)
    else:
        raise RuntimeError("Archivo de audio con formato inesperado")
    if not path.is_file() or path.stat().st_size < 14000:
        raise RuntimeError("Respuesta incompleta")
    mp3 = directory / "FactorDeGigantes_BlackBerry_RR_Fuerte.mp3"
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
         "-i", str(path), "-vn", "-ac", "1",
         "-af", "highpass=f=70,loudnorm=I=-17:TP=-1.5:LRA=9",
         "-codec:a", "libmp3lame", "-b:a", "160k", str(mp3)],
        check=True, timeout=30,
    )
    info = json.loads(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", str(mp3)], text=True, timeout=20))
    duration = float(info["format"]["duration"])
    if not 4 <= duration <= 60 or mp3.stat().st_size < 20000:
        raise RuntimeError("Duración de audio inesperada")
    # No incluir la referencia en el artefacto: sólo resultado y procedencia.
    reference.unlink()
    (directory / "pronunciacion.json").write_text(json.dumps({
        "voice_provenance": "Qwen3 VoiceDesign v3 generada en este mismo proyecto",
        "voice_reference_sha256": REFERENCE_SHA256,
        "model": "Qwen3-TTS 1.7B Base Voice Clone",
        "language": "Spanish", "original_written": EDITORIAL_TEXT,
        "synthesized": phrase, "brand_written": "BlackBerry",
        "brand_spoken": "Blákberri",
        "seconds": duration, "cost": "public_demo_no_payment",
        "voice_status": "PENDING_USER_AUDIT_NOT_OFFICIAL",
        "notes": "El modelo intenta conservar timbre; identidad y dicción deben verificarse al oído."
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"MP3 corregido generado: {mp3} ({duration:.2f}s)", flush=True)


if __name__ == "__main__":
    run()
