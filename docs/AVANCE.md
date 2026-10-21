# Historial de avance — Factor de Gigantes

> **Estado vigente 2026-10-21:** **D1 real migrada hasta 0009**; radar completo de esta etapa enlaza RSS → resolución Wikidata → páginas corporativas P856 → evaluación automática trazable, con GitHub OIDC y Worker desplegado. Datos REMOTOS verificados: 114 titulares, 2 entidades noticia–Wikidata (Toyota y América Móvil), 2 páginas corporativas accesibles con SHA-256 (Toyota y DuPont), 4 evaluaciones y **0 selecciones aprobadas**. La prioridad continúa siendo YouTube Data API REAL, contrastar afirmaciones primarias, seleccionar y conectar investigador/guionista/productora de 8–14 min. Sin YouTube no se presume ganador; YouTube y publicación permanecen bloqueados por permisos/evidencias.

## 2026-10-20 · Inicio del proyecto

**Repositorio:** https://github.com/eler30mr-star/FactordeGigantes
**Rama obligatoria:** `main`
**Estado global:** fase 1; D1 real configurada y esquema inicial aplicado; despliegue Worker y conexión al canal pendientes.

### Confirmado
- El repositorio de la cuenta `eler30mr-star` estaba vacío y con `main` como rama predeterminada.
- Se creó README inicial en el primer commit.
- Se diseñaron plan maestro y políticas editoriales.
- Se construyó la base del panel web/Worker/D1 y el renderizador preliminar de videos.
- Se añadió el flujo de CI para validación y el workflow manual para renderizar.

### Limitaciones verificables
- **D1 existe y sus tablas fueron verificadas directamente en Cloudflare.**
- **No hay despliegue del Worker confirmado.**
- **No hay conexión OAuth con YouTube ni publicación de videos.**
- **No hay secretos de producción cargados.**
- **No hay prueba de render dentro de GitHub Actions confirmada todavía.**
- Audio e imágenes del render son maquetas técnicas propias, no la calidad final exigida para monetización.

### Próximas tareas prioritarias
1. Ejecutar los tests del workflow en GitHub Actions y corregir cualquier error.
2. [HECHO] D1 creada, `database_id` conectado en `wrangler.jsonc` y esquema inicial aplicado mediante Cloudflare API. Confirmadas las tablas `jobs` y `events` y sus índices.
3. Desplegar Worker + assets y agregar secretos `ADMIN_TOKEN`, `RENDERER_TOKEN`, `GITHUB_DISPATCH_TOKEN`.
4. Configurar secrets `API_BASE_URL` y `RENDERER_TOKEN` en GitHub Actions.
5. Crear y aprobar guion real con fuentes verificadas; ejecutar un render y comprobar el MP4.
6. Mejorar calidad documental (voz neural con licencia, edición visual original, investigación y gráficos).
7. Solo después, implementar OAuth e integración de subida privada a YouTube.

### Criterio de reporte
Nunca confundir “archivo creado”, “test pasado”, “desplegado” o “publicado”. El avance registra expresamente cuál de esas etapas se ha comprobado.

### Última entrega
Se ha guardado en `main` la estructura inicial del motor:
- Panel responsivo en `public/` con formulario y cola editorial; edición de borradores y botones de revisión/aprobación.
- API Cloudflare Worker con D1, eventos y credenciales separadas para administración y render.
- Guion a previsualización mediante `tools/render.py` y `.github/workflows/render.yml` (secuencia de escenas originales y voz técnica eSpeak NG).
- Test de contrato del manifest en `tests/test_render.py` y CI `.github/workflows/check.yml`.
- Documento de despliegue con recursos, secretos y advertencias de coste.

**Verificación efectuada:** archivos visibles/recuperables por la conexión de GitHub en la rama `main`; verificación de **sintaxis JavaScript superada** en `src/worker.js` y `public/app.js` mediante compilación sintáctica aislada. **Sin verificación de tests ejecutados en GitHub Actions ni render FFmpeg real**, pues no se obtuvo estado de workflows para estos commits, y **sin despliegue** en Cloudflare. La producción audiovisual todavía es una previsualización técnica, no apta como documental final de monetización.

**Siguiente paso exacto:** crear/importar Worker `factor-de-gigantes` desde `eler30mr-star/FactordeGigantes`, rama `main`; validar CI/manifest y el despliegue, configurar secretos y ejecutar creación → revisión → aprobación → render real → descarga del MP4. Mejorar la producción documental profesional después. Después probar creación → revisión → aprobación → render real → descarga del MP4 y mejorar voz/arte documental.

## 2026-10-20 · Base Cloudflare D1 conectada
- Captura del panel del usuario y lectura autenticada de Cloudflare confirmaron la base `factor-de-gigantes-db`, UUID `ef699e75-b50a-4e28-a665-69316d10cdaf` en la cuenta de Cloudflare correspondiente.
- Se actualizó en `main` el archivo `wrangler.jsonc` con el identificador real. Commit: `8e6d1e3b1e03ce07e97586a49eb15201a0c64379`.
- Se aplicó mediante la API D1 el contenido del esquema de `migrations/0001_initial.sql` (4 sentencias: tablas `jobs` y `events`, 2 índices). La API devolvió éxito.
- Segunda consulta independiente confirmó dos tablas de aplicación: `jobs`, `events`, y sus índices. La tabla `_cf_KV` es interna de D1.
- La migración se ejecutó por API SQL y **no** por el mecanismo de historial de migraciones de Wrangler; el archivo inicial es idempotente y no debe ser modificado retroactivamente.
- **Pendiente**: crear/importar Worker, desplegar, configurar secretos y realizar una prueba funcional real. No se ha publicado ningún video.

## 2026-10-20 · Worker desplegado en Cloudflare
- Cuenta Cloudflare y servicio verificados por API: Worker `factor-de-gigantes`, despliegue `31099688-495e-4c96-87ac-3290a965198b` creado a las 16:41:44 UTC; 100 % del tráfico asignado a la versión desplegada.
- Asset binding `ASSETS` presente: panel estático incluido en el servicio.
- Binding `DB` apunta a la D1 real `ef699e75-b50a-4e28-a665-69316d10cdaf`.
- Variables `GITHUB_REPO=eler30mr-star/FactordeGigantes` y `GITHUB_WORKFLOW=render.yml` verificadas.
- Subdominio workers.dev habilitado; dirección prevista `https://factor-de-gigantes.martin30-eler.workers.dev`.
- Consulta de secretos devolvió lista vacía: `ADMIN_TOKEN`, `RENDERER_TOKEN`, `GITHUB_DISPATCH_TOKEN` todavía **NO configurados**.
- La URL /health y el panel **no pudieron probarse desde el entorno de verificación externo**; confirmar respuesta HTTP real desde navegador del propietario.
- **Siguiente paso:** configurar secretos seguros (sin publicarlos en GitHub), verificar /health, acceso autenticado a /api/jobs, posteriormente conectar Workflow GitHub Actions y probar render.

## 2026-10-20 · Inicio de autenticación administrativa
- Verificación autenticada de Cloudflare confirmó que existe un secreto llamado `ADMIN_TOKEN`, enlazado a `factor-de-gigantes` como `secret_text`, sin exponer su valor.
- La consulta de bindings confirmó que el Worker continúa enlazado a la base D1 correcta.
- `RENDERER_TOKEN` y `GITHUB_DISPATCH_TOKEN` aún no existen en el Worker.
- Pendiente comprobar que el `ADMIN_TOKEN` tiene al menos 24 caracteres (requisito del código) y que el panel acepta la autenticación; la API de Cloudflare no devuelve valores de secretos.
- Siguiente acción: agregar `RENDERER_TOKEN` fuerte en Cloudflare y el mismo valor en GitHub Actions Secrets; configurar después el token de despacho limitado al repositorio, probar acceso y render.

## 2026-10-20 · Panel web abierto por el propietario
- El propietario confirmó que la URL del panel se abrió en su navegador.
- Esa confirmación acredita acceso a la página, **no confirma por sí sola** que la autenticación de `ADMIN_TOKEN` o la creación de trabajos se haya probado.
- GitHub Actions aún requiere `RENDERER_TOKEN` en ambos servicios y `API_BASE_URL` en GitHub; el despacho requiere `GITHUB_DISPATCH_TOKEN` en Cloudflare. No se han guardado secretos en el repositorio.
- Próximo paso: comprobar que el botón «Conectar» muestra «Nuevo documental», luego configurar secretos compartidos y ejecutar una prueba de render.

## 2026-10-20 · Secreto RENDERER_TOKEN confirmado en Cloudflare
- La API de Cloudflare confirma `RENDERER_TOKEN` como `secret_text` vinculado al Worker `factor-de-gigantes`, junto con `ADMIN_TOKEN`, `ASSETS` y D1.
- El usuario comunicó que había creado el secreto solicitado. **No se puede comprobar desde el conector disponible que el mismo valor esté en GitHub Actions; verificarlo en primera prueba.**
- Quedan pendientes: en GitHub Actions, `API_BASE_URL` con el origen Worker; en Cloudflare, `GITHUB_DISPATCH_TOKEN` como secreto con PAT fino limitado a Actions write para el repositorio.
- Después realizar prueba de extremo a extremo, validando estado y artefacto MP4. Ni render real ni subida a YouTube están confirmados aún.

## 2026-10-20 · Verificación posterior a la configuración de tokens

- El usuario indicó que concluyó la configuración de los valores solicitados.
- Consulta autenticada a Cloudflare: existen `ADMIN_TOKEN` y `RENDERER_TOKEN`, ambos como `secret_text`, y D1 sigue vinculada al Worker.
- **`GITHUB_DISPATCH_TOKEN` aún NO figura en la lista de secretos del Worker**: no está completada la conexión de despacho desde el panel hasta GitHub Actions, aunque el token personal se haya generado en GitHub.
- Se verificó que el repositorio contiene `.github/workflows/render.yml` y `.github/workflows/check.yml`. El flujo `render.yml` necesita `API_BASE_URL` y `RENDERER_TOKEN` como secretos de Actions, cuyos valores o existencia no puede comprobar el conector GitHub actualmente.
- Siguiente paso **inmediato**: guardar el PAT de GitHub como secreto `GITHUB_DISPATCH_TOKEN` en `factor-de-gigantes` (Cloudflare → Settings → Variables and Secrets, tipo Secret). Luego confirmar por API y ejecutar prueba controlada de render desde el panel.
- No se ha creado ni publicado ningún video en YouTube en esta etapa.

## 2026-10-20 · Los tres secretos del Worker confirmados
- Verificación autenticada de Cloudflare: `ADMIN_TOKEN`, `RENDERER_TOKEN` y `GITHUB_DISPATCH_TOKEN` están presentes como `secret_text` en `factor-de-gigantes`.
- El Worker conserva `ASSETS`, binding D1 `DB` y variables `GITHUB_REPO`, `GITHUB_WORKFLOW`. Último despliegue observado: 2026-10-20 17:07:07 UTC.
- No se han leído ni almacenado los valores de esos secretos.
- **Próximo paso verificable:** comprobar en GitHub Actions (Settings → Secrets and variables → Actions) que existen `RENDERER_TOKEN` y `API_BASE_URL` (mismo `RENDERER_TOKEN` que Cloudflare; URL del Worker sin barra final). El conector disponible no ofrece lectura del listado de secretos del repositorio.
- Después crear un guion de prueba con fuentes, revisarlo y aprobarlo expresamente desde el panel; usar «Generar prueba» para comprobar despacho, MP4 y reporte de estado. Sin publicación a YouTube.

## 2026-10-20 · Primera prueba preparada, sin ejecución
- El usuario confirmó que agregó el secreto `RENDERER_TOKEN` en GitHub Actions; el conector GitHub no ofrece listar secretos, así que su existencia y coincidencia de valores están reportados por el propietario, no verificados mediante API.
- Consulta autenticada confirmó que Cloudflare mantiene los tres secretos: `ADMIN_TOKEN`, `RENDERER_TOKEN`, `GITHUB_DISPATCH_TOKEN`.
- Se creó un **borrador técnico** directamente en la D1 real, sin aprobación ni ejecución, para comprobar el recorrido del panel. ID: `30eceeae-70b5-315a-1bc1-d5e0d4185421`, título: `Demostración técnica del motor Factor de Gigantes`, formato `short`, 3 segmentos de prueba. Se registró el evento `created`.
- La entrada usa el guion de ejemplo `examples/documental.json`. Sus URLs son ejemplos de fuentes, no un trabajo de investigación confirmado. **No publicar este material en YouTube.**
- El propietario debe autenticar el panel, actualizar la lista, pasar el trabajo a revisión, confirmar su carácter de prueba técnica, aprobarlo, y pulsar «Generar prueba» para activar GitHub Actions.
- El éxito de la creación de MP4, entrega del artefacto y reporte `ready` **NO** está verificado aún.

## 2026-10-20 · Rechazo GitHub HTTP 403 al solicitar render
- El propietario intentó renderizar desde el panel y reportó el mensaje `GitHub rechazó el render (HTTP 403)`.
- La D1 fue consultada después: trabajo `30eceeae-70b5-315a-1bc1-d5e0d4185421` sigue en estado `approved`, no se despachó ni perdió.
- Se comprobó que `eler30mr-star/FactordeGigantes` tiene rama `main` y la conexión GitHub propietaria posee permiso admin; el workflow `render.yml` existe y declara `workflow_dispatch`. El permiso requerido por la API GitHub para ese endpoint es `Actions: write` sobre el repo. **No se conoce todavía la configuración del fine-grained PAT guardado como `GITHUB_DISPATCH_TOKEN`.**
- Se modificó `src/worker.js` en `main`, commit `a69ec4315463f807f30834cb5564e63ce11796df`, para clasificar las causas comunes de respuestas GitHub 403/401 sin incluir secretos en la salida. La sintaxis del JS modificado se validó con compilación aislada.
- La API Cloudflare confirmó un nuevo despliegue y que el código activo incluye el diagnóstico mejorado; también conservó los tres secretos.
- Siguiente paso: reintentar **una sola vez** «Generar prueba», observar el mensaje exacto si persiste y comprobar/revisar en GitHub los permisos del fine-grained PAT (resource owner `eler30mr-star`, repo `FactordeGigantes`, `Actions: Read and write`). No modificar `RENDERER_TOKEN` ni `API_BASE_URL` por este error.
- **Sin MP4 producido ni publicación YouTube hasta confirmar workflow.**

## 2026-10-20 · HTTP 403 persiste y CI comprobada
- El usuario confirmó que sigue viendo «GitHub rechazó el render (HTTP 403)» y preguntó si debía llenar el formulario de un nuevo documental. Se aclaró que **no**: existe un trabajo aprobado y el formulario es solo para trabajos nuevos.
- Lectura de GitHub Actions autenticada: se encontraron 19 ejecuciones del workflow «Comprobar base» y las más recientes finalizaron en `success`; no existe ninguna ejecución con `event=workflow_dispatch` al momento de revisar. Esto demuestra que el motor no ha arrancado, mientras que el CI básico sí se ejecuta.
- Pendiente: corregir `GITHUB_DISPATCH_TOKEN` (token PAT fine-grained: propietario `eler30mr-star`, acceso específico al repositorio, permiso `Actions: Read and write`, no caducado) y probar nuevo despacho sobre el trabajo aprobado.

## 2026-10-20 · Primer dispatch real y diagnóstico de HTTP 403 de retorno
- Tras corregir el PAT `GITHUB_DISPATCH_TOKEN` (se había elegido Contents en lugar de Actions), el propietario pulsó «Generar prueba» y GitHub aceptó el dispatch. Run **39468744180** del workflow `render.yml`.
- El primer run real **falló**: FFmpeg, eSpeak NG y Pillow se instalaron bien, pero `tools/render.py` recibió `urllib.error.HTTPError: HTTP Error 403` al solicitar el guion al Worker. El callback `tools/report.py` también recibió 403, y **no se generó MP4** ni artefacto.
- La base D1 quedó indebidamente en `queued` porque el callback falló. Tras verificar que la ejecución GitHub había finalizado con `failure`, se restableció de `queued` a `approved` conservando la revisión humana; evento `render_retry_prepared` y detalle del fallo. **No se lanzó otro render automáticamente**.
- Se reforzó `tools/render.py` en `main`, commit `3339e96ba12e629627c41f18dbf05e40cb86701b`: prueba pública `/health`, validación del producto, `User-Agent` explícito y clasificación segura de HTTP 401/403.
- Se agregó diagnóstico no bloqueante en `.github/workflows/check.yml`, commits `02e9b4f244b4a86e264acc5a1356cec87462ba65` y `b7ca7f0f2100ec2dd43c50ee3013d025e687c870`.
- **CI real comprobado en GitHub**: run 39469467971 confirmó dominio exacto `factor-de-gigantes.martin30-eler.workers.dev`, HTTP 200 en `/health` y producto esperado. Run 39469645669 confirmó que `RENDERER_TOKEN` del repositorio es válido: GET autenticado de UUID inexistente respondió HTTP 404 esperado, JSON del Worker. Los tests y sintaxis de `check.yml` también concluyeron en success.
- Se cambió además `tools/report.py` para enviar la misma identidad HTTP del renderizador, commit `31455380fcc73bd391aebf7d9da079fef844ed89`.
- **Hipótesis, no hecho confirmado:** el 403 inicial al acceder al Worker pudo relacionarse con el User-Agent predeterminado de Python; los nuevos pasos confirman acceso válido al Worker usando User-Agent específico, pero falta probar el guion real `queued` y el reporte `ready`.
- Próxima acción: el propietario debe pulsar **una vez** «Generar prueba» en el trabajo ya `approved`; revisar GitHub Actions, artefacto MP4 y estado D1. Publicación YouTube no implementada.

## 2026-10-20 · Primera generación MP4 completada de extremo a extremo
- **Run GitHub Actions 39471906672:** `render.yml` finalizó `success` en `main` para el trabajo `30eceeae-70b5-315a-1bc1-d5e0d4185421`; todas las etapas de generación, carga del artefacto y reporte al Worker pasaron.
- El artefacto `vista-previa-30eceeae-70b5-315a-1bc1-d5e0d4185421` quedó cargado como ZIP (artifact ID `12287965396`). URL: https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39471906672/artifacts/12287965396 .
- En los logs: tres escenas renderizadas con duraciones estimadas 8,5 s; 9,0 s; 8,9 s. El proceso informó salida `dist/video.mp4` de 1.086.696 bytes.
- Se descargó el ZIP y se inspeccionó el MP4 con `ffprobe`: formato vertical **720×1280**, H.264 + AAC, **25,821451 s**, **1.086.696 bytes**. Es un archivo existente, no solo estado de workflow.
- La API D1 devolvió el trabajo en estado **`ready`**, `last_error` vacío. GitHub Actions registró `Estado reportado: ready 200`.
- Primer circuito funcional confirmado: panel de aprobación → Cloudflare Worker → GitHub Actions → FFmpeg → artefacto descargable → reporte al Worker/D1.
- **Este es un render técnico de prueba, no material documental profesional ni apto para publicarse en YouTube**. Usa tarjetas originales y narración local eSpeak; no hay voz natural premium, montaje cinematográfico, assets audiovisuales licenciados, subtítulos editoriales ni subida OAuth.
- Siguiente fase: revisar visualmente y auditivamente la previsualización, mejorar calidad audiovisual, estructura documental, documentación de fuentes, UX de descarga desde el panel, y posteriormente solo si se solicita implementar subida privada a YouTube.

## 2026-10-20 · Avance motor audiovisual gratuito Piper v0.2
- Implementados y guardados en `main` los módulos `tools/voice.py` (Piper local con verificación SHA-256 del ONNX) y `tools/subtitles.py` (SRT por duración de escena, alineación aproximada).
- Integrado en `tools/render.py` movimiento de cámara Ken Burns, subtítulos incrustados, SRT externo, fichero `ficha.json`, créditos/licencias y control `ffprobe` sobre dimensiones, audio/video, duración y tamaño.
- `.github/workflows/voice-smoke.yml` instala Piper 1.8.0, recupera/cacha la voz `es_MX-ald-medium`, genera audio WAV real, renderiza un MP4 de prueba con Piper y publica artefactos temporales; las pruebas unitarias se añadieron a `tests/test_voice_subtitles.py`.
- **Ejecución real GitHub Actions 39476712983: success**. Instalación, descarga y checksum de la voz y síntesis WAV sin API de pago confirmadas.
- **Ejecución real 39477025112: success**. Primer MP4 v0.2 completo con voz Piper, subtítulos y artefactos; una inspección visual posterior detectó subtítulos desproporcionados que cubrían la escena. No se declaró suficiente.
- Se corrigieron tamaño, posición, estilo de fondo y longitud de línea de subtítulos (`tools/render.py`, `tools/subtitles.py`). **Ejecución real 39477498852: success**: MP4 v0.2 renderizado, comprobaciones de voz, metadatos y SRT superadas. Fotograma del minuto 0:09 inspeccionado visualmente; subtítulos ahora están en la franja inferior sin ocultar títulos.
- Artefacto de prueba visual: https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39477498852 ; el MP4 fue descargado e inspeccionado con FFprobe: **26,791667 s, 720×1280, H.264 y AAC, 845009 bytes**. `check.yml` en la misma revisión: run 39477499038, `success`.
- El workflow principal `render.yml` ahora instala Piper con caché e invoca `--voice-engine piper --captions burn`, entregando MP4/SRT/ficha/créditos. El **workflow remoto v0.2 con trabajo D1 nuevo todavía no se ha ejecutado**; su funcionamiento se infiere de componentes aislados, no debe marcarse como probado de extremo a extremo para la versión nueva.
- Licencias: Piper 1.8.0 (GPL-3.0-or-later). El MODEL_CARD `es_MX-ald-medium` describe dataset Unlicense y afinación desde otro modelo de voz: **pendiente auditoría de derechos derivados antes de distribuir material comercial**. No hubo subida a YouTube.
- **Siguiente entrega:** incorporar recursos visuales documentales originales/licenciados con procedencia por escena y mejorar el guion de investigación; luego pruebas de render largo y subtítulos con alineación precisa, y sólo al final OAuth subida privada.

## 2026-10-20 · Evaluación comparativa de identidad vocal

- Comentario editorial del propietario: el estilo de Piper actual se percibe demasiado parecido a un canal de descubrimientos; preferencia por una voz adulta y profesional para Factor de Gigantes.
- Se mantienen las voces del sistema remoto sin cambio: no se sustituyó automáticamente el narrador por una alternativa no escuchada.
- Se amplió tools/voice.py con un catálogo restrictivo y dos nuevos modelos de Piper; hash SHA256 tomado de páginas oficiales del modelo.
- Se agregó tools/audition.py y workflow voice-audition.yml en main. Reproducen exactamente el mismo fragmento sobre BlackBerry con tres voces, sin publicación en YouTube ni llamadas a API de pago.
- Se añadieron tests de catálogo y permiso explícito de modelos, y CI general se verificó en GitHub con éxito.
- Ejecución real GitHub Actions 39487653479 terminada en SUCCESS, artefacto de audición 12293493424 incluye es_MX-ald-medium.wav, es_MX-claude-high.wav, es_ES-davefx-medium.wav y comparacion.json. Se descargó el ZIP y verificó la presencia de las tres muestras de audio.
- Falta escuchar, puntuar y elegir el narrador oficial; posteriormente aplicar por canal la voz seleccionada con configuración de velocidad, pausas y guía de pronunciación. Antes de publicación comercial, revisar licencias de datasets, modelos y procedencia.
- Próximos pasos: selección auditiva del propietario, configuración persistente por canal en D1/panel, control de versión de narrador, pruebas del flujo de render remoto v0.2 y producción visual documental licenciada.


## 2026-10-20 · Segunda audición de voz: búsqueda de timbre más grave

- El propietario escuchó las primeras tres voces de Piper; la tercera (`es_ES-davefx-medium`) se aproximó, pero suena demasiado fina/aguda para una voz institucional adulta.
- No se cambió la voz oficial ni la configuración de renders aprobados.
- Se identificó el motor abierto Kokoro 82M, licencia Apache-2.0 declarada para el modelo, con dos voces masculinas en español: `em_alex` y `em_santa`. Sigue pendiente evaluar las licencias y procedencia de voces específicas.
- Se añadió `tools/audition_kokoro.py` y `.github/workflows/voice-kokoro.yml` para generar dos WAV originales y una tercera variante de tono ligeramente más grave (`em_alex_grave_sutil`), con idéntico texto de referencia sobre BlackBerry.
- La variante de tono no es una voz nueva y está etiquetada claramente. No hay publicación, conexión a YouTube ni API TTS de pago.
- **Pendiente de esta entrega:** confirmar en GitHub Actions que el job completó y guardó tres WAV válidos; escuchar muestras y decidir cuál se acerca a la identidad buscada.

## 2026-10-20 · Nuevas voces Kokoro verificadas (3 muestras reales)
- La audición GitHub Actions **39489493745** concluyó **success**: instalación de Kokoro 0.9.4 en CPU, generación y validación de audios, subida de artefacto `12295111773`. Enlace: https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39489493745 .
- ZIP de artefacto descargado y verificado con Python: contiene `em_alex.wav` (16,45 s), `em_santa.wav` (16,68 s), `em_alex_grave_sutil.wav` (16,43 s) y `comparacion.json`, todos WAV mono PCM 24 kHz, cada uno con más de 780 KB.
- Los dos primeros son voces masculinas Kokoro en español. El tercero es una variante técnica de `em_alex` con pitch reducido ~6 % y tempo compensado: **no es otro locutor** y debe juzgarse por naturalidad.
- Modelo Kokoro-82M de pesos con licencia declarada Apache-2.0 (source: https://huggingface.co/hexgrad/Kokoro-82M); revisar licencias y procedencia de cada voz antes de publicación con fines comerciales.
- La búsqueda responde a la evaluación del propietario de que `es_ES-davefx-medium` se acerca pero suena demasiado fina.
- No se cambió el narrador predeterminado de `render.yml`, ni se generó publicación YouTube. Próximo paso: escuchar y elegir candidata (o buscar una voz más grave todavía), después construir el selector fijo de narrador por canal.

## 2026-10-20 · Se rechaza la segunda audición Kokoro por artificiosidad

- El propietario escuchó el lote Kokoro (`em_alex`, `em_santa` y variante `em_alex_grave_sutil`) y lo rechazó: "parece narrador raro". Ninguna de estas voces queda aprobada para ser identidad del canal.
- Preferencia vigente: narración masculina adulta, natural, cálida pero con cuerpo, sobria, creíble, profesional y apta para documentales empresariales. No confundir graveza artificial con madurez; evitar pitch-shift.
- No modificar automáticamente la voz del render actual, D1 ni secretos mientras no exista una identidad vocal aceptada.
- Alternativa técnica investigada (no implementada ni probada): **ResembleAI Chatterbox Multilingual v3** y su paquete regional `Chatterbox-Multilingual-es-mx-latam`. El proveedor declara español LATAM y licencia MIT. Referencias: https://github.com/resemble-ai/chatterbox y https://huggingface.co/ResembleAI/Chatterbox-Multilingual-es-mx-latam .
- Chatterbox es más pesado que Piper/Kokoro; antes de añadirlo a renders se necesita comparar consumo real en GitHub Actions Free, disponibilidad CPU, coste temporal y calidad auditiva. No prometer ejecución gratuita ilimitada.
- Si se usa una voz de referencia para identidad estable, requerir una muestra original/expresamente licenciada o autorización del locutor; no clonar voces de figuras conocidas sin permiso.
- Próximo paso: decidir entre muestra de voz con derechos propios para una voz de marca y test de Chatterbox sin referencia, o seguir buscando una voz preentrenada natural con licencia comercial verificada. Mantener publicación de YouTube desactivada.

## 2026-10-20 · Referencia exacta de voz: Microsoft Luis (Ecuador)

- El propietario mostró una captura de Microsoft Speech Studio y seleccionó la voz **Luis, Español (Ecuador)** como ejemplo del estilo vocal deseado para Factor de Gigantes: narración masculina fluida, formal y profesional. Esta referencia reemplaza la búsqueda vaga de voces graves por un objetivo concreto.
- Se verificó en el catálogo oficial Microsoft Azure Speech el identificador API `es-EC-LuisNeural` (voz masculina estándar precompilada). Referencia: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=text-to-speech
- Integración posible mediante Azure Speech SDK/REST y un recurso Speech en Azure, utilizando clave y región en secretos (nunca en Git), **pendiente de cuenta, autorización del propietario y revisión de costos**; no se ha integrado ni sustituido la voz actual.
- Azure Speech F0 indica hasta **500.000 caracteres TTS neural/mes** para evaluación: https://azure.microsoft.com/es-es/pricing/details/speech/
- **Restricción decisiva:** según los términos de Microsoft, los derechos de uso del audio generado por voces precompiladas, incluido el uso comercial, se conceden expresamente a **clientes del nivel de pago de TTS**, no al nivel F0: https://www.microsoft.com/licensing/terms/en-US/productoffering/MicrosoftAzure/allprograms . No usar F0 como voz final de vídeos potencialmente monetizados, salvo que Microsoft otorgue confirmación contractual explícita distinta.
- Siguiente decisión: ¿priorizar la voz exacta `es-EC-LuisNeural` bajo nivel S0 medido por uso (con tope de gasto) o buscar una voz abierta/licenciada de carácter similar sin depender de Azure? Mantener la voz provisional en renders hasta resolverlo.

## 2026-10-20 · Política irreversible hasta nueva decisión: cero pagos

- El propietario rechazó expresamente la posibilidad de pagar por Azure o por la voz Microsoft Luis: «No, nada de pagos».
- Se registra **cero servicios de pago o suscripciones** como requisito de producto. No se debe recomendar Azure S0 ni usar Audio TTS de prueba gratuita si sus condiciones impiden monetizar legalmente el resultado.
- La voz `es-EC-LuisNeural` queda únicamente como **referencia acústica/editorial** (natural y profesional), no como motor habilitado.
- Próxima búsqueda: voz local/open source gratuita con calidad natural comparable, derechos comerciales claros y recursos compatibles con las cuotas gratuitas; descartar o pausar lo que exija gasto.
- El narrador en producción sigue siendo provisional (`es_MX-ald-medium` para renders técnicos): **ninguna voz definitiva seleccionada**.
- Vigilar los límites de ejecución gratuitos de GitHub Actions/Cloudflare; evitar renderizaciones o procesos masivos automáticos.


## 2026-10-20 · Búsqueda independiente de TTS gratuitos tras descartar Azure

- El propietario mantiene como condición que no haya pagos, suscripciones ni APIs de TTS facturables. Referencia acústica deseada: naturalidad profesional similar a Microsoft Luis, sin imitación/clonación de su voz.
- Revisión de fuentes primarias: MeloTTS Spanish MIT (~208 MB, CPU), Chatterbox Multilingual v3 LATAM MIT (~2,14 GB en checkpoint T3, más archivos), Qwen3-TTS 0.6B CustomVoice Apache-2.0 (~2,5 GB de distribución), CosyVoice3 0.5B Apache-2.0 (9 idiomas, español), Qwen3 VoiceDesign 1.7B Apache-2.0 (~4,52 GB).
- Se anotó matriz técnica, procedencia y restricciones en `docs/MOTOR_AUDIOVISUAL.md` con enlaces directos a model cards oficiales. Ninguno de estos motores se declara voz oficial por tener licencia abierta; falta prueba auditiva y verificación de dependencias y datos de entrenamiento.
- Se crearon `tools/audition_melo.py` y `.github/workflows/voice-melo.yml`, solo en `main`, para generar muestras de la **misma voz** MeloTTS en velocidad 1.0 y 0.9 sin distorsionar el tono. Workflow GitHub Actions `39497786790` lanzado automáticamente, sujeto a `timeout-minutes: 17` y sin credenciales externas ni publicación.
- **Resultado pendiente al registrar esta entrada**: confirmar que el workflow produjo dos WAV válidos y artefactos, y escuchar. No se cambió `render.yml` ni el narrador provisional Piper. Si el workflow falla, consignar fallo y no marcar la voz como probada.


## 2026-10-20 · Audición MeloTTS completada y verificada

- Se realizaron tres ejecuciones de `.github/workflows/voice-melo.yml` en `main`:
  - 39497786790: falló al importar MeloTTS por `pkg_resources` eliminado en versiones recientes de `setuptools`.
  - 39498261483: se solucionó `pkg_resources` fijando `setuptools<81`; después falló el inicializador MeCab por diccionario UniDic ausente, aunque la voz de destino era español.
  - **39498716070: éxito completo**, tras instalar `python -m unidic download` como exige el origen. Todas las etapas de instalación, síntesis de audio, archivo y publicación de artefacto pasaron.
- Artefacto oficial GitHub Actions **12299087396**: `audicion-melotts-factor-de-gigantes`; https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39498716070 .
- Se descargó y extrajo el artefacto. Contiene `melo_normal.wav` (17,59 s), `melo_pausada.wav` (18,96 s) y `ficha.json` con procedencia, licencia y estado no aprobado. Ambos WAV verificados: PCM mono, 44.100 Hz, 16 bit, sin errores de decodificación. También se generaron MP3 160 kbps para audición en el teléfono.
- **La segunda muestra es la misma voz** a velocidad 0,9, NO otra voz ni efecto de pitch. No se ha evaluado ni aprobado la idoneidad del timbre como narrador profesional.
- El modelo y proyecto upstream `myshell-ai/MeloTTS-Spanish` publican licencia MIT, y el proveedor afirma capacidad de síntesis en CPU. Se debe revisar el uso comercial de dependencias/modelos antes de lanzar documentales monetizados. No hubo llamadas a servicios de pago.
- `render.yml` y el narrador provisional permanecen sin modificación. No se conectó Azure ni se publicó contenido en YouTube.
- **Siguiente acción**: propietario escucha las dos variantes de MeloTTS y califica si suena adulto y profesional. Si no, buscar modelos Chatterbox/CosyVoice/VoiceDesign viables sin tarjeta, clonación de terceros ni gasto; mantener cuotas y pruebas bajo control.


## 2026-10-20 · Evaluación negativa del propietario de MeloTTS

- El propietario escuchó la audición real MeloTTS (ritmo normal y 0,9) y concluyó: **«Se escucha como tts»**. La voz no alcanza el nivel de naturalidad humana, adulta y profesional requerido por Factor de Gigantes; no queda aprobada para identidad de marca.
- Por acumulación de resultados insatisfactorios se cambia el enfoque: no seguir ajustando velocidad ni pitch de motores con timbre sintético. Evaluar primero **demos del modelo avanzado** con la misma frase, y solo integrar al motor si la audición convence y la ejecución local entra en el presupuesto gratuito.
- Próximo candidato priorizado: Chatterbox Multilingual V3 **es-MX/LatAm**, finetune en https://huggingface.co/ResembleAI/Chatterbox-Multilingual-es-mx-latam y demostración oficial https://huggingface.co/spaces/ResembleAI/Chatterbox-Multilingual-TTS-es-mx-latam. Licencia declarada MIT; modelo regional ocupa al menos 2,14 GB para la parte T3, además de decodificador de audio (1,06 GB en safetensors): estimar RAM/CPU antes de usar GitHub Actions.
- Confirmado en código upstream que Chatterbox Multilingual V3 admite `device="cpu"`, `t3_model="v3"`, `language_id="es"`, y permite variar parámetros de expresividad; sin garantía de síntesis a tiempo razonable en runners gratuitos.
- Alternativa editorial si ningún motor abierto cumple: voz humana grabada con autorización del locutor para crear un narrador propio sin usar voz ajena, y evaluar herramientas de edición de audio libres. Nunca imitar Microsoft Luis sin autorización.
- Se conserva `render.yml` y Piper como **voz técnica provisional**, sin publicación automática ni cuentas de pago. Cero nuevas audiciones pesadas hasta validar calidad comparativa y coste del siguiente candidato.

## 2026-10-20 · Rechazo de demo Chatterbox femenina; Voice Design masculino como próximo ensayo
- El propietario revisó la demo Chatterbox Multilingual es-MX/LatAm: **solo escuchó una voz femenina** y la rechazó expresamente. No proponerla de nuevo como demostración masculina ni asumir que la demo permite alternar géneros.
- La limitación es de la demostración por defecto: Chatterbox acepta una muestra de locutor distinta mediante `audio_prompt_path`, pero **solo utilizar muestras propias o con consentimiento y derechos expresos**, nunca clonar Luis de Microsoft.
- Alternativa verificada: **Qwen3-TTS Voice Design (1.7B)**, que permite describir una voz masculina madura y profesional sin referencia humana; idioma español. Demo oficial: https://huggingface.co/spaces/Qwen/Qwen3-TTS , pestaña `Voice Design`, campo `Voice Description`.
- Descripción inicial de audición: `A natural mature male Latin American Spanish documentary narrator, warm low-mid pitch, confident and calm, clearly articulated, subtle authority, measured pace, authentic human intonation, no announcer theatrics, no robotic tone.`
- Aún **no se ha generado una muestra Qwen real** desde el proyecto, ni se ha medido la capacidad de CPU/tiempo de render, ni se ha aprobado voz definitiva. La demo pública puede imponer límites de uso gratuitos; una muestra no equivale a integración local o derecho irrestricto para uso comercial.
- Mantener el flujo actual Piper como prueba técnica y prohibición de pagos. Próximo paso: evaluación auditiva de Qwen Voice Design por el propietario; luego prueba de recursos locales antes de integrar en render.

## 2026-10-20 · Primera voz Qwen3 Voice Design generada realmente (sin pagos)

- Ante la solicitud explícita «Hazlo tú, dame el audio», se integró una prueba puntual en `tools/audition_qwen.py` y `.github/workflows/voice-qwen.yml`, directamente en `main` y sin cambiar la voz actual de los renders.
- La prueba usa el **Space público oficial** `Qwen/Qwen3-TTS` con la función `generate_voice_design`; entrada: español, texto breve original sobre BlackBerry y descripción de narrador masculino adulto, latinoamericano, profesional, natural, con cuerpo y sin dramatización ni voz robótica. **No se hizo imitación ni clonación de personas.**
- **GitHub Actions run 39502577947: success.** Respuesta del Space: `Voice design generation completed successfully!`. Todas las etapas de generación, conversión MP3 y carga del artefacto terminaron correctamente.
- Artefacto `audicion-qwen-voz-masculina-factor-de-gigantes`, ID **12302050983**, contiene `Qwen3_FactorDeGigantes_VozMasculina.mp3` y `audicion.json`. Se descargó y validó con `ffprobe`: **MP3 mono, 24 kHz, 14,112 s, 282.765 bytes**. URL: https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39502577947 .
- No se usó Azure, ningún secreto ni una API de voz facturable; generación de una única prueba mediante demostración gratuita pública con cuotas/colas de terceros. **No confundir prueba pública gratuita con garantía de producción ilimitada.**
- El MP3 se entregó al propietario para escuchar. La aceptación de la calidad humana/masculina/natural queda pendiente: que el prompt solicite ese timbre **no demuestra** que la voz resultante lo cumpla.
- **Pendiente de arquitectura:** medir si Qwen3 Voice Design (1.7B) puede ejecutarse de forma autónoma en CPU gratuita para narrar documentales de 8–14 minutos, sin depender de la disponibilidad y licencias de uso de una demo alojada por terceros. No actualizar `render.yml` ni la voz institucional hasta que el propietario apruebe la muestra.

## 2026-10-20 · Qwen3 Voice Design v2: más energía, con MP3 entregado
- El propietario evaluó la muestra Qwen3 inicial y solicitó **«Le falta energía»**. La nueva pauta es voz adulta masculina con impulso, entusiasmo medido, suspenso, énfasis en palabras clave y ritmo medio-rápido, sin caer en locución excesivamente teatral o de tráiler.
- Se actualizó `tools/audition_qwen.py` en `main`: misma narración original sobre BlackBerry para facilitar la comparación; descripción vocal refinada (`captivating forward momentum`, `dynamic rhythm`, `expressive emphasis`).
- GitHub Actions `39503709220`: **success**. Demo pública Qwen3 `/generate_voice_design` respondió `Voice design generation completed successfully!`, y exportó `Qwen3_FactorDeGigantes_MasEnergia.mp3` en artefacto `12301563544`.
- Audio descargado, extraído y verificado: **MP3 mono, 24 kHz, 15,00 s, 300.525 bytes**. Entregado a través de ChatGPT como `FactorDeGigantes_Qwen3_MasEnergia.mp3`. URL evidencia: https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39503709220 .
- No hubo pagos, clave de Azure, clonación de voces ni cambios en `render.yml`. El generador Voice Design puede variar identidad vocal entre llamadas; mantener el narrador consistente a lo largo de un documental es aún una limitación arquitectónica por resolver.
- **Pendiente:** el propietario debe escuchar y decidir si la energía de esta versión se acerca al objetivo; no asumir aprobación a partir del éxito técnico ni incorporar la voz al canal hasta validar calidad y sostenibilidad gratuita.

## 2026-10-20 - Audicion Qwen v3: claridad y pronunciacion

- Evaluacion del propietario de v2: voz poco profesional, vaga, sin la claridad y pronunciacion exigidas.
- Cambio de prioridad: narrador masculino profesional de documentales, articulacion precisa, palabras completas, consonantes y vocales nitidas, ritmo medio con proyeccion firme, voz no arrastrada.
- Archivo actualizado en main: tools/audition_qwen.py. Misma frase sobre BlackBerry para comparar versiones. Nuevo MP3 Qwen3_FactorDeGigantes_DiccionProfesional.mp3.
- Postprocesamiento: filtro de graves por debajo de 70 Hz y loudnorm EBU R128 -17 LUFS, sin modificar el tono. No se afirma que estos filtros arreglen la diccion sintetizada.
- Prueba real GitHub Actions run 39504363557: SUCCESS, artefacto 12301594283. El ZIP contiene MP3 y audicion.json; MP3 verificado con ffprobe: 11.688 s, mono, 48 kHz, 234285 bytes.
- Archivo entregado al propietario para revision auditiva; voz NO aprobada aun. No hubo pagos, no se modifico el render de produccion ni se publico en YouTube.
- Pendiente: evaluar pronunciacion, timbre, autoridad y consistencia de voz entre fragmentos antes de integrar.

## 2026-10-20 · Primer timbre Qwen bien valorado; pronunciación de BlackBerry corregida en prueba de continuidad

- El propietario valoró la **tercera muestra Qwen3 Voice Design v3** como «Excelente, mucho mejor», especialmente por profesionalidad y dicción. Señaló una falla concreta: el nombre **BlackBerry** se escuchaba como «beri y berri», pronunciación inestable/repetida.
- Decisión técnica: mantener Qwen v3 **como timbre candidato preferido** y no rediseñar otra voz por ese error. La aprobación completa sigue pendiente de corregir el nombre y asegurar continuidad vocal.
- Se añadieron en la rama **`main`** los archivos `tools/voice_lexicon.py` (normalización solo para síntesis, `BlackBerry` → `Blákberi` sin afectar el texto visible), `tools/audition_qwen_clone.py` y el workflow `.github/workflows/voice-qwen-clone.yml`.
- El workflow recupera exclusivamente el audio sintético v3 desde GitHub Actions run **39504363557**, verifica SHA-256 `e03ee9359a0323d958279ea22ccb37f07aafd681dcd36667a0d318214c06e675` y usa `Qwen3-TTS Base 1.7B Voice Clone` (Space público oficial) para intentar mantener el mismo timbre al corregir el nombre. No se clona a ninguna persona real; se reutiliza un audio generado previamente para este canal.
- La ejecución **39505217153 finalizó con éxito**, artefacto **12302578597** `audicion-qwen-blackberry-con-voz-referencia`. El MP3 descargado fue examinado con ffprobe: **11.304 segundos, mono, 48 kHz, 226605 bytes**. Es una prueba verificable, no garantía de idéntica voz o pronunciación correcta; pendiente de escucha por el propietario.
- Muestra entregada como `FactorDeGigantes_BlackBerry_Corregido.mp3`. El audio v3 original permanece sin sobrescribir. Costo de proveedores TTS: **0**; no se activó Azure, no se modificó el renderizador principal y no se publicó en YouTube.
- **Riesgo de continuidad:** los artefactos GitHub Actions caducan (3 días en esta prueba); si se aprueba de forma definitiva el timbre, habrá que preservar una referencia vocal verificada y un léxico de marcas en almacenamiento persistente, sin depender de la disponibilidad del Space ni de su cuota de demo pública.
- Siguiente verificación del propietario: (1) BlackBerry como única palabra clara; (2) parecido de timbre con Qwen3 v3; (3) dicción firme. De aprobarse, diseñar preservación de identidad de marca para todo el canal.

## 2026-10-20 · Ajuste solicitado: r fuerte en Berry

- El propietario precisó que el sintetizador pronuncia «ri» con r simple en lugar de «rri» con vibrante fuerte. La corrección exacta es **r fuerte**, sin cambiar la voz Qwen v3 de dicción profesional ya considerada la mejor.
- El léxico de síntesis cambia sólo `BlackBerry` a `Blákberri` (doble `rr` entre vocales), manteniendo escritura comercial y subtítulos `BlackBerry`.
- Se actualizan a la vez el léxico, las pruebas del workflow y la salida `FactorDeGigantes_BlackBerry_RR_Fuerte.mp3`; se reutiliza como referencia la muestra sintética v3, sin introducir un locutor nuevo.
- La regla fonética y el éxito técnico **no equivalen a pronunciación garantizada**: comprobar auditivamente la vibrante fuerte y el timbre antes de aceptar para el motor definitivo.
- Coste cero, rama main; no se modifica `render.yml` ni se publica en YouTube.

- Resultado comprobado de la corrección con doble `rr`: GitHub Actions run **39506360433** terminó **success**, artefacto **12303606616** (`audicion-qwen-blackberry-rr-fuerte`). MP3 extraído y validado con `ffprobe`: 10,896 segundos, mono 48 kHz, 218.445 bytes. Enlace: https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39506360433 . Se entregó al propietario para que compruebe auditivamente la vibrante fuerte; **la generación correcta del archivo no acredita por sí sola que el fonema haya sido pronunciado como pidió**.

## 2026-10-20 · Estilo documental de naturaleza y ajuste localizado de «años»

- El propietario indicó que la versión BlackBerry con rr fuerte ya parece correcta, pero que el ritmo estaba algo rápido. Pidió una cadencia **similar al estilo de los documentales sobre animales de Discovery**, sin pedir la imitación de un narrador individual.
- Se preparó una audición basada **en el MP3 existente**, conservando voz e interpretación original: FFmpeg `atempo=0.94` y tres ampliaciones de pausa de 160 ms en silencios de final de frase. Resultado validado: `FactorDeGigantes_Documental_Naturaleza_Pausado.mp3`, MP3 de unos 12,07 s.
- El propietario valoró esta versión «Excelente», con una observación localizada: en **«Durante años»** suena «aaños», con la vocal inicial demasiado alargada.
- Se ajustó solamente la vocal inicial de ese término en el primer segundo, retirando **65 ms entre 0,5945 y 0,6595 s** y uniendo el audio con transición cruzada de 16 ms. **No se regeneró la voz**, no se alteraron los otros nombres ni el ritmo del resto de la locución.
- Nuevo archivo `FactorDeGigantes_Documental_Anos_Corregido.mp3`: validación con FFprobe, duración **12,00 s**, mono 48 kHz, **240 524 bytes**. Escucha pendiente de confirmación por el propietario: el archivo técnicamente correcto **no garantiza** la naturalidad del fonema.
- Scripts añadidos para reproducción en `main`: `tools/documentary_pacing.py` para controlar velocidad y pausas sin pagos; `tools/voice_fix_anos.py` para reparar exclusivamente la muestra aprobada, con comprobación de hash SHA-256 del audio fuente; y tests `tests/test_documentary_pacing.py`.
- No se modifica la voz provisional en `render.yml`, no se publica nada en YouTube y no se activa facturación.
- Siguiente tarea: evaluar auditivamente la vocal de «años», fijar referencia vocal persistente si queda aprobada, y comprobar capacidad y derechos de producción continuada sin coste.


## 2026-10-20 · Rechazo del recorte de «años»: efecto artificial (reversión inmediata)

- El propietario denunció que el archivo `FactorDeGigantes_Documental_Anos_Corregido.mp3` **estropeó la palabra «años»**, dejándola con un sonido similar a autotune. **Se rechaza esa muestra.**
- Causa concreta: la eliminación de 65 ms dentro de la vocal /a/ con crossfade de 16 ms creó una discontinuidad en la señal que el oído percibió como artificial. El archivo no debe servir como referencia para ningún documental.
- **Versión segura restaurada como referencia de audición**: `FactorDeGigantes_Documental_Naturaleza_Pausado.mp3`, que había recibido el calificativo «Excelente» antes de la reparación fallida; SHA-256 `9c608fe3d6c4a8280e14848a8fc3f3ac4d649ad403c727f2d833ea44cdf1c6bf`. Mantiene cadencia y el detalle original de pronunciación en «años», sin introducir autotune.
- Se **deshabilita** `tools/voice_fix_anos.py` de forma explícita, conservando aviso histórico para impedir cualquier reutilización involuntaria. No se aplicarán nuevos cortes intravocálicos ni clonaciones de una voz humana real.
- Se añadió `tools/audition_qwen_retake.py` y se cambió `.github/workflows/voice-qwen-clone.yml` para generar **una nueva toma íntegra** mediante Qwen3 y la referencia vocal de la muestra profesional v3. Sólo después se aplica ralentización global moderada `atempo=0.94` y pausas entre frases, sin modificar segmentos de la palabra.
- La corrección de «años» por regeneración queda **pendiente de audición humana**, ya que ejecutar el motor no demuestra que el fonema sea correcto o que la voz permanezca idéntica. No se modifica `render.yml`; política de cero pagos intacta.

## 2026-10-20 · Toma íntegra sin recortes — resultado de ejecución

- Ejecución real de GitHub Actions **39509095680**: **success**. La referencia Qwen v3 se descargó correctamente, el Space Qwen3 generó la locución completa y se aplicó la cadencia documental al audio entero, sin cirugía intravocálica.
- Artefacto `qwen-narrador-toma-natural-sin-cortes` ID **12303639971**. MP3 `FactorDeGigantes_Documental_TomaNatural.mp3` descargado y comprobado con FFprobe: **12,336 s**, mono, **48 kHz**, 247 245 bytes. URL: https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39509095680 .
- **Estado de calidad: pendiente de evaluación auditiva del propietario.** No se considera solucionada la articulación de «años» hasta su confirmación. La toma anterior `FactorDeGigantes_Documental_Naturaleza_Pausado.mp3` queda preservada como referencia segura y la reparación quirúrgica `voice_fix_anos.py` sigue deshabilitada.
- No se activaron servicios de pago ni se alteró el narrador del renderizador principal.

## 2026-10-20 · Aprobación auditiva de la toma documental natural

- El propietario escuchó `FactorDeGigantes_Documental_TomaNatural.mp3` y confirmó expresamente: **«Ahora está correcto»**. Se considera **muestra vocal aprobada para referencia editorial**: voz masculina profesional, clara, dicción entendible, ritmo pausado de documental de naturaleza, `BlackBerry` con doble erre según preferencia y «Durante años» natural.
- Muestra exacta aprobada: GitHub Actions [39509095680](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39509095680), artefacto `12303639971`, archivo `FactorDeGigantes_Documental_TomaNatural.mp3` (12,336 s, mono, 48 kHz).
- Se **rechaza y prohíbe reutilizar** el archivo `FactorDeGigantes_Documental_Anos_Corregido.mp3` y el método de recortar la vocal, porque generaron efecto autotune. La muestra anterior pausada queda solo como respaldo histórico.
- La aprobación corresponde **al audio escuchado**, no certifica todavía que nuevas generaciones con el mismo modelo conserven exactamente el timbre. No se ha sustituido el narrador técnico en el flujo de renderizado ni se ha configurado almacenamiento permanente de la referencia. Las grabaciones de GitHub Actions tienen retención temporal: evitar pérdida de la muestra aprobada.
- **Próximo paso prioritario:** conservar la muestra aprobada de forma persistente y verificable; diseñar un narrador reproducible con ese timbre y ese ritmo, validar derechos comerciales y ejecución sin pagos; después integrar al renderizador en `main` y probar narraciones largas sin publicar automáticamente.


## 2026-10-20 · Identidad vocal preservada y ensayo de continuidad en nuevos guiones

- **Persistencia comprobada en GitHub `main`**: `assets/voice/approved/narrador_documental_aprobado.mp3`, archivo binario real **247245 bytes**. El workflow `39510298815` de preservación terminó `success`: verificó SHA-256 `78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d` y guardó el MP3 aprobado. El audio ya no depende de la caducidad del artefacto.
- Manifiesto duradero `assets/voice/approved/reference.json` con el texto real pronunciado `Blákberri` y el texto editorial `BlackBerry`, modelo, ritmo `atempo=0.94`, pausas, aprobación del propietario y pendientes legales.
- `tools/approved_voice.py` permite recuperar sólo la referencia con aprobación y hash válidos, sin fallback silencioso. Tests en `tests/test_approved_voice.py`.
- **Paso siguiente implementado como audición**: `tools/qwen_consistency.py` usa el MP3 fijo aprobado, su transcripción y la demo Qwen3 Base para intentar generar una narración **nueva**, diferente de BlackBerry, sobre naturaleza y cambios empresariales. Mantiene la cadencia documental y rechaza entradas vacías o desmesuradas. `.github/workflows/voice-consistency.yml` lo prueba una vez en GitHub Actions; `tests/test_qwen_consistency.py` valida contratos sin hacer llamadas externas. **Pendiente de escuchar la muestra y de confirmar continuidad real**, no basta con la ejecución exitosa.
- El renderizador principal aún no utiliza este método. No habilitar como proveedor de publicación comercial mientras falte verificar derechos de output y viabilidad de ejecución local/coste cero. Las cuotas de Hugging Face ZeroGPU para usuarios sin autenticar son restringidas y no aptas como garantía de escalamiento.

## 2026-10-20 · Aprobada y almacenada la voz; continuidad verificada técnicamente

- La referencia de voz aprobada quedó almacenada **como binario permanente en la rama principal**: `assets/voice/approved/narrador_documental_aprobado.mp3`, de 247245 bytes, SHA-256 `78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d`. Ejecución de preservación `39510298815`: exitosa. Ya no depende de la caducidad del artifact.
- Manifest `assets/voice/approved/reference.json` y verificador `tools/approved_voice.py` fijan el audio aceptado, su transcripción, velocidad y checksum sin sustituirlo silenciosamente si falta o cambia.
- Prueba de **continuidad con otro guion** vía Qwen3-TTS Base 1.7B, partiendo de esa muestra fija y manteniendo la cadencia de documental: ejecución `39510650716`, exitosa. Artefacto `12304934427`; audio `FactorDeGigantes_Prueba_Continuidad_Voz.mp3` de **13,584 s**, mono y 48 kHz, checksum `7d34443491320c21b2167bafaf6591dce32303c6fa438014914bf5b6af2283af`. El usuario aún debe escuchar y confirmar identidad vocal, dicción y ritmo de esta nueva frase.
- El workflow de continuidad se ejecutó nuevamente en `39510770537` con éxito; no interpretar dos éxitos técnicos como validación auditiva de identidad.
- `tests/test_approved_voice.py` y `tests/test_qwen_consistency.py` pasaron en GitHub Actions `39510770438`; se corrigió la validación de saltos de línea del texto nuevo.
- La demo pública de Hugging Face ZeroGPU tiene cuota diaria limitada: **no se permite depender de ella para producir automáticamente documentales de larga duración**. El motor oficial actual `render.yml` no ha sido cambiado.
- Se puso en marcha una prueba controlada **sin API ni servicios facturables** del modelo Qwen3-TTS Base 0.6B en CPU del runner público gratuito GitHub Actions: script `tools/qwen_local_smoke.py`, workflow `.github/workflows/voice-qwen-cpu.yml`. El primer intento de workflow `39511250435` falló por expresión de contexto no permitida en `env`, corregida; ejecución `39511351086` iniciada y **resultado todavía pendiente de confirmar** al registrar esta nota. No anunciar éxito local antes de que entregue un MP3 real y métricas.
- GitHub documenta que el runner Linux de repositorios públicos incluye 4 CPU, 16 GB RAM, 14 GB SSD y es gratuito bajo la política vigente. Modelo 0.6B con licencia Apache-2.0. Persisten dudas de rendimiento, parecido auditivo y derechos de explotación de audios producidos en los flujos probados.


## 2026-10-20 · Qwen3-TTS Base 0.6B: síntesis **local CPU** lograda, sin API

- Resultado real: GitHub Actions run **39511351086** concluido `success`. Se instalaron PyTorch 2.8 CPU y `qwen-tts`, sin CUDA/GPU, cuenta de servicio ni API facturable; los pesos abiertos `Qwen/Qwen3-TTS-12Hz-0.6B-Base` fueron descargados y ejecutados en la VM del runner público de GitHub.
- Script ejecutado `tools/qwen_local_smoke.py`, que validó antes de inferir que el MP3 de referencia aprobado mantenía SHA-256 `78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d`.
- Muestra generada `FactorDeGigantes_Qwen_Local_CPU.mp3`: MP3 mono de 48kHz, **8,424 segundos**, 169005 bytes y SHA-256 `d9ff665031859c351acff5a781b3b73d8b914be2934c3b2bf748465bdb281fb1`. Artefacto GitHub Actions **12305867860**, adjunto `cpu-metrics.json`; source: https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39511351086 .
- Métricas observadas en una ejecución: **22,47 segundos de carga del modelo; 79,97 segundos de proceso total** (sin incluir la instalación inicial de paquetes); pico de memoria residente **6362008 KiB ≈ 6,07 GiB** (`/usr/bin/time -v`). No extrapolar linealmente estos tiempos sin benchmarking para documentos de 10 minutos.
- Se confirma técnicamente una opción **local gratuita** para síntesis con voz sintética de referencia, pero es el modelo **0.6B, diferente del 1.7B** que produjo la voz aprobada. El parecido audible, dicción y ritmo requieren nueva evaluación del propietario. **No reemplazar por el 0.6B automáticamente**.
- Qwen3-TTS Base 0.6B y paquete Qwen TTS publican licencia Apache-2.0. **Aún pendiente** la verificación legal completa de referencia/audios para usos comerciales, y la viabilidad/costo operativo de narraciones largas.
- Para evitar ejecuciones involuntarias de modelos pesados, se retira el disparo `push` del workflow CPU; queda **sólo manual `workflow_dispatch`** y restringido a repositorio público (evitar runners facturables si cambia a privado).
- Prioridades siguientes: aprobación auditiva del resultado CPU, persistencia a largo plazo de la voz ya conseguida (realizada), mediciones más extensas del narrador y, sólo con calidad/licencias/costos aptos, integración a `render.yml` y documentos completos; publicar en YouTube siempre bajo aprobación humana.

## 2026-10-20 · Evaluación del propietario del narrador local 0,6B

- Tras escuchar `FactorDeGigantes_Qwen_Local_CPU.mp3`, el propietario indicó **«Está bien el tono, como que ha cambiado un poco»**. El tono le parece aceptable, pero identifica una **variación perceptible de la identidad vocal** respecto a la toma de referencia aprobada. **Esto no equivale a aprobación del nuevo narrador** ni autoriza sustituir la voz definitiva.
- La referencia editorial aprobada (`assets/voice/approved/narrador_documental_aprobado.mp3`; SHA-256 `78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d`) permanece intacta. No alterar ni reemplazar.
- Se creó `tools/qwen17_local_smoke.py` y `.github/workflows/voice-qwen17-cpu.yml` para probar **Qwen3-TTS Base 1.7B en CPU**, el tamaño de modelo usado para generar la toma preferida, frente al 0,6B. El test usa **el mismo texto** que el experimento ligero, la misma referencia aprobada y los mismos parámetros de cadencia; limita la prueba a 12 min en runner de repositorio público, y la síntesis a 420s sin API o GPU de pago.
- **GitHub Actions run 39512992392** se inició; su resultado, consumo de memoria, duración y calidad **todavía están pendientes** en el momento de esta anotación. El éxito técnico no demuestra semejanza perceptual: el propietario decidirá al escuchar la nueva muestra.
- Mantener `render.yml` sin modificación y no publicar vídeos automáticamente; priorizar similitud con voz aprobada y recursos gratuitos verificables.


## 2026-10-20 · Resultado Qwen Base 1,7B CPU y comparación del ligero 0,6B

- La audición del modelo **`Qwen/Qwen3-TTS-12Hz-1.7B-Base` en CPU del runner GitHub Actions gratuito** fue exitosa: ejecución [39512992392](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39512992392), con voz de referencia aprobada intacta y validada por checksum, PyTorch CPU sin API pagada.
- MP3 realmente generado: `FactorDeGigantes_Qwen_17B_CPU_Voz.mp3` (7,680 segundos, mono, 48 kHz, **154 125 bytes**), SHA-256 **`29fdef191c8571f0d5a21adcd6e2202c1aed83c016385794f599320d0427255b`**; artefacto **12306875340**.
- Medición concreta: carga del modelo **20,44 segundos**, ejecución de Python hasta entrega de audio **88,62 segundos** y máximo de memoria residente **11 826 680 KiB (~11,28 GiB)**. No incluir la instalación de dependencias dentro de estos tiempos; no extrapolar directamente a documentales de larga duración.
- Se usó exactamente el mismo texto de comparación que con el modelo 0,6B. La diferencia de duración (1,7B: 7,680 s frente a 0,6B: 8,424 s) muestra que el ritmo generado puede cambiar; **la semejanza acústica real requiere que el propietario escuche ambas tomas.**
- **No se reemplaza la muestra Qwen aprobada**, en `assets/voice/approved/narrador_documental_aprobado.mp3`. El 1,7B local es candidato a preservar mejor la voz porque coincide en tamaño de modelo con el que generó la referencia, pero esto **no equivale a prueba de igualdad de timbre**.
- `.github/workflows/voice-qwen17-cpu.yml` queda **solo con lanzamiento manual** y condición `github.event.repository.private == false`, para no consumir recursos de GPU/CPU innecesariamente ni generar cobros por minutos de runners privados. No se modifica `render.yml`, no se activa publicación de YouTube ni facturación.
- **Siguiente tarea:** comparación auditiva por propietario entre el archivo local 1,7B y 0,6B; posteriormente probar trozos más extensos del elegido y fijar un proveedor/flujo con derechos comprobados, coste cero y narración consistente.

## 2026-10-20 · Confirmación definitiva de la referencia vocal exacta adjuntada por el propietario

- El propietario interrumpió la comparación de candidatos locales 0,6B/1,7B y declaró: **«Noo, esta es correcta»**, adjuntando su propio archivo `FactorDeGigantes_Documental_TomaNatural.mp3`. Este es el **único audio de identidad vocal aprobado**. La preferencia no se refiere genéricamente a Qwen 1,7B, a un tono similar ni a las generaciones locales recientes.
- Se inspeccionó directamente el archivo adjuntado por el propietario: **12,336 segundos, MP3 mono de 48 kHz, 247 245 bytes, SHA-256 `78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d`**; coincide byte a byte por hash y tamaño con `assets/voice/approved/narrador_documental_aprobado.mp3` (muestra de la toma natural aprobada).
- **Decisión editorial vinculante:** fijar **exactamente ese timbre y esa toma** como patrón de voz; las audiciones locales `FactorDeGigantes_Qwen_Local_CPU.mp3` (0,6B) y `FactorDeGigantes_Qwen_17B_CPU_Voz.mp3` (1,7B), aunque técnicamente válidas, **no están aprobadas para reemplazar el narrador**. Que un modelo sea de 1,7B no significa que produzca la misma voz en otras tomas.
- No regenerar, remezclar, ralentizar ni sustituir el archivo canónico. Para contenido nuevo, emplear la referencia inmutable y verificar identidad vocal con pruebas auditivas separadas; rechazar cualquier muestra perceptiblemente diferente.
- **Estado técnico:** referencia persistida en `main` y validada; producción de nuevas frases con fidelidad exacta todavía **no demostrada ni aprobada**. `render.yml` sigue sin Qwen y no hay publicación automática. Mantener reglas de cero pagos y comprobar derechos comerciales/viabilidad.

## 2026-10-20 · Banco de continuidad vocal en dos fragmentos (CPU 1,7B)

**Objetivo del plan maestro:** avanzar en Fase 2 (voz profesional y QA) sin reemplazar la voz única aprobada, iniciar cobros ni activar YouTube.

**Código realizado y confirmado en la rama `main`:**
- `tools/qwen_voice_continuity_batch.py`: banco con dos textos editoriales nuevos, de longitud acotada y diferentes del patrón canónico; reutiliza UNA carga del modelo local `Qwen/Qwen3-TTS-12Hz-1.7B-Base` en CPU y la referencia de `assets/voice/approved/`, previamente validada por SHA-256. Genera cada MP3 con la cadencia parametrizada aprobada, comprueba duración/tamaño y vuelve a verificar el patrón exacto al finalizar.
- Artefactos previstos si se ejecuta: `00_referencia_aprobada.mp3` (copia idéntica, sin modificar la original), `01_decision.mp3`, `02_transformacion.mp3`, `reporte_audicion.json` y guía de escucha. El reporte fija explícitamente `production_ready=false`, `generated_clips_owner_approved=false`, `commercial_rights_verified=false` y `youtube_publication_enabled=false`.
- `.github/workflows/voice-continuity-cpu.yml`: **solo `workflow_dispatch` manual**, runner Linux de repositorio público, CPU sin CUDA/API de pago, tiempo máximo de trabajo, verificación de disco y artefactos retenidos tres días. Si el repositorio se hace privado, el job no se ejecuta.
- `tests/test_qwen_voice_continuity_batch.py`: pruebas de límites, seguridad de identificadores, no repetición de texto y ausencia de aprobación automática.

**Evidencia de integración de código:** commits `4d9da9b`, `5227af5`, `5fb0a40` y corrección de descubrimiento de tests `b5ff562`. CI general sobre `b5ff562`: [run 39515949183](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39515949183), resultado `success`. Este CI **sí ejecutó los tests locales**, pero **NO ejecutó inferencia de Qwen** ni creó las dos muestras; el workflow de audición es deliberadamente manual.

**Pendiente real y prioridad inmediata:**
1. Ejecutar manualmente el workflow [Continuidad Qwen 1.7B CPU - dos tomas sin pagos](https://github.com/eler30mr-star/FactordeGigantes/actions/workflows/voice-continuity-cpu.yml) desde la rama `main`, dentro de la capacidad gratuita disponible; revisar el resultado, consumo, artefacto MP3 e informe. No reportar audio generado hasta observar un run exitoso con muestras.
2. Audición humana comparando las dos tomas contra **el MP3 original exacto**. Cualquier deriva o artificio vocal bloquea integración. No inferir identidad por checksum de referencia ni por coincidencia del modelo.
3. Si ambas muestras son aceptadas, evaluar fragmentos de mayor duración y montaje editorial, con pruebas reales de coste, QA y licencia comercial; integrar `render.yml` **únicamente** cuando haya evidencia suficiente y autorización editorial. Mantener el narrador actual sin alteraciones hasta entonces.
4. Avanzar paralelamente la investigación con fuentes y la trazabilidad de derechos audiovisuales, y después pruebas de un documental original 8–14 min. YouTube sigue sin OAuth ni subida automática.

**Estado inequívoco:** código en GitHub y tests CI **confirmados**; ejecución manual de dos audios, escucha/identidad, licencia comercial y producción **pendientes**. No se ha desplegado otro Worker ni alterado el renderizador principal.

## 2026-10-20 · Audición REAL de continuidad Qwen 1,7B: dos tomas generadas y verificadas

**Hito ejecutado, no solo preparado.** Se activó **una sola vez** el workflow en `main` usando un disparador `push` temporal autorizado por el propietario para ejecutar su prueba. El workflow se devolvió inmediatamente a **solo `workflow_dispatch` manual** (commit `08b4357`). No quedan disparadores automáticos del ensayo intensivo.

- GitHub Actions: [run 39516609592](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39516609592), conclusión **`success`**. Ejecución de generación, verificación de SHA y carga del artefacto completadas. Commit del disparador único `83af430`.
- Artefacto [12307719223](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39516609592/artifacts/12307719223): `factor-gigantes-continuidad-cpu-dos-tomas` (ZIP, cinco archivos: patrón original sin retocar, dos nuevos MP3, JSON de métricas e instrucciones). **Caduca 2026-10-23 a las 23:45 UTC** por retención gratuita de tres días; guardar una copia local antes. Los MP3 se recuperaron y sus checksums/duraciones coinciden con el reporte.
- `00_referencia_aprobada.mp3`: 12,336 s y SHA-256 `78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d`. **Idéntica a la referencia canónica original, que continúa sin modificación**.
- `01_decision.mp3`: 8,496 s, SHA-256 `68b6437729fd085e65af3e35099bd9ebf97b088d399f479199839d9e3dea4c4f`; 70,82 s generación y procesamiento.
- `02_transformacion.mp3`: 9,960 s, SHA-256 `f7019bfe413165ec2dbdee7745f8306ffff51a4ba560508bbf3712592b4990b6`; 80,23 s generación y procesamiento.
- Informe del proceso: `elapsed_seconds_without_dependency_install=172.5`, tiempo externo del paso de síntesis `2:58.30` y **máximo RSS 11 826 580 KiB ≈ 11,28 GiB** (incluye carga y procesamiento; no incluye instalación inicial). CPU PyTorch, cuatro hilos, 1.7B Base, sin API pagada.
- El informe mantuvo explícitos `generated_clips_owner_approved=false`, `voice_identity_verified_by_human=false`, `commercial_rights_verified=false` y `production_ready=false`; **éxito técnico de los MP3 NO implica continuidad vocal validada al oído**.

**Próximo paso prioritario del plan:** el propietario escuchará la muestra canónica y las dos tomas nuevas, y evaluará por separado si ambas conservan exactamente la identidad, la dicción y la naturalidad. Si hay deriva, no integrar. Si ambas son aprobadas, medir continuidad de párrafos más extensos con límites CPU gratuitos, investigar licencias de voz y contenido, y avanzar a narración de un documental de 8–14 minutos con fuentes y recursos licenciados. Sin YouTube automático, sin cambios en `render.yml`, sin cobros. No ejecutar de nuevo este workflow pesado salvo necesidad editorial expresa.


## 2026-10-20 · Revisión auditiva humana de los dos clips Qwen CPU 1,7B

**Evaluación directa del propietario:** «Sí ambas, la 1 es más fiel». La interpretación registrada es que **ambas tomas son aceptables en esta audición corta**, y que la toma **`01_decision.mp3` conserva con mayor fidelidad** el timbre de `FactorDeGigantes_Documental_TomaNatural.mp3` que `02_transformacion.mp3`.

**Evidencia exacta:**
- Ensayo completado: [workflow 39516609592](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39516609592); ZIP temporal [artefacto 12307719223](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39516609592/artifacts/12307719223), caduca el 23-10-2026.
- **Preferida para estudiar continuidad:** `01_decision.mp3`, 8,496 s, SHA-256 `68b6437729fd085e65af3e35099bd9ebf97b088d399f479199839d9e3dea4c4f`.
- **También aceptada en esta audición, menos fiel:** `02_transformacion.mp3`, 9,960 s, SHA-256 `f7019bfe413165ec2dbdee7745f8306ffff51a4ba560508bbf3712592b4990b6`.
- **Única referencia canónica definitiva:** `assets/voice/approved/narrador_documental_aprobado.mp3`, SHA-256 `78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d`. Ni el clip 1 ni el 2 sustituyen esa referencia y **no debe copiarse el clip 1 sobre el MP3 aprobado**.

**Conclusión rigurosa:** se supera **la audición humana de estas dos muestras cortas**; **no** se ha demostrado fidelidad idéntica en múltiples párrafos, control estadístico del timbre, narración larga, licencia comercial integral ni integración final al render. Las próximas pruebas deben comparar cada fragmento nuevo con la voz canónica y utilizar la mayor fidelidad relativa del clip 1 como pauta de selección, no como autorización automática para producción.

**Próximas prioridades conforme al plan:** preparar un ensayo limitado de continuidad en varios párrafos (sin mezclar identidades), medir consumo CPU, registrar resultados por toma y aplicar validación humana; revisar derechos comerciales de modelo/referencia/audio y después integrar únicamente una narración que mantenga la identidad estable. No activar servicios pagos, triggers periódicos ni subida a YouTube. Rama única `main`.


## 2026-10-20 · Fase 2: continuidad narrativa de tres párrafos + trazabilidad documental

**Trabajo en `main` comprobado (sin ramas secundarias):**
- `tools/qwen_longform_probe.py` y `tests/test_qwen_longform_probe.py`: prueba real de una historia **hipotética** de 3 párrafos consecutivos con Qwen3-TTS Base 1.7B en CPU; cada párrafo mantiene referencia SHA-256 aprobada, usa semilla documentada, parámetros originales de cadencia y validación técnica MP3 mono 48 kHz. Produce pistas separadas, versión unida con silencios solo ENTRE frases, copia intacta del MP3 de referencia y reporte JSON. Ningún archivo experimental se publica ni sustituye a la referencia.
- `.github/workflows/voice-longform-cpu.yml`: quedó exclusivamente en `workflow_dispatch`. El disparador `push` **único** usado para ejecutar esta prueba fue revertido inmediatamente en commit `b1438b2`; no queda trabajo automático de síntesis pesada.
- **Ejecución real:** [GitHub Actions 39518606909](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39518606909), `success`. Artefacto [12311066207](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39518606909/artifacts/12311066207), retención hasta **2026-10-24 00:08:53 UTC** (23-10-2026 19:08 Perú).
- **Pistas obtenidas y verificadas** por checksum y FFprobe: `01_apertura.mp3` 13,944 s; `02_conflicto.mp3` 13,944 s; `03_cierre.mp3` 14,712 s; previsualización `04_previsualizacion_unida.mp3` **43,296 s**. La muestra `00_referencia_canónica.mp3` coincide SHA-256 `78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d` con la aprobada; **no sufrió cambios**.
- Síntesis y ensamblado `elapsed_seconds_excluding_install=401.42`, y `/usr/bin/time` reportó `6:48.24` para el proceso y `11 978 044 KiB` (~11,42 GiB) de RAM pico. No usar este dato para afirmar que un documental 8–14 min cabe en el runner gratuito: pendientes escalamiento y límites por duración.
- **Identidad vocal por audición humana: pendiente para estas tres nuevas tomas.** La aprobación previa del usuario («sí ambas, la 1 es más fiel») atañe solo a `01_decision.mp3` y `02_transformacion.mp3` de la prueba ANTERIOR, no al nuevo conjunto.
- El modelo se distribuye con licencia declarada Apache-2.0 en la ficha oficial; la referencia sintética, el servicio/demo de procedencia, sus términos y la autorización comercial completa siguen con revisión pendiente. Se creó `docs/LICENCIAS_NARRACION.md` con fuentes primarias y una puerta explícita contra publicaciones no autorizadas.
- `tools/editorial_evidence.py` y `tests/test_editorial_evidence.py`: auditoría **de estructura**, fuentes HTTPS, IDs por afirmación y estados de licencias; sus resultados no autorizan publicación ni prueban la veracidad por sí mismos. `docs/FLUJO_VERIFICACION.md` documenta uso e integración pendiente D1/panel. CI [39519271278](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39519271278) en `main`: `success`.

**Pendientes inmediatos y siguientes pasos del plan:**
1. El propietario debe escuchar la versión continua de 43,296 s y las 3 tomas por separado, compararlas con la voz canónica y decir si alguno de los párrafos varía de timbre; hasta entonces **no hay aprobación auditiva del ensayo nuevo**.
2. Investigar la reutilización documentada de `create_voice_clone_prompt` de Qwen para evitar recalcular la referencia, medir estabilidad y eficiencia en nuevas pruebas acotadas; validar memoria/tiempo y compatibilidad antes de adoptarla (NO implementada aún).
3. Conectar de manera segura las evidencias y derechos por afirmación al panel y D1 en una migración nueva, sin alterar el esquema histórico; preparar guion factual respaldado por fuentes originales.
4. Después de licencias, calidad y viabilidad verificadas, abordar 8–14 min y mejoras cinematográficas. **Sin servicios pagados, sin OAuth/YouTube ni integración a `render.yml` mientras falten controles.**

**Estado preciso:** código y pruebas CI efectuados; audios nuevos GENERADOS y verificados; evaluación de identidad de estos nuevos párrafos, derechos comerciales integrales, integración al panel y render productivo PENDIENTES.


## 2026-10-20 · Aceptación auditiva del montaje continuo de 43,296 segundos

**Respuesta del propietario al escuchar la previsualización de tres párrafos:** «Está bien». Se registra como **aceptación editorial del resultado de esta audición continua**: `04_previsualizacion_unida.mp3`, 43,296 s, producido por [GitHub Actions 39518606909](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39518606909). La observación no identifica defectos adicionales ni pide cambiar timbre o cadencia.

**Alcance exacto de la aprobación:** la narración continua corta puede tomarse como referencia de calidad de este ensayo. No supone que cada futura generación vaya a conservar la identidad ni convierte las muestras en sustitutas de la **única voz canónica**, `assets/voice/approved/narrador_documental_aprobado.mp3`, SHA-256 `78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d`. Tampoco verifica términos comerciales, permisos de las salidas, calidad de un documental completo o autorización de publicar.

**Siguiente hito conforme al plan maestro, Fase 2:** pasar a mejoras reproducibles del motor para narración segmentada de varios minutos con controles de memoria, tiempos y límites gratuitos; trabajar investigación factual y derechos por afirmación, conectar después estos controles al panel y a D1, y únicamente con validación editorial/legal evaluar el primer documental de 8–14 min. Mantener cero pagos, `main` exclusivamente y sin subir a YouTube.


## 2026-10-20 · Fase 2: expediente editorial conectado al panel, Worker y esquema D1

**Objetivo realizado:** pasar de pruebas aisladas de validación de fuentes a un flujo de investigación administrable por cada documental. Trabajo exclusivamente sobre **`main`** del repositorio `eler30mr-star/FactordeGigantes`, sin ramas secundarias.

### Código implementado y confirmado en GitHub

- `src/editorial.mjs`: validador de expedientes con fuentes HTTPS, IDs únicos, documentos asociados a afirmaciones, `locator` de evidencia y estado, persona revisora, recursos y derechos (la voz es obligatoria). Los URL de fuentes del guion deben figurar en el expediente. **No** afirma haber comprobado contenido real en sitios externos.
- `migrations/0002_editorial_dossiers.sql`: nueva tabla vinculada a `jobs` que guarda expediente JSON, revisión humana, identidad del revisor y fechas, sin alterar `0001_initial.sql`.
- `src/worker.js`: nuevas rutas autenticadas `GET/PUT /api/jobs/:id/dossier` y `POST /api/jobs/:id/dossier/attest`; el editor acredita únicamente durante `review`, cuando todas las afirmaciones y licencias declaradas han sido revisadas. **Bloqueo efectivo en código** de `approve` y `dispatch` si el expediente está ausente, incompleto o no acreditado. Cambiar guion, expediente o pedir cambios invalida la acreditación previa. Si falta la tabla D1 remota, HTTP **503**, y el guardado del guion no muta datos antes de detectar el bloqueo.
- `public/index.html` y `public/app.js`: nuevo panel «Fuentes y licencias», edición JSON de expediente por trabajo, visualización de conteos, guardado y confirmación expresa del revisor; administración sin persistir `ADMIN_TOKEN` en almacenamiento del navegador.
- `tests/test_editorial_gate.mjs`: pruebas de autenticación, fuentes, bloqueo antes de revisión, revocación por cambios, despacho y comportamiento seguro sin migración. `tests/test_editorial_migration.py`: restricciones SQL/foráneas con D1 emulada en SQLite local.
- `.github/workflows/check.yml`: ejecuta los tests del Worker y contrato editorial con Node `--test`, además de la batería Python y chequeos anteriores.
- `docs/DESPLIEGUE.md` y `docs/FLUJO_VERIFICACION.md`: instrucciones concretas de migración remota, despliegue seguro y operación del nuevo panel.

### Pruebas y estado real

- [CI GitHub Actions 39521914410](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39521914410) — **`success`**, incluye `node --test tests/test_editorial_gate.mjs`, `python -m unittest discover -s tests -v`, sintaxis Worker y panel, manifest de ejemplo; diagnósticos HTTP a Cloudflare no bloqueantes. Verificaciones incrementales posteriores sobre protección ante migración ausente también completadas correctamente en GitHub.
- El conector Cloudflare no respondió correctamente al intentar consultar el estado de la base; **NO se ha aplicado la migración 0002 en D1 remota desde esta sesión**. **NO se ha confirmado un nuevo despliegue del Worker ni del panel**. El código funciona en las pruebas de integración simuladas, pero la funcionalidad todavía **no debe declararse operativa en la instancia Cloudflare**.
- Ningún vídeo se publicó; no se introdujeron servicios de pago, claves, OAuth ni se modificó la identidad canónica del narrador, su checksum o `render.yml`.
- Un editor que marque manualmente una afirmación `verificada` sigue siendo responsable de comprobar el documento real. La aplicación verifica estructura y trazabilidad declarada, **no garantiza verdad material ni derechos legales por una marca en el expediente**.

### Próximo paso prioritario verificable

1. En Cloudflare, aplicar `npx wrangler d1 migrations apply factor-de-gigantes-db --remote` tras validar cuenta y hacer respaldo; comprobar `editorial_dossiers` en D1. El primer esquema fue aplicado originalmente por API y es idempotente.
2. Desplegar Worker y assets desde `main`, verificar acceso autenticado, guardar expediente de prueba, comprobar `attest`, y que `approve`/`dispatch` respondan 409 cuando falten fuentes/validaciones. No ejecutar vídeo comercial.
3. Incorporar investigación real con fuentes primarias, metraje/música/imágenes originales con derechos, aprobación humana y guion documental. Mantener bloqueo de publicación y revisión pendiente de licencia comercial de la referencia vocal hasta evidencia concluyente.
4. En paralelo medir viabilidad de narración local de varios minutos y optimizar el Qwen CPU sin cambiar la voz aprobada ni sobrepasar cuotas.

**Estado al terminar este avance:** commits y pruebas CI **realizados**, migración y despliegue remoto **pendientes**, calidad vocal de 43,296 s **aprobada previamente** por el propietario, comercialización/publicación **no autorizadas**.


### Cierre técnico del control por escenas — revisión del avance editorial (2026-10-20)

- Se reforzó `src/editorial.mjs`: **cada segmento del guion debe figurar en al menos una afirmación documentada** mediante `segment_index` (base 1). Fuentes, localizadores, estados de revisión y licencias de voz no desaparecen al ampliar el guion.
- El formulario de expediente en `public/app.js` ahora crea automáticamente afirmaciones **pendientes** por cada escena, evitando un único registro insuficiente. No genera ni declara como verificadas las fuentes de forma automática.
- `src/worker.js`: expedientes obsoletos por cambio de fuentes o escenas se devuelven con `validation_error` y nunca se acreditan; el panel permite corregirlos sin devolver error HTTP 500. La falta de tabla `editorial_dossiers` retorna HTTP 503 antes de mutar el borrador.
- `tests/test_editorial_gate.mjs` añadió cobertura de índices inexistentes, escenas sin evidencia, migración ausente y revocación por cambios. CI de [run 39522588126](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39522588126) completada **`success`** en commit `1a14039e`; dos ejecuciones intermedias fallaron mientras el contrato y los tests se adaptaban, pero se corrigieron y la batería final volvió a verde. `docs/FLUJO_VERIFICACION.md` refleja el contrato de escena y revisión.
- **Sin despliegue validado**. Sigue siendo el principal bloqueo práctico: aplicar D1 0002 en la cuenta Cloudflare correcta, verificar la tabla y probar panel/Worker reales; las herramientas de Cloudflare conectadas no pudieron completar esa operación aquí.


## 2026-10-20 · Panel de investigación visual, D1 local verificada y primer piloto documental

**Objetivo del plan:** mejorar la preparación editorial del canal, probar con D1 real (local) y preparar el primer episodio con investigación primaria; mantener voz original y política de cero pagos.

### Cambios reales en `main`

1. **Editor visual usable desde el panel**: `public/dossier-editor.js` y actualizaciones de `public/app.js`, `public/index.html`, `public/style.css`.
   - Formularios guiados de fuentes/documentos, afirmaciones agrupadas por escena, evidencia con fuente, sección/página y estado, responsables de la revisión, y derechos de voz/imágenes/música/video/gráficos.
   - Añadir/quitar evidencias, fuentes adicionales y afirmaciones manteniendo condiciones de integridad (cada escena al menos una; sin suprimir la última voz; fuente del guion no se borra desde el expediente).
   - Edición JSON relegada a opción avanzada; se importa explícitamente y no equivale a autorizar. Cambios sin guardar impiden acreditar; controles responsivos para móvil.
   - Pruebas de funciones editoriales en `tests/test_dossier_editor.mjs`; GitHub CI [39523541399](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39523541399) **success**. No hay despliegue de esta UI confirmado en Cloudflare.

2. **Prueba real del Worker con D1 local usando Wrangler**: `tests/e2e_worker_local.mjs` y workflow `.github/workflows/worker-d1-local-e2e.yml`.
   - [GitHub Actions 39523829006](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39523829006): **success**. Instala Wrangler, ejecuta **ambas migraciones solo en D1 local aislada**, confirma que la tabla `editorial_dossiers` existe, levanta el Worker y prueba por HTTP la autenticación, creación, expediente pendiente, bloqueo 409, acreditación, aprobación, ausencia de token de dispatch real, revocación y registro de eventos.
   - El disparador `push` fue **temporal de una única prueba**, eliminado después (commit `15be8962`), por lo que el workflow quedó solo manual. **No tocó D1 remota, no desplegó ni despachó videos**.

3. **Corrección de duplicados de render**: `src/worker.js` reserva atómicamente `approved → queued` en D1 antes de llamar a GitHub Actions; evita disparar el mismo trabajo dos veces en simultáneo. Ante rechazo explícito de GitHub, restaura `approved`; si falla la red y el resultado es incierto, conserva `queued` y exige inspección manual de Actions para evitar duplicados. Además, revoca la acreditación ANTES de actualizar un guion, evitando modificaciones parciales que dejen un antiguo visto bueno.
   - `tests/test_editorial_gate.mjs` cubre duplicados, rechazo HTTP, fallo de red. GitHub CI [39524141335](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39524141335) **success**; un commit intermedio falló por el simulador antiguo y se corrigió en el commit de pruebas siguiente.
   - `GET /dossier` tampoco muestra acreditación cuando el expediente no sigue estructuralmente completo.

4. **Primer piloto editorial basado en fuentes públicas originales**: `research/blackberry/brief_investigacion.md`, `research/blackberry/expediente_preliminar.json` y `tests/test_blackberry_research.py`.
   - Tema candidato: **«BlackBerry: el gigante que tuvo que cambiar de negocio»**; líneas narrativas desde RIM (fundada en 1984), la introducción del iPhone en 2007, App Store de 2008, transformación a software en 2016 y cierre de servicios heredados en 2022 hasta su negocio de software seguro.
   - **Seis fuentes primarias** de Apple y BlackBerry con URLs y localizadores concretos; **ocho afirmaciones** trazables y esquema de 8 bloques para futuro documental de ~12 min.
   - **Ninguna afirmación está falsamente marcada verificada por un editor**: todas siguen `pendiente`, igual que licencias de voz, imágenes y música. El material no es todavía un guion factual final, investigación exhaustiva, ni autorización de producir/publicar. El guion debe incorporar información financiera independiente, revisar causalidad y obtener recursos licenciados. CI [39524514168](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39524514168) **success**.

### Estado, bloqueos y próximos pasos

- **Confirmado:** código en `main`, CI Node/Python exitosa, prueba E2E con D1 **local** real; voz de 43,296 segundos previamente aceptada. Ningún token privado revelado, servicio pago activado ni canal YouTube publicado.
- **Pendiente:** aplicar `0002_editorial_dossiers.sql` a la base **remota** Cloudflare y confirmar despliegue Worker+panel. El conector Cloudflare continúa fallando al acceder a la cuenta, por lo que **no se hicieron cambios remotos ni se puede declarar producción actualizada**. Ruta segura documentada en `docs/DESPLIEGUE.md`.
- **Pendiente:** contrastar formalmente cada fuente del piloto BlackBerry con un editor humano, conseguir fuentes independientes y derechos completos de material/voz, escribir narración original total, storyboard, primera prueba de video 8–14 min y QA.
- **Pendiente:** preparar reconciliación segura de trabajos con `dispatch` de resultado incierto, sin reintentos automáticos ni duplicados; pulir los formularios con pruebas de usabilidad en móvil tras el despliegue.
- **Orden siguiente:** D1 remota → Worker y panel remoto → ensayo autenticado con expediente real no publicado → investigación/comprobación editorial → licencia de voz y recursos → producción piloto de video. Todas las operaciones directamente en `main`.


## 2026-10-20 · Avance real: motor autónomo de investigación con IA local (Fase 2)

**Pedido del propietario:** continuar el avance y que sea la IA quien investigue los documentales, no el usuario. Trabajado directamente en main y siguiendo AGENTS.md / PLAN_PROYECTO.md.

### Trabajo implementado

- **tools/research_engine.py**: modo dossier (visita URLs de fuentes registradas y extrae pasajes candidatos vinculados a afirmaciones) y modo tema libre (busca autónomamente en MediaWiki y lee artículos secundarios). Guardias HTTPS/DNS/hosts internos, redirecciones y tamaños máximos; hashes de contenido, URLs de origen y final, errores distinguibles, fragmentos breves. Archivos de salida: reporte_investigacion.json, LECTURA_PRELIMINAR.md y evidencia_para_ia.txt. Los estados siguen en "pending_human", aunque exista pasaje coincidente.
- **tools/local_research_ai.py**: genera un borrador original a partir de pasajes documentales mediante Qwen/Qwen3-0.6B CPU, sin API generativa facturable. Rechaza generación sin evidencia; metadatos indican modelo, hashes, citas y ausencia de aprobación. Se añadió control de cifras fuera de pasajes de la fuente citada para detectar alucinaciones numéricas (no certifica exactitud histórica).
- **.github/workflows/research-ai-cpu.yml**: workflow exclusivamente MANUAL (tras un disparo controlado único y reversible) que ejecuta pruebas, consulta documentos y usa Qwen local. Acepta un tema libre o, en blanco, dossier BlackBerry; artifacts de 3 días. **No activa publicación ni cambia narrador canónico.**
- **.github/workflows/research-topic-smoke.yml**: prueba de descubrimiento desde un único tema en GitHub; disparo puntual revertido a workflow_dispatch. Sin servicio de pago ni publicación.
- **tests/test_research_engine.py** y **tests/test_local_research_ai.py**: simulaciones offline de límites y fuentes, bloqueo por falta de evidencia, búsqueda genérica y fechas numéricas inventadas.
- Documentación técnica docs/MOTOR_INVESTIGACION.md y auditoría concreta research/blackberry/qa_primer_borrador_ia.md.

### Evidencia real (no confundir tests con investigación completa)

1. **[Run 39528648495](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39528648495)**, success: de seis URLs primarias del dossier BlackBerry, **tres legibles** (S01-S03), tres bloqueadas/no analizables (S04-S06), y **cinco pasajes candidatos** para ocho afirmaciones pendientes. El modelo Qwen local 0.6B generó un borrador de **722 caracteres**, cita detectada [S01], 1:08.66 de fase de IA (incluye carga/descarga del modelo) y memoria RSS máxima 4 781 824 KiB (~4.56 GiB). Artefacto [12314626338](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39528648495/artifacts/12314626338). Los resultados fueron descargados e inspeccionados, no solo verificado un workflow verde.
2. **Error factual real detectado:** el texto IA escribió que la IPO en Toronto fue **10 de octubre de 1997**; S01 recuperada decía **28 de octubre de 1997**. Se añadió guardia audit_numeric_support con pruebas posteriores, que alertaría por esa cifra 10 ausente en pasajes de S01. La ejecución inicial **es anterior a esa corrección** y sigue siendo un borrador defectuoso; no se declara guion verificado ni renderizable.
3. **[Run 39529286991](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39529286991)**, success: con solo el tema BlackBerry, buscó y descargó **3/3 artículos secundarios** sin dossier manual. Cero hechos verificados automáticamente; es etapa de descubrimiento, todavía no investigación con fuentes primarias de cualquier tema.
4. **CI [39529112648](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39529112648)**, success: pruebas de detección de una fecha inventada. Los commits posteriores ampliaron el modo tema libre y mantuvieron la batería en verde.

### Bloqueos y próxima secuencia

1. **Investigación autónoma más rigurosa:** descubrir fuentes primarias e independientes desde tema libre, resolver PDF/reportes anuales con referencias precisas, detectar contradicciones y hechos ausentes, en vez de confiar solo en Wikipedia o un pasaje similar.
2. **Guion completo:** convertir evidencia contrastada en historia de 8–14 minutos con citas por escena, control de duración y voz original aprobada, sin alucinar cifras/causalidad.
3. **Integración del panel de producción:** actualmente la investigación ya funciona por GitHub Actions manual, pero **NO** está conectada al botón del panel. Se debe aplicar la migración 0002 D1 **remota** y desplegar Worker/GUI; Cloudflare de esta sesión no responde y **no se afirma que esté hecho**.
4. **Licencias y QA:** referencia de voz canónica SHA-256 78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d sin cambios. Los derechos comerciales de la referencia, música y recursos siguen pendientes. El sistema no sube a YouTube.
5. **Costos:** modelo ejecutado localmente en GH Actions, sin API de pago, pero vigilar minutos y cuotas de GitHub; workflows intensivos quedan solo manuales.

**Estado correcto:** primer motor de investigación y propuesta por IA probado; calidad editorial insuficiente para publicar; investigación primaria universal, desarrollo completo de guiones, Cloudflare remoto y publicación siguen pendientes. Todo realizado en main y documentado.

## 2026-10-20 · Investigación IA activable desde el panel (Fase 2, main)

### Objetivo
Continuar el motor de Factor de Gigantes mientras la laptop HP de 12 GB está descargada: la investigación se ejecuta en GitHub Actions con CPU, sin exigir una GPU local, sin servicios de pago por API y sin producción/publicación automática.

### Desarrollo real en la rama principal
- src/research-control.mjs: nuevo módulo de despacho seguro hacia research-ai-cpu.yml, únicamente ref main. Valida el tema, verifica el consentimiento, repo fijado, secreto exclusivo de Worker, máximo nominal de 4 solicitudes por día UTC y bloqueo de mismo tema/día con unicidad SQL. GitHub HTTP 204 equivale a solicitud aceptada, **no** a investigación terminada. Los rechazos y resultados de red inciertos se registran y no se reenvían automáticamente.
- migrations/0003_research_requests.sql: tabla nueva de solicitudes; conserva migraciones y datos anteriores. Estado reserved, sent, unknown o rejected con timestamps; UNIQUE(topic_key, day_utc). La cuota se comprueba en D1 por fecha, y la deduplicación es atómica. No es un procesador de trabajos ni monitor de finalización.
- src/worker.js: nuevas rutas privadas GET y POST /api/research bajo ADMIN_TOKEN, sin llamadas a render.yml o YouTube. HTTP 503 específico cuando falta la migración o token GitHub. La ruta del renderizador no puede utilizar este endpoint.
- public/index.html, public/app.js: sección «Investigar con IA» con tema, confirmación del gasto de minutos GitHub Actions, historial, enlace a resultados y errores legibles. No guarda ADMIN_TOKEN en disco.
- .github/workflows/research-ai-cpu.yml: usa la carpeta de resultados genérica dist/investigacion y artefacto factor-investigacion-ia-cpu. Sigue siendo manual y de CPU, sin nuevas generaciones automáticas.
- tests/test_research_control.mjs, tests/test_editorial_migration.py: pruebas para autenticación, cuota, rechazo/no respuesta de GitHub, deduplicación, compatibilidad de las tres migraciones y protección de datos previos. .github/workflows/check.yml ejecuta las nuevas pruebas.

### Verificaciones realizadas
- [GitHub CI 39544634359](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39544634359) completó success con los nuevos tests de control y migración SQL.
- [GitHub Actions D1 local E2E 39544778750](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39544778750) completó success: ejecutó migraciones 0001, 0002 y 0003 en D1 local Wrangler y levantó un Worker real; verificó API autenticada y denegación de envíos cuando el token GitHub no está configurado. El disparador temporal de push fue retirado inmediatamente; el workflow volvió a ejecución manual.
- Se intentó consultar Cloudflare conectado pero su herramienta devolvió un error interno. Por tanto, NO se aplicaron tablas remotas, NO se ha verificado despliegue de la nueva interfaz, NO se ha enviado una investigación real desde el panel de producción.
- En esta entrega NO se ejecutó Qwen pesado, NO se consumió ninguna API pagada y NO se cambió la voz canónica del canal.

### Próximas tareas prioritarias
1. Resolver conexión de Cloudflare; respaldar D1, aplicar migraciones 0002 y 0003 remotas, verificar las dos tablas, desplegar Worker/public de main y probar una investigación voluntaria mediante el nuevo botón. No confundir E2E local con producción.
2. Conectar resultados reales de GitHub Actions al panel (estado de ejecución y enlaces directos comprobados) sin exponer secretos ni gastar minutos por reintentos.
3. Avanzar búsqueda automática de fuentes PRIMARIAS, documentos PDF, contraste de datos y guion de 8–14 minutos; el borrador Qwen anterior tiene un error factual documentado, por eso no se publica ni se considera investigación terminada.
4. Confirmar derechos comerciales de voz y audiovisuales; retomar guion y montaje cinematográfico con identidad vocal aprobada, sin necesitar comprar equipo hasta conocer GPU de la laptop.

**Estado:** código + pruebas CI + integración con D1 LOCAL confirmados en main; despliegue Cloudflare REMOTO, uso real del botón, investigación documental completa y publicación pendientes.

## 2026-10-21 · Fase 2: seguimiento del investigador + descubrimiento de webs oficiales

**Contexto del avance:** el propietario pidió continuar sin depender de la batería/GPU de su laptop. Se trabaja **exclusivamente en `main`** de `eler30mr-star/FactordeGigantes`. No se modificó la voz original ni `render.yml`, y no se publicaron videos.

### Implementación comprobable

1. **Seguimiento de investigaciones por ejecución real de Actions:** se añadió `request_id` opcional a `.github/workflows/research-ai-cpu.yml` y `run-name` específico. `src/research-control.mjs` despacha el UUID de cada investigación y permite consultar hasta 50 runs recientes por API GitHub autenticada; la correlación exige título, rama `main`, tipo de evento, ID numérico y URL oficial correctos. `GET /api/research?runs=1` devuelve el run y su estado/conclusión, o marca consulta no disponible. Un HTTP 204 de despacho no demuestra ejecución exitosa. El panel `public/app.js` diferencia cola, ejecución, éxito y fallo, con acceso a Actions; solo consulta el estado tras iniciar la investigación o pulsar «Actualizar».
2. **Pruebas de protección y trazabilidad:** `tests/test_research_control.mjs` cubre URLs falsas, ramas distintas, respuestas 403, timeouts, runs ajenos y ausencia de estados confirmados. GitHub CI [39587493924](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39587493924): `success`. El resultado de este test usa respuestas simuladas de GitHub: falta verificación del botón con Worker/D1 remotos.
3. **Descubrimiento independiente de posibles sitios corporativos:** `tools/primary_source_discovery.py` investiga páginas vinculadas al tema mediante la API MediaWiki y la propiedad `P856` de Wikidata. Rechaza hosts privados/no HTTPS mediante `tools/research_engine.py`, pone límites de documentos, solo guarda pasajes breves y jamás marca hechos o licencias verificados. `tests/test_primary_source_discovery.py` verifica descubrimiento, falta de enlaces, fallos de red y protección URL. Se integró al workflow de investigación en temas libres, con advertencias y ejecución no bloqueante.
4. **Pruebas externas y corrección:** primera [39587995688](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39587995688), `success` pero **0 sitios** al inspeccionar dos resultados. Se amplió la búsqueda para examinar hasta cinco entidades y se repitió [39588198172](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39588198172), `success`: **1 candidato de cinco artículos**: `BlackBerry Limited`, `https://blackberry.com` desde Wikidata. **La página no se pudo leer** (`ValueError`); hay URL candidata, NO evidencia factual. No se afirmó haber verificado un hecho. Artefacto [12340022602](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39588198172/artifacts/12340022602) con `fuentes_oficiales_candidatas.json`.
5. Los workflows usados para una prueba de fuente real fueron restaurados inmediatamente a `workflow_dispatch` manual: **sin nuevas ejecuciones continuas, proveedores de pago ni publicación automática**. `docs/MOTOR_INVESTIGACION.md` detalla contratos y limitaciones.

### Bloqueos y siguiente tarea prioritaria

- **Cloudflare remota sin acceso:** la herramienta de Cloudflare devolvió error interno otra vez. NO se ha aplicado D1 0002/0003 ni desplegado el panel nuevo, ni se ha comprobado correlación real entre solicitud y Actions desde el Worker publicado.
- **Primarias:** obtener contenido original efectivo de sitios oficiales o documentos reguladores/financieros, con fecha y página; `P856` es solo una pista de la entidad. Contrastar datos de fuentes independientes y corregir el borrador Qwen anterior con error IPO.
- **Investigación y guion:** generar narración completa de 8–14 minutos únicamente tras respaldar las afirmaciones, licencias de material visual y de voz. Mantener el flujo manual controlado de GitHub sin cobrar APIs y respetar `main`.

**Estado preciso:** código implementado y CI verde; descubrimiento de un sitio oficial candidato comprobado externamente; enlace no descargado; funcionalidad remota y documental de producción aún **pendientes**.


## 2026-10-21 · Investigación de PDF con evidencia y páginas reales (Fase 2, `main`)

**Pedido del propietario:** continuar avances de Factor de Gigantes, respetando exclusivamente la rama principal, historial y la meta de investigación automática sin APIs de pago ni dependencia de su laptop.

### Implementación efectuada

1. **Nuevo analizador PDF:** `tools/pdf_sources.py`, descarga pública HTTPS protegida por validación DNS/redirecciones, tamaño máximo 4 MB, máximo 35 páginas, límites de texto y cabecera `%PDF-`, extracción textual local mediante `pypdf==5.9.0`. Sin OCR ni extracción de fotos. Rechaza PDFs cifrados/corruptos/no válidos y formatos de red inesperados.
2. **Integración de extremo a extremo dentro del investigador por expediente:** `tools/research_engine.py` acepta ahora HTML y PDF sin modificar la lista de fuentes del usuario. Registra `document_type`, `pdf_total_pages`, SHA-256 del archivo y `locator: PDF página N` por evidencia localizada. También incorpora la página al contexto de Qwen y al informe de lectura; deja `facts_verified_automatically=0`, `rights_verified_automatically=0`, `production_ready=false`.
3. **Comprobación y CLI:** `tools/pdf_probe.py` permite consultar un documento PDF original por URL HTTPS y búsqueda; el informe es JSON de referencias, no una redistribución del PDF. `tests/test_pdf_sources.py` fabrica un PDF de dos páginas para comprobar correspondencia de localizador, compatibilidad HTML y rechazo de entradas peligrosas. Workflows `check.yml` y `research-ai-cpu.yml` instalan el parser CPU versionado.
4. **Ejecución real comprobada:** [GitHub Actions 39592681746](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39592681746), `success`: documento original `https://arxiv.org/pdf/1706.03762` sobre Transformer (Vaswani et al.), PDF de **15 páginas**, **328 bloques** y **2 pasajes candidatos** en **página 1 y página 2**. Cero afirmaciones aprobadas. Se conserva artifact temporal de resultados, no el PDF completo.
5. **Tests:** batería general [39592490158](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39592490158) `success`. Se detectó y corrigió un problema de literal UTF-8 en un fixture que hacía fallar un commit intermedio; no se declaró listo hasta la ejecución verde. Workflow real de prueba restaurado a `workflow_dispatch` manual después de una única ejecución.

### Estado y bloqueos verificados

- **Código y pruebas en `main`: listos para la siguiente fase de investigación**. No se creó rama secundaria ni PR; no se usó servicio TTS o IA de pago, no se alteró `render.yml` ni la voz original aprobada.
- **PDFs grandes/escaneados y tablas financieras:** sin resolver. No presentar el texto de un PDF reducido a los primeros 35 folios como análisis suficiente de un informe corporativo completo; se debe obtener sección/página relevante con controles de integridad y verificación independiente.
- **Descubrimiento autónomo de PDFs de emisores/reguladores:** pendiente. En este ensayo se proporcionó una URL primaría explícita; aún falta encontrarlas por tema sin intervención humana.
- **Cloudflare:** la herramienta conectada `whoami` respondió error interno nuevamente; no se ejecutaron migraciones D1 remotas 0002/0003 ni se verificó despliegue del nuevo panel. El bloqueo de producción sigue vigente.
- **Control humano y licencias:** la lectura automática no acredita fechas, decisiones, cifras ni derechos de contenido audiovisual y voz. Sigue prohibido publicar un documental sin verificaciones.

### Próximo trabajo

1. Descubrir fuentes originales financieras y PDF por entidad, clasificar documentos, preservar fecha, URL, versión y página sin inventar datos. Validar con una prueba de fuente corporativa y contraste secundario independiente.
2. Crear auditoría de contradicciones entre cifras y fuentes, apoyar guion original por escena y revisión humana sin convertir un borrador Qwen en vídeo publicable.
3. Tras resolver Cloudflare, migrar D1 remota, desplegar Worker/panel, probar investigación y lectura de estado reales en producción.
4. Mantener la continuidad vocal aprobada y presupuesto gratuito para la prueba de producción audiovisual más larga, con derechos comerciales pendientes.

## 2026-10-21 · Infraestructura real recuperada y desplegada (rama obligatoria `main`)

**Solicitud autorizada:** propietario confirmó que se deben aplicar migraciones 0002 y 0003 y continuar avanzando sin ramas aparte, pagos por API ni publicaciones automáticas.

### Verificaciones y operaciones efectivamente realizadas

1. **Conexión correcta de Cloudflare:** los errores anteriores surgieron porque había dos cuentas conectadas y la herramienta requería `link_id`. Se seleccionó expresamente `Factor`, no `Primary`. Cloudflare confirmó el Worker `factor-de-gigantes` y la D1 `factor-de-gigantes-db` enlazada con el identificador esperado.
2. **Resguardo de datos previo:** se obtuvo un bookmark de Time Travel de la D1 y se solicitó una exportación SQL de las tablas `jobs` y `events`. Cloudflare API respondió estado `complete` y URL firmada temporal. La copia **no fue descargada permanentemente fuera de Cloudflare**; el enlace firmado vence y cualquier recuperación depende de la retención del servicio. No se publicaron datos de usuarios ni secretos.
3. **Migraciones remotas auténticas:** `migrations/0002_editorial_dossiers.sql` y `migrations/0003_research_requests.sql` leídas desde `main` y comparadas con los blobs esperados; ambas aplicadas mediante API SQL de D1 con `success`. Se verificaron tablas `editorial_dossiers`/`research_requests` e índices, sin anomalías en `PRAGMA foreign_key_check`. La API denegó `PRAGMA integrity_check` (`SQLITE_AUTH`), por lo que **no** se certifica un chequeo de integridad profundo.
4. **Preservación comprobada después de migrar y desplegar:** `jobs=1`, `events=8`, `editorial_dossiers=0`, `research_requests=0`. Mismo conteo de trabajos y eventos antes/después de las operaciones. Estas migraciones se ejecutaron por Cloudflare SQL API, **no** por Wrangler migrations, y `d1_migrations` todavía no existe. No crear otra D1 ni repetir SQL por rutina.
5. **Primer redespliegue controlado:** Cloudflare Builds conectado a `eler30mr-star/FactordeGigantes`, `main` y `npx wrangler deploy`. Build `729fb21f-d1d9-4f2f-999e-7e6f8cbd47de` `success`, commit `79a2ba80b95022e90acb696c81ebaa610112fa55`. El origen Worker, ASSETS, DB y secretos se conservaron.
6. **Protección de gasto por concurrencia:** se corrigió `src/research-control.mjs` para reservar cuota usando una única sentencia `INSERT OR IGNORE ... SELECT ... WHERE COUNT(*) < 4`, en lugar de dos operaciones con carrera. Consulta posterior diferencia duplicados HTTP 409 de límite diario HTTP 429. `tests/test_research_control.mjs` incorpora caso de dos peticiones simultáneas con un solo hueco; la prueba no dispara GH Actions real.
7. **Calidad obligatoria en Cloudflare Builds:** se configuró el trigger de `main` para ejecutar `node --check` y `node --test` antes del deploy, bloqueando builds con test rojo. Build `720b0c1e-b0ac-4dda-92c3-4c7110f8f862` `success`, 21 tests JS aprobados, 0 fallidos y Worker publicado.
8. **Nuevo diagnóstico interno del panel:** `src/system-readiness.mjs`, ruta autenticada `GET /api/system/status`, panel `public/index.html`/`public/app.js` y `tests/test_system_readiness.mjs`. Comprueba por lectura de sqlite_master cuatro tablas y muestra banderas de presencia de configuración GitHub, siempre sin exponer el valor de ningún token, sin contactar GitHub ni inferir autorización para publicar. HTTP 401 sin ADMIN_TOKEN, HTTP 405 con método POST; no modifica datos.
9. **Despliegue final auditado:** Cloudflare build `17eaaf34-42eb-4427-859b-0f0b8d92b262`, `success`, commit `7ccc9d4e6cf224bbc22333722e0127c1f932b4e6` de `main`, **25 pruebas Node aprobadas y cero fallos**, 2 assets nuevos/modificados subidos, versión Worker `a7695b06-938e-402e-a4ba-809fc2f2ec02` activada al 100 %. Lectura remota posterior del bundle verificó la ruta `/api/system/status` y la reserva atómica; D1 volvió a responder con los mismos datos 1/8/0/0. El Worker mantiene `ADMIN_TOKEN`, `RENDERER_TOKEN`, `GITHUB_DISPATCH_TOKEN` y D1.
10. **Monitoreo posterior al deploy:** `tools/production_smoke.py` y una comprobación no bloqueante añadida a `.github/workflows/check.yml` permiten vigilar HTML público, `/app.js`, `/health` y barrera de autenticación; esta comprobación **no se ha acreditado como ejecutada satisfactoriamente en la última versión**. No hay simulación de usuario autenticado por ChatGPT ni falsa afirmación de que se generó un documental nuevo.

### Próximas tareas prioritarias

1. Comprobar desde navegador del propietario que el panel actualizado abre, admite su token administrativo y muestra «Estado del sistema» y «Investigar con IA». Sin compartir secretos en chat.
2. Disparar **una** investigación IA real desde el panel solo cuando el propietario indique el tema; cotejar Action vinculado, informe, fuentes y borrador. Los Qwen experimentales anteriores no son guiones completos y han mostrado alucinaciones factuales.
3. Mejorar investigación primaria autónoma a PDFs oficiales/regulatorios y números con páginas, contraste entre fuentes y rechazo de contradicciones antes de narrar.
4. Construir narración documental original de 8–14 min y montaje audiovisual dentro del presupuesto de GitHub Actions, con QA, verificación de derechos de voz/visual y autorización humana. Sin publicación automática en YouTube.

**Estado final:** recuperación del conector, SQL D1 remota, dos despliegues, prueba de cuota y diagnóstico privado **COMPLETADOS Y VERIFICADOS**; uso autenticado real del panel, generación IA desde nuevo botón y documental completo **PENDIENTES**. Todo commit en `main`.

## 2026-10-21 · Auditoría editorial automatizada y documentos originales SEC (rama `main`)

### Cambios realmente implementados

1. `tools/editorial_audit.py`: examen conservador de afirmaciones existentes, URLs de procedencia y posibles huecos de evidencia. Distingue falta de pasajes, falta de corroboración desde más de un dominio, fuentes secundarias, fechas y cifras no coincidentes. Produce `AUDITORIA_EDITORIAL.json` con **cero hechos confirmados** y sin permisos de render/publicación. Una alerta es una cuestión a revisar, no una contradicción confirmada.
2. Cada `save_report()` en `tools/research_engine.py`, tanto desde expediente como desde tema libre, genera también `ESCALETA_DOCUMENTAL_10MIN_NO_APROBADA.md`. Contiene **12 bloques con duración total 600 s**, ID de afirmaciones candidatas y tareas de narración/visuales pendientes. La escaleta NO es un guion final ni una grabación.
3. `tools/edgar_discovery.py`: investigación autónoma de identificadores candidatos desde el tema mediante MediaWiki → Wikidata P5531 → SEC EDGAR. Si se consigue `submissions/CIK*.json`, se listan como posibles originales formularios 10-K/10-Q/20-F/40-F/8-K/6-K, fechas, ID de archivo y enlaces oficiales de SEC. Protección de CIK/URLs, máximo ocho documentos por entidad y registro explícito de bloqueo HTTP. **No descarga ni verifica los informes y no inventa cifras**.
4. El workflow manual `.github/workflows/research-ai-cpu.yml` agrega los contratos y una etapa acotada de búsqueda SEC por tema; el investigador Qwen recibe solo el informe de pasajes previamente recopilado, sin usar la mera lista SEC como hechos. Nuevos artefactos esperados: `AUDITORIA_EDITORIAL.json`, `ESCALETA_DOCUMENTAL_10MIN_NO_APROBADA.md` y, en investigaciones de tema libre, `sec_edgar_documentos_candidatos.json`.
5. `tests/test_editorial_audit.py` contiene 5 pruebas sobre cifras, fechas, falta de fuentes y escaleta; `tests/test_edgar_discovery.py` contiene 6 pruebas sobre IDs, formato de archivos, SEC inaccesible y ausencia de pruebas falsas. Ninguna test usa API paga ni consume tokens de Qwen.

### Verificación efectiva y despliegue

- **Cloudflare Builds `c6bfd5a1-3cd9-4201-b945-8d653f58f5a3`: `success`.** Ejecutó 25 pruebas JavaScript y las **11 pruebas Python**, todas verdes, al compilar el commit `cc90a481878d9e2c7ddca7c75dd1a28a09b73d71` de `main`. Wrangler completó despliegue de la versión `c110910e-c4ac-4561-bb06-110c40be0fef`. Para futuras compilaciones Cloudflare tiene incorporado el chequeo Python junto con el control previo JavaScript.
- Se preparó prueba independiente `.github/workflows/edgar-smoke.yml` con tema real Apple Inc., sin Qwen ni render. **Aún no se verificó un resultado real de SEC de esa prueba**; no afirmar accesibilidad ni existencia de archivos regulatorios por un test simulado. Su disparador temporal de push fue retirado y quedó solo manual.
- No se modificaron D1, credenciales, voz canónica, licencias, publicaciones YouTube ni la rama de trabajo. Los resultados de extracción dependen de la disponibilidad remota del proveedor y de sus reglas de acceso.
- La implementación queda desplegada en el repositorio conectado y el pipeline manual; no se ha ejecutado Qwen pesado en este avance ni se ha hecho prueba autenticada del nuevo botón desde el navegador del propietario.

### Siguientes pasos que no deben omitirse

1. Comprobar acceso real a SEC o registrar su rechazo, obtener un filing original íntegro y extraer hechos por sección/página con límites CPU. Contrastar CIK con identidad del emisor y con datos de otros organismos.
2. Construir motor para comparar **métrica + unidad + empresa + periodo** sin llamar contradicción a cifras de años diferentes, antes de redactar narración.
3. Redactar y verificar documental original completo 8–14 min; auditar frases, visuales, subtítulos y licencias de locución. Los 12 bloques son solo estructura pendiente de desarrollar.
4. Validar acceso real desde el panel de producción y una investigación voluntaria elegida por el propietario, con seguimiento de ejecución. Mantener desactivada subida automática a YouTube.

**Estado:** código probado y desplegado, sin hechos verificados ni episodio final. La fase documental tiene avances de ingeniería, pero la producción audiovisual continúa pendiente.

## 2026-10-21 · Comparador SEC XBRL, expediente consolidado y enlaces corporativos (main)

### Hito técnico implementado y probado

1. **Datos financieros estructurados:** `tools/financial_facts.py` utiliza el endpoint público XBRL de SEC `data.sec.gov/api/xbrl/companyfacts/CIK*.json`, con límite estricto de 9 MB, HTTPS, validación DNS pública, CIK exacto y taxonomía `us-gaap`. Conservar solo métricas explícitas, unidad USD, número decimal finito, fechas inicial/final, año/periodo fiscal, formulario y accession; generar `SEC_XBRL_HECHOS_NO_VERIFICADOS.json`. No hay interpretación libre ni datos fabricados.
2. **Comparador seguro:** agrupa únicamente por CIK, etiqueta de métrica, moneda, tipo de periodo y fechas exactas. Nunca mezcla ejercicios distintos o métricas diferentes. Si dos valores difieren para el mismo periodo, emite alerta `same_period_different_reported_values_review_required`, no una contradicción verificada ni fraude. No prueba autoría ni derechos.
3. **Flujo real controlado:** `tools/financial_probe.py` toma un CIK candidato del descubrimiento EDGAR y prueba como máximo una consulta XBRL. Si SEC rechaza, registra estado `sec_unavailable_or_unreadable`, tipo/código HTTP y cero observaciones verificadas. El workflow `research-ai-cpu.yml` incorpora esta etapa solo para tema libre y sin obligar a que XBRL sea accesible; Qwen y render no toman decisiones editoriales automáticas.
4. **Paquete para revisor:** `tools/editorial_package.py` consolida pasajes del investigador, auditoría, documentos SEC candidatos y XBRL opcional. Escribe `EXPEDIENTE_EDITORIAL_PENDIENTE.json` y `EXPEDIENTE_PARA_REVISOR.md`, con localizadores, alertas, bloqueos y acciones pendientes por afirmación. `ready_for_narration`, `ready_for_render` y `ready_for_youtube` permanecen `false`.
5. **Fuentes alternativas cuando SEC no responde:** `tools/official_document_links.py` localiza, dentro de HTML corporativo previamente obtenido, hipervínculos realmente presentes hacia PDF, informes anuales y páginas de inversores. Sin crawling, suposiciones de URL ni descarga de archivos; hosts ajenos aparecen como candidatos externos. Integrado en `tools/primary_source_discovery.py`, con `linked_document_candidates` y conteo global.
6. **Pruebas y control antes de deploy:** `tools/production_preflight.sh` es ahora el comando de compilación de Cloudflare, con `node --check`, 25 pruebas JS y seis grupos de pruebas Python (34 casos). GitHub CI [39625136678](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39625136678) `success`; Cloudflare build `18d882b5-39f5-4524-aa13-1db876e3ebdb` `success` desplegó desde `main` commit `cb54813a158c957e4f3b57651c211fb57e53a572`, versión `1489175a-38ca-403a-9477-a2a466f39b4c`.
7. **Producción verificada tras desplegar:** lectura Cloudflare API confirmó la versión activa y D1 intacta: 1 trabajo, 8 eventos, 0 expedientes editoriales, 0 solicitudes de investigación. Se mantuvieron el Worker, la rama `main`, las credenciales originales y los bloqueos de publicación. No se inició una investigación pesada con Qwen ni un render.
8. **Pruebas externas SEC, límites reales registrados:** [39621724636](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39621724636) obtuvo 1 CIK candidato desde Wikidata para el tema Apple Inc. pero SEC `submissions` devolvió `HTTPError`, 0 filings recuperados. [39624310668](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39624310668) consultó XBRL con CIK de prueba conocido: `sec_unavailable_or_unreadable` por `HTTPError`, **0 hechos financieros reales**. Ambos workflows se dejaron solo manuales. Las cifras de las pruebas unitarias son datos artificiales, nunca referencias reales de Apple.

### Estado y próximos pasos no cerrados

- La etapa de comparación técnica está probada; **no se pudo contrastar un estado financiero real** porque la SEC bloqueó las solicitudes externas. No emplear intermediarios no autorizados ni falsear la fuente; buscar informes originales corporativos accesibles y conservar su URL/version/página.
- Los enlaces corporativos se detectan en HTML en pruebas; todavía no se comprobó un informe real de esa ruta ni se extrajeron sus tablas con unidad/período.
- Obtener al menos una pareja de cifras auténticas y comparables (empresa + métrica + periodo + unidad) y revisión humana de documentación primaria/secundaria.
- Convertir hallazgos validados en guion narrativo original de **8–14 minutos**, con contenido audiovisual legal y narrador cuya licencia comercial esté acreditada. Crear MP4 de prueba sin publicación a YouTube.
- Probar login y lectura autenticada del panel y ejecutar una investigación real desde el botón solo cuando el propietario elija tema explícito. Cero solicitudes consumidas de las cuatro diarias durante este trabajo.

**Resultado:** código, tests, documentación y despliegue del comparador / expediente en producción técnica completados, con datos de usuario preservados; acceso real SEC, hechos aprobados y documental completo todavía pendientes. Todo cambio en `main`, sin PR ni ramas secundarias.

## 2026-10-21 · Primer bloque narrativo documental con datos BlackBerry originales (main)

**Alcance:** el propietario pidió avanzar hacia contenido real, no seguir únicamente en infraestructura. Se mantuvo la regla obligatoria de modificar exclusivamente `main` y nunca publicar automáticamente a YouTube.

### Completado con evidencia

1. **Fuentes originales recuperadas:** `tools/blackberry_sources_pilot.py` descarga dos comunicados financieros PDF de BlackBerry Investor Relations (FY2024 y FY2025) y busca pasajes definidos con página física, SHA-256, URL y base contable. En [GitHub Actions 39630703040](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39630703040), prueba real `success`, descargó **2/2 PDF y localizó 5/5 datos**, en páginas 2 y 16. Datos localizados: ingresos FY2024 presentados entonces US$853 millones; US$218 millones vinculados a venta de patentes; ingresos FY2025 US$534,9 millones; QNX FY2025 US$236 millones; e ingresos FY2024 comparativos de US$759,1 millones incluidos en el comunicado de FY2025. Los PDF completos no se distribuyeron en los artefactos.
2. **Precaución esencial:** FY2024 US$853m reportados en 2024 y FY2024 US$759,1m como comparativo de 2025 no deben restarse ni utilizarse para tasas de crecimiento sin revisar cambios de alcance y operaciones discontinuadas. Una localización textual por máquina no equivale a verificación editorial.
3. **Paquete editorial actualizado:** `tools/editorial_package.py` puede sumar `HECHOS_BLACKBERRY_2024_2025_CON_PAGINAS.json` al expediente, conservando URL/página, base contable y banderas `pending_human`. `tests/test_editorial_package.py` cubre explícitamente los dos importes FY2024, su alerta de comparabilidad y la prohibición de aprobar automáticamente.
4. **Investigación Qwen piloto:** `.github/workflows/research-ai-cpu.yml` ejecutará el sondeo de estos PDF solo cuando el tema sea vacío (piloto BlackBerry), antes de consolidar el dossier. No significa que Qwen ya haya generado desde ese flujo un documental terminado.
5. **Primer texto narrativo real:** `research/blackberry/PRIMER_BLOQUE_NARRATIVO_FUENTES_REALES.md` contiene cuatro escenas originales (~3–4 minutos previstos), preguntas narrativas, cifras referenciadas, localizadores de documentos, ideas visuales sin licencia asumida y bloqueos específicos para revisión. Es un **borrador para evaluar**, no un guion de 8–14 minutos completo ni audio/MP4.
6. **Validación:** el workflow de prueba de PDF y las pruebas de contrato en `main` terminaron exitosamente; la comprobación de GitHub del commit narrativo fue [39631313656](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39631313656) `success`. La última ejecución CI observada [39631477093](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39631477093) también reportó `success`. Los cambios realizados en GitHub no demuestran por sí mismos la generación de un nuevo video ni la revisión comercial de medios.

### Pendiente prioritario

- Verificar de forma editorial las notas contables del 10-K completo, la clasificación de Cylance y las cifras complementarias de comunicaciones seguras y licencias antes de aprobar la narración.
- Obtener fuentes independientes para cronología BlackBerry, competencia, QNX y consecuencias; ampliar el borrador a un **guion original de 8–14 minutos** con cada dato vinculado a evidencia revisada.
- Auditar permisos comerciales del narrador y recursos visuales/musicales; luego generar un MP4 piloto como prueba, **sin subirlo automáticamente a YouTube**.
- Demostrar una investigación voluntaria desde el panel publicado, autenticada por el propietario; no consumir acciones pesadas sin su decisión explícita.

**Estado preciso:** dos documentos primarios efectivamente descargados y cinco pasajes localizados; primer bloque narrativo escrito y guardado en `main`; documental largo, grabación, render final y publicación todavía pendientes.

## 2026-10-21 · Primer guion documental LARGO BlackBerry y cronograma de 12 escenas (main)

### Objetivo de esta ejecución
El propietario pidió continuar el avance hacia un documental terminado, sin más pruebas aisladas de infraestructura. Se trabajó directamente en `main`, sin generar rama ni PR, sin ejecutar Qwen pesado, sin compras y sin publicar en YouTube.

### Entregables guardados en GitHub
- `research/blackberry/FUENTES_GUION_10MIN.json`: siete referencias directas/museísticas a los hechos narrados, con URL y alcance: Smithsonian sobre dispositivos tempranos, comunicados de 2016 de externalización de hardware, resultados FY2024/FY2025 de BlackBerry, 10-K FY2025 y circular corporativa FY2025. Una URL no acredita licencia audiovisual.
- `research/blackberry/GUION_DOCUMENTAL_11MIN_NO_APROBADO.md`: **12 escenas, 1.691 palabras de voz en off original y objetivo de montaje 11:50 (710 s)**. Desarrolla el origen y correo móvil, estrategia hardware 2016, QNX, Cylance y cuentas FY2024/FY2025. Utiliza identificadores de las siete fuentes al final de cada escena y propone visuales originales. La estimación de locución a 145 palabras/min es aprox. 11,7 min sin pausas; necesita medición de voz real y ajuste de escenas. No se presenta como audio grabado ni como video exportado.
- `tools/blackberry_script_quality.py` + `tests/test_blackberry_script_quality.py`: validación automática de 12 escenas, ritmo y tiempos contiguos, presencia de fuentes válidas y avisos de no aprobación. El reporte `QA_ESTRUCTURAL_GUION.json` marca explícitamente `factual_gate_passed=false`, `commercial_voice_license_verified=false` y `youtube_publication_authorized=false`.
- `tools/blackberry_edl.py` + `tests/test_blackberry_edl.py`: exporta `EDL_PREVIA_12_ESCENAS.json` con inicio, fin, duración, fuentes y propuesta de imágenes de cada escena. **No contiene pistas de voz, música ni imágenes**; `render_allowed=false` para todas las escenas. Sirve para planear el primer montaje futuro.
- `tools/production_preflight.sh` incluye los nuevos grupos de pruebas Python y la generación de ambos reportes de QA/EDL, de modo que una versión mal formada no pase al despliegue.
- El bloque financiero ya validado en [39630703040](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39630703040) aportó dos comunicados PDF verdaderamente descargados y cinco datos ubicados por página. El manuscrito conserva la advertencia esencial: **FY2024 US$853m reportado en 2024 ≠ FY2024 US$759,1m reformulado en 2025 para fines de comparación automática**.

### Estado de verificación
- CI del nuevo QA en GitHub [39634135450](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39634135450): `success`.
- CI del nuevo EDL en GitHub [39634462696](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39634462696): `success`.
- Al redactar este registro, el nuevo commit de actualización del plan `af604759` se había enviado a GitHub y su CI estaba en cola. **No confundir pruebas estáticas aprobadas con aprobación editorial, voz definitiva o MP4 verificado.**
- No se realizó una prueba de locución humana ni se cambió la voz canónica. No se verificaron derechos de imágenes/música, ni se modificaron tokens o D1. No se disparó una investigación pesada desde el panel.

### Siguientes prioridades de producción
1. Auditar escena por escena el manuscrito contra las fuentes, enfatizando historia de dispositivos, anuncio 2016, descripción QNX y reexpresión por Cylance; eliminar o reformular cualquier afirmación débil.
2. Crear visuales cinematográficos **originales y licenciables**, no copiar fotos del museo o capturas completas de documentos. Preparar assets versionados e identificación de permisos.
3. Acreditar derechos comerciales de narración aprobada. Producir un **audio real**, medir ritmo/duración, ajustar la EDL y generar un MP4 reproducible de prueba, **sin publicar automáticamente**.
4. Mantener el desarrollo en `main`, acompañar todo avance con esta bitácora y seguir dejando pendientes las pruebas reales de panel administrativo e investigación voluntaria.

**Estado:** existe un manuscrito narrativo de largo documental y una EDL preliminar estructurada. NO existe todavía MP4 final de 11:50, voz comercial validada ni visto bueno factual/licencias.

### Verificación final del guion y montaje — 2026-10-21

- **QA real GitHub Actions:** [39634858858](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39634858858), `success`. Se ejecutaron **5 pruebas de texto/citas + 2 de línea de tiempo**, cero fallos. El informe confirmó `ESCENAS=12`, `PALABRAS=1691`, `DURACION_SEGUNDOS=710`, `ALERTAS_ESTRUCTURALES=[]` y `AUTORIZACION_YOUTUBE=false`.
- Se generaron y archivaron **dos artefactos de control**: `QA_ESTRUCTURAL_GUION.json` y `EDL_PREVIA_12_ESCENAS.json`, disponibles en [artefacto 12359629466](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39634858858/artifacts/12359629466), sujeto a caducidad normal de GitHub Actions.
- `.github/workflows/blackberry-guion-qa.yml` volvió a **`workflow_dispatch` exclusivamente manual** inmediatamente después de la prueba; no se instaló un pipeline de publicación.
- En una consulta administrativa posterior a la prueba, la integración Cloudflare devolvió un bloqueo del servicio de herramientas; **no se afirmó haber comprobado o redeplegado una versión nueva del Worker desde ese conector**. La comprobación de GitHub y los commits a `main` sí son reales y están confirmados.
- Pendiente crítico: comprobación humana del texto íntegro y de la atribución de cada afirmación, validación de licencia de la voz canónica, creación de visuales de uso lícito y generación de audio + MP4 de prueba sin YouTube. Un QA estructural `success` no equivale a documental listo.

## 2026-10-21 · Primera previsual MP4 reproducible — BlackBerry, 12 escenas

**Meta de esta iteración:** obtener un archivo audiovisual real y comprobar su duración y codec, sin comprar APIs, usar la laptop descargada ni publicar contenido no aprobado.

### Código y archivos realmente producidos en `main`

- `tools/render_blackberry_animatic.py` lee el guion y la EDL verificable de doce escenas; dibuja 12 tarjetas originales de estilo documental mediante Pillow (fondo, rejilla, símbolos geométricos, títulos y progreso). No utiliza imágenes de archivo ni descargadas, no incluye música ni locución y mantiene rótulos visibles de uso interno. Empaqueta el resultado en H.264 MP4 sin audio con FFmpeg. Emite `ESTADO_PREVISUAL.json`.
- `.github/workflows/blackberry-previsual-mp4.yml` instala `Pillow==11.3.0` y `imageio-ffmpeg==0.6.0`, comprueba las siete pruebas de estructura/EDL, produce MP4, extrae sus metadatos y sube MP4+informes a GitHub Actions. La tarea queda `workflow_dispatch` manual, no vigilancia ni publicación recurrente.
- **Primera corrida [39635497277](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39635497277) fallida:** el runner no tenía `ffmpeg`. Se corrigió mediante FFmpeg empaquetado `imageio-ffmpeg` y un ejecutable accesible desde PATH, sin modificar el equipo físico.
- **Segunda corrida [39635649958](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39635649958) EXITOSA:** doce escenas convertidas en `BLACKBERRY_PREVISUAL_30S_SIN_VOZ.mp4`. Confirmación real: 30,04 segundos, 1280×720, codec H.264, 204.427 bytes; banderas `audio_present=false`, `youtube_publication_authorized=false`. El ZIP de [artefacto 12360967934](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39635649958/artifacts/12360967934) contiene MP4, `ESTADO_PREVISUAL.json` y `METADATOS_VIDEO.json`; caduca según política de Actions. Se descargó y se verificó con `ffprobe` local. El usuario recibió enlace de reproducción a la copia temporal de la conversación en `/mnt/data/blackberry_previsual/BLACKBERRY_PREVISUAL_30S_SIN_VOZ.mp4`.
- No se modificó D1, Cloudflare, secretos ni voz canónica; la integración Cloudflare no permitió verificar una compilación adicional en esta etapa. El pipeline de video funciona desde GitHub Actions en CPU, sin depender de la GPU/RAM de la laptop.

### Alcance preciso y próximos pasos

- **Hecho:** existe un MP4 real de previsualización **de 30 segundos** sobre la estructura de 12 escenas; gráficos originales con fondo, títulos y fuentes. **No** contiene la historia narrada ni sus escenas cinematográficas desarrolladas.
- **Pendiente:** confirmar/licenciar voz comercial, pasar narración de 1.691 palabras a audio, validar el ritmo real, producir visuales/animaciones originales por escena (sin copiar fotos de archivo), sincronizar 11:50 de montaje y generar MP4 completo de 8–14 minutos.
- **Pendiente:** auditoría factual de afirmaciones, evaluación editorial de materiales y aprobación de propietario antes de cualquier publicación en YouTube.
- Todo commit sigue en `main`, y el despliegue/pipeline automático de YouTube sigue deshabilitado.

**Resultado del turno:** GUION LARGO ✅ | FUENTES REGISTRADAS ✅ | QA + EDL ✅ | MP4 CORTO DE PRUEBA ✅ | AUDIO LICENCIADO ❌ | VIDEO DOCUMENTAL LARGO ❌ | PUBLICACIÓN YOUTUBE ❌.

## 2026-10-21 · Corrección audiovisual por comentario del propietario: movimiento Y audio

**Señalamiento recibido:** la previsual BlackBerry de 30 s solo mostraba textos y fondo casi fijo y carecía de audio. La crítica fue correcta: era una prueba de codificación, **no una muestra cinematográfica aceptable**.

### Implementación y resultados reales

1. **Identidad vocal recuperada sin sustituciones:** se leyó `assets/voice/approved/reference.json` y `tools/approved_voice.py`. La referencia exacta es `narrador_documental_aprobado.mp3` (12,336 segundos, SHA256 `78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d`). Su estatus es `approved_by_owner_for_editorial_reference`, **derechos comerciales pendientes**, no una nueva narración de 11 minutos. Se mantuvo sin tocar.
2. **Nuevo motor corto:** `tools/render_blackberry_motion_intro.py` dibuja fotogramas independientes con Pillow para cuatro actos de la introducción: teléfono con movimiento de cámara, red dinámica de mensajes, circuitos de software y aparición de título final. Cada frame usa una variación temporal; ya no son solo imágenes repetidas con texto. Usa audio MP3 aprobado con `-map 1:a:0` y lo codifica como AAC, H.264 720p a 24 fps, 297 frames. El resultado está marcado como `documentary_complete=false` y `commercial_rights_verified=false`.
3. **Pruebas:** `tests/test_blackberry_motion_intro.py` incluye cuatro casos de hash/duración de voz, diferencias reales entre fotogramas de una misma escena, identidad visual de los cuatro actos y rechazo de tiempos inválidos.
4. **Error identificado y corregido de CI:** primeras ejecuciones de `Comprobar base` [39636899012](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39636899012) y [39636975047](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39636975047) fallaron al importar Pillow. Se corrigió `.github/workflows/check.yml` para instalar `Pillow==11.3.0` junto con `pypdf`. **No ocultar fallos previos**.
5. **Prueba de generación auténtica:** GitHub Actions [39636975142](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39636975142) `success`; cuatro tests de movimiento y de voz aprobados, render MP4 `BLACKBERRY_INTRO_MOVIMIENTO_VOZ_REFERENCIA.mp4` de **12,33 segundos**, 1280×720, H.264 + **AAC**, 1 623 429 bytes. `PISTA_AUDIO_VERIFICADA=true`, `FOTOGRAMAS=297`, SHA de voz igual al canónico, `PUBLICACION_AUTORIZADA=false`. Descarga: [artefacto 12360694777](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39636975142/artifacts/12360694777).
6. **Verificación en contenedor:** ZIP descargado; FFprobe confirmó audio AAC, video H.264, 1280×720 y 12,3333 s. Se extrajeron imágenes en 0,8 / 3,8 / 6,9 / 10,4 s, que muestran diferentes actos visuales. El workflow `.github/workflows/blackberry-motion-voice.yml` quedó únicamente manual después de la corrida exitosa, sin publicación YouTube.
7. **Cuidado de interpretación:** esta muestra ahora **sí tiene movimiento y la voz original**, pero **sigue siendo animación gráfica conceptual**, no material cinematográfico realista ni el episodio narrado completo. El sonido es la muestra original de introducción de 12 s; todavía no existen once minutos de voz con aprobación ni pista de música comercial.

### Próxima acción no resuelta

- Desarrollar un lenguaje visual documental con planos originales de lugares/objetos reconstruidos o metraje licenciado y movimientos de cámara, no títulos flotantes como contenido principal.
- Construir la narración larga a partir de la identidad vocal canónica con pruebas independientes y derechos comerciales validados. No usar una voz sintética distinta sin evaluación del propietario; no mezclar audio de referencia y texto no coincidente.
- Sincronizar voz/visuales por escena con ritmo probado, revisar fuentes BlackBerry y exportar un primer montaje de 8–14 min; sin publicación automática ni pagos no aprobados.

**Estado:** OBSERVACIÓN DEL USUARIO ATENDIDA EN INTRO CORTA ✅ | PRUEBA MP4 CON AUDIO ✅ | DOCUMENTAL LARGO CINEMATOGRÁFICO ❌. Todo persistido en `main`.

## 2026-10-21 · Primera escena REAL del guion BlackBerry: voces nuevas y montaje sincronizado (main)

**Objetivo concreto del propietario:** continuar hacia el documental completo después de aprobar la introducción animada de 12,33 s con sonido. La introducción y el SHA de la voz canónica `78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d` se preservan sin edición ni sustitución.

### Avances guardados en `main`
- `tools/qwen_blackberry_scene01.py`: extrae **literalmente el texto narrado de la Escena 01** del manuscrito BlackBerry de 12 escenas; valida que los cuatro segmentos tengan de 150 a 260 caracteres y reconstruyan todas las palabras en el mismo orden. Qwen3-TTS Base 1.7B CPU recibe únicamente la referencia vocal aprobada; semilla fija; exporta 4 MP3, muestra combinada con silencios entre fragmentos, copia intacta de la referencia, checksums y reporte `ESTADO_ESCENA01_VOZ.json`. No cambia el guion o el MP3 canónico, no usa servicio TTS pagado.
- `tests/test_qwen_blackberry_scene01.py`: exactitud de los cuatro segmentos del guion, rechazo de cambios sin revisión, flags de aprobación falsa. GitHub CI [39639684664](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39639684664) `success`.
- `.github/workflows/blackberry-scene01-voice.yml`: ejecución única de investigación de voz desde `main`, Qwen 1.7B CPU en GitHub Actions. [Ejecución 39639684819](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39639684819) iniciada. El resultado queda **PENDIENTE DE FINALIZACIÓN Y AUDICIÓN** al escribir este asiento. Si falla, registrar error exacto y no afirmar que existen MP3 nuevos.
- `tools/render_blackberry_scene01.py`: compositor de montaje original H264/AAC. Comprueba el SHA de cada uno de los cuatro MP3 y que los textos coincidan literalmente con el guion. Mide el audio y crea planos originales en movimiento con cambios de toma cada cinco segundos y transiciones; produce MP4 del primer capítulo con exactamente la duración real del audio. El render continúa marcado como `new_voice_approved=false`, `rights_commercially_verified=false` y `youtube_publication_allowed=false`.
- `tests/test_render_blackberry_scene01.py`: cambios reales de fotogramas dentro de una toma, cambio de planos, límites de tiempo, texto original. CI [39640085857](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39640085857) `success`.
- `.github/workflows/blackberry-scene01-video.yml`: job de solo lectura del repositorio que, si el workflow de voz termina correctamente, recoge su artefacto `fdg-blackberry-escena01-voz-para-audicion`, verifica los cuatro archivos y crea MP4 H264/AAC con informe de fotogramas, duración y audio; no publica a YouTube ni toca Cloudflare o D1. Disparador de primera prueba `workflow_run` será retirado tras validar el primer render. También admite uso manual con ID de corrida.
- **No atribuir tiempos ni archivo de salida antes de ver los artefactos reales.** La síntesis Qwen de otros párrafos consumió minutos de CPU y casi 12 GiB RAM de runner en ensayos anteriores, por lo que esta ejecución está acotada a una sola escena y cuatro fragmentos, sin iniciar los otros once capítulos a ciegas.

### Pendientes
1. Revisar que finalice [39639684819](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39639684819) con cuatro MP3 reales y que `blackberry-scene01-video.yml` exporte un MP4 con audio decodificable, duración medida y cambios de planos; si falla, corregir en `main` y repetir solo el paso fallido.
2. Escuchar cada toma nueva y contrastar la identidad del narrador; **no confundir la voz original aprobada de 12 s con aprobación de estos nuevos minutos**.
3. Completar auditoría editorial y licencias; ampliar paso a paso a las 12 escenas sin sobrepasar cuotas CPU, generar audio/visual original y MP4 final de 8–14 min. No hay publicación automática ni derecho comercial confirmado.

**Estado de esta entrega:** nueva generación de voz y nuevo compositor implementados; CI de contratos verde; render del primer capítulo y aceptación vocal todavía en ejecución/pendientes. Todo en `main`.

### Resultado real Qwen para BlackBerry escena 01 — 2026-10-21, 17:10 UTC

- La generación con Qwen3-TTS Base 1.7B en CPU **sí concluyó**: [workflow 39639684819](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39639684819), `success`.
- Cuatro archivos MP3 generados **desde frases literales del manuscrito**, condicionados por la referencia vocal oficial **sin modificarla**:
  - `01_teclado.mp3`: **15,840 s** (245 caracteres).
  - `02_segunda_historia.mp3`: **13,632 s** (220 caracteres).
  - `03_pregunta.mp3`: **11,448 s** (166 caracteres).
  - `04_seguiremos.mp3`: **14,568 s** (236 caracteres).
- Unión `05_escena01_unida.mp3` de **56,520 s**; comprobado tanto por el reporte Qwen como con FFprobe tras descargar ZIP a la sesión. [Artefacto temporal 12365895069](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39639684819/artifacts/12365895069). Incluye 4 MP3, unión, copia del MP3 canónico y manifest de control. El SHA canónico sigue siendo `78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d`; los audios nuevos **no están aprobados auditivamente por el propietario**.
- Consumo observado: memoria máxima `11978384 KiB` (~11,42 GiB) en GitHub runner; generación desde aprox. 17:01 hasta 17:10 UTC. No se contrató API de pago ni se utilizó laptop propia.
- El propietario recibió enlace directo en conversación para escuchar `/mnt/data/BlackBerry_Escena01_Audio/05_escena01_unida.mp3`; el archivo fue descargado del artefacto, no inventado.
- Se inició automáticamente el render del tramo sincronizado [39641357257](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39641357257) tras concluir Qwen, respetando la verificación del estado `success`; al redactar este asiento el video estaba codificándose y no se afirmaba todavía MP4 finalizado.
- Añadido además `tools/blackberry_voice_schedule.py` y `tests/test_blackberry_voice_schedule.py` para planificar **12 escenas enteras** con división por oraciones/cláusulas y preservación textual; se conservan banderas de `generated_voice_clips=0` para el resto de escenas. Este planificador no sintetiza audio ni dispara cargas Qwen de otras escenas; está cubierto por CI `Comprobar base`.
- `.github/workflows/blackberry-scene01-voice.yml` volvió a modo `workflow_dispatch` **manual**, sin nueva generación pesada por push. El workflow de montaje quedará también solo manual después de comprobar la primera prueba.

**Conclusión del audio:** por primera vez existe casi un minuto de narración nueva del texto real de BlackBerry con referencia al timbre canónico; falta aceptación auditiva humana y licencia comercial. No aprobar ni publicar automáticamente.

### MP4 real de primer capítulo y programación de 12 escenas — 2026-10-21, 17:12 UTC

- **Render audiovisual completado:** GitHub Actions [39641357257](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39641357257) `success`. Descargó los cuatro MP3 de la corrida 39639684819, comprobó hashes y correspondencia literal con las cuatro partes del guion, y generó `BLACKBERRY_ESCENA01_CON_VOZ_NUEVA_REVISAR.mp4`. El propio workflow constató audio AAC, H.264 1280×720 y duración **56,500 s**, 679 fotogramas escritos; [artefacto 12364518448](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39641357257/artifacts/12364518448).
- **Inspección adicional realizada:** se descargó ZIP a conversación, se extrajo MP4 de **5.036.997 bytes**, FFprobe confirmó duración `56.500000`, H.264, 1280×720 y AAC. Se extrajeron cinco fotogramas en 2, 11, 23, 36 y 48 s, y se revisó una hoja de contacto: aparece movimiento y cambia de plano, pero **reutiliza escenas visuales abstractas**. No es todavía reconstrucción cinematográfica realista ni un producto apto para publicación.
- **Enlaces directos compartidos con el propietario:** `/mnt/data/BlackBerry_Escena01_Audio/05_escena01_unida.mp3` y `/mnt/data/BlackBerry_Capitulo01/BLACKBERRY_ESCENA01_CON_VOZ_NUEVA_REVISAR.mp4`. Son copias en la conversación y **no deben confundirse con publicación a YouTube**.
- Se retiró el disparador `workflow_run` temporal de `.github/workflows/blackberry-scene01-video.yml` y se había retirado el disparador `push` de voz. **Ambos siguen disponibles manualmente**, sin gasto automático de nueva IA.
- El nuevo `tools/blackberry_voice_schedule.py` + `tests/test_blackberry_voice_schedule.py` extrae texto íntegro por escenas y lo reparte en fragmentos de 120–260 caracteres, permitiendo cortes en oraciones y comas, sin omitir ni resumir material. `research/blackberry/LOTE_AUDIO_VISUAL_12_ESCENAS.json` está comprometido en `main`: **12 escenas, 56 partes programadas**, solo las **4 tomas de la escena 01** constan generadas; quedan **52 partes sin generar**, 11 escenas sin montaje. Estado editorial y derechos permanecen pendientes.
- La prueba del validador de video, de texto exacto y del planificador se ejecuta por `Comprobar base` en cada commit de `main`. No activar la síntesis masiva de 52 tomas sin comprobar primero calidad auditiva, cuotas CPU, legalidad y la correspondencia de las escenas.

### Próxima prioridad realmente bloqueante

1. Escuchar y valorar **los 56,52 segundos nuevos**: identidad de voz, dicción de BlackBerry, naturalidad y transiciones. La voz de referencia original de 12,336 s no se modificó, pero **ninguno de los cuatro clips nuevos tiene aprobación automática**.
2. Mejorar la imagen (actualmente abstracta y repetida) con B-roll original y movimiento cinematográfico coherente con historia y fuentes. El MP4 de prueba demuestra continuidad AV, no calidad de documental terminado.
3. Ejecutar escena 02 solo tras determinar si las nuevas tomas son aceptables; 11 escenas/52 tomas aún pendientes. Conservar plan y trazas auditivas y de derechos por cada escena.
4. Validar fuentes/historia, derechos de voz y visuales, montaje completo de 8–14 min y **cero publicación YouTube automática**.

**Estado actualizado y demostrado:** primera escena BLACKBERRY = audio real 56,52 s ✅, MP4 con ese audio 56,50 s ✅, render H.264/AAC QA verde ✅; guion de 12 escenas y plan 56 partes ✅; derechos, aprobación vocal y documental largo ❌.

## 2026-10-21 · Decisión arquitectónica definitiva: el sistema hace TODO, ChatGPT no fabrica cada episodio

**Corrección expresa del propietario:** «la meta final es que todo el trabajo lo haga el sistema, no tú», y mencionó **Qwen o Gemini para realizar las investigaciones**. Esto cambia la prioridad de desarrollo: el objetivo no es acumular escenas que el asistente elabora manualmente, sino terminar una plataforma automática reutilizable desde cualquier tema.

### Cambios realizados en este turno (solo `main`)

1. Documento nuevo `docs/ARQUITECTURA_AUTONOMA.md`: fija el criterio de aceptación `tema → descubrimiento y extracción de fuentes → investigador IA → contraste factual → guion original → planificación audiovisual → narración autorizada → montaje MP4 de 8–14 min → QA → revisión del propietario`, sin que ChatGPT escriba personalmente el próximo documental. YouTube queda deshabilitado por defecto y sujeto a autorización.
2. `docs/PLAN_PROYECTO.md`: prioridad **P0** añadida al principio y sección de reorientación al final. Se documenta que BlackBerry es solo una prueba, no la forma definitiva de producir cada episodio.
3. Investigador pluggable propuesto: **Gemini API gratuita** (modelos gratuitos disponibles dependiendo de cuenta/cuota y política de datos) y **Qwen3 LLM local** (investigación textual CPU). El actual Qwen3-TTS solo genera voz; no confundirlo con el investigador. La integración real de Gemini, clave, prueba de red, calidad y cuotas **NO se ha ejecutado ni configurado**. Qwen3-0.6B ya tuvo experimentos pero no avala una investigación autónoma robusta.
4. Reglas obligatorias: evidencia primaria con URL, SHA, periodo/unidad/citas; comparaciones automáticas no dan hechos humanos verificados; ninguna contratación/API pagada, secreto en GitHub/Cloudflare únicamente, fuentes públicas en modalidades gratuitas y ningún contenido comercial sin derechos.

### Estado y siguiente hito verificable

**Hecho:** documentos de arquitectura y plan actualizados en el repositorio, sin cambio de proveedor en producción. No se ha hecho investigación Gemini ni generado contenido nuevo; no afirmar lo contrario.

**P0.1 siguiente:** implementar un contrato de proveedores `gemini_free`/`qwen_local`, pruebas sin clave ni gasto, y hacer un **ensayo real de investigación completa de un tema nuevo** por la plataforma tras configurar Gemini de forma segura (si se selecciona) o usar un Qwen LLM viable. Registrar exactamente fuentes, respuestas, latencia, límites de coste y errores. Luego conectar las etapas hasta MP4. El propietario debe supervisar/aprobar resultados, no realizar tareas técnicas.

**Recordatorio:** mantener exclusivamente `main` y documentar cada implementación, CI y despliegue por separado. La dirección se considera acordada; no regresar a producción manual permanente del chat.

### Primer componente implementado de la reorientación — contrato Gemini/Qwen (2026-10-21)

**Código real comprometido en `main`:**
- `tools/research_providers.py`: contrato común que transforma únicamente pasajes documentales originales en entradas identificadas (hasta 24, con `source_id`, URL, fragmento y página), construye un prompt estructurado y exige salida JSON con afirmaciones candidatas y preguntas de investigación pendientes. Cada cita que devuelva un modelo debe apuntar a un ID real incluido en la solicitud; de lo contrario se rechaza. Ningún modelo marca hechos verificados por sí mismo.
- `run_gemini_free`: adaptador HTTP de `gemini-2.5-flash` o `gemini-2.5-flash-lite`, con clave `GEMINI_API_KEY` por secreto y **bloqueo hasta confirmar la modalidad gratuita**. No hay clave configurada/confirmada ni llamadas reales realizadas; el control evita que el código active el proveedor inadvertidamente. Esto **no puede garantizar por sí solo** que una clave ya facturable no genere cargos: el estado de la cuenta deberá comprobarse antes de utilizarla.
- `run_qwen_local`: adaptador de generación local inyectable que acepta respuestas del Qwen LLM en el mismo contrato de evidencia. Es interfaz y pruebas de contrato; el motor de texto Qwen experimental existente aún no se conecta directamente a esta interfaz en el workflow de producción.
- `tests/test_research_providers.py`: 5 pruebas offline con proveedor simulado sobre fuente original, salida JSON, citas inventadas, opción gratuita obligatoria, ausencia de claves, hash de prompt y bloqueo de aprobación/publicación; cero créditos/API usados.
- `tools/production_preflight.sh`: añadió la prueba de estos proveedores a las condiciones de despliegue; la comprobación general `.github/workflows/check.yml` ejecuta automáticamente todas las pruebas Python de `tests`.

**Verificación de este lote:** CI [39644919482](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39644919482) `success` con adaptadores y tests; después se actualizó el preflight (commit `528a4d0588254aee772d77432a805d67becf13b0`), cuya comprobación [39644991576](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39644991576) estaba en ejecución al registrar este punto. No se afirma que Gemini haya investigado o que el ciclo autónomo end-to-end ya funcione.

**Siguiente integración prioritaria:** añadir selección de investigador en workflow/panel y conectar los pasajes del propio motor al adaptador; configurar una clave Gemini solo a petición/mediante secretos y validación de cuota gratuita; realizar primera investigación automatizada de un tema *sin fuentes ni guion preparados por ChatGPT*, con una ruta Qwen viable para contingencias. Comparar calidad, evidencia, tiempos y límites antes de automatizar guion/producción.

## 2026-10-21 · Cambio de requisito: radar autónomo de mercado, selección, fabricación y publicación

**Instrucción expresa del propietario:** la IA responsable debe estudiar en tiempo cercano al real la demanda del mercado (con la frescura y cuotas que permiten las fuentes), descubrir temas sin esperar entrada manual, clasificarlos, investigar la mejor oportunidad, transferir resultados a los motores audiovisuales y, tras autorización, **subir/programar el episodio con el propio sistema en YouTube**. ChatGPT se limita al desarrollo de la plataforma, no escribe/procesa manualmente cada documental de manera permanente.

### Código y decisiones ya guardados en `main`

1. Se corrigió el principio de `docs/ARQUITECTURA_AUTONOMA.md` y la portada de `docs/PLAN_PROYECTO.md`: el disparador estándar es el radar, no un tema que escribe el propietario. El portal permite preferencias/nicho y un tema manual como excepción, no como requisito.
2. Documento nuevo `docs/INTELIGENCIA_MERCADO.md`: mercado, fuentes, variables, criterios, límites, selección de emergentes/evergreen, ciclo D1, guardas, analítica posterior y carga YouTube controlada. No confundir señales de Wikipedia con volumen de búsqueda ni datos YouTube con éxito garantizado.
3. `tools/market_radar.py`: primer selector determinista. Requiere, para cada candidato elegible, estadísticas de 3–30 videos públicos de YouTube de hasta 90 días, observadas hace menos de ocho días, una señal independiente de interés por Wikipedia con dos ventanas equivalentes de 7 días y al menos una URL de fuente original. Excluye duplicados publicados, datos fuera de fecha y ausencia de métricas. Puntaje heurístico documentado y desglosado; permite abstenerse de seleccionar.
4. `tools/market_sources.py`: primer colector con clave de YouTube Data API (2 llamadas como máximo, 10 videos por candidato, limitación regional configurada y validación de estadísticas), y Wikimedia Pageviews de 14 días completos. Si la clave o muestra falta, el colector falla explícitamente: no inventa datos ni simula tráfico. **Todavía recibe entidades/temas del siguiente descubridor por desarrollar, no los extrae por sí mismo desde señales generales del mercado.**
5. Pruebas `tests/test_market_radar.py` y `tests/test_market_sources.py` con datos totalmente **sintéticos como fixtures**. No se usaron claves de YouTube, Gemini, Google Trends ni datos de un mercado verdadero en estas pruebas. `tools/production_preflight.sh` añade ambas baterías como condición de compilación del proyecto.

### Verificación y límites

- CI [39648768592](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39648768592) `success` después de añadir los colectores y pruebas; otras comprobaciones intermedias también aprobadas.
- Se añadieron los tests al preflight en el commit `6f12a0938d86e6213480b751a6fddc08887bb1c7`. **No** declarar confirmación de deploy remoto Cloudflare basándose solo en CI.
- **Aún no existe** radar en vivo conectado a YouTube, Google Trends alfa, Analytics propio, feed de noticias, descubridor automático de empresas ni un ranking de mercado real. `market_radar.py` demuestra el contrato de selección pero **no que funcione end-to-end**.
- **No se ha habilitado publicación a YouTube**. El producto debe terminar actuando como productor y también como operador de carga/agenda después de que se autorice el episodio, con OAuth y derechos comerciales acreditados.

### Próximas tareas prioritarias

1. Conectar credenciales de YouTube Data API mediante secretos, solo con permisos/consentimiento y cuotas verificadas. Descubrir temas desde señales **reales** del nicho sin requerir nombres propuestos por ChatGPT/propietario; extraer entidades y evitar duplicados.
2. Validar primer ranking no simulado para varias empresas, con fuentes y puntuación guardada en D1 y canal de estado visible. Añadir API Trends exclusivamente si se aprueba acceso alfa.
3. Elegir automáticamente el candidato suficiente, investigar con Gemini/Qwen, citar, verificar y redactar guion por el sistema. Después generar voz/escenas, montar y controlar MP4 de 8–14 minutos de manera autónoma.
4. Realizar flujo YouTube OAuth → revisión/permiso editorial → upload/programación automática por sistema → analytics → siguiente ranking, sin activarlo antes de garantías y licencia.

**Estado de esta etapa:** prioridad y arquitectura corregidas, ranking/colección de muestras y pruebas incorporadas al repositorio. **Estudio en vivo, selección autónoma de temas y autopublicación todavía pendientes.** Todo en `main`, con historial y sin gastos.

## 2026-10-21 · Primer descubrimiento automático de una empresa REAL + serie de interés

**Objetivo del propietario:** avanzar hacia una plataforma que elija los mejores temas en base a mercado, sin que ChatGPT proporcione manualmente empresas, guiones o material. Se trabajó solo en `main`.

### Implementación nueva
1. `tools/topic_discovery.py`: lee Wikimedia Pageviews Top (es/en), verifica identidad/clase empresa en Wikidata mediante P31 y conserva candidato, QID, idioma, fecha, enlace/ranking. Es un **descubridor desde señales**, no una lista de empresas hardcodeada. Filtra personas, títulos especiales y URLs inseguras. Controla hasta 180 artículos por wiki y 12 lotes Wikidata como topes de código; las pruebas reales usaron 120 artículos por idioma y 8 lotes.
2. Se cambió en `tools/market_sources.py` el límite de respuesta JSON de 1 MB a 5 MB, aún acotado, con encabezado `User-Agent` identificable según política del proveedor. La primera prueba había demostrado que 1 MB no alcanzaba para el top diario.
3. Enriquecimiento opcional `--enrich-interest`: consulta Wikimedia Pageviews para **14 días completos** de una página detectada, separando 7 días recientes de 7 previos, máximo seis empresas por ejecución. Si falla un proveedor no inventa cifras.
4. `tests/test_topic_discovery.py`: siete casos unitarios para clasificación/ausencia de señal/fechas/idiomas/URLs/consulta real simulada de 14 días. Los tests fueron ejecutados por el CI general (Python unittest discover).
5. `.github/workflows/topic-discovery-smoke.yml`: primera prueba disparada temporalmente por `push` y posteriormente convertida en **workflow diario programado a las 10:17 UTC + manual**, con límites de solicitudes y sin Qwen, Gemini ni YouTube.

### Evidencia real de red (no simulada)
- [Primera ejecución 39650638377](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39650638377): **failure** al superar el tamaño de lectura original de 1 MB. Se corrigió y repitió, no se ocultó el fallo.
- [Ejecución 39650844704](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39650844704): **success**, 240 artículos en es/en, 8 lotes Wikidata, **1 empresa candidata Theranos** (Q16956307), con QID y enlace de Wikipedia. Ningún estudio completo ni tema seleccionado para video.
- [Ejecución 39651368713](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39651368713): **success**, los mismos 240 artículos y 8 lotes, con **1 serie real de 14 días** completada. El ZIP de artefacto `12370101388` fue descargado y JSON leído: `Theranos`, 291.435 visualizaciones del artículo en la semana 14–20 de octubre y 55.952 en la semana 7–13 de octubre, fuente `en.wikipedia.org`; `observed_at=2026-10-21`. Son visitas al artículo, NO búsquedas Google, demanda garantizada de YouTube ni retención del canal.
- Registro permanente editorial en `research/market/VALIDACION_RADAR_2026-10-21.md`. Informe operativo JSON permanece en artefacto GitHub de retención limitada y en ZIP de la conversación; falta almacenar series futuras en D1.

### Próximos pasos
1. Añadir otras fuentes de descubrimiento más inmediatas para no depender de Wikipedia con desfase de ~3 días y aumentar muestra a varias compañías.
2. Conectar YouTube Data API y obtener estadísticas observadas, saturación, formatos y crecimiento real del propio canal al tener OAuth; **no simular interés** ni publicar sin autorización.
3. Persistir candidatos/rankings en D1 y conectar el selector con Gemini/Qwen para que el sistema investigue, redacte, narre, monte y entregue un MP4 original de 8–14 minutos.
4. Mantener derechos y revisión editorial como puertas obligatorias antes de una subida/programación de YouTube hecha por el mismo sistema.

**Estado:** descubrió por sí mismo la primera empresa candidata y midió interés en Wikimedia ✅; estudio comparativo profesional de mercado, tema ganador, producción completa y autopublicación aún pendientes ❌. Todo en `main`, sin pagos ni publicación.

## 2026-10-21 · Segunda ronda de descubrimiento autónomo y almacenamiento probado

**Necesidad del propietario:** el propio sistema investiga mercado permanentemente, decide los mejores temas y posteriormente investiga, narra, monta y sube a YouTube después de garantías; no depender del chat. **Todo commit fue directo a `main`.**

### Resultado con fuentes externas verdaderas

1. `tools/topic_discovery.py` + workflow ampliados a **360 artículos Wikipedia es/en** y máximo **12 lotes Wikidata** por corrida, con enriquecimiento de hasta seis páginas mediante ventanas comparables de 14 días. [Ejecución 39652155079](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39652155079) `success`: **Theranos Q16956307** y **DuPont Corporation Q221062** identificadas sin que ChatGPT introdujera esos nombres; se obtuvieron dos series de interés, con días de referencia 18 y 21 octubre (top con 3 días de retraso). Visitas por semana: Theranos 291.435/55.952 y DuPont 3.512/338. **Solo interés Wikimedia**, ningún ranking validado de demanda YouTube.
2. Migración nueva `migrations/0004_market_intelligence.sql`: tablas aditivas `market_runs`, `market_entities`, `market_pageview_observations`, `market_interest_windows`, `market_selection_decisions`. No afecta `jobs`, `events`, `research_requests` ni `editorial_dossiers`; **NO se ejecutó en D1 remoto**.
3. `tools/market_persistence.py`: esquema SQLite compatible D1, transacciones idempotentes, verificación QID, fechas, host Wikimedia, métricas y ventanas completas; `tests/test_market_persistence.py` cubre historial multi-día, ausencia de duplicados y preservación de migraciones previas. CI [39652800696](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39652800696) `success`.
4. [Prueba real integrada 39652982369](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39652982369) `success`: descubrimiento externo y medición, seguida de escritura de **SQLite local**. Se descargó artifact 12369113919 y se leyó con SQLite: `market_runs=1`, `market_entities=2`, `market_pageview_observations=2`, `market_interest_windows=2`, `market_selection_decisions=0`. `D1_PRODUCCION_MODIFICADA: FALSE`. Archivo local nuevo por ejecución, **aún no historial remoto persistente**.
5. `tools/production_preflight.sh` agregó pruebas de `test_topic_discovery.py` y `test_market_persistence.py`. Se retiró el disparador `push` temporal de la prueba integrada y dejó el workflow de investigación pública **diario (10:17 UTC) + manual**, sin gasto de IA ni publicación.

### Documentación/evidencia

- `research/market/VALIDACION_RADAR_2026-10-21.md` recoge la primera prueba de 240 artículos.
- `research/market/VALIDACION_RADAR_360_2026-10-21.md` recoge la prueba ampliada a 360 artículos y validación de SQLite, ambos con enlaces a workflows.
- Los artefactos diarios GitHub caducan; solo la documentación y el código están conservados permanentemente en `main`.

### Próximas tareas prioritarias

- Identificar cuenta Factor en Cloudflare, confirmar respaldo y aplicar D1 0004 remoto sin sobrescribir trabajos existentes; crear vía autenticada para guardar el radar diario y visualizarlo en panel.
- Incorporar noticias/trends actuales y YouTube Data API para comparar interés de **varios** temas, audiencia hispanohablante, competencia relativa y fuentes primarias suficientes. No elegir por solo Wikipedia.
- Implementar elección automática + Gemini/Qwen investigador y control factual → guion → voz → escenas → MP4 8–14 min → revisión editorial/derechos → YouTube OAuth y publicación por el propio sistema.
- Mantener decisiones explicables, cuotas y logs; evitar IA de pago no autorizada y no atribuir al motor una investigación completa que todavía no realiza.

**Estado:** radar de descubrimiento real y primer almacenamiento SQLite verificados; persistencia D1 remota, selección de mejor tema YouTube y productora end-to-end pendientes.


## 2026-10-21 · API administrativa del radar de mercado (continuación)

### Código implementado en main
- Nuevo `src/market-radar.mjs`: consulta limitada y exclusivamente de lectura de `market_runs`, `market_entities` y `market_interest_windows`. No realiza escrituras, ni decisiones editoriales, ni publica videos.
- `src/worker.js`: ruta `GET /api/market/radar?limit=30`, ubicada después del guard de `ADMIN_TOKEN`. El token del renderizador no autoriza el endpoint; respuesta 405 para otros métodos, 400 para límites fuera de 1-100 y 503 si falta migración 0004.
- `tests/test_market_radar_api.mjs`: contratos de consultas de solo lectura, límites, banderas fail-closed y migración ausente.
- `.github/workflows/check.yml`: nueva prueba incluida en CI de rama main.

### Distinción de estados y riesgos
- Los cambios de código han sido enviados a GitHub en `main`; **no se ha aplicado migración 0004 en D1 remoto ni desplegado este nuevo Worker desde este avance**.
- El endpoint solo presentará filas reales cuando se configure persistencia remota; datos SQLite generados en runners siguen siendo efímeros.
- Una observación Wikimedia nunca equivale a demanda YouTube; `market_study_complete`, `youtube_data_verified` y `automatic_publication_allowed` permanecen falsos.
- Antes de aplicar D1 0004: identificar cuenta/DB real, revisar respaldo, confirmar conservación de tablas y filas antiguas y realizar migración aditiva controlada.

### Próximas tareas prioritarias
1. Confirmar CI incluido `tests/test_market_radar_api.mjs`.
2. Identificar cuenta Cloudflare Factor y respaldo D1, aplicar migración 0004 en la DB correcta y verificar las tablas sin alterar `jobs`, `events` ni expedientes.
3. Implementar ingesta autenticada con idempotencia y trazabilidad de procedencia desde workflow diario a D1; nunca incluir tokens en artifacts/logs.
4. Añadir proveedor de noticias y señales YouTube reales para comparar múltiples temas antes de cualquier selección.
5. Conectar selección fundamentada con investigación Gemini/Qwen, fact-check, guion, voz, visuales, QA y subida a YouTube solo tras aprobación.



## 2026-10-21 · HITO NUEVO: radar persistente REAL con GitHub OIDC, D1 y panel

### Auditoría previa y migración remota
- Cuenta conectada: Cloudflare **Factor**, no `Primary`. DB exacta `factor-de-gigantes-db` UUID `ef699e75-b50a-4e28-a665-69316d10cdaf`.
- Antes de alterar D1: se leyó `sqlite_master`, se verificaron tablas 0001–0003, se registró bookmark Time Travel y Cloudflare confirmó exportación SQL temporal. El punto de restauración no debe confundirse con copia externa permanente.
- Se aplicó **`migrations/0004_market_intelligence.sql`** directamente a D1 remota con su SQL aditivo original; resultado OK y cinco tablas presentes: `market_runs`, `market_entities`, `market_pageview_observations`, `market_interest_windows`, `market_selection_decisions`.
- Recuento conservado antes/después: `jobs=1`, `events=8`, `editorial_dossiers=0`, `research_requests=0`. Sin pérdida de registros previos.

### Backend y seguridad implementados
- `src/market-ingest.mjs`: validación de entidades QID, fechas, series completas, métricas enteras, dominio Wikimedia, presupuestos y estados no autorizados. Escribe con `DB.batch` transaccional e identificador derivado de SHA-256 canónico. Inserciones idempotentes para reportes repetidos; no activa render ni YouTube.
- `src/github-oidc.mjs`: verificación de firma RS256 con claves públicas GitHub y claims de audiencia, `repository_id`, `workflow_ref`, rama, evento y tiempo. **No se utiliza un token de ingesta de larga duración**.
- `src/worker.js`: ruta `POST /api/market/ingest` únicamente mediante OIDC y ruta `GET /api/market/radar` únicamente con `ADMIN_TOKEN`.
- `tools/push_market_radar.py`: obtiene credencial efímera de GitHub Actions y reporta éxito solo cuando la API confirma escritura D1.
- `.github/workflows/topic-discovery-smoke.yml`: descubrimiento diario + manual, `id-token: write`, envía reporte a Worker sin almacenar el JWT; después de prueba temporal de integración se **retiraron tanto `push` como la concesión OIDC para evento `push`**.
- `tests/test_market_ingest.mjs`, `tests/test_github_oidc.mjs`, `tests/test_push_market_radar.py` y CI Node/Python añadidos y validados.

### Evidencia de funcionamiento real
- La primera ejecución de integración falló con 401 durante el despliegue/ajuste de credenciales efímeras. No se contó como éxito y se revisó.
- **[GitHub Actions 39658991775](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39658991775): `success`**. Recopilación pública real, prueba SQLite, autenticación OIDC, HTTP 201 y persistencia D1 confirmadas.
- Se leyó D1 remota *después* del éxito: `market_runs=1`; `market_entities=2`; `market_pageview_observations=2`; `market_interest_windows=2`; `market_selection_decisions=0`. Se comprobaron otra vez `jobs=1`, `events=8`.
- No se introdujeron manualmente nombres de empresas ni valores de mercado; la ejecución obtuvo entidades y cifras desde las fuentes públicas.
- Cloudflare API mostró versiones desplegadas del Worker que incluyen el verificador OIDC y la escritura D1; el build sigue sincronizándose desde `main`.

### Panel y presentación del histórico
- `public/index.html` incorpora sección «Radar de oportunidades» dentro del espacio autenticado.
- `public/app.js` consulta `/api/market/radar?limit=30` y presenta candidatos, ventanas y procedencia como **visitas a artículos Wikimedia**, nunca como demanda de YouTube; se usa `textContent` para evitar inyección HTML.
- Pendiente comprobación visual autenticada desde el navegador del propietario; el código y las comprobaciones CI no equivalen a navegación manual.

### Qué falta para la meta final
1. Añadir **descubrimiento oportuno de noticias y empresas** y guardar fuentes/time series en D1; ampliar variedad y continuidad de candidatos.
2. Conectar YouTube Data API (con cuota/credencial permitida) para observar videos recientes de cada mercado hispanohablante y comparar competencia y relevancia. Sin ello **no existe ranking YouTube real**.
3. Crear decisión explicable, auditada y basada en múltiples fuentes: motivo de elección, exclusión, conflictos y certeza, no elegir por popularidad de Wikipedia.
4. Conectar mejor tema → dossier investigador Gemini/Qwen → fact-check y citas → guion 8–14 min → voz/escenas originales → QA audiovisual real.
5. Añadir autorización editorial, derechos y OAuth oficial de YouTube; publicar solo con aprobación y sin contenido reutilizado.
6. Validar experiencia completa del panel y plan de restauración/coste operativos.

**Resultado inequívoco de esta sesión:** persiste autónomamente el radar en D1 con OIDC probado. **No** está concluida la investigación integral de mercado ni la producción/publicación automática. Historial y código en `main`.



## 2026-10-21 · P0: noticias actuales, preselección temática y D1 remota

### Nuevas funciones implementadas, no solo auditadas
- `tools/news_discovery.py`: colector ejecutable de **Google Noticias RSS** en cuatro consultas generales de empresas, innovación, tecnología e industria (ES/EN, PE/MX/US). Las consultas NO contienen nombres de empresas preseleccionadas. Conserva titulares, fecha UTC, URL del agregador, medio atribuido y categoría, con límites de tamaño, 72 horas de frescura, deduplicación y fallos explícitos.
- `migrations/0005_news_leads.sql`: nuevas tablas `market_news_runs` y `market_news_leads`; los registros nuevos quedan `unverified`, sin autorización editorial ni demanda YouTube calificada. Migración **aplicada y tablas verificadas en Cloudflare D1 REMOTA**, cuenta `Factor`. Se registró bookmark Time Travel antes de aplicarla.
- `src/news-ingest.mjs`, `tools/push_news_radar.py` y `src/worker.js`: ingesta vía `POST /api/market/news/ingest` con **GitHub OIDC** y validación estricta del payload. Escrituras por lote de D1, IDs estables para deduplicar y bloqueo explícito de autorización de videos. `GET /api/market/news` lee las noticias con `ADMIN_TOKEN`.
- `.github/workflows/topic-discovery-smoke.yml`: se amplió el radar diario para buscar noticias, preservar el reporte original y almacenarlo mediante identidad OIDC temporal en la misma base, sin APIs pagadas. **Se retiró el disparador temporal `push` al finalizar la prueba**; programación diaria 10:17 UTC y activación manual permanecen.
- `src/news-triage.mjs`: preselección **heurística y explicable** de relevancia documental; puntúa señales del titular (innovación, cambio empresarial, disrupción, industria) y penaliza material promocional, guías para invertir y noticias de mera cotización. Puntuación ≠ demanda YouTube ni aprobación editorial.
- `public/index.html` y `public/app.js`: sección privada «Noticias empresariales recientes» con medio atribuido, fecha, vínculo original del agregador y relevancia exploratoria. Uso de `textContent` para titulares ajenos.
- `tests/test_news_discovery.py`, `tests/test_news_ingest.mjs`, `tests/test_news_triage.mjs`: comprobación de fuentes, no simulación de resultados, deduplicación, frescura, seguridad, clasificación y prohibición de calificar temas sin señales externas; integradas en CI.

### Prueba integrada con fuentes y D1 verdaderas
- **[GitHub Actions 39668778079](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39668778079) `success`**: Wikimedia siguió funcionando, el nuevo colector RSS consultó sus fuentes y el Worker persistió sus resultados con OIDC real.
- Lectura de **Cloudflare D1 remota** posterior a ejecución: `market_news_runs=1` y `market_news_leads=100`, recortado al límite configurado. `market_runs=1`, `market_entities=2`, `jobs=1`, `events=8`: lo existente se preservó. Los titulares provenían de distintas fuentes atribuidas por el agregador, como Perú 21, AFR y Banca y Negocios. No se debe asumir que cada uno es editorialmente útil o verdadero.
- La **primera** prueba integral de noticias falló por HTTP 401 mientras la nueva versión del verificador OIDC se desplegaba; se diagnosticó, y la repetición tras el despliegue terminó `success`. La caída inicial no se declara éxito.
- Los permisos de `push` incorporados SOLO para la prueba se retiraron tanto del workflow como del validador OIDC, con CI posterior exitosa. No hay publicación YouTube.

### Limitaciones y siguiente fase
- Los 100 artículos almacenados son **titulares RSS de agregador**, no 100 temas verificados ni datos competitivos YouTube; puede haber noticias no pertinentes. No se han leído automáticamente los artículos originales.
- La puntuación de relevancia del título es un **filtro preliminar**, no puntuación de oportunidad de mercado; no se promueve automáticamente una noticia a investigación ni a guion.
- **Próximo P0**: obtener estadísticas observadas de YouTube Data API para temas/candidatos (con credenciales/cuotas permitidas), detectar y agrupar narrativas de varias noticias y contraste de fuentes primarias, computar competencia y crecimiento por región, y persistir una selección fundamentada. Solo después conectar Gemini/Qwen y el motor profesional de documental con revisión editorial.
- El navegador privado del propietario sigue pendiente de prueba visual autenticada. La lectura de D1 y el despliegue de código no equivalen a login probado.

**Estado final del bloque:** radar de empresas + radar de noticias con persistencia diaria D1 real ✅; preselección editorial sin IA y lectura desde panel implementadas ✅; estudio de mercado YouTube / mejor tema / documental integral / autopublicación autorizada pendientes ❌.


## 2026-10-21 · Hito P0: YouTube Data API por empresa y región, persistencia D1 y cuota sin pagos

### Desarrollo real en `main`
- Reutilizado `tools/market_sources.py` (cliente oficial YouTube Data API v3 `search.list` + `videos.list`) y agregado `channel_id` público solo si viene en la respuesta; jamás se estima retención o CTR ajenos.
- Nuevo `tools/youtube_market_study.py`: elige **únicamente las empresas descubiertas por Wikimedia/Wikidata**, hasta 2 y dos mercados hispanohablantes `MX` / `ES`, sin temas escritos manualmente por ChatGPT. Máximo **4 pares empresa-región, 4 búsquedas y 4 solicitudes de estadísticas** por ejecución; calcula muestras de videos recientes, mediana observada de vistas/día de antigüedad, canales identificados, región y fecha. Es **comparación exploratoria**, no prueba de demanda global.
- **Actualización documentada de cuota octubre de 2026:** el método `search.list` dispone ahora de bucket independiente por llamadas (hasta 100 al día por defecto, 1 unidad por llamada); `videos.list` cuesta 1 unidad en su cuota respectiva. Límite de este workflow: **4 llamadas de búsqueda + 4 de videos = 8 unidades solicitadas entre ambos buckets** por corrida, nunca 404 unidades de la fórmula antigua. Referencia oficial: https://developers.google.com/youtube/data/determine_quota_cost (actualizada 2026-10-15). La cuota real del proyecto debe comprobarse en Google Cloud antes de habilitarla.
- **Bloqueo de coste por defecto**: el workflow solo realiza llamadas si GitHub tiene `YOUTUBE_DATA_API_KEY` y la variable `YOUTUBE_MARKET_BUDGET_ENABLED=1`. Sin ambas, registra omisión explícita: ninguna llamada YouTube, ninguna muestra ni dato inventado, ningún proveedor cobrable alternativo.
- Migración aditiva `migrations/0006_youtube_observations.sql`: `market_youtube_runs`, `market_youtube_queries`, `market_youtube_videos`. **Aplicada a D1 remota Factor** tras verificar tablas previas, bookmark Time Travel y exportación temporal; se conservaron `jobs=1`, `events=8` y `market_news_leads=100`. **La restricción SQL de cuota es deliberadamente un límite superior amplio; la validación aplicativa impone el presupuesto real de 8 unidades.**
- `src/youtube-market.mjs`: valida procedencia, presupuestos, fechas, IDs, conteo de videos/canales y **recalcula la mediana sobre los valores de cada video**, rechazando métricas incoherentes. Persiste lotes D1 idempotentes con IDs SHA-256. No aprueba investigación, guiones ni YouTube.
- `src/worker.js`: nuevo `POST /api/market/youtube/ingest` protegido por GitHub OIDC, y `GET /api/market/youtube` con el `ADMIN_TOKEN` existente. No requiere token de ingesta adicional.
- `tools/push_youtube_study.py` envía los resultados solo a Worker Factor, con OIDC efímero, ocultando secretos. `.github/workflows/topic-discovery-smoke.yml` lo ejecuta condicionalmente después del radar real Wikimedia/RSS.
- Sección de **Comparación YouTube** agregada a `public/index.html` y `public/app.js`: muestran empresas, países, tamaño muestral, mediana por video y canales identificados cuando existan datos; con 0 datos, se muestra estado de insuficiencia sin ranking falso.
- Pruebas nuevas `tests/test_youtube_market_study.py`, `tests/test_youtube_market.mjs`, `tests/test_youtube_schema.py`; actualizadas `tests/test_market_sources.py` indirectamente por campos adicionales. Validan límite de llamadas, modo sin clave, fallos, fuentes, firma/lógica administrativa, FK y conservación del esquema.

### Evidencia y estado operativo
- Cloudflare API verificó **tres tablas nuevas presentes** en la D1 real y el Worker desplegado con endpoints/INSERT de YouTube.
- Recuento observado tras migración: `market_youtube_runs=0`, `market_youtube_queries=0`, `market_youtube_videos=0`. Esto **NO** significa que se haya medido competencia: el servicio espera las condiciones de cuota/API. No se configuraron secretos ni facturación en esta intervención.
- GitHub Actions CI incluye pruebas JS/Python reales de contrato. Los videos de las pruebas son **fixtures**, no métricas de mercado.
- Respetadas las reglas: cero pagos, ninguna búsqueda con clave en logs, cero publicaciones, cero cambios destructivos, únicamente rama `main`.

### Próximo hito funcional sin desviar prioridad
1. Confirmar con la cuenta de Google si existe proyecto YouTube Data API con cuota gratuita disponible y **sin facturación activada**; registrar de forma segura clave GitHub `YOUTUBE_DATA_API_KEY` y activar `YOUTUBE_MARKET_BUDGET_ENABLED=1` únicamente si se autoriza el consumo de cuota gratuita. Probar la ingesta pública y verificar filas remotas, sin inventar estadísticas.
2. Automatizar obtención de **fuentes primarias verificables** sobre empresas/eventos detectados y vincular titulares RSS con entidades canónicas (Wikidata) y fuentes originales, conservando procedencia.
3. Generar ranking comparable multiseñal y persistir `market_selection_decisions`, con estado `sin_datos_suficientes` cuando falten fuentes o YouTube. No usar la mediana de videos como pronóstico de crecimiento propio.
4. Encadenar investigación Gemini gratuita o Qwen local, evidencias, guion, voz oficial aprobada y MP4 profesional de 8–14 min con QA; publicación en YouTube siempre condicionada a revisión y permisos.

**No declarar completada fase P0:** el colector y su almacenamiento están implementados, pero falta primera ejecución con estadísticas YouTube auténticas y conexión de evidencia primaria para selección fundamentada.


## 2026-10-21 · P0 — Continuación: cotejo automático de fuentes y prueba integral (migración 0007)

### Código en main
- `tools/market_news_join.py`: asocia empresas realmente descubiertas por Wikimedia con titulares realmente obtenidos por RSS, por coincidencia textual normalizada y límites de palabra, quitando sufijos societarios genéricos. No utiliza lista fija de compañías, LLM, datos inventados ni adivina identidades. Excluye nombres ambiguos/cortos, fechas dispares y dominios fuera del agregador. Conserva evidencia de ambos extremos.
- `migrations/0007_entity_news_links.sql`: tablas aditivas `market_entity_news_runs` y `market_entity_news_links`. FK a `market_entities` y `market_news_leads`, estado `candidate_needs_entity_confirmation`, sin aprobación ni datos de YouTube.
- `src/market-cross-signals.mjs`: valida procedencia, tamaño, fechas, IDs, titular que contiene la mención y estados editoriales pendientes; persistencia por lote D1 idempotente, sin alterar manualmente un enlace confirmado/rechazado. API administrativa de lectura `GET /api/market/cross` y entrada OIDC `POST /api/market/cross/ingest` integrada en el Worker.
- `tools/push_market_cross.py`: transporte desde GitHub Actions a Cloudflare con JWT OIDC efímero, sin compartir ni imprimir tokens. `.github/workflows/topic-discovery-smoke.yml`: correlación + persistencia después de RSS y antes del sondeo YouTube condicional.
- `public/index.html`, `public/app.js`: sección de coincidencias con noticia y empresa y estado explícito de no verificación; interfaz sin HTML inyectado a partir de titulares externos.
- `tests/test_market_news_join.py` y `tests/test_market_cross_signals.mjs`: false positive tests, deduplicación, rechazo de aprobaciones falsas, datos de prueba marcados como fixtures, integración CI.

### Despliegue y prueba real
- Antes de alterar D1 se comprobó la base `factor-de-gigantes-db` en la cuenta Cloudflare Factor, obtuvo bookmark Time Travel y Cloudflare completó una exportación SQL temporal (no una copia externa permanente). Se verificó conservación inicial de registros.
- **Migración 0007 aplicada directamente en D1 REMOTA**: dos tablas presentes; las anteriores conservadas.
- Para lanzar una única prueba real se habilitó temporalmente `push` en el workflow y verificador OIDC, exclusivamente en `main`. El guardado del nuevo paso funcionó mediante el circuito Cloudflare autenticado.
- **[GitHub Actions 39673977211](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39673977211): `success`.** Pasaron descubrimiento Wikimedia, SQLite local, ingesta D1, RSS real, correlación, ingesta del cruce y paso de YouTube bajo presupuesto.
- Lectura independiente posterior a D1: `market_entity_news_runs=1`, `market_entity_news_links=0`; `market_entities=2`, `market_news_leads=106`, `jobs=1`, `events=8`. El sistema examinó 100 noticias en esa corrida, pero no halló ninguna mención textual confiable de las 2 empresas. **0 coincidencias es una observación real, no un fallo ni una licencia para inventar entidades.**
- YouTube: `market_youtube_runs=0`, `market_youtube_queries=0`, `market_youtube_videos=0`. La fase está **implementada pero no validada contra la API pública con credenciales reales**. No se ha consumido cuota de Google ni activado facturación desde aquí.
- **Cierre del modo prueba:** se eliminaron de nuevo tanto el evento `push` del workflow como su autorización en `src/github-oidc.mjs`. Las únicas entradas conservadas son `schedule` y `workflow_dispatch`. Se restauró el test que rechaza `push`.

### Próxima prioridad P0
1. Verificar que existe un proyecto YouTube Data API con cuota gratis **sin facturación**, y que están disponibles credencial `YOUTUBE_DATA_API_KEY` y permiso explícito `YOUTUBE_MARKET_BUDGET_ENABLED=1`; no pedir ni introducir clave en chat. Sin esos requisitos el módulo no llama a YouTube, informa el bloqueo sin inventar métricas.
2. Incorporar más candidatos desde noticias actuales a entidades Wikidata, con precisión medible y verificación de fuentes primarias; ampliar la cobertura de temas sin aumentar pagos.
3. Tras obtener muestras reales de competencia YouTube, comparar oportunidad de varios temas, justificar descartes, registrar `market_selection_decisions` en D1 y asignar `sin_datos_suficientes` cuando corresponda. Vincular sólo elegibles a investigador Gemini gratuito / Qwen local.
4. Después guion con evidencias, voz canónica aprobada, visuales originales/licenciados, documental 8–14 min, QA, autorización editorial y subida a YouTube con OAuth permitido.

**Conclusión técnica:** se han integrado y probado dos nuevos módulos en producción (ingesta informativa y cotejo), y se preparó YouTube condicionado a cuota. No confundir infraestructura lista con inteligencia de mercado competitiva completada.


## 2026-10-21 · P0 FUNCIONAL: entidades de noticias, páginas corporativas y evaluaciones D1 automáticas (0008–0009)

### Construcción integrada en main
- **`tools/news_entity_discovery.py`**: extrae hasta dos términos corporativos potenciales de cada uno de ocho titulares públicos recientes de medios distintos; consulta Wikidata `wbsearchentities` y confirma **clasificación P31 de empresa + etiqueta exacta**, en hasta 16 búsquedas y una obtención de atributos. Sin nombres precargados por ChatGPT. Las relaciones siguen siendo hipótesis hasta leer y contrastar los artículos originales.
- `migrations/0008_news_entities_assessments.sql`, `src/news-entity-ingest.mjs` y `src/worker.js`: guarda entidades sugeridas y sus titulares, fuente Wikidata, posibles dominios oficiales, errores y estado editorial sin aprobar. Ruta OIDC de escritura `POST /api/market/entities/ingest`.
- **`src/market-assessment.mjs`**: evaluador directo del historial REAL en D1, reúne empresas descubiertas Wikimedia y noticias Wikidata, cuenta ventanas Wikipedia, noticias y **regiones YouTube realmente medidas**, escribe snapshots explicables `market_assessment_runs` y `market_assessments` (evaluación diaria idempotente); registra faltantes y bloquea selección/guion/publicación si faltan datos YouTube o fuentes primarias verificadas. Endpoint OIDC `POST /api/market/assess/run` y lectura privada `GET /api/market/opportunities`. No se crea «ganador» ficticio.
- **`tools/market_official_evidence.py`** reutiliza seguridad del descargador del investigador (`fetch_public`, HTTPS, verificación de DNS público y redirecciones, límite de bytes/tiempo). Recupera hasta **3 sitios P856** hallados en Wikidata y conserva URL/resolución, SHA-256 del HTML, cantidad de bloques y enlaces candidatos a documentos. Ningún artículo original, comunicado, derecho o afirmación empresarial se aprueba automáticamente.
- `migrations/0009_official_evidence.sql`, `src/market-official-ingest.mjs`, `tools/push_news_entity_assess.py`: persisten evidencia oficial como **candidata no contrastada** en D1 real por GitHub OIDC efímero; lectura administrativa `GET /api/market/official`.
- Workflow diario `.github/workflows/topic-discovery-smoke.yml`: ahora ejecuta **Wikimedia → RSS → identificación de empresas Wikidata → páginas oficiales seguras → cruce de titulares → YouTube condicional por cuota → evaluación y persistencia de bloqueos**. Se añadieron tests Python/Node y controles de presupuestos. No requiere que ChatGPT introduzca un tema ni escriba un episodio.
- Panel administrativo `public/index.html` y `public/app.js` expone evaluación auditable de oportunidades y lista de fuentes oficiales, con mensajes claros de falta de datos. Los contenidos no se inyectan como HTML.

### Pruebas y producción verificadas
- GitHub CI de nuevas pruebas Python/JS (incluido `test_news_entity_discovery.py`, `test_news_entity_ingest.mjs`, `test_market_assessment.mjs`, `test_market_official_evidence.py` y `test_market_official_ingest.mjs`) resultó `success`; hubo un error de sintaxis inicial en el colector y fue corregido antes de declarar éxito.
- **E2E primera tanda:** [Actions 39676935229](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39676935229), `success` con resolución Wikidata y evaluación D1. Lectura directa posterior: `market_news_entity_runs=1`, **2 relaciones noticia–empresa** (Q482267 América Móvil y Q53268 Toyota), `market_assessment_runs=1`, **4 empresas evaluadas**, `qualified_count=0`, `selected_wikidata_id=NULL`.
- **E2E segunda tanda:** [Actions 39678008994](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39678008994), `success` incluyendo descarga segura de páginas P856 y persistencia por OIDC. D1 confirmó `market_official_source_runs=1`, `market_official_source_items=2` (Toyota: 3 bloques, DuPont: 21 bloques, ambos con hash SHA-256). **0 hechos/propiedad intelectual verificados**. Hay 114 titulares RSS acumulados, 1 trabajo y 8 eventos intactos.
- Cloudflare cuenta Factor, DB `factor-de-gigantes-db`: migrations **0008 y 0009 aplicadas directamente a D1 remota** tras verificar esquema, bookmark Time Travel y exportación SQL temporal. Los trabajos existentes y las señales anteriores se conservaron. Las páginas oficiales y la evaluación **son resultados del sistema, no de generación manual de contenido por ChatGPT**.
- Los `push` temporales usados para dos pruebas integrales se retiraron del workflow **y de la lista de eventos permitidos por el verificador OIDC**. Permanecen `schedule` diario y `workflow_dispatch` manual.
- No se activó facturación ni cuota YouTube; `market_youtube_runs=0` al final de las pruebas, sin estadísticas inventadas. No se ejecutó un render documental final ni publicación.

### Prioridades siguientes, sin reiniciar auditorías
1. **P0 sin resolver:** clave y presupuesto *gratuito autorizado* de YouTube Data API, sin facturación. Conectar muestras reales de videos/canales en regiones hispanohablantes; comprobar que no se agota cuota y no se imprimen secretos. Si falta autorización, seguir otros módulos sin costo.
2. **P0/P1:** usar los documentos P856 recuperados como puertas de investigación, descargar originales oficiales y extraer afirmaciones comprobables con fechas/páginas, cotejar independientemente con medios y reguladores. Actualmente `primary_sources_verified=0`; no activar selección automática todavía.
3. Tras completar evidencia real multifuente, ampliar el evaluador para poder pasar de `awaiting_evidence` a candidatura seleccionable/cola persistente, con auditoría y autorización editorial separada.
4. Integrar `gemini_free` o `qwen_local` investigador y guionista, voz oficial, visuales y MP4 profesional 8–14 minutos; asegurar QA derechos, y solo luego OAuth/publicación aprobada.

**Estado honesto:** P0 ha avanzado en integración y persistencia real. El proyecto total aún está lejos de su final; no se asigna porcentaje inventado ni se confunden dos páginas descargadas con un documental autónomo.
