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
- [ ] Configurar secretos reales y ejecutar de extremo a extremo con credenciales propias.
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