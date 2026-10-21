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
