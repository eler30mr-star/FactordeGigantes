# Montaje completo de Factor de Gigantes

La investigación de desarrollo la prepara Codex por indicación del propietario. Los proveedores de investigación permanecen pausados hasta la prueba final integrada. Este bloque implementa un motor genérico; no acredita todavía un documental narrado aceptado ni operación autónoma completa.

## Material de desarrollo revisable

`research/theranos-development/EPISODIO_DESARROLLO.json` y `GUION_PRUEBA_CITADO.md`: 1.600 palabras, ocho escenas, nueve fuentes consultadas directamente (SEC, Justicia, FDA y análisis contextual). Corte histórico: 7 de diciembre de 2022. La duración estimada es 11:36 a 138 palabras por minuto. Las citas acompañan a cada párrafo; acusación, acuerdo civil y condena no se confunden.

El origen `codex_development_research` identifica esta preparación. No modifica el expediente autónomo D1 ni simula una investigación de Gemini/Groq/Qwen. El mismo contrato acepta un borrador autónomo validado por `tools.episode_package.from_autonomous`, conservando texto, fuentes y huella de evidencias.

## Prueba de montaje sin proveedores

```bash
python -m pip install 'Pillow==11.3.0'
python -m tools.approved_voice --check
python -m tools.episode_render --episode research/theranos-development/EPISODIO_DESARROLLO.json --out dist/theranos-development --technical-test
```

Requiere FFmpeg/FFprobe y fuentes DejaVu. Exporta un MP4 completo con gráficos originales, SRT/VTT, capítulos, fuentes, guion, informe y `REVISAR.html`. El audio es una señal técnica expresamente identificada: **no contiene locución**. QA decodifica el archivo y examina duración, audio y video; no sustituye revisión factual, licencias, audición ni valoración estética.

En GitHub Actions, `development-episode.yml`, modo `technical`, reproduce esta exportación y entrega `fdg-episode-technical-review` durante siete días. No carga modelos ni utiliza claves de búsqueda.

## Prueba final de voz y montaje

El modo `final_ai` requiere `confirm_final_test=true` explícito para esa ejecución, o la habilitación global correspondiente. La confirmación individual no reactiva cron ni proveedores de investigación.

Qwen3-TTS Base 1.7B CPU genera las tomas con la referencia original `assets/voice/approved/narrador_documental_aprobado.mp3`, SHA `78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d`. No hay sustitución por otra voz. El motor aplica la cadencia aprobada, conserva cada carácter y divide las tareas por escena (hasta dos escenas simultáneas).

Cada WAV tiene un checkpoint vinculado al texto, referencia, modelo, cadencia y contenido del audio. `resume_run_id` recupera artefactos del intento anterior y genera sólo tomas faltantes o inválidas. Los artefactos caducados ya no son recuperables. Una ejecución fallida guarda las tomas terminadas; los presupuestos de tiempo y la matriz evitan procesos ilimitados. La velocidad real en CPU y la identidad percibida requieren la prueba final.

Con todas las tomas válidas, el montaje exige duración real de ocho a catorce minutos y QA sobre el MP4. Los subtítulos se ajustan a cada toma; no se declara alineación fonética verificada. Entrega `fdg-episode-narrated-review`, pendiente de audición y revisión humana.

## Panel, seguridad y reintentos

Un trabajo autónomo importado necesita expediente completo, revisión humana y aprobación existentes antes de despachar. El panel llama al workflow canónico, nunca al renderizador de voz alternativo. `RENDERER_TOKEN` permite recuperar sólo el contexto aprobado y reportar el resultado; `ADMIN_TOKEN` no sirve en esas rutas.

El Worker compara la narración con el borrador trazable. Una edición requiere actualizar su trazabilidad. Al recibir un resultado, verifica manifiesto aprobado, referencia, tipo de voz, duración, formato, QA y ausencia de permisos inventados. Una señal técnica no puede marcar el trabajo como documental narrado. El cambio a `ready` y su evento se guardan en una transacción D1, con callbacks idempotentes.

Un fallo conserva el expediente y su aprobación. «Reintentar montaje» recupera el identificador de la ejecución anterior. «Abrir exportación» enlaza únicamente al resultado oficial de Actions del repositorio; no publica contenido. Un timeout de despacho de resultado incierto bloquea la repetición ciega.

No se requiere migración nueva. Las claves no se escriben en paquetes ni checkpoints. La publicación en YouTube, los derechos comerciales y la aprobación editorial continúan separados del éxito técnico.
