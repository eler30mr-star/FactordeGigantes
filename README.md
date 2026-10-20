# Factor de Gigantes — Motor de producción para YouTube

Sistema propio de creación y revisión de documentales sobre **empresas, inventos, decisiones e innovación**. Repositorio oficial del proyecto, desarrollado **directamente en la rama principal `main`**.

**Estado:** desarrollo inicial. Ninguna integración de YouTube ni producción comercial está configurada todavía.

## Objetivo

Operar desde un panel web en Cloudflare un flujo auditable:
idea → investigación con fuentes → guion original → revisión → autorización → renderizado de video → control de calidad → publicación en YouTube (en una fase posterior y con conexión OAuth autorizada).

**Principios**: originalidad editorial; atribución y licencias de imágenes/audio; fuentes verificadas; sin publicación sin aprobación; secretos fuera de GitHub y del navegador; coste controlado; observabilidad; vídeos largos prioritarios y Shorts complementarios. Los documentos de planificación y avance están en `docs/`.

## Componentes propuestos

- **Cloudflare Worker + D1**: API, panel administrativo, base de datos y aprobaciones.
- **GitHub Actions + FFmpeg**: render de pruebas en runners de GitHub. Archivos de prueba como artefactos de CI.
- **Producción original**: guiones revisados con fuentes y recursos propios/licenciados; voz local preliminar.
- **YouTube**: subida real se implementará en una fase posterior tras configurar OAuth, cuotas y revisiones.

## Primer arranque

El código y las instrucciones operativas se incorporan por etapas. Ver `docs/PLAN_PROYECTO.md` y `docs/AVANCE.md`.

> Este proyecto no pretende garantizar la monetización. YouTube evalúa originalidad, autenticidad y cumplimiento de políticas.
