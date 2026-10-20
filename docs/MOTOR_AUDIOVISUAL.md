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

## Restricción económica absoluta: sin pagos

La voz Microsoft `es-EC-LuisNeural` es solo una **referencia de calidad**. Tras comprobar que el uso comercial requiere condiciones del nivel de pago de Azure, el propietario ha descartado Azure y todos los servicios con coste. No se implementará integración comercial Microsoft Speech ni se pedirá configurar una cuenta facturable.

Priorizar motores locales gratuitos con derechos comerciales explícitos de pesos y voces; comparar naturalidad sin efectos artificiales. Comprobar requisitos de CPU/memoria y respetar las cuotas gratuitas existentes de GitHub Actions y Cloudflare, deteniendo el trabajo si no se puede garantizar coste cero. No confundir gratuidad de inferencia con autorización de licencia o ejecución ilimitada.


## Búsqueda verificable de voces gratuitas — 2026-10-20

**Referencia de sonido**: Luis de Microsoft Speech (`es-EC-LuisNeural`) exclusivamente como descripción de naturalidad, dicción formal y fluidez. No usar API Microsoft ni copiar su identidad vocal.

| Modelo abierto | Licencia publicada | Idioma | Tamaño / viabilidad | Estado |
| --- | --- | --- | --- | --- |
| `myshell-ai/MeloTTS-Spanish` | MIT, incluido checkpoint | ES | ~208 MB, CPU en tiempo real según proveedor | Audición en GitHub Actions `39497786790`; pendiente resultado auditivo |
| `ResembleAI/Chatterbox-Multilingual-es-mx-latam` | MIT | Español LATAM | Modelo especializado ~2.14 GB de pesos más archivos compartidos; riesgo de RAM/tiempo en runner CPU | Candidato, no probado |
| `Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice` | Apache-2.0 | ES y nueve idiomas más | ~2.5 GB repositorio; sus nueve locutores nativos son de otros idiomas, evaluar acento en ES | Candidato técnico, no probado |
| `FunAudioLLM/Fun-CosyVoice3-0.5B-2512` | Apache-2.0 | ES y ocho idiomas más | ~500M parámetros, dependencias exigentes; muestreo por voz de referencia legítima | Candidato técnico, no probado |
| `Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign` | Apache-2.0 | ES y nueve idiomas más | ~4.52 GB; permite diseñar estilo vocal por instrucciones, alto coste CPU | Futuro, no usar por defecto |

**Fuentes primarias**:
- https://huggingface.co/myshell-ai/MeloTTS-Spanish
- https://github.com/myshell-ai/MeloTTS
- https://huggingface.co/ResembleAI/Chatterbox-Multilingual-es-mx-latam
- https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice
- https://huggingface.co/FunAudioLLM/Fun-CosyVoice3-0.5B-2512
- https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign

**Descartados**: proveedores TTS que requieren suscripción para uso comercial (Azure Speech F0), modelos con pesos NC y cualquier clonación de Luis u otros narradores sin licencia/consentimiento.

**Seguridad y control de gasto**: audiciones exclusivamente en CPU, con `timeout-minutes`, sin tarjeta ni claves API, sin acciones recurrentes de generación masiva; la existencia de un nivel gratis de GitHub no implica capacidad ilimitada. No declarar narrador aprobado hasta evaluación auditiva humana.


## MeloTTS rechazado por timbre artificial; siguiente puerta de calidad

Tras escuchar dos muestras reales, el propietario considera que **MeloTTS suena como TTS**. No declararlo narrador definitivo aunque su funcionamiento haya quedado probado.

Siguiente ensayo: **Chatterbox Multilingual V3 LatAm**. Model card MIT: https://huggingface.co/ResembleAI/Chatterbox-Multilingual-es-mx-latam . Demo pública alojada por el proveedor: https://huggingface.co/spaces/ResembleAI/Chatterbox-Multilingual-TTS-es-mx-latam . Es un finetune de español latinoamericano con entrenamiento regional y control de expresividad; puede ofrecer mayor naturalidad, no es garantía. El repositorio contiene checkpoint principal ~2,14 GB y decoder ~1,06 GB; no se ha demostrado eficiencia en la cuota gratis de GitHub Actions.

**Regla de decisión:** primero audición real; después prueba de memoria, latencia, derechos y ejecución local; solo entonces cambio de narrador previa autorización. Si ningún sintetizador gratuito suena humano, considerar grabación de voz humana propia/con licencia. Prohibido usar voces ajenas clonadas sin permiso y probar una suscripción de pago.

## La demo femenina de Chatterbox no sirve como evaluación del narrador requerido
El propietario indicó que la demo enlazada presenta una sola voz femenina y no le gusta. Debe descartarse esa demo como opción para aprobar una voz masculina. El motor general sí puede condicionar otra voz mediante `audio_prompt_path`, pero eso requiere una referencia legalmente utilizable y consentimiento; no utilizar una voz real ajena sin permiso.

### Nueva prueba editorial recomendada: Qwen3-TTS Voice Design
- Demo oficial activa: https://huggingface.co/spaces/Qwen/Qwen3-TTS (usar `Voice Design` y seleccionar idioma español).
- Texto descriptivo del personaje: `A mature professional male narrator from Latin America, natural human voice, warm and full low-mid register, confident but not theatrical, calm documentary cadence, nuanced pauses, crisp Spanish articulation, no robotic texture.`
- Modelo abierto: https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign (licencia Apache-2.0 declarada por proyecto); no requiere muestra humana en modo Voice Design.
- Demostración gratuita sujeta a colas/cuotas del proveedor; ninguna garantía de funcionamiento indefinido ni de acento exacto. No intentar generación automática de videos ni establecer voz fija sin aprobación.
- **Pendiente técnico:** medir RAM/CPU/tiempo del modelo 1.7B, licencias de dependencias/modelos, coste cero real y persistencia de identidad vocal en documentales largos.

## Qwen3 Voice Design — demostración generada y verificada

- `tools/audition_qwen.py` es una prueba de voz por descripción que utiliza el **Space público** de Qwen, no una cuenta de Azure ni una API pagada. `.github/workflows/voice-qwen.yml` ejecuta la audición en GitHub Actions para `main`.
- Prompt: voz masculina madura, española latinoamericana neutra, profesional, cálida, profunda pero humana, pausada, sin actuación exagerada.
- Audio real confirmado: https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39502577947 . Resultado MP3 de 14,112 s / 24 kHz, artefacto 12302050983, generado con éxito mediante endpoint Voice Design del Space oficial.
- El modelo abierto Qwen3-TTS Voice Design 1.7B está publicado bajo Apache-2.0; **los términos del proveedor del Space y sus cuotas pueden diferir**. Usarlo para una audición puntual no garantiza producción comercial automatizada gratuita, continua ni sin límites.
- El propietario debe escuchar la muestra y decidir si encaja con la identidad; **no se ha cambiado la voz oficial ni el workflow de render**.

## Qwen3 Voice Design: segunda muestra con mayor energía
- Feedback: primera demo Qwen3 demasiado calmada para Factor de Gigantes.
- Versión de audición revisada para pedir un narrador adulto entusiasta, con ritmo dinámico, tensión narrativa, énfasis y voz humana natural; no simplemente aumentar volumen o modificar artificialmente el pitch.
- Prueba real: GitHub Actions 39503709220 completado, artefacto 12301563544. MP3 de 15,0 s (mono, 24 kHz) verificado por `ffprobe`.
- Precaución: Voice Design genera un timbre nuevo en cada petición, así que la consistencia de una identidad vocal a lo largo de docenas de escenas requiere estudio. La voz oficial aún no ha sido aprobada; render del canal intacto.

## Pronunciación de marcas y referencia vocal Qwen v3

La voz Qwen3 Voice Design **v3 de dicción profesional** fue la primera considerada claramente mejor por el propietario. Halló un fallo fonético en el nombre BlackBerry. Para no perder el timbre, se implementó un flujo de ensayo con:
- **Léxico de síntesis** en `tools/voice_lexicon.py`: conserva «BlackBerry» en guion, titulares y subtítulos, pero envía «Blákberi» al TTS como una sola palabra. También admite `blackberry` con variaciones de mayúsculas. No altera plurales ni términos que contienen el nombre como subcadena.
- **Referencia sintética propia**: Qwen3 v3 del run 39504363557. Validación de checksum SHA-256 antes de usarla; convertida a WAV 24 kHz.
- **Voice Clone** oficial Qwen3 Base 1.7B: demo https://huggingface.co/spaces/Qwen/Qwen3-TTS , método `/generate_voice_clone` con referencia v3 y texto idéntico.
- **Run de prueba** https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39505217153, completo y exitoso. Artefacto 12302578597, MP3 mono 48 kHz y 11.304 s.

Advertencias: `Voice Clone` no garantiza coincidencia perfecta con el timbre original ni pronunciación correcta, requieren validación al oído. `voice_lexicon.py` aún no está conectado al `render.yml` productivo: solo forma parte del ensayo. Las demos públicas tienen colas, restricciones y no garantizan producción gratuita perpetua. No hay voz institucional irrevocablemente aprobada ni proveedor con facturación activada.

## Cadencia documental aprobada provisionalmente y corrección de «años» (2026-10-20)

Referente editorial de estilo: documentales de naturaleza narrados con calidez, serenidad y pausas deliberadas; **no clonación o imitación exacta de narradores identificables**. La voz Qwen3 v3, reproducida con referencia vocal, es la favorita del propietario, sujeto a corregir fallos concretos.

`tools/documentary_pacing.py` implementa `ffmpeg atempo=0.94` y añade hasta tres pausas de 0,16 s insertando silencio sin modificar los samples de habla. Sólo funciona con FFmpeg/FFprobe locales. Es un ajuste de tempo, no un nuevo modelo vocal.

Tras la aprobación expresada como «Excelente» en la versión pausada, el propietario detectó una vocal `a` demasiado larga en `años` al inicio. `tools/voice_fix_anos.py` acorta esa vocal unos 65 ms con crossfade de 16 ms. **Su algoritmo incorpora el SHA256 del MP3 de referencia** y no debe aplicarse a otro audio sin reidentificar la posición exacta de la vocal. Resultado MP3: ~12,0 s, mono 48kHz.

No usar ediciones quirúrgicas temporales como solución general para nombres o dicción deficiente. Para nuevos documentales crear un banco reproducible de referencias vocales y léxico de pronunciación con control de calidad auditivo. La voz institucional aún no está conectada al render; ningún proveedor de pago está autorizado.
