# Motor audiovisual — Factor de Gigantes

**Estado:** previsualización técnica mejorada. Ningún render se publica automáticamente.

## Voz local gratuita
- **Motor:** Piper TTS 1.8.0 (https://pypi.org/project/piper-tts/), licencia GPL-3.0-or-later, ejecutado en CPU de GitHub Actions. No requiere token de IA.
- **Voz:** `es_MX-ald-medium` (español mexicano), publicada por Rhasspy: https://huggingface.co/rhasspy/piper-voices/tree/main/es/es_MX/ald/medium .
- Modelo ONNX de ~63 MB descargado bajo demanda y verificado con SHA-256 `019b3803293c93e34a206dd2e53a3889209a514e786fd7144f7b70196c579b63`. El cache de GitHub Actions evita repetir descargas cuando sea posible.
- **Licencia editorial:** el MODEL_CARD https://huggingface.co/rhasspy/piper-voices/blob/main/es/es_MX/ald/medium/MODEL_CARD declara dataset Unlicense pero el modelo fue afinado desde otra voz; **verificar derechos del modelo derivado antes de publicar comercialmente**. El motor GPL puede exigir obligaciones al redistribuir el software.
- eSpeak NG permanece como modo técnico explícito, nunca fallback oculto.
- Para una prueba de voz sin aprobar ni publicar un video: `.github/workflows/voice-smoke.yml`.

## Mejoras audiovisuales
- Cada escena tiene tarjetas editoriales originales, animación Ken Burns con FFmpeg y entrada en fundido.
- `subtitulos.srt` sale del texto aprobado con tiempos aproximados basados en duración real del audio; no es alineación fonética por palabra.
- `video.mp4` puede contener subtítulos incrustados y la entrega incluye `subtitulos.srt`, `creditos.txt` y `ficha.json` con fuentes, motor y advertencias.
- Se valida por FFprobe presencia de video H.264, audio, dimensiones, duración y tamaño, antes de reportar terminado.
- Gráficos y tarjetas originales **no** sustituyen metraje documental ni investigación real.

## Uso
```bash
python -m pip install Pillow==11.3.0 piper-tts==1.8.0
python tools/render.py --manifest examples/documental.json --voice-engine piper --captions burn --output dist/video.mp4
```

El workflow remoto usará Piper **solo cuando su prueba real pase**. El primer MP4 del proyecto sigue siendo una maqueta histórica y no se altera.

## Pendientes prioritarios
1. Escuchar y evaluar voz, revisar licencia específica para uso monetizado.
2. Integrar biblioteca visual original/licenciada, imágenes de archivo atribuidas y revisión por escena.
3. Mejorar subtítulos con alineación fonética, música con licencias y sonoridad.
4. Validar flujo completo de documental 8–14 minutos sin exceder cuotas gratuitas.
5. Añadir acceso seguro a artefactos desde panel, retención y controles de calidad humana.
