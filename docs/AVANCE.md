# Historial de avance — Factor de Gigantes

## 2026-10-20 · Inicio del proyecto

**Repositorio:** https://github.com/eler30mr-star/FactordeGigantes
**Rama obligatoria:** `main`
**Estado global:** fase 1 iniciada; despliegue y conexión al canal pendientes.

### Confirmado
- El repositorio de la cuenta `eler30mr-star` estaba vacío y con `main` como rama predeterminada.
- Se creó README inicial en el primer commit.
- Se diseñaron plan maestro y políticas editoriales.
- Se construyó la base del panel web/Worker/D1 y el renderizador preliminar de videos.
- Se añadió el flujo de CI para validación y el workflow manual para renderizar.

### Limitaciones verificables
- **No hay despliegue Cloudflare confirmado.**
- **No hay conexión OAuth con YouTube ni publicación de videos.**
- **No hay secretos de producción cargados.**
- **No hay prueba de render dentro de GitHub Actions confirmada todavía.**
- Audio e imágenes del render son maquetas técnicas propias, no la calidad final exigida para monetización.

### Próximas tareas prioritarias
1. Ejecutar los tests del workflow en GitHub Actions y corregir cualquier error.
2. Crear D1, configurar `database_id` de Wrangler y aplicar migración.
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

**Siguiente paso exacto:** validar CI/manifest, corregir cualquier fallo, y desplegar Worker/D1 usando los recursos reales de Cloudflare y secretos seguros. Después probar creación → revisión → aprobación → render real → descarga del MP4 y mejorar voz/arte documental.