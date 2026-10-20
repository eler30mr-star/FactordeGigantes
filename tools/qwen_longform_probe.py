"""Ensayo de 3 párrafos enlazados con Qwen3 1.7B, CPU local, sin servicios de pago.

No reproduce un documental real: el caso editorial es HIPOTÉTICO. La muestra
canónica aprobada solo condiciona el timbre, jamás se modifica ni reemplaza.
Los audios nuevos requieren una NUEVA escucha humana, aunque el test sea verde.
"""
import json
import shutil
import subprocess
import tempfile
import time
import wave
from pathlib import Path

from tools.approved_voice import approved_reference, hash_file
from tools.documentary_pacing import run as apply_pacing

MODEL = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
OUTPUT = Path("dist/continuidad-tres-parrafos")
SEED = 20261020
PARAGRAPHS = (
    ("01_apertura", "Imagina una empresa que dominó su mercado durante años. Sus directivos confiaban tanto en el éxito obtenido, que dejaron de observar cómo cambiaban las necesidades de sus clientes. La primera señal parecía pequeña."),
    ("02_conflicto", "Mientras el equipo defendía las decisiones del pasado, surgieron competidores con ideas distintas. No tenían los mismos recursos, pero entendieron algo esencial: la innovación empieza cuando se escucha al usuario."),
    ("03_cierre", "Esta historia hipotética nos recuerda que ningún liderazgo está garantizado. El reto no es adivinar cada cambio, sino reconocer a tiempo cuándo debe evolucionar una estrategia. Ese es el factor detrás de un gigante."),
)
MIN_CLIP_SECONDS = 7
MAX_CLIP_SECONDS = 50
MAX_TOTAL_SECONDS = 145
MIN_CLIP_BYTES = 60_000
GAP_SECONDS = 0.38


def validate_paragraphs(paragraphs, reference_text):
    if not isinstance(paragraphs, (tuple, list)) or len(paragraphs) != 3:
        raise ValueError("Este ensayo permite exactamente tres párrafos")
    names, phrases = set(), set()
    for index, item in enumerate(paragraphs, 1):
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            raise ValueError("Cada párrafo requiere id y texto")
        name, phrase = item
        if name != f"{index:02d}_{('apertura','conflicto','cierre')[index-1]}":
            raise ValueError("ID fuera de orden o no permitido")
        if not isinstance(phrase, str) or not 150 <= len(phrase) <= 260:
            raise ValueError("Texto fuera del límite acotado de prueba")
        if phrase != phrase.strip() or any(c in phrase for c in "\r\n\x00"):
            raise ValueError("El guion debe ser un párrafo sin saltos de línea")
        if phrase.casefold() in phrases or phrase.casefold() == reference_text.casefold():
            raise ValueError("No repetir el texto canónico ni otro párrafo")
        names.add(name)
        phrases.add(phrase.casefold())
    if sum(len(p) for _, p in paragraphs) > 750:
        raise ValueError("Presupuesto de caracteres rebasado")
    return True


def probe_mp3(path):
    data = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries",
        "stream=codec_name,sample_rate,channels:format=duration",
        "-of", "json", str(path)], text=True, timeout=25))
    streams = data.get("streams", [])
    if len(streams) != 1 or streams[0].get("codec_name") != "mp3":
        raise RuntimeError("Se esperaba MP3 de un solo canal de audio")
    if (int(streams[0].get("sample_rate", 0)), streams[0].get("channels")) != (48000, 1):
        raise RuntimeError("Formato del MP3 no coincide con el contrato")
    return round(float(data["format"]["duration"]), 3)


def build_preview(parts, destination, tempdir):
    """Unir copias de audios generados con silencio entre frases, sin cortar fonemas."""
    frame_rate, frame_width = 48000, 2
    pcm = bytearray()
    for index, part in enumerate(parts):
        decoded = tempdir / f"part_{index}.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(part),
                        "-ac", "1", "-ar", str(frame_rate), "-c:a", "pcm_s16le",
                        str(decoded)], check=True, timeout=75)
        with wave.open(str(decoded), "rb") as recording:
            if (recording.getframerate(), recording.getsampwidth(), recording.getnchannels()) != (frame_rate, frame_width, 1):
                raise RuntimeError("WAV intermedio inválido")
            if index:
                pcm.extend(bytes(round(GAP_SECONDS * frame_rate) * frame_width))
            pcm.extend(recording.readframes(recording.getnframes()))
    joined = tempdir / "preview.wav"
    with wave.open(str(joined), "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(frame_width)
        writer.setframerate(frame_rate)
        writer.writeframes(pcm)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(joined),
                    "-c:a", "libmp3lame", "-b:a", "160k", str(destination)],
                   check=True, timeout=90)
    return probe_mp3(destination)


def report_result(reference_sha, clips, preview, elapsed):
    if len(clips) != 3 or not all(c["auditory_approval"] == "pending" for c in clips):
        raise ValueError("No declarar listo un lote incompleto o no revisado")
    return {
        "project": "Factor de Gigantes",
        "experiment": "continuidad_en_tres_parrafos_hipoteticos",
        "text_is_hypothetical": True,
        "model": MODEL, "cpu_only": True, "api_paid": False,
        "random_seed": SEED,
        "reference_sha256": reference_sha,
        "canonical_reference_untouched": True,
        "previous_owner_feedback": "ambas tomas cortas aceptables; 01_decision mas fiel",
        "clips": clips, "assembled_preview": preview,
        "elapsed_seconds_excluding_install": round(elapsed, 2),
        "owner_approved_new_clips": False,
        "human_identity_review": "pending",
        "commercial_rights_verified": False,
        "ready_for_documentary_render": False,
        "youtube_publication_enabled": False,
    }


def run(output=OUTPUT):
    import torch
    import soundfile as sf
    from qwen_tts import Qwen3TTSModel

    reference, manifest = approved_reference()
    if manifest.get("model") != "Qwen3-TTS-12Hz-1.7B-Base":
        raise RuntimeError("Modelo distinto del de la referencia canónica")
    validate_paragraphs(PARAGRAPHS, manifest["reference_text"])
    start = time.monotonic()
    original_hash = hash_file(reference)
    target = Path(output)
    target.mkdir(parents=True, exist_ok=True)
    torch.set_num_threads(4)
    torch.manual_seed(SEED)
    model = Qwen3TTSModel.from_pretrained(
        MODEL, device_map="cpu", dtype=torch.float32, attn_implementation="sdpa"
    )
    clips = []
    with tempfile.TemporaryDirectory() as folder:
        temp = Path(folder)
        source_wav = temp / "canonical-reference.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(reference),
                        "-vn", "-ac", "1", "-ar", "24000", "-c:a", "pcm_s16le",
                        str(source_wav)], check=True, timeout=45)
        for name, phrase in PARAGRAPHS:
            if hash_file(reference) != original_hash:
                raise RuntimeError("La referencia canónica cambió: bloquear proceso")
            print("Generando párrafo", name, flush=True)
            t0 = time.monotonic()
            with torch.inference_mode():
                audios, sr = model.generate_voice_clone(
                    text=phrase, language="Spanish", ref_audio=str(source_wav),
                    ref_text=manifest["reference_text"])
            if not len(audios):
                raise RuntimeError("El modelo no devolvió una forma de onda")
            raw_wav = temp / (name + ".wav")
            sf.write(str(raw_wav), audios[0], sr)
            final = target / (name + ".mp3")
            pace = manifest["pacing"]
            apply_pacing(raw_wav, final, speed=pace["atempo"],
                         pause_seconds=pace["extra_pause_seconds"],
                         max_breaks=pace["max_pauses"])
            duration = probe_mp3(final)
            if not MIN_CLIP_SECONDS <= duration <= MAX_CLIP_SECONDS or final.stat().st_size < MIN_CLIP_BYTES:
                raise RuntimeError(name + ": muestra no supera QA técnica")
            clips.append({
                "id": name, "file": final.name, "text": phrase,
                "duration_seconds": duration, "sha256": hash_file(final),
                "processing_seconds": round(time.monotonic() - t0, 2),
                "auditory_approval": "pending",
            })
        preview_file = target / "04_previsualizacion_unida.mp3"
        assembled = build_preview([target / (name + ".mp3") for name, _ in PARAGRAPHS],
                                  preview_file, temp)
    duration_sum = sum(c["duration_seconds"] for c in clips)
    if assembled > MAX_TOTAL_SECONDS or assembled < duration_sum - 0.5:
        raise RuntimeError("Duración concatenada fuera del presupuesto")
    if hash_file(reference) != original_hash:
        raise RuntimeError("La referencia canónica cambió")
    original_copy = target / "00_referencia_canónica.mp3"
    shutil.copyfile(reference, original_copy)
    if hash_file(original_copy) != original_hash:
        raise RuntimeError("La copia no coincide con el audio aprobado")
    preview = {
        "file": preview_file.name,
        "duration_seconds": assembled,
        "sha256": hash_file(preview_file),
        "gap_seconds": GAP_SECONDS,
        "generated_clips_count": len(clips),
        "not_for_publication": True,
    }
    report = report_result(original_hash, clips, preview, time.monotonic() - start)
    (target / "reporte_continuidad.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (target / "LEEME.txt").write_text(
        "FACTOR DE GIGANTES - SOLO AUDICIÓN EDITORIAL\n"
        "Escuche 00 (referencia original), los párrafos 01, 02, 03 y la versión 04 unida.\n"
        "Compare identidad vocal, dicción, transiciones, ritmo y ausencia de artefactos.\n"
        "El guion es HIPOTÉTICO, no relata hechos de una empresa real.\n"
        "Ninguna toma nueva está aprobada automáticamente. Uso comercial pendiente.\n",
        encoding="utf-8"
    )
    print("REPORTE_FINAL:", json.dumps(report, ensure_ascii=False), flush=True)
    return report


if __name__ == "__main__":
    run()
