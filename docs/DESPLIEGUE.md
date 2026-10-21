# Despliegue inicial del motor

> No ejecutar hasta haber configurado las cuentas propias. No pegar tokens ni claves dentro del repositorio o del chat.

## 1. Herramientas

Necesitas Node.js reciente, `npm` y `wrangler`. En el repo: `npm install` y `npx wrangler login`.

## 2. Cloudflare D1 — COMPLETADO (2026-10-20)

La base real ya existe: `factor-de-gigantes-db`, UUID `ef699e75-b50a-4e28-a665-69316d10cdaf`. Se sustituyó el ID en `wrangler.jsonc` y las tablas `jobs`, `events` y sus índices fueron creadas mediante la API SQL de Cloudflare y verificados posteriormente.

**No crear otra base D1 ni ejecutar manualmente los CREATE TABLE ahora.** La migración SQL se aplicó fuera del mecanismo de historial de Wrangler; el script de migración es idempotente y Wrangler podría registrar su aplicación en un despliegue posterior.

## 2B. Migración editorial 0002 — PENDIENTE EN D1 REMOTA

La integración del nuevo expediente documental exige `migrations/0002_editorial_dossiers.sql`. El código y la migración se probaron en GitHub Actions **en base local**, pero **no hay confirmación de que esta tabla exista aún en la D1 remota**. Antes de desplegar el nuevo Worker desde `main`:

1. Confirmar estar en la cuenta Cloudflare correcta (base `factor-de-gigantes-db` ya existente). No crear otra base ni copiar un ID diferente.
2. Desde el repositorio actualizado a `main` y con sesión Wrangler autorizada, ejecutar:

```sh
npm install
npx wrangler d1 migrations apply factor-de-gigantes-db --remote
npx wrangler d1 execute factor-de-gigantes-db --remote --command "SELECT name FROM sqlite_master WHERE type='table' AND name='editorial_dossiers';"
```

El segundo comando debe devolver exactamente la tabla `editorial_dossiers`. La primera migración `0001_initial.sql` tiene instrucciones `IF NOT EXISTS`; como se aplicó en su momento fuera del historial de Wrangler, puede ser registrada de nuevo por la herramienta sin borrar los datos. Revisar el mensaje de Wrangler y hacer copia de respaldo antes de operar sobre datos reales.

3. Solo tras verificar la tabla, ejecutar `npx wrangler deploy` o confirmar el build/deploy automático ya configurado.
4. Acceder al panel y probar un expediente `draft → review → acreditación humana → approved` con datos de prueba **sin lanzar render de producción**. Comprobar en `events` los eventos `dossier_saved` y `dossier_attested`, y que las aprobaciones incompletas devuelvan HTTP 409.
5. No crear secretos nuevos ni modificar `GITHUB_DISPATCH_TOKEN` si ya funcionan; nunca imprimir valores.

Si se despliega código nuevo antes de migrar, las rutas editoriales responderán **HTTP 503** con una advertencia explícita, evitando aprobar expedientes sobre tablas ausentes. Esta comprobación no equivale a un despliegue exitoso.

## 3. Crear/importar Worker desde GitHub

1. Cloudflare → Workers & Pages → Create application → Import a repository.
2. Vincular GitHub y seleccionar la cuenta `eler30mr-star`, repositorio `FactordeGigantes`.
3. Proyecto **Worker** (no una página web estática independiente).
4. Nombre exacto del Worker: `factor-de-gigantes` (debe coincidir con `wrangler.jsonc`).
5. Rama de producción: `main`; directorio raíz `/`.
6. Build: `npm install` si se requiere; deploy: `npx wrangler deploy` o `npm run deploy`.
7. Pulsar Deploy y verificar el panel y `/health`. El Worker usará la configuración D1 en `wrangler.jsonc`.
8. Después del deploy, Worker → Settings → Variables and Secrets → Add secret; configurar `ADMIN_TOKEN`, `RENDERER_TOKEN` y `GITHUB_DISPATCH_TOKEN` con valores independientes y largos. `GITHUB_DISPATCH_TOKEN` requiere GitHub fine-grained PAT limitado a este repo y Actions write.

Alternativamente, desde ordenador con Wrangler autenticado, `npm install && npx wrangler deploy` despliega directamente sin integración GitHub.

## 4. GitHub Actions


Agregar en Settings → Secrets and variables → Actions:
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