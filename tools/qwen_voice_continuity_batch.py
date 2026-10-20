"""Audición EXPERIMENTAL de continuidad en dos fragmentos con Qwen Base 1.7B.

La muestra del propietario es inmutable. Este script NO genera el narrador
oficial, NO modifica render.yml y NO autoriza uso comercial ni publicación.
Prueba manual en CPU, con entradas fijas para limitar recursos gratuitos.
"""
import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from tools.approved_voice import approved_reference, hash_file
from tools.documentary_pacing import run as apply_pacing

MODEL = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
OUTPUT = Path("dist/continuidad-cpu-17b")
CASES = (
    ("01_decision", "A veces, una decisión silenciosa cambia el rumbo de una empresa. Lo que hoy parece pequeño, mañana puede mover una industria."),
    ("02_transformacion", "Detrás de cada gran transformación hay preguntas difíciles. Algunas compañías escuchan a tiempo; otras descubren demasiado tarde las consecuencias."),
)
MAX_OUTPUT_SECONDS = 35
MIN_OUTPUT_SECONDS = 3
MIN_OUTPUT_BYTES = 50_000


def validate_cases(cases, reference_text):
    """Protege contra lotes grandes, guiones arbitrarios y repetir la referencia."""
    if not isinstance(cases, (tuple, list)) or len(cases) != 2:
        raise ValueError("Este ensayo gratuito exige exactamente dos fragmentos fijos")
    seen_names, seen_texts = set(), set()
    for name, phrase in cases:
        if not isinstance(name, str) or not name.startswith(("01_", "02_")):
            raise ValueError("Identificador de fragmento no permitido")
        if name in seen_names or "/" in name or "\\" in name or ".." in name:
            raise ValueError("Identificador repetido o inseguro")
        if not isinstance(phrase, str) or not 60 <= len(phrase) <= 190:
            raise ValueError("Texto fuera de presupuesto de longitud")
        if "\n" in phrase or "\r" in phrase or phrase != phrase.strip():
            raise ValueError("El texto debe ser un párrafo limpio")
        if phrase.casefold() in seen_texts or phrase.casefold() == reference_text.casefold():
            raise ValueError("Una nueva toma no puede repetir el texto")
        seen_names.add(name)
        seen_texts.add(phrase.casefold())
    if {name[:2] for name, _ in cases} != {"01", "02"}:
        raise ValueError("Se requieren las tomas 01 y 02")
    return True


def make_report(reference_sha, clips, elapsed_seconds):
    if len(clips) != 2:
        raise ValueError("Faltan fragmentos; no se puede certificar el lote")
    return {
        "project": "Factor de Gigantes",
        "purpose": "audicion_de_continuidad_no_productiva",
        "model": MODEL,
        "hardware": "CPU",
        "paid_api": False,
        "reference_sha256": reference_sha,
        "reference_is_owner_approved": True,
        "generated_clips_owner_approved": False,
        "voice_identity_verified_by_human": False,
        "commercial_rights_verified": False,
        "production_ready": False,
        "youtube_publication_enabled": False,
        "elapsed_seconds_without_dependency_install": round(elapsed_seconds, 2),
        "clips": clips,
        "human_review": {
            "required": True,
            "status": "pending",
            "criteria": ["identidad vocal frente a referencia", "naturalidad", "diccion", "cadencia", "ausencia de defectos"],
        },
    }


def run(output=OUTPUT):
    import torch
    import soundfile as sf
    from qwen_tts import Qwen3TTSModel

    reference, meta = approved_reference()
    if meta.get("model") != "Qwen3-TTS-12Hz-1.7B-Base":
        raise RuntimeError("El modelo no coincide con el manifest de la referencia")
    validate_cases(CASES, meta["reference_text"])
    target = Path(output)
    target.mkdir(parents=True, exist_ok=True)
    original_sha = hash_file(reference)
    torch.set_num_threads(4)
    start = time.monotonic()
    print("Audición Qwen 1.7B en CPU (2 fragmentos, sin APIs pagadas).", flush=True)
    model = Qwen3TTSModel.from_pretrained(
        MODEL, device_map="cpu", dtype=torch.float32, attn_implementation="sdpa"
    )
    clips = []
    with tempfile.TemporaryDirectory() as folder:
        temp = Path(folder)
        ref_wav = temp / "referencia_24khz.wav"
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-i", str(reference), "-vn",
             "-ac", "1", "-ar", "24000", "-c:a", "pcm_s16le", str(ref_wav)],
            check=True, timeout=45,
        )
        for name, phrase in CASES:
            if hash_file(reference) != original_sha:
                raise RuntimeError("La muestra canónica fue alterada: suspender prueba")
            print("Sintetizando", name, flush=True)
            t0 = time.monotonic()
            with torch.inference_mode():
                audios, sample_rate = model.generate_voice_clone(
                    text=phrase,
                    language="Spanish",
                    ref_audio=str(ref_wav),
                    ref_text=meta["reference_text"],
                )
            raw = temp / (name + ".wav")
            sf.write(str(raw), audios[0], sample_rate)
            final = target / (name + ".mp3")
            pace = meta["pacing"]
            details = apply_pacing(
                raw, final, speed=pace["atempo"],
                pause_seconds=pace["extra_pause_seconds"],
                max_breaks=pace["max_pauses"],
            )
            duration = details["duration"]
            if not MIN_OUTPUT_SECONDS <= duration <= MAX_OUTPUT_SECONDS:
                raise RuntimeError(name + ": duración fuera de límites")
            if final.stat().st_size < MIN_OUTPUT_BYTES:
                raise RuntimeError(name + ": archivo de audio incompleto")
            clips.append({
                "id": name,
                "text": phrase,
                "file": final.name,
                "sha256": hash_file(final),
                "duration_seconds": round(duration, 3),
                "generation_and_processing_seconds": round(time.monotonic() - t0, 2),
                "pacing": details,
                "auditory_approval": "pending",
            })

    if hash_file(reference) != original_sha:
        raise RuntimeError("La referencia canónica cambió durante la prueba")
    comparison = target / "00_referencia_aprobada.mp3"
    shutil.copyfile(reference, comparison)
    if hash_file(comparison) != original_sha:
        raise RuntimeError("La copia de referencia no coincide byte a byte")
    report = make_report(original_sha, clips, time.monotonic() - start)
    (target / "reporte_audicion.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (target / "LEER_ANTES_DE_APROBAR.txt").write_text(
        "FACTOR DE GIGANTES — AUDICIÓN EXPERIMENTAL\n\n"
        "00_referencia_aprobada.mp3 es la única identidad canónica autorizada.\n"
        "Compare al oído 01_decision.mp3 y 02_transformacion.mp3 contra ella.\n"
        "Coteje el timbre, dicción, ritmo y artefactos vocales en AMBOS fragmentos.\n"
        "Éxito técnico NO es aprobación del narrador, licencia comercial ni render final.\n"
        "No activar el motor en render.yml hasta aceptación humana y revisión legal.\n",
        encoding="utf-8",
    )
    print("AUDICION_GENERADA:", json.dumps(report, ensure_ascii=False), flush=True)
    return report


if __name__ == "__main__":
    run()
