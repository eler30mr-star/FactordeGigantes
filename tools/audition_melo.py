"""Prueba de voz MeloTTS en CPU, sin servicios externos de pago."""
from pathlib import Path
import json
import wave

TEXT = (
    "Durante años, una empresa dominó el mercado de los teléfonos inteligentes. "
    "Sus decisiones parecían incuestionables. "
    "Hasta que una nueva tecnología cambió las reglas del juego. "
    "En Factor de Gigantes investigamos las decisiones que cambiaron el mundo."
)

def generate(folder="dist/voz-melotts"):
    from melo.api import TTS
    out = Path(folder)
    out.mkdir(parents=True, exist_ok=True)
    model = TTS(language="ES", device="cpu")
    ids = model.hps.data.spk2id
    if "ES" not in ids:
        raise RuntimeError("Falta la voz ES en MeloTTS")
    samples = []
    for speed, label in [(1.0, "melo_normal"), (0.9, "melo_pausada")]:
        wav = out / (label + ".wav")
        model.tts_to_file(TEXT, ids["ES"], str(wav), speed=speed)
        with wave.open(str(wav), "rb") as file:
            seconds = file.getnframes() / file.getframerate()
            rate = file.getframerate()
        if seconds < 6 or wav.stat().st_size < 100000:
            raise RuntimeError(f"Audio incompleto: {wav}")
        samples.append({
            "file": wav.name, "speed": speed,
            "duration_seconds": round(seconds, 2), "sample_rate": rate,
            "engine": "MeloTTS-Spanish", "license": "MIT",
            "voice_decision": "audition_only_not_approved"
        })
        print(f"{wav.name}: {seconds:.1f}s / {rate} Hz", flush=True)
    (out / "ficha.json").write_text(
        json.dumps({"script": TEXT, "samples": samples,
                    "model": "myshell-ai/MeloTTS-Spanish",
                    "source": "https://huggingface.co/myshell-ai/MeloTTS-Spanish",
                    "publication": "none"}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    return samples

if __name__ == "__main__":
    generate()
