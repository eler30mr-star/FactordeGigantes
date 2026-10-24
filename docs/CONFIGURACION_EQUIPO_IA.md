# Equipo de investigación — Factor de Gigantes

Implementación por funciones, 2026-10-22. Ninguna respuesta de IA equivale a
fuente primaria, verificación factual, permiso audiovisual o autorización de
guion/publicación. El narrador canónico no cambia.

## Funciones y orden de ejecución

| Componente | Función | Cuándo se ejecuta |
| --- | --- | --- |
| Referencias Wikipedia | Descubrir URLs externas observadas, priorizando autoridades | Una consulta pública por empresa seleccionada; no usa Wikipedia como prueba |
| Tavily | Encontrar documentos originales y contexto | Dos búsquedas básicas, con clave y modalidad gratuita confirmada |
| Exa | Ampliar descubrimiento semántico | Dos búsquedas, sin Contents/Agent/Answer/Monitors, con clave y modalidad gratuita confirmada |
| Cloudflare AI | Clasificar pasajes como documentales, promocionales o inciertos | Una inferencia por binding AI, solo si el modo gratuito fue confirmado en el Worker |
| Qwen3-0.6B local | Extracción preliminar y respaldo del analista | Una inferencia CPU con cuatro pasajes; sin clave ni API pagada |
| Gemini 3.8 Flash | Analista principal del expediente | Una llamada, sin grounding ni herramientas externas cobrables |
| Mistral Small | Alternativa del analista | Solo si Gemini no entrega afirmaciones válidas; modelo/acceso sujetos al plan de la cuenta |
| OpenRouter free | Última alternativa remota | Solo si lo anterior falla; router `openrouter/free`, precio máximo de entrada/salida cero, sin plugins |
| Groq GPT-OSS-120B | Revisar afirmaciones contra los extractos | Una llamada si existen afirmaciones; no usa Browser Search ni Compound |

Si las alternativas remotas no están disponibles, se reutiliza la extracción
Qwen; no se carga un segundo modelo ni se repite su inferencia. La clasificación
es consultiva: no elimina pasajes del manifiesto. La revisión busca contradicción,
falta de contexto y confusión entre acusación/sentencia/opinión, pero **no acredita
corroboración independiente** por sí misma. La calidad del modelo pequeño sigue
sujeta a evaluación; una salida JSON válida no prueba calidad documental.

El recolector descarga como máximo cuatro documentos originales (hasta dos autoridades y dos fuentes de otros dominios cuando ambas clases existen; su independencia requiere revisión; máximo uno por hostname) con el
descargador existente: HTTPS público, DNS y redirecciones controladas, límite
de bytes, extracción HTML o primera docena de páginas PDF (máximo 350 páginas
físicas). Solo admite texto que mencione la entidad seleccionada, conserva hash,
URL, página/bloque y hasta diez pasajes breves. No transforma resúmenes del
buscador en evidencia. No contiene listas fijas de compañías ni URLs inventadas.
Un enlace gubernamental no demuestra que el contenido sea una sentencia ni que
dos comunicados sean fuentes independientes. La lectura de PDF puede ser parcial.

## Configuración segura en GitHub

En el repositorio, Settings → Secrets and variables → Actions → Secrets:

| Secreto | Necesidad |
| --- | --- |
| `TAVILY_API_KEY` | Buscador principal |
| `EXA_API_KEY` | Buscador complementario |
| `GEMINI_API_KEY` | Analista principal |
| `GROQ_API_KEY` | Revisor |
| `MISTRAL_API_KEY` | Alternativa opcional |
| `OPENROUTER_API_KEY` | Alternativa opcional |

No poner claves en issues, logs, archivos, variables públicas ni mensajes.
`YOUTUBE_DATA_API_KEY` sigue siendo independiente y se utiliza solo para medir
mercado YouTube. La conexión existente con Cloudflare no proporciona estas claves.

Para cada cuenta, verificar primero que está en modalidad gratuita, sin
facturación automática ni recarga. Después crear la variable Actions del mismo
proveedor con valor `1`:

```
TAVILY_RESEARCH_FREE_CONFIRMED=1
EXA_RESEARCH_FREE_CONFIRMED=1
GEMINI_RESEARCH_FREE_CONFIRMED=1
GROQ_RESEARCH_FREE_CONFIRMED=1
MISTRAL_RESEARCH_FREE_CONFIRMED=1
OPENROUTER_RESEARCH_FREE_CONFIRMED=1
```

Estas variables son declaraciones del operador; el código no tiene permiso
para auditar la facturación de las cuentas. **Una cuota de llamadas no puede
garantizar costo cero si se conecta por error una cuenta pagada.** Sin clave o
confirmación no hay reserva ni llamada a ese proveedor. No se necesita activar
todos: comenzar con los cuatro primeros; las alternativas son opcionales.

`RESEARCH_PROVIDER` ausente utiliza el equipo. `disabled` impide llamadas de IA
y buscadores autenticados; conserva el descubrimiento público y la evidencia.
`qwen_local` evita las inferencias remotas; los buscadores siguen dependiendo de
sus claves/confirmaciones. El workflow no genera ni publica videos.

## Cloudflare

`wrangler.jsonc` incorpora el binding `AI`, con el modelo fijo
`@cf/meta/llama-3.1-8b-instruct`. **No necesita una nueva clave en GitHub**: el
radar llama a una ruta protegida con su identidad OIDC y el Worker usa el binding.

`CLOUDFLARE_AI_FREE_CONFIRMED` queda en **`0`**. Confirmar el plan gratuito
de la cuenta y luego cambiar a `1` en la configuración versionada del Worker.
Una edición temporal del dashboard puede ser sobrescrita por el próximo despliegue.
No se modifica el plan ni se compra capacidad. La conexión OAuth disponible
rechazó la lectura de suscripciones (403); no se declara el plan verificado.

## Límites del proyecto y auditoría

Migración aditiva `0013_ai_research_team.sql`, sin reconstruir tablas previas.
Cada llamada externa requiere reservar primero en D1. Una única inserción SQL
condicional aplica límites diarios y mensuales, incluso si se repite el workflow.
La reserva es de un solo uso. Un error/timeout consume la reserva por prudencia;
no se vuelve a llamar ni se devuelve capacidad ante resultado ambiguo.

| Proveedor | Máximo diario | Máximo mensual | Máximo por ejecución |
| --- | ---: | ---: | ---: |
| Tavily | 8 | 200 | 2 búsquedas básicas |
| Exa | 4 | 60 | 2 búsquedas |
| Gemini | 4 | 100 | 1 inferencia |
| Groq | 4 | 100 | 1 inferencia |
| Mistral | 2 | 40 | 1 inferencia |
| OpenRouter | 2 | 40 | 1 inferencia |
| Cloudflare | 4 | 100 | 1 clasificación |

Son límites **propios del proyecto en solicitudes**, no la cuota global del
proveedor, ni créditos monetarios/neurones garantizados. Otras aplicaciones con
la misma cuenta pueden consumir cuota. Ante 402/429/432 se detiene ese cliente;
el informe guarda un código seguro, sin cuerpo remoto, clave o URL de petición.
Entradas/salidas tienen presupuesto de texto, sin herramientas cobrables.

Rutas de escritura reservadas al OIDC exacto del radar `main` (manual/programado):

- `POST /api/market/ai-budget/reserve`
- `POST /api/market/ai-classify`
- `POST /api/market/ai-pipeline/ingest`

`GET /api/market/ai-pipeline` es solo administrativo. El panel muestra etapas,
fuentes descargadas, afirmaciones, observaciones del revisor y reservas del mes.
Tokens ADMIN/RENDERER no autorizan las escrituras del radar. La API valida
referencias E###, empresa única, fechas, hashes, categorías y revisiones completas;
calcula alertas de cifras no presentes en los pasajes. Ninguna alerta numérica
es verificación de hechos. Los CHECK SQL mantienen aprobaciones en cero.

Cuando se guardan pasajes de la empresa activa, su cola pasa de
`awaiting_sources` a `researching`. No pasa a aprobada ni se crea un trabajo de video.
El historial del investigador anterior sigue disponible por separado.

## Qué falta demostrar

- Pruebas con transporte simulado no son inferencias reales de proveedores.
- Actualmente el propietario solo ha confirmado la clave YouTube. Los demás
  requieren su configuración segura y una prueba real acotada posterior.
- El pipeline requiere cobertura y corroboración documental suficiente,
  guion original, continuidad vocal larga, derechos y QA audiovisual para
  completar documentales de 8–14 minutos. Esta entrega no acredita esa meta.

## Referencias oficiales consultadas 2026-10-22

- Gemini: https://ai.google.dev/gemini-api/docs/pricing y
  https://ai.google.dev/gemini-api/docs/deprecations
- Tavily: https://docs.tavily.com/documentation/api-credits y
  https://docs.tavily.com/documentation/api-reference/endpoint/search
- Exa: https://exa.ai/pricing y https://exa.ai/docs/reference/search
- Groq: https://console.groq.com/docs/rate-limits y
  https://console.groq.com/docs/structured-outputs
- Mistral: https://docs.mistral.ai/getting-started/quickstarts/studio/activate-and-generate-api-key
- OpenRouter: https://openrouter.ai/docs/guides/routing/routers/free-router
- Cloudflare: https://developers.cloudflare.com/workers-ai/platform/pricing/ y
  https://developers.cloudflare.com/workers-ai/features/json-mode/

Gemini 2.5 tiene acceso restringido a usuarios previos; el adaptador antiguo
conserva compatibilidad pero el nuevo equipo usa 3.8 Flash. No se promete que los
proveedores mantengan las mismas condiciones gratuitas indefinidamente.


## Guion al panel (migración 0014)

Después de aplicar `0014_autonomous_script_drafts.sql` y desplegar el Worker,
activar `AUTONOMOUS_SCRIPT_INGEST_ENABLED=1` en variables Actions. El paso
`tools.push_documentary_draft` usa OIDC, sin claves nuevas. Sólo acepta borradores
trazables de expedientes activos con fuentes suficientes. Trabajo y expediente
quedan pendientes de revisión humana. El mismo artefacto puede reimportarse sin
generar otro guion ni sobrescribir cambios del editor. El render autónomo con
voz canónica y recursos de escena sigue pendiente; estos trabajos están protegidos
frente al renderizador de previsualización.

El cron de las 00:20 UTC sólo reanuda revisión (19:20 America/Lima). El radar
principal mantiene las 10:17 UTC. Las cuotas D1 originales no cambian.
