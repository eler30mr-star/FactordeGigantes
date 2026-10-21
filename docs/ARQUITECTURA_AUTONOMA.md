# Factor de Gigantes — arquitectura de la fábrica documental autónoma

**Decisión de producto 2026-10-21 · Prioridad P0 · Rama main**

## Meta definitiva (criterio de aceptación)

**El propietario selecciona un tema y Factor de Gigantes ejecuta el trabajo completo mediante SU PROPIO SISTEMA**, sin que ChatGPT tenga que investigar, escribir, generar el guion, manejar la voz o editar el video a mano en cada episodio.

Entradas: tema, idioma y preferencias opcionales (duración objetivo, tipo de historia). Salidas: documental MP4 de 8–14 minutos, subtítulos, expediente de fuentes, guion versionado, pistas de voz, manifiesto de derechos y resumen de QA. La función del propietario es **supervisar/aprobar**, no fabricar capítulos. La publicación a YouTube permanece **manual y deshabilitada por defecto** mientras no exista autorización editorial/comercial y una política de publicación aceptada.

**No basta** con que ChatGPT redacte guiones, llame a Qwen y ensamble manualmente un video. El piloto BlackBerry valida piezas pero no es el producto final.

## Motor de investigación: proveedor intercambiable

Separar dos disciplinas distintas:

- **LLM investigador y guionista:** Gemini API o Qwen3 texto. Analiza información **ya recuperada y registrada**, plantea nuevas búsquedas, coteja evidencia, distingue incertidumbres y redacta propuestas de guion con identificadores de afirmaciones.
- **TTS narrador:** Qwen3-TTS de clonación de voz, con referencia canónica, checksum y prueba de licencia. No asumir que Qwen3-TTS investiga.

**Opción preferida para primer experimento comparativo:** Gemini 2.5 Flash en nivel gratuito, si está disponible en la cuenta y se configura una clave válida. La API gratuita tiene cuotas y puede usar entradas/salidas para mejorar productos de Google: usar únicamente fuentes corporativas públicas, nunca secretos, datos privados ni documentos confidenciales. Ver https://ai.google.dev/gemini-api/docs/pricing y https://ai.google.dev/gemini-api/docs/rate-limits. La disponibilidad, cuotas, términos y nombres de modelo pueden cambiar: confirmar al probar, no prometer cuota garantizada.

**Alternativa y resiliencia:** Qwen3 texto de pesos abiertos, ejecutado localmente/CPU en GitHub Actions. Ya existe la prueba con `Qwen/Qwen3-0.6B`, pero no considerarlo automáticamente suficientemente fiable para investigar/debatir cifras complejas. Evaluar un modelo Qwen de texto más capaz cuantizado solo si cabe en CPU/RAM/cuota; no sustituir el narrador. No enviar prompts a una API externa de Qwen sin control de coste.

**Interfaz deseada** `ResearchProvider`:
- `analyze_evidence(topic, source_passages, constraints) -> claim_candidates[]`
- `request_missing_sources(claim_candidates) -> search_tasks[]`
- `draft_story(verified_evidence, duration) -> scenes[]`
- `provider_name, model_version, prompt_sha256, costs, tokens, execution_id`
- `evidence_url, content_hash, page_or_section, fetched_at, entity, period, currency, factual_status`

Proveedores `gemini_free` y `qwen_local` configurables sin tocar el resto del pipeline. Sin clave gratuita verificable, **bloquear Gemini o usar Qwen local**, sin activar automáticamente una cuenta de pago. `GEMINI_API_KEY` solo en secreto de GitHub/Cloudflare cuando corresponda, nunca en documentos o repositorio. Ni Google AI Studio abierto manualmente ni una conversación de ChatGPT sustituyen una API conectada al sistema.

## Orquestación automatizada: etapas reales

1. **Tema y expediente:** genera ID persistente, estado y presupuesto por episodio en D1. No depender del chat ni de un nombre hardcodeado como BlackBerry.
2. **Descubrimiento de fuentes:** buscador y rastreador acotados por HTTPS; portales oficiales, reguladores, documentos financieros, universidades, bibliotecas y prensa con acceso permitido; respetar límites/robots/licencias. Capturar URL, fecha, SHA-256, página/bloque. No inventar fuentes inaccesibles.
3. **Investigación LLM (Gemini/Qwen):** extraer preguntas y hechos propuestos, buscar más documentos cuando no haya suficiente soporte, identificar disensiones de alcance/periodo y producir matriz de afirmación→evidencia.
4. **QA factual automático:** verificar mecánicamente citas, enlaces, hashes, números, fechas, entidades y periodos. El texto de la IA **nunca es fuente primaria**; contradicciones complejas y conclusiones controvertidas se marcan para revisión, no se declaran verificadas solo por el modelo.
5. **Guionista autónomo:** redactar un guion original de 8–14 minutos desde evidencias con citas por escena, tensión narrativa, estructura, estimación de palabras y elementos visuales. Rechazar guiones vacíos, ambiguos o sin fuentes mínimas.
6. **Planificador de escenas visuales:** cada escena con duración, tipo de plano, b-roll original/licenciado, gráfica o recreación, animación y movimiento de cámara; evitar fondo estático y carteles durante minutos. Si falta material válido, bloquear exportación comercial.
7. **Narración:** generar todas las tomas mediante el TTS seleccionado y voz canónica autorizada; QA de dicción, volumen, pausas, duración, hashes y sincronía. Una muestra de voz aceptada editorialmente no prueba por sí misma licencia comercial.
8. **Montaje automático:** alinear voz, imágenes/movimientos, subtítulos, rótulos, música autorizada; exportar H.264/AAC MP4 y un previsual de aprobación. Se usa GitHub Actions/CPU dentro de un límite o GPU autorizada, nunca consumir pagos de forma silenciosa.
9. **QA de episodio completo:** validador FFprobe/audio, duración, fuentes, derechos, textos/subtítulos, errores y métricas de render. Guardar estados, artefactos y motivo de fallo para reintento por etapa **sin repetir investigaciones o síntesis ya válidas**.
10. **Revisión/aprobación del propietario:** entrega previsual, dossier, alertas y formulario de aprobación; no autoriza automáticamente la publicación. YouTube queda inactivo salvo decisión y permisos explícitos.

## Lo que funciona HOY y lo que no

- **Implementado/probado:** extracción de algunos PDF originales BlackBerry, auditoría estructural, pruebas de descubrimiento SEC (rechazada por HTTP), Qwen3-0.6B investigador experimental, Qwen3-TTS narrador, cuatro tomas nuevas para la escena 01, MP4 de ~56,5 segundos y previsual animada. Panel/D1 y flujos manuales existen.
- **NO completado:** investigación multi-etapa autónoma general para cualquier tema, modelo Gemini integrado, motor de búsqueda independiente de un expediente fijado a mano, guion completo escrito siempre por el sistema, visuales cinematográficos suficientes, voces de las 12 escenas aprobadas, exportación documental autónoma de 8–14 minutos y QA factual sin intervención de ChatGPT.
- **Estado de Gemini:** arquitectura acordada; falta integración API real y clave de servicio en el entorno del proyecto. Ninguna API Gemini se ha llamado desde el sistema hasta comprobarlo con test real. No pedir claves por chat.
- **Estado de Qwen investigador:** ya existen pruebas pero Qwen3-0.6B no ha demostrado capacidad documental editorial suficiente. Qwen TTS sí produjo muestras, que requieren revisión auditiva y comercial.

## Nueva secuencia de prioridades

**P0.1** Implementar adaptador de investigación `gemini_free` y adaptador `qwen_local` bajo contrato común; pruebas con fixtures sin coste; prueba real de Gemini solo tras configurar el secreto voluntariamente y verificar nivel gratuito.

**P0.2** Investigación de un tema nuevo **sin que ChatGPT proporcione fuentes, guion ni texto**, con resultados descargables de cada etapa: matriz de hechos, preguntas pendientes, guion y citas; medir calidad vs Qwen de texto.

**P0.3** Conectar el proveedor elegido a un orquestador persistente, cuotas, estados, reintentos por etapa y decisiones de bloqueo. Lanzar desde el panel «Investigar» usando tema arbitrario.

**P0.4** Construir guionista, generador de escenas y render de larga duración genéricos; BlackBerry es fixture del piloto, no código específico para todos los documentales.

**P0.5** Verificar primer episodio **generado íntegramente por el sistema**: trazabilidad 100% de afirmaciones narradas, 8–14 min, MP4 con voz y escenas dinámicas, y bloqueo de YouTube hasta autorización.

## No objetivos y reglas irreversibles

No sustituir automáticamente un proveedor agotado por una API de pago. No enviar documentación confidencial a la modalidad gratuita de Gemini. No presentar opiniones de IA como hechos. No vender licencias inexistentes. No depender de la computadora portátil del propietario. Mantener cambios en `main`, documentar avance real y no inventar que el sistema ya está terminado.

**Esta es la dirección definitiva del producto. Las mejoras futuras deben acercarnos a este criterio de aceptación, no limitarse a crear manualmente otro episodio piloto.**
