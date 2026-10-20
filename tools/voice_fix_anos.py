"""Ajuste LOCALIZADO del alargamiento 'aaños' de la muestra aprobada.

No sintetiza otra voz ni modifica el resto de palabras. Requiere numpy,
soundfile y ffmpeg. Los tiempos de edición son exclusivos de ESTA muestra;
el checksum impide aplicarlos inadvertidamente a un audio distinto.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile


REFERENCE_SHA256 = "9c608fe3d6c4a8280e14848a8fc3f3ac4d649ad403c727f2d833ea44cdf1c6bf"
START_SECONDS = 0.5945
END_SECONDS = 0.6595
CROSSFADE_SECONDS = .016


def shorten_initial_a(source: Path, target: Path):
    import numpy as np
    import soundfile as sf
    if hashlib.sha256(source.read_bytes()).hexdigest() != REFERENCE_SHA256:
        raise ValueError("El MP3 no coincide con la muestra documental aprobada")
    audio, sr = sf.read(source)
    if audio.ndim != 1 or sr != 48000:
        raise RuntimeError("Se esperaba un MP3 mono a 48 kHz")
    a = round(START_SECONDS * sr)
    b = round(END_SECONDS * sr)
    fade = round(CROSSFADE_SECONDS * sr)
    if not 0 < a < b < len(audio) or b + fade > len(audio):
        raise ValueError("Intervalo fuera de rango")
    x = np.asarray(audio, dtype=np.float64)
    ramp = .5 - .5 * np.cos(np.linspace(0, np.pi, fade))
    joined = x[a:a+fade] * (1-ramp) + x[b:b+fade] * ramp
    edited = np.concatenate((x[:a], joined, x[b+fade:]))
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as folder:
        wav = Path(folder) / "anos_sin_alargamiento.wav"
        sf.write(wav, edited, sr, subtype="PCM_24")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav),
                        "-c:a", "libmp3lame", "-b:a", "160k", str(target)],
                       check=True, timeout=45)
    if target.stat().st_size < 100000:
        raise RuntimeError("La salida está vacía o incompleta")
    return {"trimmed_vowel_ms": round((b-a)/sr * 1000, 1),
            "crossfade_ms": CROSSFADE_SECONDS * 1000,
            "original_brand": "BlackBerry", "modified_voice": False,
            "result_path": str(target)}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    args = parser.parse_args()
    print(json.dumps(shorten_initial_a(args.source, args.target), indent=2))
