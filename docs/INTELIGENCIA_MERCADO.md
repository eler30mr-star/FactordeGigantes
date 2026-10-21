# Factor de Gigantes · Inteligencia de mercado autónoma

**Dirección obligatoria: el sistema encuentra los temas, no el propietario ni ChatGPT.**

**Fase P0 — 2026-10-21.** El usuario no proporcionará una lista manual de temas ni tendrá que investigar una empresa para cada documental. La función del sistema es actuar como **equipo completo de investigación de mercado, dirección editorial y producción**, usando datos observados y registrando sus razones.

## Ciclo permanente y medible

**RADAR → DESCUBRIMIENTO → CLASIFICACIÓN → INVESTIGACIÓN PROFUNDA → GUION → PREPRODUCCIÓN → VOZ → VISUALES → MONTAJE → QA → APROBACIÓN → YOUTUBE → ANALÍTICA → RADAR.**

- Estado real de cada episodio en D1; nunca depender de una conversación con ChatGPT.
- Sondeos periódicos por fuente y región con cuotas. Frecuencia sugerida para configuración: mercado diario, alertas informativas cada pocas horas cuando se permita y análisis del canal tras cada publicación. **No prometer streaming instantáneo:** YouTube, Wikimedia y Trends tienen latencia, cuotas y/o restricciones. Evitar llamadas sin cambios.
- El radar diferencia dos tipos de contenido: **oportunidad emergente** (cambio de interés reciente respaldado por fuentes) y **evergreen** (historia o innovación con demanda sostenida). Dar espacio a ambas clases y evitar un canal que persiga solo titulares.
- Temas de la marca: empresas, historias empresariales, tecnología, innovación, industrias, competencia, decisiones transformadoras y disrupción. Categorías configurables, sin fórmulas de clickbait que traicionen los hechos.
- Estudios del público objetivo por lengua/país: español, audiencia internacional, diferencias geográficas y formatos 8–14 minutos; no inferir preferencias locales solo por residencia del operador.

## Fuentes y reglas de interpretación

| Fuente | Señal utilizable | Límite que nunca se debe ocultar |
|---|---|---|
| YouTube Data API | Videos recientes, visualizaciones, fecha de publicación, canales y muestras competitivas | Las vistas de otros canales no revelan retención/CTR privados ni garantizan audiencia propia |
| Analytics del propio canal | CTR, impresiones, duración vista, retención, crecimiento y canales de tráfico cuando estén disponibles | Solo tras autorización OAuth del propietario y en métricas que realmente conceda YouTube |
| Wikimedia Pageviews | Cambios de interés por una entidad/artículo, comparando periodos equivalentes | No es volumen de búsqueda en Google ni audiencia asegurada en YouTube |
| Google Trends API alfa | Tendencias de búsqueda por región y temporalidad | Acceso restringido; no asumir que la cuenta dispone de él |
| Comunicados, informes, reguladores, noticias verificadas | Sucesos y documentación para un tema investigable | Son fuentes de hechos, no necesariamente mediciones de demanda |
| Historial de Factor de Gigantes | Qué funcionó con nuestra audiencia y qué temas ya se publicaron | La muestra es inicialmente pequeña; no inventar conclusiones por 1–2 videos |

## Descubrimiento automático (pendiente de conectar)

Un **colector de mercado** debe leer publicaciones o tendencias del nicho, extraer nombres de empresas y eventos que realmente aparezcan en los datos, asignarles entidad canónica y construir propuestas de documental. No usar un listado estático de 10 temas o una respuesta de IA sin fuentes. A cada propuesta se añade una o más URLs de origen, fecha, descripción del evento, ángulo narrativo y posible disponibilidad de información corporativa.

Un **modelo de investigación** Gemini/Qwen propone enfoques y preguntas, pero no inventa estadísticas ni toma su propia respuesta como evidencia. El sistema contrasta cada candidato con YouTube, señales independientes y disponibilidad de fuentes antes de enviarlo al ranking.

**No declarar "el mejor tema" si faltan muestras o datos recientes.** Un candidato sin estadísticas válidas debe quedar pendiente para nueva medición.

## Selector de oportunidades (implementado como primera versión)

- \`tools/market_sources.py\`: colector YouTube Data API con **como máximo dos llamadas por tema**, 10 videos y validación de muestra; requiere secreto \`YOUTUBE_DATA_API_KEY\`. Colector Wikipedia mediante Wikimedia Pageviews para ventana completa de 14 días (7 recientes y 7 anteriores), con procedencia y límites. No activa pagos ni contacta proveedores sin invocación. El colector de YouTube por ahora **requiere que otro módulo le entregue nombres descubiertos**: no es todavía descubrimiento end-to-end.
- \`tools/market_radar.py\`: consume observaciones fechadas y documentos primarios; rechaza muestras YouTube de menos de tres videos, estadísticas inválidas, datos caducados (más de 7 días), señales de Wikipedia incompletas, temas repetidos y ausencia de fuentes documentales.
- Solo después de reunir al menos señal de YouTube + señal independiente de interés + posible fuente primaria, calcula un **puntaje heurístico transparente**: velocidad observada de vistas 35 %, cambio relativo de interés 25 %, competencia observada 15 %, fuentes primarias 15 %, novedad 10 % (neutral hasta disponer de analítica propia).
- **La fórmula no está calibrada aún con resultados del canal**. Sus puntuaciones no predicen reproducciones reales, viralidad, calidad factual ni rentabilidad. Deben ajustarse al contar con suficientes videos publicados y resultados observados.
- \`tests/test_market_sources.py\`, \`tests/test_market_radar.py\`: pruebas offline con datos **inventados únicamente como fixtures**. Nunca utilizar sus números como tendencia real.
- \`market_radar.py --input datos_reales.json\` genera ranking o falla por falta de información. No debe entregar un episodio a producción sin el expediente market/identidad/evidencia y un control de costes.

### Pendientes técnicos inmediatos

1. **Descubrimiento independiente:** ingesta real de temas por consultas amplias al nicho, resultados recientes, extracción de entidades con Gemini/Qwen y desambiguación frente a Wiki/Wikidata. El sistema, no el humano, creará la lista de candidatos.
2. **Acceso a estadísticas reales:** conectar YouTube Data API autorizada sin exponer clave, medir cuotas y respuestas de 403/429; completar Wikimedia con URLs de artículos validados. Trends solamente si la cuenta obtiene autorización alfa.
3. **Prueba de mercado no simulada:** generar una clasificación de al menos 3 candidatos del mismo mercado/idioma, procedentes del radar; guardar muestras, puntuaciones, descartes y limitaciones. Revisar que el primero tenga evidencia primaria disponible.
4. **Orquestador de producción:** almacenar ranking en D1 y enviar automáticamente el candidato elegido al motor de investigación; usar presupuestos, reintentos idempotentes, límites diarios y estados visibles en panel.
5. **Modelos investigadores independientes de ChatGPT:** Gemini o Qwen recuperan fuentes, investigan, contrastan y redactan el guion. El TTS de Qwen solo se ocupa de voz.
6. **Video profesional:** assets visuales y audio comercialmente autorizados, escenas variadas, sincronización y control integral de duración 8–14 minutos.
7. **YouTube:** después de autorización OAuth y aprobación editorial/comercial del episodio, el sistema genera metadatos, sube o programa mediante API, registra el ID y mide rendimiento. No debe publicarse a partir de un ranking sin revisión.

## Control de publicación

**Nunca interpretar "producción autónoma" como "publicar información sin verificar"**. Las tareas manuales que queden deben ser aprobaciones de responsabilidad editorial o derechos, no la creación de archivos ni selección de tema. El sistema tiene que realizar también la subida/agenda por YouTube cuando esté autorizado, y conservar el registro de quién aprobó, qué versión y cuándo.

**Estado real al 2026-10-21:** arquitectura reorientada y dos componentes de clasificación/colectores implementados con pruebas offline; **sin estudio en vivo completado, sin selección autónoma de un tema real, sin conexión YouTube API confirmada, sin publicación**. Continuar en \`main\` y documentar pruebas reales, no simuladas.

## Hito ejecutado — descubrimiento de empresas sin tema manual (21 octubre 2026)

- `tools/topic_discovery.py`: descubre entidades **a partir de rankings diarios Wikimedia es/en** (no de una lista preparada por ChatGPT), contrasta identificadores y tipos empresariales directos Wikidata P31, conserva página, ranking y visualizaciones; registra URL oficial Wikidata como **candidata, no fuente validada**. No confunde artículo popular con mejor oportunidad YouTube.
- Pruebas `tests/test_topic_discovery.py`: personas excluidas, URL oficial insegura excluida, controles estrictos de fecha/lotes, idiomas permitidos, rechaza datos corruptos y prueba enriquecimiento de interés de 14 días. Todo offline con fixtures; **no se presentan como tendencias reales**.
- `.github/workflows/topic-discovery-smoke.yml` ejecuta lectura pública limitada **una vez al día** programada para 10:17 UTC, y permite lanzamiento manual. Usa datos de tres días atrás por latencia de Wikimedia. No ejecuta IA de pago ni vídeo/YouTube, ni descarga Wikipedia sin limitaciones de tamaño.
- Prueba con datos reales inicial [39650638377](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39650638377) falló por respuesta mayor de 1 MB. Se ajustó límite acotado a 5 MB.
- Pruebas [39650844704](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39650844704) y [39651368713](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39651368713) **exitosas**: 240 artículos (Wikipedia en español e inglés), 8 consultas Wikidata, 1 entidad empresarial (Theranos Q16956307) y 1 serie completa de 14 días de Pageviews. Visitas al artículo inglés: 291.435 del 14 al 20 octubre, 55.952 del 7 al 13 octubre. Registro en `research/market/VALIDACION_RADAR_2026-10-21.md`.
- **Límite de interpretación:** esto es señal auténtica de interés en Wikipedia y una entidad clasificada, no todavía oportunidad demostrada de YouTube. Falta detectar más temas, analizar canales/videos comparables, contrastar fuentes y completar ranking. El motor `market_radar.py` sigue bloqueando selección si faltan sus otras señales.
- La fuente genera artefactos con retención limitada; todavía falta persistir observaciones y decisiones en D1 para seguimiento longitudinal.

**Estado actual:** descubrimiento autónomo de candidatas/medición de interés y programación diaria funcionando ✅; selección profesional del mejor tema para video, investigación completa, publicación y cierre analítico siguen sin completar.

## Segundo avance real 2026-10-21 — cobertura e historial de mercado

El sondeo aumentó su cobertura a **360 artículos populares** entre Wikipedia en español e inglés, con un máximo de 12 lotes Wikidata y 6 artículos enriquecidos con 14 días de interés. Resultado real [39652155079](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39652155079): **Theranos (Q16956307)** y **DuPont Corporation (Q221062)** detectadas, ambas con series completas.

- Theranos, artículo inglés: 291.435 visitas entre el 14–20 de octubre y 55.952 entre el 7–13.
- DuPont Corporation, artículo español: 3.512 visitas entre el 14–20 de octubre y 338 entre el 7–13.
- Estas cantidades **no** son volumen de Google Search, reproducciones YouTube ni indicadores de retención o CTR. La empresa más popular en Wikipedia no se promociona automáticamente a episodio.
- `migrations/0004_market_intelligence.sql` define tablas persistentes para ejecución, identidad de empresas, observaciones, interés y decisiones. `tools/market_persistence.py` almacena reportes idempotentemente; probó compatibilidad con migraciones anteriores usando SQLite local. CI general incluye `tests/test_market_persistence.py`.
- [39652982369](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39652982369) `success`: el workflow diario generó y subió un snapshot local SQLite con dos entidades, dos observaciones y dos series. **No** significa que D1 remoto o el panel estén conectados; el snapshot se recrea por cada ejecución y tiene retención temporal.
- Historial factual y enlaces precisos en `research/market/VALIDACION_RADAR_360_2026-10-21.md`.

**Próximo hito:** persistencia real en D1 de los snapshots por día, señal de noticias actuales, conexión autenticada a YouTube Data API y cálculo de oportunidad relativa + selección de temas aptos. Nunca publicar ni generar un guion por ver solo un pico de Wikipedia.


## Tercer avance operativo — noticias RSS y clasificación previa (21 octubre 2026)

**Lo realmente ejecutado:** junto al radar Wikimedia existente, el sistema explora cuatro búsquedas temáticas RSS (empresas, innovación, tecnología e industria) en español e inglés sin nombres fijos de empresas. `tools/news_discovery.py` conserva atribución del agregador, fecha y URL; la migración `0005_news_leads.sql` fue aplicada en D1 remota Factor, no solo simulada.

La ejecución [39668778079](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39668778079) terminó con `success` y se leyeron posteriormente en D1 **1 corrida informativa y 100 titulares almacenados**, además de 2 empresas Wikimedia. Los 100 son el **límite de muestra** y no una estimación de noticias totales ni 100 ideas viables.

El módulo `src/news-triage.mjs` asigna **relevancia preliminar del titular**, con reglas auditables para cambios empresariales, innovación, competencia y tecnología, penalizando titulares puramente comerciales/financieros. Esta puntuación **no usa cifras de demanda**, no demuestra interés de usuarios y no ordena una producción documental; requiere original de noticia, triangulación de fuentes y mercado real YouTube.

Ruta siguiente: resolver identidad de entidades y eventos, contrastar noticias con fuentes primarias, YouTube Data API para métricas observadas y establecer un ranking **multi-señal** con razones trazables. Después, recién conectar investigación autónoma y producción documental. No usar titulares RSS como hechos narrables.
