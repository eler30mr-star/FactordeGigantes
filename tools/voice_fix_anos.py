"""La corrección quirúrgica de 'años' quedó RETIRADA por artefactos audibles.

Esta implementación se conserva únicamente como aviso histórico y no modifica audio.
La solución admitida es regenerar la frase completa con la voz de referencia.
"""


def shorten_initial_a(*_args, **_kwargs):
    raise RuntimeError(
        "Procedimiento retirado: el recorte de la vocal en 'años' produjo "
        "un sonido artificial/autotune. Generar una nueva toma íntegra."
    )


if __name__ == "__main__":
    raise SystemExit(
        "ERROR: procedimiento deshabilitado por calidad. "
        "Use tools/audition_qwen_retake.py."
    )
