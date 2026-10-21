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

## 2D. Diagnóstico privado de producción — disponible

La versión Cloudflare `a7695b06-938e-402e-a4ba-809fc2f2ec02`, correspondiente al commit `7ccc9d4e6cf224bbc22333722e0127c1f932b4e6` de `main`, se desplegó mediante build `17eaaf34-42eb-4427-859b-0f0b8d92b262` (`success`). La compilación ejecutó **25 pruebas Node, 0 fallos**, y subió 2 assets actualizados del panel. Se verificó por API que el código desplegado incluye `/api/system/status` y la reserva de cuota atómica de `/api/research`.

Una vez conectado el panel con `ADMIN_TOKEN`, la nueva sección «Estado del sistema» permite consultar mediante `GET /api/system/status` si existen `jobs`, `events`, `editorial_dossiers`, `research_requests` y si se reconoce la configuración del repositorio/token para investigación. El diagnóstico está protegido y solo devuelve **banderas**: no expone valores de secretos, ni llama a GitHub, ni prueba permisos Actions, ni verifica derechos de uso.

**Verificación pendiente con navegador:** probar el acceso autenticado de una sesión real y comprobar que el nuevo panel muestra la información. Las comprobaciones de Cloudflare/API del código y D1 son positivas; no se afirma haber hecho login en nombre del propietario ni haber lanzado IA.

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

## 2E. Radar de mercado en D1 y autorización OIDC (21 de octubre de 2026)

**Producción verificada, no es una maqueta.** Se identificó cuenta Cloudflare **Factor** y base `factor-de-gigantes-db` (`ef699e75-b50a-4e28-a665-69316d10cdaf`). Antes de la migración 0004 se registró un bookmark Time Travel y exportación SQL temporal. Se aplicó el SQL **aditivo** original `migrations/0004_market_intelligence.sql` mediante Cloudflare D1 SQL API y se verificó que las cinco tablas `market_*` existían. Los recuentos existentes no cambiaron: `jobs=1`, `events=8`, `editorial_dossiers=0`, `research_requests=0`.

**Primera escritura integrada real:** ejecución de GitHub Actions [39658991775](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39658991775) con `success`: descubrió entidades de Wikimedia, midió series, guardó snapshot SQLite local y, por primera vez, envió el informe con identidad GitHub OIDC. Verificación posterior directamente en D1 remota: `market_runs=1`, `market_entities=2`, `market_pageview_observations=2`, `market_interest_windows=2`, `market_selection_decisions=0`. Esta es persistencia remota efectiva, no el artefacto de GitHub.

### Seguridad sin secretos compartidos adicionales
- `POST /api/market/ingest`: valida criptográficamente RS256 mediante el JWKS oficial `https://token.actions.githubusercontent.com/.well-known/jwks`, audiencia `factor-de-gigantes-market-v1`, identificador inmutable del repositorio, archivo exacto de workflow, rama `main`, vigencia y evento `schedule` o `workflow_dispatch`. No acepta `ADMIN_TOKEN` ni `RENDERER_TOKEN` como sustitutos.
- `.github/workflows/topic-discovery-smoke.yml`: concede solo `contents: read` e `id-token: write`; ejecuta descubrimiento diario a las 10:17 UTC (según disponibilidad de GitHub Actions) o manual. **El trigger temporal de `push` usado durante la integración fue eliminado** y el verificador OIDC también bloquea `push`.
- `tools/push_market_radar.py`: solicita JWT temporal al proveedor oficial GitHub Actions y llama únicamente al Worker esperado. Nunca imprime JWT ni el token de bootstrap.
- `GET /api/market/radar?limit=30`: lectura protegida por `ADMIN_TOKEN` de empresas, ventanas y corridas, sin publicar ni elegir automáticamente un documental. La sección «Radar de oportunidades» del panel permite ver estos datos una vez autenticado.
- **No configurar `MARKET_INGEST_TOKEN`**: la credencial persistente propuesta originalmente se sustituyó por OIDC. Continúa usando el secreto existente `API_BASE_URL` en GitHub Actions; sin esa URL la corrida falla de manera visible, no simula guardado.

### Alcance y límites
- La lista de empresas proviene de Wikimedia/Wikidata; páginas vistas no son resultados de YouTube, estimaciones de CTR ni evidencia de que un tema sea ganador.
- `market_study_complete=false` y `automatic_publication_allowed=false`. No hay decisión editorial, generación completa del documental ni subida a YouTube.
- Antes de habilitar selección automática: fuentes más recientes, métricas reales de YouTube/competencia, puntuaciones explicables, revisión de fuentes primarias y presupuesto de API.
- La ejecución de prueba no constituye una copia de seguridad permanente de toda D1; conservar política de respaldos y Time Travel antes de futuras migraciones.


## 2F. Radar de inteligencia: entidades, noticias y YouTube (21-10-2026)

**Verificado en Cloudflare Factor:** D1 `ef699e75-b50a-4e28-a665-69316d10cdaf`, migraciones **0001–0007** aplicadas con preservación de los datos existentes. Radar Wikimedia y RSS conectado al workflow diario protegido por GitHub OIDC y persistencia D1. Primera correlación automática comprobada [Actions 39673977211](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39673977211): 2 empresas, 100 noticias examinadas y 0 coincidencias precisas en esa corrida; sin inventar vínculos. El panel muestra secciones Radar, Noticias, Coincidencias y Comparación YouTube tras introducir `ADMIN_TOKEN`.

### Activación futura de YouTube Data API (no configurarla mediante chat)
- El colector `tools/youtube_market_study.py` ya está conectado al workflow y desplegado, pero permanece **inactivo sin autorización**.
- Solo habilitar si el propietario verifica directamente en la consola Google Cloud un proyecto YouTube Data API gratuito sin facturación y decide utilizar su cuota incluida. Guardar la clave **únicamente** como secreto de Actions `YOUTUBE_DATA_API_KEY`. No escribirla en archivos, tickets, mensajes ni logs.
- Añadir la variable del repositorio **`YOUTUBE_MARKET_BUDGET_ENABLED`** con valor `1` solo tras esa verificación y autorización. El workflow requiere **ambos** valores. Con cualquiera ausente, el paso imprime omisión y no consume cuota ni produce observaciones falsas.
- Presupuesto máximo diseñado: **2 compañías seleccionadas por los datos del radar × 2 regiones (MX, ES) = hasta 4 búsquedas `search.list` y 4 llamadas `videos.list`** por corrida; sin paginación. En la cuota publicada el 15-10-2026 cada llamada cuesta 1 unidad; `search.list` pertenece a un bucket separado (límite inicial de 100 llamadas/día), mientras `videos.list` utiliza cuota de otros endpoints. Ver https://developers.google.com/youtube/data/determine_quota_cost. No activar facturación ni ampliaciones de cuota para este proyecto.
- La base almacena videos públicos reales, medianas de vistas por día de antigüedad y canales cuando Google devuelve un ID oficial. Esto **no** permite observar CTR ni retención de canales ajenos, elegir automáticamente un tema sin fuentes primarias, ni realizar publicaciones.
- Para revisar resultados autenticados: `GET /api/market/youtube`, `GET /api/market/cross`; sus endpoints de ingesta requieren OIDC de GitHub Actions del workflow oficial en `main`, nunca el token de render ni el de administración.
- El disparador `push` se habilitó temporalmente para la verificación de extremo a extremo y **fue retirado**; el radar solo funciona diariamente y manualmente.

### Estados que NO deben confundirse
- **Probado:** escritura y lectura D1 de titulares RSS y corrida de cruces, migraciones, CI, Worker/panel desplegados.
- **Pendiente:** muestras YouTube con API real (las tablas se encontraban vacías), verificación de artículos originales, selección fundamentada y producción documental final.
- **No autorizado:** compra de servicios, IA de pago, render/publicación no revisada o OAuth de subida sin aprobación.
