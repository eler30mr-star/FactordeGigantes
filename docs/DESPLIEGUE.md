# Factor de Gigantes — estado de producción y despliegue

> No ejecutar hasta haber configurado las cuentas propias. No pegar tokens ni claves dentro del repositorio o del chat.

## 1. Herramientas

Necesitas Node.js reciente, `npm` y `wrangler`. En el repo: `npm install` y `npx wrangler login`.

## 2. Cloudflare D1 — COMPLETADO (2026-10-20)

La base real ya existe: `factor-de-gigantes-db`, UUID `ef699e75-b50a-4e28-a665-69316d10cdaf`. Se sustituyó el ID en `wrangler.jsonc` y las tablas `jobs`, `events` y sus índices fueron creadas mediante la API SQL de Cloudflare y verificados posteriormente.

**No crear otra base D1 ni ejecutar manualmente los CREATE TABLE ahora.** La migración SQL se aplicó fuera del mecanismo de historial de Wrangler; el script de migración es idempotente y Wrangler podría registrar su aplicación en un despliegue posterior.

## 2B. Estado de producción — 21 de octubre de 2026 (CONFIRMADO)

- **Cuenta conectada:** `Factor` de Cloudflare, separada de `Primary`. Utilizar siempre esa conexión para este proyecto.
- **Worker:** `factor-de-gigantes`; URL `https://factor-de-gigantes.martin30-eler.workers.dev`.
- **D1 real:** `factor-de-gigantes-db` (`ef699e75-b50a-4e28-a665-69316d10cdaf`), enlazada como `DB` al Worker.
- **Migraciones 0001, 0002, 0003:** tablas e índices de `jobs`, `events`, `editorial_dossiers` y `research_requests` presentes en D1 REMOTA. `0002` y `0003` aplicadas el 2026-10-21 mediante Cloudflare D1 SQL API, con los archivos originales del repo. No hace falta volver a crear estas tablas.
- **Preservación de datos:** antes 1 trabajo + 8 eventos; después 1 trabajo + 8 eventos. Nuevas tablas vacías (0 expedientes, 0 solicitudes). La consulta de claves foráneas no encontró infracciones.
- **Respaldo:** se generó una exportación SQL de `jobs`/`events` en Cloudflare antes de las migraciones, y se registró un bookmark de Time Travel antes de los cambios. **El enlace firmado de la exportación caduca**, y esta acción no constituye un respaldo externo permanente descargado. Confirmar vigencia de Time Travel y efectuar respaldos adicionales antes de migraciones futuras.
- **Secretos existentes:** `ADMIN_TOKEN`, `RENDERER_TOKEN` y `GITHUB_DISPATCH_TOKEN` figuran como `secret_text`. Nunca se leyeron sus valores ni se duplicaron.
- **Despliegue de código:** build de Cloudflare `720b0c1e-b0ac-4dda-92c3-4c7110f8f862` (`success`) desde commit de `main` `ad13c545ec0d61cbc10284987bb01d06a85d7ca7`, ejecutó **21 tests JS, cero fallos**, `npx wrangler deploy` y publicó versión `d6a44edd-1039-405f-ae87-51e64bfddb0e` con 100 % del tráfico. Asset binding, D1 y tres secretos permanecen intactos.

**Importante sobre el historial de migraciones:** 0001–0003 se aplicaron mediante la API SQL remota en lugar del mecanismo de seguimiento de Wrangler; no se creó la tabla `d1_migrations` en ese procedimiento. Los scripts originales usan `IF NOT EXISTS`. Si una migración futura se aplica con `wrangler d1 migrations apply --remote`, consultar su plan y confirmar que cualquier repetición de 0001–0003 sea idempotente. **No copiar de nuevo comandos de creación manual ni restaurar la base a un momento anterior por rutina.**

## 2C. Investigación desde el panel — estado operacional y límites

El Worker desplegado incluye `/api/research` y acceso al editor de expedientes; las tablas D1 necesarias existen. El formulario «Investigar con IA» crea solicitudes solo al recibir confirmación del administrador, usa Qwen local en GitHub Actions y **no** inicia videos, publicaciones ni compras.

El límite de 4 solicitudes por día UTC se aplica con **reserva atómica** en D1 desde la versión de `main` indicada arriba. `research_requests` tiene la restricción `UNIQUE(topic_key,day_utc)`, lo que evita repetir el mismo tema. Ante red incierta se marca `unknown`, sin reintentar automáticamente.

El panel permite ver ejecuciones vinculadas desde GitHub Actions mediante `request_id`; `sent` **no equivale a investigación finalizada**. Los textos del investigador son propuestas sin verificación humana, licencia ni autorización de render/publicación.

**Siguiente verificación real pendiente:** realizar una lectura/autenticación del panel desde el navegador del propietario con `ADMIN_TOKEN` y luego, únicamente con su decisión explícita de investigar un tema, comprobar un `workflow_dispatch` real y sus artefactos. No se ha enviado una investigación pagada o pesada de manera automática durante las migraciones ni pruebas.

## 3. Recuperación o recreación excepcional del Worker

**Esta sección es solo para un escenario de recuperación. El Worker, la D1 y los secretos ya existen: NO crear otro Worker ni otra base.**\n\n1. Cloudflare → Workers & Pages → Create application → Import a repository.
2. Vincular GitHub y seleccionar la cuenta `eler30mr-star`, repositorio `FactordeGigantes`.
3. Proyecto **Worker** (no una página web estática independiente).
4. Nombre exacto del Worker: `factor-de-gigantes` (debe coincidir con `wrangler.jsonc`).
5. Rama de producción: `main`; directorio raíz `/`.
6. Build: `npm install` si se requiere; deploy: `npx wrangler deploy` o `npm run deploy`.
7. Pulsar Deploy y verificar el panel y `/health`. El Worker usará la configuración D1 en `wrangler.jsonc`.
8. Después del deploy, Worker → Settings → Variables and Secrets → Add secret; configurar `ADMIN_TOKEN`, `RENDERER_TOKEN` y `GITHUB_DISPATCH_TOKEN` con valores independientes y largos. `GITHUB_DISPATCH_TOKEN` requiere GitHub fine-grained PAT limitado a este repo y Actions write.

Alternativamente, desde ordenador con Wrangler autenticado, `npm install && npx wrangler deploy` despliega directamente sin integración GitHub.

## 4. GitHub Actions

Los secretos de conexión fueron usados con éxito en la prueba del renderizador. No regenerar ni imprimir valores por rutina. Si se reconstruye el entorno, entonces agregar en Settings → Secrets and variables → Actions:
- Secret `API_BASE_URL`: URL pública base del Worker (https://...workers.dev o dominio propio, sin barra final).
- Secret `RENDERER_TOKEN`: mismo valor configurado en Cloudflare.

Habilitar Actions del repositorio. La API del Worker dispara `render.yml` en `main`. GitHub tiene límites de minutos incluidos, especialmente para repositorios privados; controlar ejecución y evitar gastar cuotas por trabajos grandes.

## 5. Uso básico

1. Abrir URL del Worker (panel) desde PC o teléfono.
2. Escribir `ADMIN_TOKEN` en el campo de acceso; no queda almacenado en disco o localStorage.
3. Crear trabajo con título, enfoque, **al menos dos fuentes URL https** y entre 2 y 18 segmentos originales.
4. En «Fuentes y licencias», abrir el expediente del trabajo y completar sus fuentes documentales, evidencias por afirmación y derechos de todos los recursos audiovisuales usados, incluida la voz. Cada `locator` debe apuntar a una sección/página real y las marcas `verificada` requieren lectura humana de los documentos.
5. Pasar el guion a revisión. El editor debe acreditar la revisión en el expediente usando «Confirmar revisión de hechos y derechos» e identificándose; solo entonces es posible pulsar «Aprobar». Guardar un expediente **no** significa verificarlo.
6. Hacer clic en «Generar prueba». La acción GitHub produce MP4 descargable en «Actions → Render de prueba»; nunca se sube a YouTube automáticamente.

## 6. Seguridad antes de producción

- Configurar Cloudflare Access en dominio propio y desactivar el subdominio público adicional si se necesita protección adicional. La API está protegida por tokens, pero el HTML público no es secreto.
- Nunca incluir claves OAuth, Google, API de IA ni PAT en frontend, guiones o trazas.
- No habilitar publicación sin revisión legal/editorial, scopes mínimos y revocación de tokens.
- Limitar tamaño y frecuencia de acciones; vigilar facturación y cuotas.
- El primer deploy necesita revisión de las limitaciones vigentes del plan Cloudflare.
- En caso de token filtrado, revocarlo y rotarlo de inmediato.

## 7. Si falla el render

Revisar `.github/workflows/render.yml`, pestaña Actions; comprobar `API_BASE_URL`, `RENDERER_TOKEN`, estados en el panel. Los errores se registran en `jobs.last_error`. No publicar material de demostración.