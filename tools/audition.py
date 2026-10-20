#!/usr/bin/env python3
"""Audición A/B de voces locales. No cambia el narrador del canal ni publica."""
import json
from pathlib import Path
import subprocess
import wave

from tools.voice import MODEL_NAME, VOICE_CATALOG, synthesize

SCRIPT = (
    "Durante años, una empresa dominó el mundo de la comunicación móvil. "
    "Pero una decisión cambió su destino. "
    "Esta es la historia de BlackBerry, y del momento en que el liderazgo dejó de ser suficiente."
)
CANDIDATES = [
    MODEL_NAME,
    "es_MX-claude-high",
    "es_ES-davefx-medium",
]

def create_audition(output_dir, cache_dir):
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    summary = []
    for name in CANDIDATES:
        path = root / f"{name}.wav"
        synthesize(SCRIPT, path, "piper", cache_dir, model_name=name)
        with wave.open(str(path), "rb") as audio:
            seconds = audio.getnframes() / audio.getframerate()
            if audio.getnchannels() != 1 or seconds < 4:
                raise RuntimeError(f"Muestra de voz incompleta: {name}")
            sample_rate = audio.getframerate()
        spec = VOICE_CATALOG[name]
        summary.append({
            "model": name,
            "language": spec["language"],
            "model_card": spec["card"],
            "seconds": round(seconds, 2),
            "sample_rate": sample_rate,
            "comparison_script": SCRIPT,
            "license_status": "requires_review_before_commercial_publication",
            "role": "current_reference" if name == MODEL_NAME else "candidate",
        })
        print(f"{name}: {seconds:.1f}s, {path.stat().st_size} bytes", flush=True)
    (root / "comparacion.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="dist/audicion")
    parser.add_argument("--cache", default="~/.cache/factor-de-gigantes/voices")
    args = parser.parse_args()
    create_audition(args.output, args.cache)

if __name__ == "__main__":
    main()
