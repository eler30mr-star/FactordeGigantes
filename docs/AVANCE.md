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
