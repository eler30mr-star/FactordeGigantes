# Factor de Gigantes — sistema de automatización de YouTube

Repositorio oficial: **eler30mr-star/FactordeGigantes** · rama única de trabajo **`main`**.

## Meta

Plataforma propia para gestionar documentales originales en español sobre grandes empresas, innovación, inventos y decisiones históricas. Flujo editorial:

**idea e investigación → guion con fuentes → revisión humana → aprobación → render de previsualización → control de calidad → publicación autorizada en YouTube (fase futura)**.

El sistema NO publica videos automáticamente en esta primera etapa. No está conectado a un canal de YouTube todavía. Esto protege el canal de errores y contenido repetitivo que afecte su monetización.

## Tecnología

- **Cloudflare Workers + D1 + static assets**: panel, API privada, revisión y estados.
- **GitHub Actions**: motor de render activable desde el panel (workflow_dispatch).
- **FFmpeg + Pillow + Piper TTS (voz neuronal local)**: motor de previsualización con movimientos de cámara, subtítulos y ficha técnica. Piper ya está validado en GitHub Actions con WAV y MP4 reales, y ahora es el motor predeterminado del workflow de render.\n- **eSpeak NG**: modo exclusivamente técnico para comparaciones y diagnósticos; la voz no constituye una versión publicable.
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
- `examples/documental.json` — ejemplo técnico, NO un guion publicado.\n- `tools/voice.py` — motor Piper local con checksum de modelo y motor eSpeak técnico.\n- `tools/subtitles.py` — generación de subtítulos SRT aproximados.\n- `.github/workflows/voice-smoke.yml` — prueba auditiva independiente de voz neuronal.\n- `docs/MOTOR_AUDIOVISUAL.md` — licencias, procedencia, mejoras y limitaciones del motor.

## Estado

**Backend técnico conectado y radar real:** Worker y D1 desplegados; base `0001–0004` migrada; el descubridor diario detectó compañías públicas sin lista manual y un workflow autenticado con **GitHub OIDC** confirmó la escritura real de dos empresas y dos series Wikimedia en D1. El panel cuenta con sección privada de radar. El render preliminar está comprobado, pero la investigación competitiva YouTube, elección autónoma fundamentada, documental profesional integral y OAuth/publicación todavía no están terminados. **No hay publicación automática a YouTube**. Ver `docs/AVANCE.md`.

## Límites y costes

Los planes gratuitos tienen cuotas. Renders largos consumen minutos de GitHub Actions, y la base D1/Workers tiene límites. La generación de voz local no requiere una API de pago, pero las licencias de voz/entrenamiento y la investigación y producción cinematográfica con material licenciado todavía requieren evaluación editorial y costes controlados.

La única cuenta de YouTube autorizada para el proyecto debe conectarse mediante OAuth oficial en una etapa posterior; nunca se almacenarán contraseñas de Google.