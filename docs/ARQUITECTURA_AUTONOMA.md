# Factor de Gigantes — arquitectura de la fábrica documental autónoma

**Decisión de producto 2026-10-21 · Prioridad P0 · Rama main**

## Meta definitiva (criterio de aceptación)

**Factor de Gigantes monitorea el mercado, descubre por sí mismo los temas más prometedores y ejecuta mediante SU PROPIO SISTEMA toda la investigación, selección editorial, guion, narración, escenas, montaje y preparación de publicación**, sin que ChatGPT ni el propietario deban investigar o elegir manualmente cada episodio.

Entradas ordinarias: señales de mercado observadas periódicamente, nicho del canal, mercados/idiomas, historial de videos y políticas del propietario. Seleccionar tema manualmente será solamente una opción excepcional de administración, no la entrada obligatoria. Salidas: documental MP4 de 8–14 minutos, subtítulos, expediente de fuentes, guion versionado, pistas de voz, manifiesto de derechos y resumen de QA. La función del propietario es **supervisar/aprobar**, no fabricar capítulos. La publicación a YouTube permanece **manual y deshabilitada por defecto** mientras no exista autorización editorial/comercial y una política de publicación aceptada.

**No basta** con que ChatGPT redacte guiones, llame a Qwen y ensamble manualmente un video. El piloto BlackBerry valida piezas pero no es el producto final.


## PRIORIDAD 0 — Radar profesional que propone, clasifica y selecciona los temas

**Este componente inicia el sistema**; ninguna IA debe pasar directamente de una ocurrencia a un guion o una publicación.

**Recopilación periódica (no promesa de streaming continuo):** programar comprobaciones regulares de las fuentes públicas y del historial del canal, con frecuencia ajustable a cuotas reales, sin gastar recursos en peticiones o IA cuando no hay cambios. Registrar zona geográfica, idioma, fecha observada y ventana de muestra. Cada indicador debe tener procedencia, intervalo, tamaño de muestra y nivel de confianza.

**Fuentes de inteligencia de mercado:**
- YouTube Data API: `search.list` descubre publicaciones y `videos.list` obtiene estadísticas públicas con clave y cuota habilitadas. Medir velocidad de visualizaciones observadas por día, antigüedad, publicaciones recientes, formato, canales comparables y saturación. Un resultado de búsqueda no es representativo de todo YouTube y las vistas de un canal grande no prueban que el tema funcionará en Factor de Gigantes. Documentación oficial https://developers.google.com/youtube/v3/docs/search/list y https://developers.google.com/youtube/v3/docs/videos/list
- YouTube Analytics API del **canal conectado**: cuando se autorice OAuth, utilizar duración media de visualización, retención, CTR de impresiones, tráfico, impresiones, suscriptores por video y publicaciones pasadas donde las métricas estén disponibles. Los datos privados de la competencia no son accesibles: **no inventar retención ni CTR de terceros**. https://developers.google.com/youtube/analytics
- Google Trends API **alpha** solo si la cuenta del proyecto tiene acceso autorizado. No suponer que es pública ni permanente. https://developers.google.com/search/apis/trends
- Wikipedia Pageviews, noticias verificadas, comunicados corporativos, reguladores, investigaciones universitarias y otras fuentes permitidas como señales auxiliares; **no** confundir búsquedas de Google, visitas de Wikipedia, noticias o datos YouTube como si fueran la misma métrica.
- Proponer entidades y narrativas a partir de las señales recogidas, no usar una lista fija de diez empresas para siempre. Desduplicar temas previamente producidos, evaluar actualidad, evergreen, interés regional y capacidad de investigar con fuentes originales.

**Clasificación y decisión editorial:**
1. Descubrir candidatos desde tendencias y videos/noticias realmente observados y etiquetarlos por sector, entidad, evento y enfoque narrativo.
2. Calcular oportunidades con fórmula auditable: demanda, aceleración reciente, competencia relativa, disponibilidad de fuentes primarias, singularidad narrativa, adecuación al historial real del canal, vigencia, riesgos y costo estimado.
3. Calificar **calidad de datos** y grado de confianza; si faltan muestras suficientes o fuentes confiables, devolver `sin_datos_suficientes`, NO fabricar una recomendación.
4. Producir ranking razonado y expediente de mercado con métricas y enlaces para 3–10 candidatos. Seleccionar el mejor **elegible** para investigación profunda, no declarar viralidad garantizada.
5. Mantener una cola de producción: `market_discovered → market_ranked → research_queued → evidence_checked → script_draft → editorial_review → voice → visuals → render → quality_gate → approval → youtube_upload`. Registrar intentos, dependencias y bloqueos.
6. Aprender del propio canal tras publicar: comparar proyecciones con desempeño real, evitar duplicar episodios, mejorar ponderaciones y distinguir estacionalidad de tendencias fugaces.

**Límites de publicación:** el sistema preparará miniatura, título, descripción, capítulos, subtítulos, etiquetas y calendario; tras aprobación editorial/comercial explícita y OAuth de canal, ejecutará **él mismo** la carga y programación mediante YouTube Data API. Esto automatiza la operación sin abrir un canal de publicación no autorizado. No existe permiso de subir videos solo por poder investigar el mercado.

**Lo implementado a 2026-10-21:** `tools/market_radar.py` recibe observaciones con fecha, muestras YouTube, proxy Wikimedia y documentos primarios; exige al menos dos señales, rechaza estadísticas ausentes/caducadas y videos duplicados; genera ranking heurístico y motivos de descarte. `tests/test_market_radar.py` incluye datos exclusivamente **sintéticos** para probar el contrato. **No existe aún un colector de tendencias en vivo conectado, ni un ranking basado en el mercado real del canal**. Hay que construirlo, conectar API con cuotas, ejecutar prueba real y medir resultados antes de considerar completo el radar.

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

1. **Radar de mercado y expediente:** capta señales reales, elige autónomamente los mejores temas elegibles y genera ID persistente, estado, procedencia, puntuación y presupuesto por episodio en D1. No depender del chat ni de un nombre hardcodeado como BlackBerry.
2. **Descubrimiento de fuentes:** buscador y rastreador acotados por HTTPS; portales oficiales, reguladores, documentos financieros, universidades, bibliotecas y prensa con acceso permitido; respetar límites/robots/licencias. Capturar URL, fecha, SHA-256, página/bloque. No inventar fuentes inaccesibles.
3. **Investigación LLM (Gemini/Qwen):** extraer preguntas y hechos propuestos, buscar más documentos cuando no haya suficiente soporte, identificar disensiones de alcance/periodo y producir matriz de afirmación→evidencia.
4. **QA factual automático:** verificar mecánicamente citas, enlaces, hashes, números, fechas, entidades y periodos. El texto de la IA **nunca es fuente primaria**; contradicciones complejas y conclusiones controvertidas se marcan para revisión, no se declaran verificadas solo por el modelo.
5. **Guionista autónomo:** redactar un guion original de 8–14 minutos desde evidencias con citas por escena, tensión narrativa, estructura, estimación de palabras y elementos visuales. Rechazar guiones vacíos, ambiguos o sin fuentes mínimas.
6. **Planificador de escenas visuales:** cada escena con duración, tipo de plano, b-roll original/licenciado, gráfica o recreación, animación y movimiento de cámara; evitar fondo estático y carteles durante minutos. Si falta material válido, bloquear exportación comercial.
7. **Narración:** generar todas las tomas mediante el TTS seleccionado y voz canónica autorizada; QA de dicción, volumen, pausas, duración, hashes y sincronía. Una muestra de voz aceptada editorialmente no prueba por sí misma licencia comercial.
8. **Montaje automático:** alinear voz, imágenes/movimientos, subtítulos, rótulos, música autorizada; exportar H.264/AAC MP4 y un previsual de aprobación. Se usa GitHub Actions/CPU dentro de un límite o GPU autorizada, nunca consumir pagos de forma silenciosa.
9. **QA de episodio completo:** validador FFprobe/audio, duración, fuentes, derechos, textos/subtítulos, errores y métricas de render. Guardar estados, artefactos y motivo de fallo para reintento por etapa **sin repetir investigaciones o síntesis ya válidas**.
10. **Revisión/aprobación del propietario:** entrega previsual, dossier, alertas y formulario de aprobación; no autoriza automáticamente la publicación. Tras aprobación editorial/comercial y permisos OAuth explícitos, el sistema podrá realizar la subida y programación por sí solo; la aprobación es la puerta, no una tarea manual de subir archivos.

## Lo que funciona HOY y lo que no

- **Implementado/probado:** extracción de algunos PDF originales BlackBerry, auditoría estructural, pruebas de descubrimiento SEC (rechazada por HTTP), Qwen3-0.6B investigador experimental, Qwen3-TTS narrador, cuatro tomas nuevas para la escena 01, MP4 de ~56,5 segundos y previsual animada. Panel/D1 y flujos manuales existen.
- **NO completado:** investigación multi-etapa autónoma general para cualquier tema, modelo Gemini integrado, motor de búsqueda independiente de un expediente fijado a mano, guion completo escrito siempre por el sistema, visuales cinematográficos suficientes, voces de las 12 escenas aprobadas, exportación documental autónoma de 8–14 minutos y QA factual sin intervención de ChatGPT.
- **Estado de Gemini:** arquitectura acordada; falta integración API real y clave de servicio en el entorno del proyecto. Ninguna API Gemini se ha llamado desde el sistema hasta comprobarlo con test real. No pedir claves por chat.
- **Estado de Qwen investigador:** ya existen pruebas pero Qwen3-0.6B no ha demostrado capacidad documental editorial suficiente. Qwen TTS sí produjo muestras, que requieren revisión auditiva y comercial.

## Nueva secuencia de prioridades

**P0.0** Implementar colectores reales (YouTube Data API, Analytics del propio canal, Trends solo si está permitido y proxies fiables), detector de temas, ranking, programador periódico, trazas D1 y selección de oportunidad sin intervención humana. No declarar estudio real hasta recuperar métricas observadas.

**P0.1** Implementar adaptador de investigación `gemini_free` y adaptador `qwen_local` bajo contrato común; pruebas con fixtures sin coste; prueba real de Gemini solo tras configurar el secreto voluntariamente y verificar nivel gratuito.

**P0.2** Investigación de un tema nuevo **sin que ChatGPT proporcione fuentes, guion ni texto**, con resultados descargables de cada etapa: matriz de hechos, preguntas pendientes, guion y citas; medir calidad vs Qwen de texto.

**P0.3** Conectar el proveedor elegido a un orquestador persistente, cuotas, estados, reintentos por etapa y decisiones de bloqueo. Lanzar desde el panel «Investigar» usando tema arbitrario.

**P0.4** Construir guionista, generador de escenas y render de larga duración genéricos; BlackBerry es fixture del piloto, no código específico para todos los documentales.

**P0.5** Verificar primer episodio **generado íntegramente por el sistema**: trazabilidad 100% de afirmaciones narradas, 8–14 min, MP4 con voz y escenas dinámicas, y bloqueo de YouTube hasta autorización.

## No objetivos y reglas irreversibles

No sustituir automáticamente un proveedor agotado por una API de pago. No enviar documentación confidencial a la modalidad gratuita de Gemini. No presentar opiniones de IA como hechos. No vender licencias inexistentes. No depender de la computadora portátil del propietario. Mantener cambios en `main`, documentar avance real y no inventar que el sistema ya está terminado.

**Esta es la dirección definitiva del producto. Las mejoras futuras deben acercarnos a este criterio de aceptación, no limitarse a crear manualmente otro episodio piloto.**
