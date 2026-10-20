"""Genera una nueva toma COMPLETA con la misma referencia vocal.

Evita recortar vocales, aplicar autotune, fusionar sílabas o sustituir fonemas.
El resultado no reemplaza ninguna muestra anterior: requiere aprobación auditiva.
"""
import json
from pathlib import Path

from tools.audition_qwen_clone import run as regenerate_full
from tools.documentary_pacing import run as documentary_pace


def run():
    raw_dir = Path("dist/retake-raw")
    final_dir = Path("dist/retake-natural")
    final_dir.mkdir(parents=True, exist_ok=True)
    regenerate_full(output_dir=str(raw_dir))
    raw = raw_dir / "FactorDeGigantes_BlackBerry_RR_Fuerte.mp3"
    if not raw.is_file():
        raise RuntimeError("La generación íntegra no produjo un MP3")
    result = final_dir / "FactorDeGigantes_Documental_TomaNatural.mp3"
    info = documentary_pace(raw, result, speed=0.94, pause_seconds=0.16, max_breaks=3)
    if result.stat().st_size < 100000:
        raise RuntimeError("Salida demasiado pequeña")
    (final_dir / "ficha.json").write_text(json.dumps({
        "origin": "Qwen3 Voice Clone referencia Qwen3 v3",
        "text": "Durante años, BlackBerry parecía invencible. Sus decisiones definían el futuro de la comunicación. Hasta que una nueva generación cambió las reglas. Esto es Factor de Gigantes.",
        "full_text_regenerated": True,
        "word_level_surgery": False,
        "pitch_correction": False,
        "global_pacing": info,
        "status": "prueba_auditiva_pendiente",
        "payment": "none"
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Nueva toma completa, sin cirugía vocal: {result}; duración {info['duration']:.3f}s", flush=True)


if __name__ == "__main__":
    run()
