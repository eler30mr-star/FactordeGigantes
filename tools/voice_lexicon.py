"""Reglas puntuales de pronunciación para TTS, no para títulos ni subtítulos."""
import re

# Texto visible/editorial se conserva; sólo se adapta la entrada de síntesis.
_BLACKBERRY = re.compile(r"(?<!\w)BlackBerry(?!\w)", flags=re.IGNORECASE)


def spoken_text(editorial_text: str) -> str:
    """Normalizar nombres propios para pronunciación española, sin repetir palabras."""
    if not isinstance(editorial_text, str):
        raise TypeError("Se requiere texto")
    return _BLACKBERRY.sub("Blákberi", editorial_text)
