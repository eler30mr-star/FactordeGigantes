# Factor de Gigantes — sistema de automatización de YouTube

Repositorio oficial: **eler30mr-star/FactordeGigantes** · rama única de trabajo **`main`**.

## Meta

Plataforma propia para gestionar documentales originales en español sobre grandes empresas, innovación, inventos y decisiones históricas. Flujo editorial:

**idea e investigación → guion con fuentes → revisión humana → aprobación → render de previsualización → control de calidad → publicación autorizada en YouTube (fase futura)**.

El sistema NO publica videos automáticamente en esta primera etapa. No está conectado a un canal de YouTube todavía. Esto protege el canal de errores y contenido repetitivo que afecte su monetización.

## Tecnología

- **Cloudflare Workers + D1 + static assets**: panel, API privada, revisión y estados.
- **GitHub Actions**: motor de render activable desde el panel (workflow_dispatch).
- **FFmpeg + Pillow + eSpeak NG**: ensamblado de previsualizaciones originales sin API de pago. eSpeak NG es una voz técnica provisional; no pretende ser la narración final del canal.
- **Sin n8n obligatorio ni máquina local encendida**.

## Archivos clave

- `docs/PLAN_PROYECTO.md` — visión, arquitectura, seguridad, monetización y fases.
- `docs/AVANCE.md` — historial preciso y próximo paso.
- `docs/DESPLIEGUE.md` — configuración manual en Cloudflare y GitHub.
- `src/worker.js` — API Worker.
- `public/` — panel web.
- `migrations/` — modelo de datos D1.
- `.github/workflows/render.yml` — ensamblado de videos.
- `tools/render.py` — motor de video.
- `examples/documental.json` — un ejemplo de prueba, NO un guion publicado.

## Estado

**Primera implementación de ingeniería.** No desplegado ni autenticado con YouTube. Se necesitan cuenta Cloudflare, D1, secretos y pruebas con ejecuciones reales. Consultar `docs/AVANCE.md`.

## Límites y costes

Los planes gratuitos tienen cuotas. Renders largos consumen minutos de GitHub Actions, y la base D1/Workers tiene límites. La generación comercial de video, la voz natural y material documental visual pueden requerir presupuestos y licencias.

La única cuenta de YouTube autorizada para el proyecto debe conectarse mediante OAuth oficial en una etapa posterior; nunca se almacenarán contraseñas de Google.