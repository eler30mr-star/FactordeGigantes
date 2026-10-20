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

# Candidatas para audición. La lista no constituye autorización de publicación.
VOICE_CATALOG = {
    MODEL_NAME: {
        "sha256": MODEL_SHA256,
        "base": MODEL_BASE,
        "card": MODEL_CARD,
        "language": "es_MX",
        "description": "Voz actual de referencia, español latinoamericano",
    },
    "es_MX-claude-high": {
        "sha256": "3ef40a71ea63852cd8ab7e6fa7d2ecdcfa67a0b47c9c48e3f10e02ee02083ea0",
        "base": "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_MX/claude/high/",
        "card": "https://huggingface.co/rhasspy/piper-voices/blob/main/es/es_MX/claude/high/MODEL_CARD",
        "language": "es_MX",
        "description": "Candidata de mayor calidad del catálogo Piper; evaluar timbre",
    },
    "es_ES-davefx-medium": {
        "sha256": "6658b03b1a6c316ee4c265a9896abc1393353c2d9e1bca7d66c2c442e222a917",
        "base": "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/medium/",
        "card": "https://huggingface.co/rhasspy/piper-voices/blob/main/es/es_ES/davefx/medium/MODEL_CARD",
        "language": "es_ES",
        "description": "Candidata castellana, escuchar antes de elegir",
    },
}

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

def ensure_voice(cache_dir, model_name=MODEL_NAME):
    """Cargar solo modelos declarados y verificados mediante checksum."""
    if model_name not in VOICE_CATALOG:
        raise ValueError("Voz no autorizada en el catálogo de pruebas")
    spec = VOICE_CATALOG[model_name]
    folder = Path(cache_dir).expanduser().resolve()
    model = folder / (model_name + ".onnx")
    config = folder / (model_name + ".onnx.json")
    if not model.is_file() or sha256(model) != spec["sha256"]:
        _download(spec["base"] + model.name, model, 85 * 1024 * 1024)
    if sha256(model) != spec["sha256"]:
        model.unlink(missing_ok=True)
        raise RuntimeError("Checksum de modelo Piper incorrecto")
    if not config.is_file():
        _download(spec["base"] + config.name, config, 80000)
    try:
        cfg = json.loads(config.read_text(encoding="utf-8"))
        if cfg["audio"]["sample_rate"] != 22050 or cfg["language"]["code"] != spec["language"]:
            raise ValueError("Modelo o idioma incorrecto")
    except (ValueError, KeyError, TypeError, OSError) as exc:
        config.unlink(missing_ok=True)
        raise RuntimeError("Archivo de configuración de Piper inválido") from exc
    return model

def synthesize(text, destination, engine, cache_dir, model_name=MODEL_NAME):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Narración vacía")
    output = Path(destination)
    output.parent.mkdir(parents=True, exist_ok=True)
    if engine == "piper":
        model = ensure_voice(cache_dir, model_name)
        cmd = [sys.executable, "-m", "piper", "-m", str(model), "-f", str(output), "--", text]
    elif engine == "espeak":
        cmd = ["espeak-ng", "-v", "es", "-s", "155", "-w", str(output), text]
    else:
        raise ValueError("Motor de voz no permitido")
    subprocess.run(cmd, check=True, timeout=180, stdout=subprocess.DEVNULL)
    if not output.is_file() or output.stat().st_size < 128:
        raise RuntimeError("La síntesis no generó audio WAV")

def credits(engine, model_name=MODEL_NAME):
    if engine == "piper":
        if model_name not in VOICE_CATALOG:
            raise ValueError("Voz no autorizada")
        return ("Motor Piper TTS (GPL-3.0-or-later): https://github.com/OHF-Voice/piper1-gpl\n"
                + "Modelo " + model_name + ": " + VOICE_CATALOG[model_name]["card"] + "\n"
                + "Audición técnica. Verificar licencia del modelo y su entrenamiento antes de publicación comercial.\n")
    return "Voz de prueba eSpeak NG; no publicar.\n"
