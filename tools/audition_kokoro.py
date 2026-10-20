#!/usr/bin/env python3
"""Audición Kokoro en español: muestras locales, sin secretos ni publicación."""
import json
from pathlib import Path
import subprocess
import wave

TEXT = (
    "Hubo un tiempo en que BlackBerry parecía invencible. "
    "Sus teléfonos dominaban las decisiones de los ejecutivos y las grandes empresas. "
    "Sin embargo, una transformación del mercado puso a prueba su estrategia. "
    "En Factor de Gigantes analizamos las decisiones que cambiaron el mundo."
)
VOICES = ("em_alex", "em_santa")
REPO_ID = "hexgrad/Kokoro-82M"

def generate(output):
    import numpy as np
    import soundfile as sf
    from kokoro import KPipeline

    root = Path(output)
    root.mkdir(parents=True, exist_ok=True)
    pipeline = KPipeline(lang_code="e", repo_id=REPO_ID, device="cpu")
    samples = []
    for voice in VOICES:
        chunks = []
        for _, _, audio in pipeline(TEXT, voice=voice, speed=0.96):
            if audio is not None:
                block = audio.detach().cpu().numpy() if hasattr(audio, "detach") else np.asarray(audio)
                if block.size:
                    chunks.append(block.reshape(-1))
        if not chunks:
            raise RuntimeError(f"Kokoro no produjo audio: {voice}")
        sound = np.concatenate(chunks)
        path = root / f"{voice}.wav"
        sf.write(str(path), sound, 24000, subtype="PCM_16")
        with wave.open(str(path), "rb") as f:
            duration = f.getnframes() / f.getframerate()
        if duration < 6 or path.stat().st_size < 200000:
            raise RuntimeError(f"Muestra incompleta: {voice} ({duration:.1f}s)")
        samples.append({"name": voice, "type": "unmodified_model",
                        "duration_seconds": round(duration, 2),
                        "filename": path.name, "source": REPO_ID,
                        "language": "Spanish", "publication_status": "audition_only"})
        print(f"Kokoro {voice}: {duration:.1f}s", flush=True)

    # Procesado leve opcional: una variante de la misma voz, no una voz distinta.
    variant = root / "em_alex_grave_sutil.wav"
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(root / "em_alex.wav"),
        "-af", "asetrate=22560,aresample=24000,atempo=1.06383",
        "-ac", "1", "-ar", "24000", str(variant)
    ], check=True, timeout=45)
    if variant.stat().st_size < 200000:
        raise RuntimeError("La variante grave no contiene audio completo")
    samples.append({"name": "em_alex_grave_sutil", "type": "processed_variant",
                    "filename": variant.name, "source": REPO_ID,
                    "note": "Misma voz em_alex con tono -6% y duración casi constante",
                    "publication_status": "audition_only"})
    (root / "comparacion.json").write_text(json.dumps(
        {"script": TEXT, "engine": "Kokoro 82M", "model_license": "Apache-2.0",
         "note": "Escuchar antes de seleccionar; auditar procedencia de voces.",
         "samples": samples}, ensure_ascii=False, indent=2), encoding="utf-8")
    return samples

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="dist/audicion-kokoro")
    args = p.parse_args()
    generate(args.out)
