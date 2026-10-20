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

**Integración probada:** Piper es la voz elegida por defecto en `.github/workflows/render.yml`. CI real `39477498852` pasó una prueba de MP4 completo, audio, subtítulos y metadatos. El modelo permanece sujeto a revisión de licencias antes de publicación comercial. El primer MP4 histórico no se altera.

## Pendientes prioritarios
1. Escuchar y evaluar voz, revisar licencia específica para uso monetizado.
2. Integrar biblioteca visual original/licenciada, imágenes de archivo atribuidas y revisión por escena.
3. Mejorar subtítulos con alineación fonética, música con licencias y sonoridad.
4. Validar flujo completo de documental 8–14 minutos sin exceder cuotas gratuitas.
5. Añadir acceso seguro a artefactos desde panel, retención y controles de calidad humana.

## Ajuste de contraste verificado (2026-10-20)

La primera ejecución producía subtítulos desmesurados y tapaba la escena debido a la escala ASS en vertical. Se redujeron `FontSize` y `MarginV`, se introdujo un fondo semitransparente y se limitó cada línea a 30 caracteres en Shorts. Se inspeccionó un fotograma real del nuevo archivo: texto inferior legible y título despejado. Run de QA: https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39477498852 .

## Audición de narrador adulto y profesional — 20 de octubre de 2026

Preferencia del propietario: tono más adulto, seguro y profesional que la voz actual percibida como de canal de descubrimientos. Se considera mantener una identidad vocal única para todo el canal, con alternativas para pruebas, pero ninguna nueva voz queda designada automáticamente.

Workflow: .github/workflows/voice-audition.yml
Herramienta: tools/audition.py (Piper TTS CPU, 3 voces, texto idéntico).
Modelos: es_MX-ald-medium (referencia), es_MX-claude-high (alternativa en español mexicano, dataset declarado Apache-2.0), es_ES-davefx-medium (castellano, dataset declarado CC0 y ajuste desde otro modelo). Todos con SHA256 fijo.

Validación: ejecución GitHub Actions 39487653479 terminó en success, con tres WAV y comparacion.json, artefacto 12293493424. La presencia de muestras no garantiza afinidad editorial: el propietario debe escuchar y elegir. Las licencias de entrenamiento y el uso comercial aún requieren verificación.


## Segunda ronda de búsqueda vocal (más grave y madura)

Se inició una audición con Kokoro 82M para no limitar las opciones a Piper. El modelo declara licencia Apache-2.0 y cuenta con voces españolas `em_alex` y `em_santa`. Son candidatas, no la voz oficial. Se generará una tercera **variante procesada** de `em_alex` con reducción de tono suave (-6 %), no un narrador independiente. Workflow `.github/workflows/voice-kokoro.yml` y generador `tools/audition_kokoro.py`.

Requisitos para elegir voz: adulto, profesional, profundidad real sin efecto robótico, articulación clara, español aceptable para público internacional, licencia de explotación y modelo estable. La voz elegida deberá aplicarse consistentemente a futuros videos, y los cambios de identidad requerirán aprobación humana. No hay selección definitiva.

## Rechazo editorial de Kokoro y futura alternativa

El propietario rechazó las voces `em_alex`, `em_santa` y `em_alex_grave_sutil`: las percibe extrañas como narradores documentales. También había observado que Piper `es_ES-davefx-medium` suena demasiado fina. **No se ha escogido voz institucional definitiva**.

La nueva pauta es no seguir afinando pitches de voces de poca naturalidad. Evaluar **Chatterbox Multilingual v3** (modelo MIT con español, paquete latinoamericano) como candidato aún **no integrado ni probado**. Estimar uso de CPU/RAM y minutos de GitHub Actions antes de ejecutar. Una voz de referencia deberá tener cesión explícita para clonación o ser una grabación propia. Ninguna opción puede declararse comercialmente apta solo por el permiso general del repositorio.

## Referencia de narrador escogida: Microsoft Luis (Ecuador)

El propietario identifica como orientación principal la voz **Luis** en la galería Microsoft Speech Studio, en español ecuatoriano, por su narración formal y fluida. El nombre de API oficial es `es-EC-LuisNeural`, disponible en Azure AI Speech estándar. La captura la describe como voz juvenil; se tomará su naturalidad y formalidad como criterio, no una edad artificialmente impuesta.

Fuente de catálogo: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=text-to-speech

### Requisitos de integración (todavía no implementados)
1. Recurso Speech de Azure con región y clave, protegida exclusivamente como secreto en GitHub Actions; nunca mostrarla ni subirla al repositorio.
2. Proveedor de voz seleccionable, desacoplado del compositor FFmpeg: `piper` actual o `azure-speech` futuro con voz fija `es-EC-LuisNeural`.
3. Validación de WAV/PCM y límites de tiempo/caracteres antes del render. Bloquear la síntesis antes de gastar si se supera presupuesto; no alternar voces silenciosamente.
4. Evaluación comparativa con el mismo guion y aceptación del propietario; ninguna actualización automática de identidad vocal.
5. Condición legal importante: los términos de Microsoft conceden el derecho de uso del audio TTS precompilado, incluso comercial, a los **clientes de nivel de pago**. El nivel gratuito F0 ofrece cuota de pruebas (500.000 caracteres/mes), pero no debe asumirse autorización comercial.
   - Términos: https://www.microsoft.com/licensing/terms/en-US/productoffering/MicrosoftAzure/allprograms
   - Cuotas: https://azure.microsoft.com/es-es/pricing/details/speech/
   - Autenticación Azure Speech: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/rest-text-to-speech

No se ha configurado Azure ni se ha generado audio desde Azure en el proyecto.
