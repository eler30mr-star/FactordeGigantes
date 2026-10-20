# Despliegue inicial del motor

> No ejecutar hasta haber configurado las cuentas propias. No pegar tokens ni claves dentro del repositorio o del chat.

## 1. Herramientas

Necesitas Node.js reciente, `npm` y `wrangler`. En el repo: `npm install` y `npx wrangler login`.

## 2. Cloudflare D1

1. Ejecutar: `npx wrangler d1 create factor-de-gigantes-db`.
2. Copiar el `database_id` mostrado a `wrangler.jsonc`, reemplazando `REEMPLAZAR_ID_D1`.
3. Ejecutar `npx wrangler d1 migrations apply factor-de-gigantes-db --remote`.
4. Crear secretos distintos y largos: `npx wrangler secret put ADMIN_TOKEN`, `npx wrangler secret put RENDERER_TOKEN`, `npx wrangler secret put GITHUB_DISPATCH_TOKEN`.
5. `GITHUB_DISPATCH_TOKEN` debe ser un fine-grained PAT, limitado a este repositorio, con permisos necesarios para Actions (write) para iniciar el workflow. No usar token de cuenta completo.
6. Desplegar: `npx wrangler deploy`. Anotar URL del Worker.

## 3. GitHub Actions

Agregar en Settings → Secrets and variables → Actions:
- Secret `API_BASE_URL`: URL pública base del Worker (https://...workers.dev o dominio propio, sin barra final).
- Secret `RENDERER_TOKEN`: mismo valor configurado en Cloudflare.

Habilitar Actions del repositorio. La API del Worker dispara `render.yml` en `main`. GitHub tiene límites de minutos incluidos, especialmente para repositorios privados; controlar ejecución y evitar gastar cuotas por trabajos grandes.

## 4. Uso básico

1. Abrir URL del Worker (panel) desde PC o teléfono.
2. Escribir `ADMIN_TOKEN` en el campo de acceso; no queda almacenado en disco o localStorage.
3. Crear trabajo con título, enfoque, **al menos dos fuentes URL https** y entre 2 y 18 segmentos originales.
4. Pasar a revisión, comprobar investigación y aprobar.
5. Hacer clic en «Generar prueba». La acción GitHub produce MP4 descargable en «Actions → Render de prueba»; nunca se sube a YouTube automáticamente.

## 5. Seguridad antes de producción

- Configurar Cloudflare Access en dominio propio y desactivar el subdominio público adicional si se necesita protección adicional. La API está protegida por tokens, pero el HTML público no es secreto.
- Nunca incluir claves OAuth, Google, API de IA ni PAT en frontend, guiones o trazas.
- No habilitar publicación sin revisión legal/editorial, scopes mínimos y revocación de tokens.
- Limitar tamaño y frecuencia de acciones; vigilar facturación y cuotas.
- El primer deploy necesita revisión de las limitaciones vigentes del plan Cloudflare.
- En caso de token filtrado, revocarlo y rotarlo de inmediato.

## 6. Si falla el render

Revisar `.github/workflows/render.yml`, pestaña Actions; comprobar `API_BASE_URL`, `RENDERER_TOKEN`, estados en el panel. Los errores se registran en `jobs.last_error`. No publicar material de demostración.