# Plan maestro — Factor de Gigantes

**Fecha inicial:** 2026-10-20 · **Repositorio:** `eler30mr-star/FactordeGigantes` · **rama:** `main`

## 1. Propósito y meta final

Crear y operar una productora documental semiautomatizada y propia para el canal **Factor de Gigantes** (`@FactordeGigantes`), enfocada en grandes compañías, inventos, tecnología, modelos de negocio, decisiones decisivas y sus consecuencias. El objetivo de negocio es construir una audiencia sostenida y eventualmente solicitar monetización, **sin prometer resultados ni ingresos**.

El sistema debe permitir gestionar varios proyectos editoriales y, en un futuro, varios canales, con controles por cuenta y trazabilidad. Primero validar un canal y su calidad.

## 2. Identidad editorial

- Idioma: español latinoamericano comprensible internacionalmente.
- Estilo: documentales investigados, cinematográficos y accesibles.
- Promesa: descubrir el factor detrás de una gran transformación.
- Eslogan: *Las decisiones que cambiaron el mundo*.
- Formatos: documental 8–14 minutos (principal); Short 30–60 segundos (complementario).
- Cadencia orientativa al madurar: dos documentales y varios Shorts semanales, limitada por calidad/coste.
- Identidad visual: negro/charcoal, oro, elementos industriales y tecnológicos; no usar metraje ajeno sin derechos.

## 3. Reglas editoriales innegociables

1. Cada video parte de una pregunta o tesis específica, no de un guion genérico reescrito.
2. Investigación original con fuentes públicas comprobables. Registrar URL, fecha, atribución y afirmaciones a verificar.
3. Evitar datos inventados, exageraciones y acusaciones no sustentadas.
4. Licencias verificadas de música, imágenes, voces y video. No reutilizar videos de terceros para eludir copyright.
5. Separar claramente visualizaciones recreadas con IA de grabaciones reales cuando corresponda; respetar declaraciones de contenido sintético de YouTube.
6. Un humano autoriza antes de renderizar y de publicar. Nunca generar o publicar en masa sin revisión.
7. Guardar documentación editorial y técnica, sin exponer claves o datos personales.
8. Consultar las políticas vigentes de monetización de YouTube para contenido reutilizado e inauténtico antes de cada lanzamiento.

## 4. Arquitectura y componentes

### Plano de control (Cloudflare)

- Cloudflare Worker sirve API administrativa y archivos estáticos del panel.
- D1 guarda proyectos, guiones aprobados, estado y registro de cambios.
- `ADMIN_TOKEN` protege la API desde el panel en MVP; no persistir token en navegador.
- `RENDERER_TOKEN` protege rutas para el runner.
- `GITHUB_DISPATCH_TOKEN` permite al Worker solicitar una acción `workflow_dispatch`.
- Control de transición de estados: `draft → review → approved → queued → rendering → ready`; `failed` permite diagnóstico.
- Nunca incrustar credenciales o secretos en archivos estáticos.

### Plano de producción (GitHub Actions)

- Runner recibe `job_id` únicamente, obtiene el guion aprobado de la API segura.
- Genera voz preliminar sin servicios externos, tarjetas visuales propias y video H.264 usando FFmpeg.
- Entrega el MP4 como artefacto del workflow (no publica en YouTube).
- Reporta éxito/error a la API y conserva evidencia de ejecución.

### Futuro: producción de calidad y distribución

- Investigación asistida por IA con fuentes trazables y revisión de hechos.
- Voz neural con derechos de uso comercial, material visual original/licenciado, motion graphics y edición avanzada.
- Servicio de render escalable para documentales largos según coste real.
- R2 para recursos y previsualizaciones, con retención limitada.
- OAuth 2.0 YouTube Data API, subida como privado, revisión humana y publicación programada.
- YouTube Analytics para retención, CTR, horas, conversiones y pruebas de títulos.
- Opcional: herramientas AI de pago con límites de gasto por ejecución.

## 5. Modelo de datos inicial

`jobs`: `id`, `title`, `status`, `format`, `manifest_json`, `review_note`, `last_error`, `created_at`, `updated_at`. `events`: log auditable de acciones y transiciones. En el futuro separar entidades `channels`, `research_sources`, `assets`, `licenses`, `renders`, `publications` y `metrics`.

## 6. Hitos verificables

### Fase 0 — Fundamentos
- [x] Repositorio y rama principal identificados.
- [x] Plan y documento de avance.
- [x] Contrato de datos y diseño inicial de controles.
- [ ] Pruebas de seguridad y funcionamiento del primer despliegue.

### Fase 1 — MVP de guion a previsualización
- [x] API, D1, panel, controles de aprobación.
- [x] Workflow GitHub Actions para renders bajo demanda.
- [x] Script de render con escenas y narración provisional.
- [x] Configurar secretos reales y ejecutar de extremo a extremo con credenciales propias. Confirmado en run 39471906672 (MP4 v0.1) y D1 `ready`.
- [ ] Verificar costos, fallos y accesibilidad móvil.

### Fase 2 — Producción documental profesional
- [ ] Investigación con trazabilidad por afirmación.
- [ ] Generación asistida de guiones; verificación humana.
- [ ] Voz natural con licencia comercial.
- [ ] Motion graphics, recortes, cronologías, imágenes con derechos, música comercial autorizada.
- [ ] QA automático audiovisual y revisión humana completa.
- [ ] Pruebas de videos 8–14 min y Shorts.

### Fase 3 — Distribución
- [ ] Autenticación OAuth de canal YouTube (consentimiento explícito).
- [ ] Subida como privado/no listado y programación solo tras aprobación.
- [ ] Comprobar estado/verificación del proyecto de YouTube API, cuotas y políticas.
- [ ] Control de duplicados, errores, reintentos y auditoría de publicaciones.

### Fase 4 — Analítica, optimización y escala
- [ ] YouTube Analytics; panel KPIs por video y periodo.
- [ ] Optimización editorial con historial de decisiones.
- [ ] Presupuestos mensuales y alertas; expansión a varios canales sólo si hay retorno.

## 7. Reglas de desarrollo

- Todo trabajo directamente en `main` según la forma de sincronización de este proyecto.
- `docs/AVANCE.md` se actualiza en cada entrega con hecho, pendiente y siguiente acción.
- Código y visuales específicos del producto; no plantillas genéricas sin propósito.
- No marcar como terminado ningún punto sin prueba ejecutada.
- Sin secrets en Git, videos con copyright, ni publicación automática sin consentimiento.
- Cada cambio debe tener verificación, rutas claras de rollback y posibilidad de continuar después.

## 8. Aceptación final

Un documental puede investigarse, guionizarse, producirse con calidad, revisarse, publicarse con permiso y medirse desde una plataforma coherente; con flujo automatizado, evidencias de originalidad y coste controlado. Ningún simple video genérico prueba esa meta.
## 9. Entrega audiovisual v0.2 (2026-10-20)

- Motor de voz neuronal local Piper y modelo `es_MX-ald-medium` incorporados; smoke y generación de MP4 comprobados en GitHub Actions, sin API de IA de pago.
- Workflows de render usan voz Piper predeterminada, gráficas editoriales con movimiento Ken Burns, subtítulos quemados y archivos auxiliares `subtitulos.srt`, `ficha.json`, `creditos.txt`.
- Validación de códecs, resolución y duración mediante `ffprobe`. Se corrigió a partir de una revisión visual real la escala excesiva de subtítulos verticales.
- Requisitos no alcanzados: calidad editorial cinematográfica, metraje con licencias, verificaciones de fuentes/afirmaciones, validación de derechos de voz derivada, alineación fonética y OAuth YouTube. Este hito es una previsualización **técnica mejorada**, no producción final apta para monetización.

## 10. Identidad vocal del canal — decisión editorial

El propietario ha definido una voz objetivo más adulta, profesional, seria, natural, con autoridad y pronunciación clara para historias de empresas, innovaciones y decisiones. Idealmente español latinoamericano comprensible internacionalmente. No asumir una edad real ni género del locutor a partir de los nombres de modelos; se evaluarán auditivamente.

- Mantener una sola voz institucional estable para documentales y Shorts.
- Conservar voces alternativas como candidatas para audición, pruebas o narraciones especiales; nunca sustituir automáticamente al narrador oficial.
- El modelo actual, es_MX-ald-medium, queda como referencia técnica hasta aprobar una nueva identidad.
- Audición A/B/C preparada con es_MX-ald-medium, es_MX-claude-high y es_ES-davefx-medium; reproducir el mismo texto y revisar timbre, neutralidad, pausas, claridad, pronunciación de empresas y licencias.
- El panel necesitará configuración persistente de identidad vocal: modelo, velocidad, pausas, pronunciaciones especiales, prueba auditiva y control de versión.
- No activar publicación comercial de ningún modelo sin revisar términos del dataset, pesos y entrenamiento.

## Política económica definitiva — cero pagos (2026-10-20)

Decisión expresa del propietario: **no utilizar servicios de pago, suscripciones, saldos de prueba que luego se facturen, ni motores que requieran contratar un nivel pagado para explotar comercialmente los audios**.

- Descartar la contratación Azure Speech S0 y cualquier API TTS pagada. La voz Microsoft `es-EC-LuisNeural` se conserva **solo como referencia de estilo** (natural, formal, fluida), no como dependencia, proveedor ni voz oficial aprobada.
- Priorizar motores locales, de código abierto y modelos con derechos de uso comercial **verificados para cada voz/modelo**, no solo para el motor base.
- Antes de integrar un proveedor, comprobar licencia de pesos, dataset, referencias y restricciones de redistribución y uso comercial.
- No activar por defecto facturación, claves de servicios cobrables, upgrades de planes ni workflows que incurran en cargo sin autorización explícita posterior del propietario.
- **Gratis no significa ilimitado:** verificar cuotas de GitHub Actions/Cloudflare; establecer límites de duración, reintentos y frecuencia para mantener el proyecto dentro de las franquicias gratuitas. Ante agotamiento, detener/posponer en vez de generar cargos.
- No reducir calidad con filtros artificiales de pitch; la identidad vocal final será una voz natural seleccionada mediante audición real y fijada para todos los videos.
- Desarrollo y registro de avance directamente en `main`.

## Dirección vocal de referencia: documentales de naturaleza (20-10-2026)

El usuario elige **como referencia de ESTILO**, no como persona a imitar, el narrador masculino de documentales de animales de Discovery: cadencia más pausada, voz cálida, serena, inteligible y profesional, autoridad contenida y buen manejo de silencios. El canal continúa siendo sobre historia empresarial y decisiones influyentes.

- El narrador preferido sigue siendo la **tercera muestra Qwen3 de dicción profesional**, con BlackBerry pronunciado aproximadamente «Blákberri» (rr fuerte).
- La última versión de prueba se ralentizó con `atempo=0.94` (sin cambiar altura) y se añadieron tres pausas de 160 ms en silencios entre frases; los resultados se mantendrán sujetos a evaluación humana.
- La corrección de la «a» prolongada en **«Durante años»** es un ajuste puntual, no una modificación global del ritmo ni una voz nueva.
- Cero pagos, sin clonación de personas identificables, cambios solo en rama `main`; pendiente integración al render hasta que la voz y la arquitectura sean sostenibles.


## Hito alcanzado: referencia vocal guardada y motor CPU experimental funcional (2026-10-20)

- Patrón auditivo del narrador aprobado, inalterado en `assets/voice/approved/narrador_documental_aprobado.mp3`, con verificador SHA-256, manifest y protección frente a cambios accidentales.
- Qwen3 Base 1.7B ha generado correctamente nueva frase al usar la referencia en la **demo pública con cuota limitada**; no permite asumir producción masiva.
- Qwen3 Base 0.6B ya ha sintetizado por primera vez localmente en CPU de GitHub Actions, sin API ni GPU pagada; rendimiento medido para solo 8,424 segundos de audio. La **aprobación audible de la muestra 0.6B no existe todavía**.
- Para llegar a la meta final, falta: verificar calidad y consistencia de la voz en muchos fragmentos; medir coste temporal en documentales completos sin sobrepasar recursos gratuitos; comprobar derechos de uso comercial y eliminar la dependencia de demos con cuotas; integrar al motor/render y panel sólo después de esas verificaciones.
- Nada de pagar, no incorporar automáticamente voces peores, ni publicar audiovisuales sin revisión.


## Hito adicional — mismo modelo 1,7B funcionando en CPU (2026-10-20)

Tras detectar una ligera diferencia de timbre en la audición Qwen 0,6B, se ejecutó la versión `Qwen3-TTS Base 1,7B` en CPU gratuita, con salida MP3 verificable, mismos datos de referencia y mismo guion. La prueba terminó con éxito: 7,680 s de audio, ~88,62 s de ejecución del proceso Python y ~11,28 GiB de RAM pico; workflow 39512992392.

La variante local de mayor tamaño no reemplaza todavía la voz elegida ni supone autorización comercial. Faltan comparación auditiva humana, robustez en segmentos largos, cálculo real de throughput, licencias aplicables y conservación de la cadencia vocal. Las pruebas CPU pesadas son manuales y solo en repositorio público.

## Decisión editorial vinculante: una sola voz canónica

Confirmación expresa del propietario mediante nueva subida: `FactorDeGigantes_Documental_TomaNatural.mp3` **es la voz correcta**. Coincide exactamente con el MP3 versionado en `assets/voice/approved/narrador_documental_aprobado.mp3` (SHA-256 `78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d`).

No se acepta automáticamente el 0,6B ni el 1,7B local como sustituto, aunque sean ejecutables con CPU gratis. Ambos son ensayos sin aprobación vocal. Objetivo de ingeniería: producir nuevas frases que suenen como **esta identidad exacta**, sin modificar la referencia, sin usar servicios de pago y sin activar publicación en YouTube. Si no se demuestra continuidad, mantener bloqueada la integración de Qwen.

## Subhito de Fase 2 — continuidad vocal segmentada sin pagos (2026-10-20)

- [x] Crear banco de dos fragmentos para experimentar continuidad de la voz fija en Qwen Base 1,7B CPU (script, tests y workflow manual en `main`); CI de contratos [39515949183](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39515949183) exitosa.
- [ ] Ejecutar el workflow manual `voice-continuity-cpu.yml`, comprobar dos MP3 nuevos y revisar métricas y límites gratuitos (crear el workflow no equivale a ejecutarlo).
- [ ] Obtener aceptación auditiva **expresa de ambas tomas** por el propietario comparándolas con `FactorDeGigantes_Documental_TomaNatural.mp3` inalterado.
- [ ] Demostrar continuidad en narraciones largas, validar derechos comerciales de todos los componentes, implementar QA de voz/visual y recién entonces evaluar integración en `render.yml`.
- [ ] Continuar investigación con fuentes verificables, activos originales con licencia y producción de primer documental 8–14 min.

**Restricciones vigentes:** cero pagos, únicamente `main`, patrón vocal canónico único, experimentos no equivalen a aprobación, y ninguna publicación en YouTube sin consentimiento expreso. Fase 2 sigue **abierta**.
