# Historial de avance — Factor de Gigantes

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
