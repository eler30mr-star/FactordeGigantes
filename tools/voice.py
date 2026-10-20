"""Motor de voz local de Factor de Gigantes. Sin API de pago ni claves."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.request

MODEL_NAME = "es_MX-ald-medium"
MODEL_SHA256 = "019b3803293c93e34a206dd2e53a3889209a514e786fd7144f7b70196c579b63"
MODEL_BASE = "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_MX/ald/medium/"
MODEL_CARD = "https://huggingface.co/rhasspy/piper-voices/blob/main/es/es_MX/ald/medium/MODEL_CARD"

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _download(url, destination, limit):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix="voz-", suffix=".partial", dir=destination.parent)
    partial = Path(name)
    try:
        with os.fdopen(fd, "wb") as file:
            request = urllib.request.Request(url, headers={"User-Agent": "FactorDeGigantes-Voice/1.0"})
            with urllib.request.urlopen(request, timeout=90) as response:
                size = 0
                for chunk in iter(lambda: response.read(1024 * 1024), b""):
                    size += len(chunk)
                    if size > limit:
                        raise ValueError("El modelo excede el límite de tamaño")
                    file.write(chunk)
        partial.replace(destination)
    finally:
        partial.unlink(missing_ok=True)

def ensure_voice(cache_dir):
    folder = Path(cache_dir).expanduser().resolve()
    model = folder / (MODEL_NAME + ".onnx")
    config = folder / (MODEL_NAME + ".onnx.json")
    if not model.is_file() or sha256(model) != MODEL_SHA256:
        _download(MODEL_BASE + model.name, model, 85 * 1024 * 1024)
    if sha256(model) != MODEL_SHA256:
        model.unlink(missing_ok=True)
        raise RuntimeError("Checksum de modelo Piper incorrecto")
    if not config.is_file():
        _download(MODEL_BASE + config.name, config, 80000)
    try:
        cfg = json.loads(config.read_text(encoding="utf-8"))
        if cfg["audio"]["sample_rate"] != 22050 or cfg["language"]["code"] != "es_MX":
            raise ValueError("Modelo o idioma incorrecto")
    except (ValueError, KeyError, TypeError, OSError) as exc:
        config.unlink(missing_ok=True)
        raise RuntimeError("Archivo de configuración de Piper inválido") from exc
    return model

def synthesize(text, destination, engine, cache_dir):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Narración vacía")
    output = Path(destination)
    output.parent.mkdir(parents=True, exist_ok=True)
    if engine == "piper":
        model = ensure_voice(cache_dir)
        cmd = [sys.executable, "-m", "piper", "-m", str(model), "-f", str(output), "--", text]
    elif engine == "espeak":
        cmd = ["espeak-ng", "-v", "es", "-s", "155", "-w", str(output), text]
    else:
        raise ValueError("Motor de voz no permitido")
    subprocess.run(cmd, check=True, timeout=180, stdout=subprocess.DEVNULL)
    if not output.is_file() or output.stat().st_size < 128:
        raise RuntimeError("La síntesis no generó audio WAV")

def credits(engine):
    if engine == "piper":
        return ("Motor Piper TTS (GPL-3.0-or-later): https://github.com/OHF-Voice/piper1-gpl\n"
                + "Modelo " + MODEL_NAME + ": " + MODEL_CARD + "\n"
                + "El MODEL_CARD declara dataset bajo Unlicense y derivación de otra voz. "
                + "Verificar derechos del modelo derivado antes de distribución comercial.\n")
    return "Voz de prueba eSpeak NG; no publicar.\n"
