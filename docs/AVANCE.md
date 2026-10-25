# Historial de avance — Factor de Gigantes

## 2026-10-25 · Publicación inmediata y programación autorizadas implementadas

Se añade al panel el cierre posterior a la subida privada: elegir publicar ahora o programar una fecha UTC, identificar responsable y autorizar explícitamente el SHA exacto del video revisado. Ningún cron, investigación ni callback de subida puede iniciar esta operación. El servidor comprueba revisión completa, archivo, estado privado y canal conectado antes de reservar.

Se verifica la operación en YouTube con lectura posterior. Reservas e identificadores persistentes impiden doble envío; los resultados inciertos se reconcilian consultando sin repetir PUT. Se conserva la configuración editable de estado del video y no se modifica snippet. La autorización y confirmación quedan registradas en eventos.

**OAuth:** documentación oficial `videos.update` exige un scope de edición adicional al de subida. Se implementa ampliación opcional mediante botón y consentimiento Google con `youtube.force-ssl`. Se guardan los scopes realmente devueltos y se rechaza un consentimiento ampliado incompleto conservando la conexión previa. La conexión normal no amplía permisos. El canal real no se ha reconectado ni se han leído credenciales.

**Verificación:** 157 contratos Node aprobados localmente, incluidos siete nuevos de autorización independiente, hash/revisión, publicación inmediata, fecha UTC, preservación de campos, incertidumbre sin reenvío, canal equivocado, roles y consentimiento OAuth ampliado. Google simulado: no se atribuye publicación ni programación real. Sintaxis y YAML correctos.

**D1:** migración aditiva 0020 aplicada y verificada, tabla de publicaciones vacía, exportación existente todavía en `review`, claves foráneas correctas. Ninguna subida, publicación o programación real iniciada.

Operación y referencia oficial en `docs/PUBLICACION_YOUTUBE.md`. CI y despliegue del bloque se verificarán tras el commit. Siguen pendientes aceptación del nuevo flujo con proveedores, calibración del mercado, revisión humana del documental y primer recorrido real de subida/publicación autorizadas. La pausa de IA se conserva.

## 2026-10-25 · Conexión de episodio desplegada y CI final aprobado

Código final `9bf621d` en main; CI `40196188102` aprobado en contratos, cobertura Python, QA audiovisual y smoke. La primera integración `f82bbe6` también pasó CI `40196092277`. Se verificó el código realmente servido por Cloudflare: incluye la tabla de episodios investigados, el control de respuesta de guion repetida y la guarda de confirmación tardía. Deployment `7cddd9c4-b442-4cc0-a10f-09c709895a96`, versión `381b6edc-45ef-4e80-b2a7-eb9a568ec54d`, al 100 %.

La migración 0019 está aplicada. La aceptación local incluye 150 contratos Node y tres pruebas Python nuevas; el test integrado crea guion, trabajo y expediente pendientes sin usar la cola/selección de mercado antigua. No se han invocado proveedores reales ni renderizado otro documental y se mantiene la pausa. El registro posterior de MP4 queda conectado al fin correcto del workflow narrado; su primer recorrido con un nuevo episodio aún debe comprobarse.

**Próximo paso:** aceptación real del nuevo flujo y calibración del mercado cuando se habilite la prueba integrada; después completar publicación/programación con autorización. No confundir esta entrega de integración con aceptación factual, licencia, escucha o publicación del documental.

### Reintentos y confirmaciones tardías

Se refuerza la idempotencia del guardado del guion: repetir la misma respuesta conserva el trabajo existente; otra versión se rechaza sin sobrescribirlo. Una confirmación tardía de despacho no puede reactivar una investigación que ya quedó bloqueada. Regresiones con SQLite y el guion citado real de prueba aprobadas; total local **150 Node**. La aceptación con proveedores reales permanece pendiente y la pausa no cambia.

## 2026-10-25 · Episodio elegido → investigación enfocada → guion para revisión

**Implementación:** el chat y la selección automática calibrada pueden despachar la fase `episode` del workflow existente. La entrada es el episodio D1, con empresa, enfoque y origen, no la cola de mercado antigua. Automático apagado no bloquea las instrucciones manuales; la pausa de IA sí se respeta. Reservas atómicas evitan doble despacho y limitan a cuatro intentos diarios. Un resultado de red incierto bloquea reenvíos hasta revisión de Actions.

El runner comprueba identidad corporativa observada sin adivinar empresas alternativas; ambigüedad o insuficiencia dejan un bloqueo. Las búsquedas documentales, el análisis y el guion conservan el enfoque elegido. Los documentos y llamadas de proveedores comprueban la pausa antes de continuar. No se fabrica puntuación de mercado para una instrucción manual.

**Integración editorial:** investigación persistida y vinculada al episodio; guion válido crea trabajo, expediente y procedencia en una transacción, pendientes de revisión humana. Se reutiliza el motor canónico de render ya existente después de la aprobación correspondiente. Se añade registro por `workflow_run` de exportaciones narradas exitosas de main para que el MP4 terminado llegue al reproductor y a revisión, sin iniciar subida ni publicación.

**Pruebas:** 149 contratos Node aprobados localmente, incluidos seis nuevos: despacho con automático apagado, pausa sin escrituras, concurrencia, incertidumbre, bloqueo/reintento y creación real de borrador editorial con SQLite y guion Python citado. Esta última confirma cero filas de selección/cola de mercado heredada y ninguna aprobación fabricada. Tres pruebas Python nuevas aprobadas: pausa, identidad no ambigua y conservación de empresa/enfoque. Sintaxis y YAML correctos. No se ejecutaron proveedores reales ni se produjo otro video.

**D1:** migración aditiva 0019 aplicada realmente, cero solicitudes nuevas del propietario, trabajo anterior conservado, automático apagado y claves foráneas íntegras. CI y despliegue del código nuevo pendientes de confirmar después del commit.

**Límites:** la pausa de investigadores y la puerta de calibración de mercado siguen vigentes. La ejecución real con proveedores, la calidad del guion/video y la publicación autorizada aún requieren su aceptación integrada; no se declara terminado el proyecto. Ante identidad o fuentes insuficientes se conserva la selección y el informe, sin inventar contenido para renderizar.

## 2026-10-25 · Cierre verificado de despliegue del estudio v2

Código `9bbfbe2`, CI `40195019845` finalizado en success: contratos, cobertura Python, QA audiovisual y smoke de producción aprobados. Cloudflare registra deployment `34ff213b-351d-435f-876e-73932fb5e853`, versión `511416bc-9245-460b-bd38-7ae2e3b3b18c`, al 100 %. Se conserva `FINAL_AI_INTEGRATION_ENABLED=0` y no hay indicador de selector validado. Las migraciones 0017 y 0018 ya están aplicadas; el modo real continúa apagado y no se han creado episodios ni estudios para el propietario.

La prueba real de extracción/reproducción preparada del MP4 pertenece al CI anterior `40193908327`, que verificó ZIP y MP4 de 30.308.212 bytes sin regenerar narración. La aceptación de usuario en navegador y la calibración del mercado con APIs reales no se inventan.

Quedan la conexión de la elección por chat/estudio al pipeline enfocado de investigación, guion y producción; la aceptación integrada de IA cuando corresponda; y el cierre autorizado de publicación/programación. El almacenamiento y la cola del investigador antiguo dependen de la selección de mercado heredada: la siguiente integración debe usar el episodio elegido como fuente de verdad, conservar su enfoque y no fabricar un score de mercado para las instrucciones manuales.

## 2026-10-25 · Reproductor desplegado y estudio YouTube comparativo v2 implementado

**Cierre real del reproductor:** código `ac6a53c`, CI `40193908327` aprobado. El job de contratos recuperó el ZIP existente y el extractor utilizado por el panel confirmó `archive_verified=true`, `video_verified=true`, `video_bytes=30308212`, tipo `video/mp4`, cero modelos generados y sin autorización de publicación. Smoke posterior aprobó archivos servidos y barreras privadas. Cloudflare deployment `3c7e8dbb-749f-4450-85aa-8506f62587be`, versión `3c84607c-8d29-4053-a90c-154affb29d36`. Esto acredita bytes y despliegue; no inventa escucha o aceptación visual humana del documental.

**Nuevo estudio:** búsqueda inicial de YouTube desde tres consultas del nicho, propuestas de dos/tres empresas con IA gratuita reservada en D1, consultas comparativas y referencias de publicaciones habituales de hasta doce canales. No se investigan hechos ni se recogen PDFs de cada candidata. El Worker calcula las puntuaciones desde métricas observadas, devuelve razones y exige dos empresas realmente comparables para elegir. No se confunden visitas por edad con crecimiento, búsquedas regionales con procedencia de espectadores ni muestras con demanda total.

**Calidad y control:** mínimo cuatro videos largos, dos ejemplos recientes, varias consultas y comparación con tres canales con tres referencias cada uno; medianas para evitar que un video excepcional decida. Se documentan criterios, ponderaciones y limitaciones en `docs/ESTUDIO_YOUTUBE.md`. Reservas por día, bloqueo por episodio activo, comprobaciones de modo antes de consultas y antes de guardar; apagado concurrente cancela la elección. Informes incompletos conservan un bloqueo visible y no producen episodio. La fase `opportunity` y horario diario usan este flujo; el radar anterior sigue retirado.

**Estado de activación:** la pausa de investigadores permanece. Además, `YOUTUBE_SELECTOR_VALIDATED` ausente/distinto de 1 conserva los estudios como calibración, sin elegir episodio automáticamente. No se habilita este indicador sin revisar muestras reales. Las pruebas actuales de mercado usan datos simulados; no se declara calibración real ni oportunidad diaria ya operativa.

**D1 remota:** migración aditiva 0018 aplicada y verificada; tabla de estudios vacía, modo apagado/revisión 0, cero infracciones FK. No se ejecutaron proveedores ni se creó un episodio para el propietario.

**Verificación local del bloque:** 143 contratos Node aprobados y cuatro pruebas Python nuevas aprobadas; sintaxis y YAML correctos. Cubren muestras insuficientes, formatos cortos, outlier, duplicados, procedencia, caducidad, reservas diarias, calibración, apagado concurrente y persistencia idempotente. CI y despliegue de este bloque se comprobarán tras publicarlo.

**Pendientes exactos:** calibración real del estudio cuando se habilite la prueba integrada y conectar la selección de ambos modos a investigación enfocada → guion → producción reanudable. El chat todavía registra la elección; no despacha ese recorrido completo. La publicación/programación autorizada sigue pendiente de completar y aceptar. El proyecto no se declara terminado.

## 2026-10-25 · Control persistente habilitado y reproductor privado implementado

**Verificaciones remotas:** CI del primer bloque `e952902`, run `40193057049`, terminó correctamente en contratos, QA audiovisual y smoke. Cloudflare registra despliegue `1d5be723-a461-4ebb-97ed-35e1b676d996`, versión `12a3dcce-5b6b-4364-9fc3-d2dafeb047e8`. Faltaban las tablas de control; se aplicó realmente la migración 0017 con seis sentencias correctas. Consulta posterior confirma modo apagado/revisión 0, cero episodios nuevos, un trabajo y una exportación previos conservados, y claves foráneas sin infracciones. No se modificó la pausa de investigadores.

**Implementación del reproductor:** API de lectura ADMIN entrega por streaming únicamente el artefacto narrado registrado. Comprueba identidad, origen, caducidad, digest y tamaño; no entrega credenciales GitHub ni enlaces firmados al navegador. El cliente valida SHA del ZIP y MP4, extrae solo el video y crea un Blob reproducible con controles, audio y desplazamiento dentro del panel. Se libera al actualizar. Límite explícito de 80 MiB; el archivo actual ocupa 30.308.212 bytes. Los archivos caducados muestran un bloqueo sin regenerar producción. La preparación descarga el paquete antes de reproducir; no es streaming progresivo del MP4 ni almacenamiento permanente.

**Interfaz:** las fuentes, listas históricas y herramientas anteriores quedan en un apartado desplegable; sus consultas se realizan al abrirlo, evitando llenar la portada al conectar. Se conserva la descarga y toda la información previa.

**Pruebas ejecutadas:** 135 contratos Node locales correctos, incluidos siete nuevos de ZIP almacenado/deflactado, integridad, caducidad, origen, streaming incompleto, roles y montaje/liberación del reproductor. Sintaxis y YAML correctos. Se añade aceptación en CI marcada `[preview-e2e]` para recuperar el artefacto real existente y verificarlo con el mismo extractor, sin IA ni render nuevos. Su resultado y el despliegue de este bloque se registrarán después de confirmarlos; no se atribuye todavía reproducción observada en navegador.

**Siguiente bloque:** estudio comparativo YouTube y conexión del episodio a la investigación enfocada. El chat actual guarda la elección; no se declara aún cadena autónoma terminada ni autorización de publicación.

## 2026-10-25 · Primer bloque implementado: control del canal y selección por chat

**Implementación en main:** API ADMIN de estado, cambio de modo y chat; migración aditiva `0017_channel_control.sql`; botón automático encendido/apagado y conversación en el panel. El modo es persistente por canal, apagado por defecto, con revisión condicional y registro de actor autenticado. Las instrucciones explícitas seleccionan empresa y tema; las ambiguas abren un diálogo breve persistente. Reintentos conservan identificador y no duplican episodios. Un episodio activo no se reemplaza silenciosamente.

El selector anterior deja de estar disponible por API. Se añade preflight OIDC al workflow de descubrimiento antes de cualquier recolección: apagado bloquea el inicio; el colector antiguo permanece retirado incluso si se solicita encendido. **El nuevo estudio comparativo YouTube todavía no está implementado**: encendido expresa el modo guardado y muestra un bloqueo concreto, sin elegir arbitrariamente ni activar el radar Wikimedia anterior.

**Estado del chat:** guarda una selección real de episodio con origen chat. La interpretación inicial es conservadora y no invoca un LLM; pide empresa/enfoque cuando faltan. **No despacha aún investigación ni producción**. La respuesta lo declara y conserva la pausa de investigadores. No confundir registro de la instrucción con video generado.

**Verificación local realizada:** 128 contratos Node aprobados (119 existentes y 9 nuevos con SQLite real, API y eventos del panel); cuatro pruebas Python del preflight aprobadas; sintaxis de Worker, app y módulos nuevos correcta; YAML de ambos workflows parseado. Node se ejecutó con `--test-isolation=none` por las restricciones del proceso hijo del entorno. No se ejecutó la suite Python audiovisual completa, que no cambia. La primera comprobación ampliada requirió recuperar el fixture existente de Theranos; tras recuperarlo pasan todos los contratos Node.

**Infraestructura consultada:** D1 remota y binding del Worker corresponden a `ef699e75-b50a-4e28-a665-69316d10cdaf`; la pausa remota sigue en 0. No se leyeron secretos. **Migración remota y despliegue pendientes**: la conexión GitHub funciona, pero Git por terminal falla al conectar al proxy; un intento posterior de acceso de red quedó bloqueado y fue interrumpido por el usuario. No se alteraron datos ni modo reales del propietario, no se invocaron investigadores ni se publicaron videos.

**Siguiente paso exacto:** aplicar/verificar migración 0017 y desplegar este bloque; aceptar el botón y el chat en el panel real. A continuación implementar el estudio comparativo YouTube y conectar el episodio elegido al investigador, respetando habilitación vigente. El reproductor embebido y la producción integrada siguen pendientes. P0/P1 han comenzado; no se declaran completos.

## 2026-10-25 · Estudio de mercado exigente y control automático encendido/apagado

**Instrucción del propietario:** la selección de tema y empresa debe surgir de un estudio de mercado bien hecho, nunca de elegir por elegir. El panel tendrá botón automático encendido/apagado; apagado, el propietario da los temas y empresas que deben investigar las IA.

**Actualización documental:** el plan incorpora comparación de alternativas YouTube, contexto por canal/edad/formato, actualidad y saturación, criterios versionados y mínimos de suficiencia que deben validarse antes de activar el selector. La decisión explica evidencias y descartes; sin evidencia suficiente no hay selección. También especifica persistencia por canal del modo, guardas en servidor/cron/colas, carreras al apagar y continuidad de episodios manuales. P0 y P1 incluyen estos requisitos.

**Próximas tareas prioritarias:** implementar primero modo persistente y contrato de episodio con pruebas de apagado/cron/chat, estudio de mercado y selección antes de investigación; después panel y reproductor. Estas precisiones complementan P0–P3 de la entrada anterior. El modo apagado no significa desactivar IA: investiga y produce lo pedido por chat. La publicación sigue requiriendo autorización.

**Verificación y alcance:** revisión de plan y avance actuales en main y conservación del historial. Solo documentación; sin pruebas de aplicación, despliegue, cambio real de modo, llamadas IA ni publicaciones. Los criterios se registran como pendientes, no implementados. La pausa previa se conserva. Base: `e94cf55d38555031471dcc66190fe00cefab2449`.

## 2026-10-25 · Dirección corregida por el propietario: automatización del canal

**Alcance de esta entrega:** actualización documental en `main`. El propietario rechaza recopilar e investigar muchas empresas antes de seleccionar el video. Exige búsqueda diaria orientada a oportunidades YouTube del nicho conocido → selección de un tema y una empresa → investigación del elegido → producción → reproducción del video en el panel → publicación autorizada. Añade un segundo inicio por chat, indicando él mismo tema y empresa, que converge en el mismo flujo.

### Cambios realizados

- Se reorganiza `docs/PLAN_PROYECTO.md` con una dirección vigente al inicio, criterios de aceptación y prioridades P0–P3. El plan previo se conserva íntegro en un anexo identificado como histórico, con su encabezado adaptado.
- Se distingue comparación acotada de candidatos de investigación profunda: esta última solo comienza después de elegir el episodio.
- Se especifican chat operativo y reproductor embebido de MP4 real; descarga/Actions no cumplen el requisito de visualizar el video.
- Se define la publicación/programación del canal como parte del objetivo final y se mantiene autorización humana, licencias, voz canónica y cero pagos.
- Esta entrada fija las próximas prioridades sin borrar el historial técnico ni atribuir funcionalidades nuevas al código existente.

### Verificación y límites de esta entrega

Lectura por conexión GitHub de AGENTS, plan, avance, panel y rutas relevantes; comparación con las instrucciones actuales del propietario. Revisión documental del orden de etapas y de que los criterios nuevos permanecen pendientes. Conservación del cuerpo anterior del plan y del avance comprobada al construir los reemplazos. Commit base revisado: `ca0611b53d500ee0ada88893a5a1162103100d5b`.

No se ejecutan suites de aplicación por ser cambios de documentación; no se modifica código, cron, D1, secretos, despliegues ni se lanzan investigadores, renders o publicaciones. Los resultados de CI y despliegue del historial pertenecen a entregas anteriores. La pausa de investigación continúa vigente. Esta actualización no demuestra el funcionamiento del flujo corregido.

### Próximas tareas prioritarias — vigentes

1. **P0:** búsqueda YouTube del nicho → selección persistente única → investigación solo del elegido; chat como entrada alternativa, misma orquestación y prevención de duplicados.
2. **P1:** portada centrada en episodio/chat/avance y reproducción del MP4 dentro del panel, con entrega autenticada y manejo de caducidad.
3. **P2:** integrar y aceptar el recorrido real de las IA para ambos inicios, con reanudación y presupuestos; habilitación de investigadores según autorización vigente.
4. **P3:** publicación/programación autorizada y confirmada en YouTube; aprendizaje con métricas propias disponibles.

**Siguiente paso exacto:** implementar el contrato de episodio y las dos entradas del P0 con pruebas del orden de llamadas que impidan investigación antes de selección. No ampliar la recolección de datos como sustituto de ese bloque.

## Historial previo a la corrección de dirección

Las menciones a «próximo paso», «prioridad» o «bloque actual» que siguen se conservan como registro de su fecha. Para continuar, rigen las prioridades vigentes de arriba y el plan actualizado.

> **Estado técnico registrado antes de la corrección de dirección, 2026-10-25:** documental de desarrollo **narrado completo**, 11:11, ocho escenas y 56 tomas Qwen CPU; montaje y QA reales aprobados. [Descargar video, guion, fuentes y subtítulos](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40163555937/artifacts/12588892336). Panel con avance/descargas y conexión OAuth desplegados; CI de código `42fb42469c49dafcecd73b2a1bb524f56f2792d6` aprobado (112 Node y cobertura Python/FFmpeg). Material investigado directamente por Codex, no resultado autónomo del equipo investigador. Investigación pausada; audición, aceptación profesional y derechos comerciales pendientes. El canal Factor de Gigantes ya está conectado por OAuth; el subidor privado y su revisión final ya están desplegados, con el episodio registrado y la primera subida real pendiente de autorización por episodio. **El proyecto completo aún no está terminado y no se ha publicado en YouTube.**


> **Estado histórico 2026-10-22:** `main` incluye radar YouTube real y selección D1, investigación Qwen/Gemini/Groq E2E confirmada previamente, pero Theranos mantiene 7 afirmaciones no contrastadas de una sola noticia y cola `awaiting_sources`. **Bloque actual:** ampliación real de fuentes públicas (Wikimedia + GDELT sin clave + Tavily/Exa opcionales), 8 intentos acotados, historial D1 de hasta cinco rondas, reutilización solo ante evidencia nueva y omisión de IA si el documento no cambió. CI antiguo falló por expectativas del límite de 4 y el orden antiguo; tests corregidos en `main`, CI/E2E del HEAD aún por confirmar. Guion y publicación no autorizados.

## 2026-10-20 · Inicio del proyecto

**Repositorio:** https://github.com/eler30mr-star/FactordeGigantes
**Rama obligatoria:** `main`
**Estado global:** fase 1; D1 real configurada y esquema inicial aplicado; despliegue Worker y conexión al canal pendientes.

### Confirmado
- El repositorio de la cuenta `eler30mr-star` estaba vacío y con `main` como rama predeterminada.
- Se creó README inicial en el primer commit.
- Se diseñaron plan maestro y políticas editoriales.
- Se construyó la base del panel web/Worker/D1 y el renderizador preliminar de videos.
- Se añadió el flujo de CI para validación y el workflow manual para renderizar.

### Limitaciones verificables
- **D1 existe y sus tablas fueron verificadas directamente en Cloudflare.**
- **No hay despliegue del Worker confirmado.**
- **No hay conexión OAuth con YouTube ni publicación de videos.**
- **No hay secretos de producción cargados.**
- **No hay prueba de render dentro de GitHub Actions confirmada todavía.**
- Audio e imágenes del render son maquetas técnicas propias, no la calidad final exigida para monetización.

### Próximas tareas prioritarias
1. Ejecutar los tests del workflow en GitHub Actions y corregir cualquier error.
2. [HECHO] D1 creada, `database_id` conectado en `wrangler.jsonc` y esquema inicial aplicado mediante Cloudflare API. Confirmadas las tablas `jobs` y `events` y sus índices.
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

**Siguiente paso exacto:** crear/importar Worker `factor-de-gigantes` desde `eler30mr-star/FactordeGigantes`, rama `main`; validar CI/manifest y el despliegue, configurar secretos y ejecutar creación → revisión → aprobación → render real → descarga del MP4. Mejorar la producción documental profesional después. Después probar creación → revisión → aprobación → render real → descarga del MP4 y mejorar voz/arte documental.

## 2026-10-20 · Base Cloudflare D1 conectada
- Captura del panel del usuario y lectura autenticada de Cloudflare confirmaron la base `factor-de-gigantes-db`, UUID `ef699e75-b50a-4e28-a665-69316d10cdaf` en la cuenta de Cloudflare correspondiente.
- Se actualizó en `main` el archivo `wrangler.jsonc` con el identificador real. Commit: `8e6d1e3b1e03ce07e97586a49eb15201a0c64379`.
- Se aplicó mediante la API D1 el contenido del esquema de `migrations/0001_initial.sql` (4 sentencias: tablas `jobs` y `events`, 2 índices). La API devolvió éxito.
- Segunda consulta independiente confirmó dos tablas de aplicación: `jobs`, `events`, y sus índices. La tabla `_cf_KV` es interna de D1.
- La migración se ejecutó por API SQL y **no** por el mecanismo de historial de migraciones de Wrangler; el archivo inicial es idempotente y no debe ser modificado retroactivamente.
- **Pendiente**: crear/importar Worker, desplegar, configurar secretos y realizar una prueba funcional real. No se ha publicado ningún video.

## 2026-10-20 · Worker desplegado en Cloudflare
- Cuenta Cloudflare y servicio verificados por API: Worker `factor-de-gigantes`, despliegue `31099688-495e-4c96-87ac-3290a965198b` creado a las 16:41:44 UTC; 100 % del tráfico asignado a la versión desplegada.
- Asset binding `ASSETS` presente: panel estático incluido en el servicio.
- Binding `DB` apunta a la D1 real `ef699e75-b50a-4e28-a665-69316d10cdaf`.
- Variables `GITHUB_REPO=eler30mr-star/FactordeGigantes` y `GITHUB_WORKFLOW=render.yml` verificadas.
- Subdominio workers.dev habilitado; dirección prevista `https://factor-de-gigantes.martin30-eler.workers.dev`.
- Consulta de secretos devolvió lista vacía: `ADMIN_TOKEN`, `RENDERER_TOKEN`, `GITHUB_DISPATCH_TOKEN` todavía **NO configurados**.
- La URL /health y el panel **no pudieron probarse desde el entorno de verificación externo**; confirmar respuesta HTTP real desde navegador del propietario.
- **Siguiente paso:** configurar secretos seguros (sin publicarlos en GitHub), verificar /health, acceso autenticado a /api/jobs, posteriormente conectar Workflow GitHub Actions y probar render.

## 2026-10-20 · Inicio de autenticación administrativa
- Verificación autenticada de Cloudflare confirmó que existe un secreto llamado `ADMIN_TOKEN`, enlazado a `factor-de-gigantes` como `secret_text`, sin exponer su valor.
- La consulta de bindings confirmó que el Worker continúa enlazado a la base D1 correcta.
- `RENDERER_TOKEN` y `GITHUB_DISPATCH_TOKEN` aún no existen en el Worker.
- Pendiente comprobar que el `ADMIN_TOKEN` tiene al menos 24 caracteres (requisito del código) y que el panel acepta la autenticación; la API de Cloudflare no devuelve valores de secretos.
- Siguiente acción: agregar `RENDERER_TOKEN` fuerte en Cloudflare y el mismo valor en GitHub Actions Secrets; configurar después el token de despacho limitado al repositorio, probar acceso y render.

## 2026-10-20 · Panel web abierto por el propietario
- El propietario confirmó que la URL del panel se abrió en su navegador.
- Esa confirmación acredita acceso a la página, **no confirma por sí sola** que la autenticación de `ADMIN_TOKEN` o la creación de trabajos se haya probado.
- GitHub Actions aún requiere `RENDERER_TOKEN` en ambos servicios y `API_BASE_URL` en GitHub; el despacho requiere `GITHUB_DISPATCH_TOKEN` en Cloudflare. No se han guardado secretos en el repositorio.
- Próximo paso: comprobar que el botón «Conectar» muestra «Nuevo documental», luego configurar secretos compartidos y ejecutar una prueba de render.

## 2026-10-20 · Secreto RENDERER_TOKEN confirmado en Cloudflare
- La API de Cloudflare confirma `RENDERER_TOKEN` como `secret_text` vinculado al Worker `factor-de-gigantes`, junto con `ADMIN_TOKEN`, `ASSETS` y D1.
- El usuario comunicó que había creado el secreto solicitado. **No se puede comprobar desde el conector disponible que el mismo valor esté en GitHub Actions; verificarlo en primera prueba.**
- Quedan pendientes: en GitHub Actions, `API_BASE_URL` con el origen Worker; en Cloudflare, `GITHUB_DISPATCH_TOKEN` como secreto con PAT fino limitado a Actions write para el repositorio.
- Después realizar prueba de extremo a extremo, validando estado y artefacto MP4. Ni render real ni subida a YouTube están confirmados aún.

## 2026-10-20 · Verificación posterior a la configuración de tokens

- El usuario indicó que concluyó la configuración de los valores solicitados.
- Consulta autenticada a Cloudflare: existen `ADMIN_TOKEN` y `RENDERER_TOKEN`, ambos como `secret_text`, y D1 sigue vinculada al Worker.
- **`GITHUB_DISPATCH_TOKEN` aún NO figura en la lista de secretos del Worker**: no está completada la conexión de despacho desde el panel hasta GitHub Actions, aunque el token personal se haya generado en GitHub.
- Se verificó que el repositorio contiene `.github/workflows/render.yml` y `.github/workflows/check.yml`. El flujo `render.yml` necesita `API_BASE_URL` y `RENDERER_TOKEN` como secretos de Actions, cuyos valores o existencia no puede comprobar el conector GitHub actualmente.
- Siguiente paso **inmediato**: guardar el PAT de GitHub como secreto `GITHUB_DISPATCH_TOKEN` en `factor-de-gigantes` (Cloudflare → Settings → Variables and Secrets, tipo Secret). Luego confirmar por API y ejecutar prueba controlada de render desde el panel.
- No se ha creado ni publicado ningún video en YouTube en esta etapa.

## 2026-10-20 · Los tres secretos del Worker confirmados
- Verificación autenticada de Cloudflare: `ADMIN_TOKEN`, `RENDERER_TOKEN` y `GITHUB_DISPATCH_TOKEN` están presentes como `secret_text` en `factor-de-gigantes`.
- El Worker conserva `ASSETS`, binding D1 `DB` y variables `GITHUB_REPO`, `GITHUB_WORKFLOW`. Último despliegue observado: 2026-10-20 17:07:07 UTC.
- No se han leído ni almacenado los valores de esos secretos.
- **Próximo paso verificable:** comprobar en GitHub Actions (Settings → Secrets and variables → Actions) que existen `RENDERER_TOKEN` y `API_BASE_URL` (mismo `RENDERER_TOKEN` que Cloudflare; URL del Worker sin barra final). El conector disponible no ofrece lectura del listado de secretos del repositorio.
- Después crear un guion de prueba con fuentes, revisarlo y aprobarlo expresamente desde el panel; usar «Generar prueba» para comprobar despacho, MP4 y reporte de estado. Sin publicación a YouTube.

## 2026-10-20 · Primera prueba preparada, sin ejecución
- El usuario confirmó que agregó el secreto `RENDERER_TOKEN` en GitHub Actions; el conector GitHub no ofrece listar secretos, así que su existencia y coincidencia de valores están reportados por el propietario, no verificados mediante API.
- Consulta autenticada confirmó que Cloudflare mantiene los tres secretos: `ADMIN_TOKEN`, `RENDERER_TOKEN`, `GITHUB_DISPATCH_TOKEN`.
- Se creó un **borrador técnico** directamente en la D1 real, sin aprobación ni ejecución, para comprobar el recorrido del panel. ID: `30eceeae-70b5-315a-1bc1-d5e0d4185421`, título: `Demostración técnica del motor Factor de Gigantes`, formato `short`, 3 segmentos de prueba. Se registró el evento `created`.
- La entrada usa el guion de ejemplo `examples/documental.json`. Sus URLs son ejemplos de fuentes, no un trabajo de investigación confirmado. **No publicar este material en YouTube.**
- El propietario debe autenticar el panel, actualizar la lista, pasar el trabajo a revisión, confirmar su carácter de prueba técnica, aprobarlo, y pulsar «Generar prueba» para activar GitHub Actions.
- El éxito de la creación de MP4, entrega del artefacto y reporte `ready` **NO** está verificado aún.

## 2026-10-20 · Rechazo GitHub HTTP 403 al solicitar render
- El propietario intentó renderizar desde el panel y reportó el mensaje `GitHub rechazó el render (HTTP 403)`.
- La D1 fue consultada después: trabajo `30eceeae-70b5-315a-1bc1-d5e0d4185421` sigue en estado `approved`, no se despachó ni perdió.
- Se comprobó que `eler30mr-star/FactordeGigantes` tiene rama `main` y la conexión GitHub propietaria posee permiso admin; el workflow `render.yml` existe y declara `workflow_dispatch`. El permiso requerido por la API GitHub para ese endpoint es `Actions: write` sobre el repo. **No se conoce todavía la configuración del fine-grained PAT guardado como `GITHUB_DISPATCH_TOKEN`.**
- Se modificó `src/worker.js` en `main`, commit `a69ec4315463f807f30834cb5564e63ce11796df`, para clasificar las causas comunes de respuestas GitHub 403/401 sin incluir secretos en la salida. La sintaxis del JS modificado se validó con compilación aislada.
- La API Cloudflare confirmó un nuevo despliegue y que el código activo incluye el diagnóstico mejorado; también conservó los tres secretos.
- Siguiente paso: reintentar **una sola vez** «Generar prueba», observar el mensaje exacto si persiste y comprobar/revisar en GitHub los permisos del fine-grained PAT (resource owner `eler30mr-star`, repo `FactordeGigantes`, `Actions: Read and write`). No modificar `RENDERER_TOKEN` ni `API_BASE_URL` por este error.
- **Sin MP4 producido ni publicación YouTube hasta confirmar workflow.**

## 2026-10-20 · HTTP 403 persiste y CI comprobada
- El usuario confirmó que sigue viendo «GitHub rechazó el render (HTTP 403)» y preguntó si debía llenar el formulario de un nuevo documental. Se aclaró que **no**: existe un trabajo aprobado y el formulario es solo para trabajos nuevos.
- Lectura de GitHub Actions autenticada: se encontraron 19 ejecuciones del workflow «Comprobar base» y las más recientes finalizaron en `success`; no existe ninguna ejecución con `event=workflow_dispatch` al momento de revisar. Esto demuestra que el motor no ha arrancado, mientras que el CI básico sí se ejecuta.
- Pendiente: corregir `GITHUB_DISPATCH_TOKEN` (token PAT fine-grained: propietario `eler30mr-star`, acceso específico al repositorio, permiso `Actions: Read and write`, no caducado) y probar nuevo despacho sobre el trabajo aprobado.

## 2026-10-20 · Primer dispatch real y diagnóstico de HTTP 403 de retorno
- Tras corregir el PAT `GITHUB_DISPATCH_TOKEN` (se había elegido Contents en lugar de Actions), el propietario pulsó «Generar prueba» y GitHub aceptó el dispatch. Run **39468744180** del workflow `render.yml`.
- El primer run real **falló**: FFmpeg, eSpeak NG y Pillow se instalaron bien, pero `tools/render.py` recibió `urllib.error.HTTPError: HTTP Error 403` al solicitar el guion al Worker. El callback `tools/report.py` también recibió 403, y **no se generó MP4** ni artefacto.
- La base D1 quedó indebidamente en `queued` porque el callback falló. Tras verificar que la ejecución GitHub había finalizado con `failure`, se restableció de `queued` a `approved` conservando la revisión humana; evento `render_retry_prepared` y detalle del fallo. **No se lanzó otro render automáticamente**.
- Se reforzó `tools/render.py` en `main`, commit `3339e96ba12e629627c41f18dbf05e40cb86701b`: prueba pública `/health`, validación del producto, `User-Agent` explícito y clasificación segura de HTTP 401/403.
- Se agregó diagnóstico no bloqueante en `.github/workflows/check.yml`, commits `02e9b4f244b4a86e264acc5a1356cec87462ba65` y `b7ca7f0f2100ec2dd43c50ee3013d025e687c870`.
- **CI real comprobado en GitHub**: run 39469467971 confirmó dominio exacto `factor-de-gigantes.martin30-eler.workers.dev`, HTTP 200 en `/health` y producto esperado. Run 39469645669 confirmó que `RENDERER_TOKEN` del repositorio es válido: GET autenticado de UUID inexistente respondió HTTP 404 esperado, JSON del Worker. Los tests y sintaxis de `check.yml` también concluyeron en success.
- Se cambió además `tools/report.py` para enviar la misma identidad HTTP del renderizador, commit `31455380fcc73bd391aebf7d9da079fef844ed89`.
- **Hipótesis, no hecho confirmado:** el 403 inicial al acceder al Worker pudo relacionarse con el User-Agent predeterminado de Python; los nuevos pasos confirman acceso válido al Worker usando User-Agent específico, pero falta probar el guion real `queued` y el reporte `ready`.
- Próxima acción: el propietario debe pulsar **una vez** «Generar prueba» en el trabajo ya `approved`; revisar GitHub Actions, artefacto MP4 y estado D1. Publicación YouTube no implementada.

## 2026-10-20 · Primera generación MP4 completada de extremo a extremo
- **Run GitHub Actions 39471906672:** `render.yml` finalizó `success` en `main` para el trabajo `30eceeae-70b5-315a-1bc1-d5e0d4185421`; todas las etapas de generación, carga del artefacto y reporte al Worker pasaron.
- El artefacto `vista-previa-30eceeae-70b5-315a-1bc1-d5e0d4185421` quedó cargado como ZIP (artifact ID `12287965396`). URL: https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39471906672/artifacts/12287965396 .
- En los logs: tres escenas renderizadas con duraciones estimadas 8,5 s; 9,0 s; 8,9 s. El proceso informó salida `dist/video.mp4` de 1.086.696 bytes.
- Se descargó el ZIP y se inspeccionó el MP4 con `ffprobe`: formato vertical **720×1280**, H.264 + AAC, **25,821451 s**, **1.086.696 bytes**. Es un archivo existente, no solo estado de workflow.
- La API D1 devolvió el trabajo en estado **`ready`**, `last_error` vacío. GitHub Actions registró `Estado reportado: ready 200`.
- Primer circuito funcional confirmado: panel de aprobación → Cloudflare Worker → GitHub Actions → FFmpeg → artefacto descargable → reporte al Worker/D1.
- **Este es un render técnico de prueba, no material documental profesional ni apto para publicarse en YouTube**. Usa tarjetas originales y narración local eSpeak; no hay voz natural premium, montaje cinematográfico, assets audiovisuales licenciados, subtítulos editoriales ni subida OAuth.
- Siguiente fase: revisar visualmente y auditivamente la previsualización, mejorar calidad audiovisual, estructura documental, documentación de fuentes, UX de descarga desde el panel, y posteriormente solo si se solicita implementar subida privada a YouTube.

## 2026-10-20 · Avance motor audiovisual gratuito Piper v0.2
- Implementados y guardados en `main` los módulos `tools/voice.py` (Piper local con verificación SHA-256 del ONNX) y `tools/subtitles.py` (SRT por duración de escena, alineación aproximada).
- Integrado en `tools/render.py` movimiento de cámara Ken Burns, subtítulos incrustados, SRT externo, fichero `ficha.json`, créditos/licencias y control `ffprobe` sobre dimensiones, audio/video, duración y tamaño.
- `.github/workflows/voice-smoke.yml` instala Piper 1.8.0, recupera/cacha la voz `es_MX-ald-medium`, genera audio WAV real, renderiza un MP4 de prueba con Piper y publica artefactos temporales; las pruebas unitarias se añadieron a `tests/test_voice_subtitles.py`.
- **Ejecución real GitHub Actions 39476712983: success**. Instalación, descarga y checksum de la voz y síntesis WAV sin API de pago confirmadas.
- **Ejecución real 39477025112: success**. Primer MP4 v0.2 completo con voz Piper, subtítulos y artefactos; una inspección visual posterior detectó subtítulos desproporcionados que cubrían la escena. No se declaró suficiente.
- Se corrigieron tamaño, posición, estilo de fondo y longitud de línea de subtítulos (`tools/render.py`, `tools/subtitles.py`). **Ejecución real 39477498852: success**: MP4 v0.2 renderizado, comprobaciones de voz, metadatos y SRT superadas. Fotograma del minuto 0:09 inspeccionado visualmente; subtítulos ahora están en la franja inferior sin ocultar títulos.
- Artefacto de prueba visual: https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39477498852 ; el MP4 fue descargado e inspeccionado con FFprobe: **26,791667 s, 720×1280, H.264 y AAC, 845009 bytes**. `check.yml` en la misma revisión: run 39477499038, `success`.
- El workflow principal `render.yml` ahora instala Piper con caché e invoca `--voice-engine piper --captions burn`, entregando MP4/SRT/ficha/créditos. El **workflow remoto v0.2 con trabajo D1 nuevo todavía no se ha ejecutado**; su funcionamiento se infiere de componentes aislados, no debe marcarse como probado de extremo a extremo para la versión nueva.
- Licencias: Piper 1.8.0 (GPL-3.0-or-later). El MODEL_CARD `es_MX-ald-medium` describe dataset Unlicense y afinación desde otro modelo de voz: **pendiente auditoría de derechos derivados antes de distribuir material comercial**. No hubo subida a YouTube.
- **Siguiente entrega:** incorporar recursos visuales documentales originales/licenciados con procedencia por escena y mejorar el guion de investigación; luego pruebas de render largo y subtítulos con alineación precisa, y sólo al final OAuth subida privada.

## 2026-10-20 · Evaluación comparativa de identidad vocal

- Comentario editorial del propietario: el estilo de Piper actual se percibe demasiado parecido a un canal de descubrimientos; preferencia por una voz adulta y profesional para Factor de Gigantes.
- Se mantienen las voces del sistema remoto sin cambio: no se sustituyó automáticamente el narrador por una alternativa no escuchada.
- Se amplió tools/voice.py con un catálogo restrictivo y dos nuevos modelos de Piper; hash SHA256 tomado de páginas oficiales del modelo.
- Se agregó tools/audition.py y workflow voice-audition.yml en main. Reproducen exactamente el mismo fragmento sobre BlackBerry con tres voces, sin publicación en YouTube ni llamadas a API de pago.
- Se añadieron tests de catálogo y permiso explícito de modelos, y CI general se verificó en GitHub con éxito.
- Ejecución real GitHub Actions 39487653479 terminada en SUCCESS, artefacto de audición 12293493424 incluye es_MX-ald-medium.wav, es_MX-claude-high.wav, es_ES-davefx-medium.wav y comparacion.json. Se descargó el ZIP y verificó la presencia de las tres muestras de audio.
- Falta escuchar, puntuar y elegir el narrador oficial; posteriormente aplicar por canal la voz seleccionada con configuración de velocidad, pausas y guía de pronunciación. Antes de publicación comercial, revisar licencias de datasets, modelos y procedencia.
- Próximos pasos: selección auditiva del propietario, configuración persistente por canal en D1/panel, control de versión de narrador, pruebas del flujo de render remoto v0.2 y producción visual documental licenciada.


## 2026-10-20 · Segunda audición de voz: búsqueda de timbre más grave

- El propietario escuchó las primeras tres voces de Piper; la tercera (`es_ES-davefx-medium`) se aproximó, pero suena demasiado fina/aguda para una voz institucional adulta.
- No se cambió la voz oficial ni la configuración de renders aprobados.
- Se identificó el motor abierto Kokoro 82M, licencia Apache-2.0 declarada para el modelo, con dos voces masculinas en español: `em_alex` y `em_santa`. Sigue pendiente evaluar las licencias y procedencia de voces específicas.
- Se añadió `tools/audition_kokoro.py` y `.github/workflows/voice-kokoro.yml` para generar dos WAV originales y una tercera variante de tono ligeramente más grave (`em_alex_grave_sutil`), con idéntico texto de referencia sobre BlackBerry.
- La variante de tono no es una voz nueva y está etiquetada claramente. No hay publicación, conexión a YouTube ni API TTS de pago.
- **Pendiente de esta entrega:** confirmar en GitHub Actions que el job completó y guardó tres WAV válidos; escuchar muestras y decidir cuál se acerca a la identidad buscada.

## 2026-10-20 · Nuevas voces Kokoro verificadas (3 muestras reales)
- La audición GitHub Actions **39489493745** concluyó **success**: instalación de Kokoro 0.9.4 en CPU, generación y validación de audios, subida de artefacto `12295111773`. Enlace: https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39489493745 .
- ZIP de artefacto descargado y verificado con Python: contiene `em_alex.wav` (16,45 s), `em_santa.wav` (16,68 s), `em_alex_grave_sutil.wav` (16,43 s) y `comparacion.json`, todos WAV mono PCM 24 kHz, cada uno con más de 780 KB.
- Los dos primeros son voces masculinas Kokoro en español. El tercero es una variante técnica de `em_alex` con pitch reducido ~6 % y tempo compensado: **no es otro locutor** y debe juzgarse por naturalidad.
- Modelo Kokoro-82M de pesos con licencia declarada Apache-2.0 (source: https://huggingface.co/hexgrad/Kokoro-82M); revisar licencias y procedencia de cada voz antes de publicación con fines comerciales.
- La búsqueda responde a la evaluación del propietario de que `es_ES-davefx-medium` se acerca pero suena demasiado fina.
- No se cambió el narrador predeterminado de `render.yml`, ni se generó publicación YouTube. Próximo paso: escuchar y elegir candidata (o buscar una voz más grave todavía), después construir el selector fijo de narrador por canal.

## 2026-10-20 · Se rechaza la segunda audición Kokoro por artificiosidad

- El propietario escuchó el lote Kokoro (`em_alex`, `em_santa` y variante `em_alex_grave_sutil`) y lo rechazó: "parece narrador raro". Ninguna de estas voces queda aprobada para ser identidad del canal.
- Preferencia vigente: narración masculina adulta, natural, cálida pero con cuerpo, sobria, creíble, profesional y apta para documentales empresariales. No confundir graveza artificial con madurez; evitar pitch-shift.
- No modificar automáticamente la voz del render actual, D1 ni secretos mientras no exista una identidad vocal aceptada.
- Alternativa técnica investigada (no implementada ni probada): **ResembleAI Chatterbox Multilingual v3** y su paquete regional `Chatterbox-Multilingual-es-mx-latam`. El proveedor declara español LATAM y licencia MIT. Referencias: https://github.com/resemble-ai/chatterbox y https://huggingface.co/ResembleAI/Chatterbox-Multilingual-es-mx-latam .
- Chatterbox es más pesado que Piper/Kokoro; antes de añadirlo a renders se necesita comparar consumo real en GitHub Actions Free, disponibilidad CPU, coste temporal y calidad auditiva. No prometer ejecución gratuita ilimitada.
- Si se usa una voz de referencia para identidad estable, requerir una muestra original/expresamente licenciada o autorización del locutor; no clonar voces de figuras conocidas sin permiso.
- Próximo paso: decidir entre muestra de voz con derechos propios para una voz de marca y test de Chatterbox sin referencia, o seguir buscando una voz preentrenada natural con licencia comercial verificada. Mantener publicación de YouTube desactivada.

## 2026-10-20 · Referencia exacta de voz: Microsoft Luis (Ecuador)

- El propietario mostró una captura de Microsoft Speech Studio y seleccionó la voz **Luis, Español (Ecuador)** como ejemplo del estilo vocal deseado para Factor de Gigantes: narración masculina fluida, formal y profesional. Esta referencia reemplaza la búsqueda vaga de voces graves por un objetivo concreto.
- Se verificó en el catálogo oficial Microsoft Azure Speech el identificador API `es-EC-LuisNeural` (voz masculina estándar precompilada). Referencia: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=text-to-speech
- Integración posible mediante Azure Speech SDK/REST y un recurso Speech en Azure, utilizando clave y región en secretos (nunca en Git), **pendiente de cuenta, autorización del propietario y revisión de costos**; no se ha integrado ni sustituido la voz actual.
- Azure Speech F0 indica hasta **500.000 caracteres TTS neural/mes** para evaluación: https://azure.microsoft.com/es-es/pricing/details/speech/
- **Restricción decisiva:** según los términos de Microsoft, los derechos de uso del audio generado por voces precompiladas, incluido el uso comercial, se conceden expresamente a **clientes del nivel de pago de TTS**, no al nivel F0: https://www.microsoft.com/licensing/terms/en-US/productoffering/MicrosoftAzure/allprograms . No usar F0 como voz final de vídeos potencialmente monetizados, salvo que Microsoft otorgue confirmación contractual explícita distinta.
- Siguiente decisión: ¿priorizar la voz exacta `es-EC-LuisNeural` bajo nivel S0 medido por uso (con tope de gasto) o buscar una voz abierta/licenciada de carácter similar sin depender de Azure? Mantener la voz provisional en renders hasta resolverlo.

## 2026-10-20 · Política irreversible hasta nueva decisión: cero pagos

- El propietario rechazó expresamente la posibilidad de pagar por Azure o por la voz Microsoft Luis: «No, nada de pagos».
- Se registra **cero servicios de pago o suscripciones** como requisito de producto. No se debe recomendar Azure S0 ni usar Audio TTS de prueba gratuita si sus condiciones impiden monetizar legalmente el resultado.
- La voz `es-EC-LuisNeural` queda únicamente como **referencia acústica/editorial** (natural y profesional), no como motor habilitado.
- Próxima búsqueda: voz local/open source gratuita con calidad natural comparable, derechos comerciales claros y recursos compatibles con las cuotas gratuitas; descartar o pausar lo que exija gasto.
- El narrador en producción sigue siendo provisional (`es_MX-ald-medium` para renders técnicos): **ninguna voz definitiva seleccionada**.
- Vigilar los límites de ejecución gratuitos de GitHub Actions/Cloudflare; evitar renderizaciones o procesos masivos automáticos.


## 2026-10-20 · Búsqueda independiente de TTS gratuitos tras descartar Azure

- El propietario mantiene como condición que no haya pagos, suscripciones ni APIs de TTS facturables. Referencia acústica deseada: naturalidad profesional similar a Microsoft Luis, sin imitación/clonación de su voz.
- Revisión de fuentes primarias: MeloTTS Spanish MIT (~208 MB, CPU), Chatterbox Multilingual v3 LATAM MIT (~2,14 GB en checkpoint T3, más archivos), Qwen3-TTS 0.6B CustomVoice Apache-2.0 (~2,5 GB de distribución), CosyVoice3 0.5B Apache-2.0 (9 idiomas, español), Qwen3 VoiceDesign 1.7B Apache-2.0 (~4,52 GB).
- Se anotó matriz técnica, procedencia y restricciones en `docs/MOTOR_AUDIOVISUAL.md` con enlaces directos a model cards oficiales. Ninguno de estos motores se declara voz oficial por tener licencia abierta; falta prueba auditiva y verificación de dependencias y datos de entrenamiento.
- Se crearon `tools/audition_melo.py` y `.github/workflows/voice-melo.yml`, solo en `main`, para generar muestras de la **misma voz** MeloTTS en velocidad 1.0 y 0.9 sin distorsionar el tono. Workflow GitHub Actions `39497786790` lanzado automáticamente, sujeto a `timeout-minutes: 17` y sin credenciales externas ni publicación.
- **Resultado pendiente al registrar esta entrada**: confirmar que el workflow produjo dos WAV válidos y artefactos, y escuchar. No se cambió `render.yml` ni el narrador provisional Piper. Si el workflow falla, consignar fallo y no marcar la voz como probada.


## 2026-10-20 · Audición MeloTTS completada y verificada

- Se realizaron tres ejecuciones de `.github/workflows/voice-melo.yml` en `main`:
  - 39497786790: falló al importar MeloTTS por `pkg_resources` eliminado en versiones recientes de `setuptools`.
  - 39498261483: se solucionó `pkg_resources` fijando `setuptools<81`; después falló el inicializador MeCab por diccionario UniDic ausente, aunque la voz de destino era español.
  - **39498716070: éxito completo**, tras instalar `python -m unidic download` como exige el origen. Todas las etapas de instalación, síntesis de audio, archivo y publicación de artefacto pasaron.
- Artefacto oficial GitHub Actions **12299087396**: `audicion-melotts-factor-de-gigantes`; https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39498716070 .
- Se descargó y extrajo el artefacto. Contiene `melo_normal.wav` (17,59 s), `melo_pausada.wav` (18,96 s) y `ficha.json` con procedencia, licencia y estado no aprobado. Ambos WAV verificados: PCM mono, 44.100 Hz, 16 bit, sin errores de decodificación. También se generaron MP3 160 kbps para audición en el teléfono.
- **La segunda muestra es la misma voz** a velocidad 0,9, NO otra voz ni efecto de pitch. No se ha evaluado ni aprobado la idoneidad del timbre como narrador profesional.
- El modelo y proyecto upstream `myshell-ai/MeloTTS-Spanish` publican licencia MIT, y el proveedor afirma capacidad de síntesis en CPU. Se debe revisar el uso comercial de dependencias/modelos antes de lanzar documentales monetizados. No hubo llamadas a servicios de pago.
- `render.yml` y el narrador provisional permanecen sin modificación. No se conectó Azure ni se publicó contenido en YouTube.
- **Siguiente acción**: propietario escucha las dos variantes de MeloTTS y califica si suena adulto y profesional. Si no, buscar modelos Chatterbox/CosyVoice/VoiceDesign viables sin tarjeta, clonación de terceros ni gasto; mantener cuotas y pruebas bajo control.


## 2026-10-20 · Evaluación negativa del propietario de MeloTTS

- El propietario escuchó la audición real MeloTTS (ritmo normal y 0,9) y concluyó: **«Se escucha como tts»**. La voz no alcanza el nivel de naturalidad humana, adulta y profesional requerido por Factor de Gigantes; no queda aprobada para identidad de marca.
- Por acumulación de resultados insatisfactorios se cambia el enfoque: no seguir ajustando velocidad ni pitch de motores con timbre sintético. Evaluar primero **demos del modelo avanzado** con la misma frase, y solo integrar al motor si la audición convence y la ejecución local entra en el presupuesto gratuito.
- Próximo candidato priorizado: Chatterbox Multilingual V3 **es-MX/LatAm**, finetune en https://huggingface.co/ResembleAI/Chatterbox-Multilingual-es-mx-latam y demostración oficial https://huggingface.co/spaces/ResembleAI/Chatterbox-Multilingual-TTS-es-mx-latam. Licencia declarada MIT; modelo regional ocupa al menos 2,14 GB para la parte T3, además de decodificador de audio (1,06 GB en safetensors): estimar RAM/CPU antes de usar GitHub Actions.
- Confirmado en código upstream que Chatterbox Multilingual V3 admite `device="cpu"`, `t3_model="v3"`, `language_id="es"`, y permite variar parámetros de expresividad; sin garantía de síntesis a tiempo razonable en runners gratuitos.
- Alternativa editorial si ningún motor abierto cumple: voz humana grabada con autorización del locutor para crear un narrador propio sin usar voz ajena, y evaluar herramientas de edición de audio libres. Nunca imitar Microsoft Luis sin autorización.
- Se conserva `render.yml` y Piper como **voz técnica provisional**, sin publicación automática ni cuentas de pago. Cero nuevas audiciones pesadas hasta validar calidad comparativa y coste del siguiente candidato.

## 2026-10-20 · Rechazo de demo Chatterbox femenina; Voice Design masculino como próximo ensayo
- El propietario revisó la demo Chatterbox Multilingual es-MX/LatAm: **solo escuchó una voz femenina** y la rechazó expresamente. No proponerla de nuevo como demostración masculina ni asumir que la demo permite alternar géneros.
- La limitación es de la demostración por defecto: Chatterbox acepta una muestra de locutor distinta mediante `audio_prompt_path`, pero **solo utilizar muestras propias o con consentimiento y derechos expresos**, nunca clonar Luis de Microsoft.
- Alternativa verificada: **Qwen3-TTS Voice Design (1.7B)**, que permite describir una voz masculina madura y profesional sin referencia humana; idioma español. Demo oficial: https://huggingface.co/spaces/Qwen/Qwen3-TTS , pestaña `Voice Design`, campo `Voice Description`.
- Descripción inicial de audición: `A natural mature male Latin American Spanish documentary narrator, warm low-mid pitch, confident and calm, clearly articulated, subtle authority, measured pace, authentic human intonation, no announcer theatrics, no robotic tone.`
- Aún **no se ha generado una muestra Qwen real** desde el proyecto, ni se ha medido la capacidad de CPU/tiempo de render, ni se ha aprobado voz definitiva. La demo pública puede imponer límites de uso gratuitos; una muestra no equivale a integración local o derecho irrestricto para uso comercial.
- Mantener el flujo actual Piper como prueba técnica y prohibición de pagos. Próximo paso: evaluación auditiva de Qwen Voice Design por el propietario; luego prueba de recursos locales antes de integrar en render.

## 2026-10-20 · Primera voz Qwen3 Voice Design generada realmente (sin pagos)

- Ante la solicitud explícita «Hazlo tú, dame el audio», se integró una prueba puntual en `tools/audition_qwen.py` y `.github/workflows/voice-qwen.yml`, directamente en `main` y sin cambiar la voz actual de los renders.
- La prueba usa el **Space público oficial** `Qwen/Qwen3-TTS` con la función `generate_voice_design`; entrada: español, texto breve original sobre BlackBerry y descripción de narrador masculino adulto, latinoamericano, profesional, natural, con cuerpo y sin dramatización ni voz robótica. **No se hizo imitación ni clonación de personas.**
- **GitHub Actions run 39502577947: success.** Respuesta del Space: `Voice design generation completed successfully!`. Todas las etapas de generación, conversión MP3 y carga del artefacto terminaron correctamente.
- Artefacto `audicion-qwen-voz-masculina-factor-de-gigantes`, ID **12302050983**, contiene `Qwen3_FactorDeGigantes_VozMasculina.mp3` y `audicion.json`. Se descargó y validó con `ffprobe`: **MP3 mono, 24 kHz, 14,112 s, 282.765 bytes**. URL: https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39502577947 .
- No se usó Azure, ningún secreto ni una API de voz facturable; generación de una única prueba mediante demostración gratuita pública con cuotas/colas de terceros. **No confundir prueba pública gratuita con garantía de producción ilimitada.**
- El MP3 se entregó al propietario para escuchar. La aceptación de la calidad humana/masculina/natural queda pendiente: que el prompt solicite ese timbre **no demuestra** que la voz resultante lo cumpla.
- **Pendiente de arquitectura:** medir si Qwen3 Voice Design (1.7B) puede ejecutarse de forma autónoma en CPU gratuita para narrar documentales de 8–14 minutos, sin depender de la disponibilidad y licencias de uso de una demo alojada por terceros. No actualizar `render.yml` ni la voz institucional hasta que el propietario apruebe la muestra.

## 2026-10-20 · Qwen3 Voice Design v2: más energía, con MP3 entregado
- El propietario evaluó la muestra Qwen3 inicial y solicitó **«Le falta energía»**. La nueva pauta es voz adulta masculina con impulso, entusiasmo medido, suspenso, énfasis en palabras clave y ritmo medio-rápido, sin caer en locución excesivamente teatral o de tráiler.
- Se actualizó `tools/audition_qwen.py` en `main`: misma narración original sobre BlackBerry para facilitar la comparación; descripción vocal refinada (`captivating forward momentum`, `dynamic rhythm`, `expressive emphasis`).
- GitHub Actions `39503709220`: **success**. Demo pública Qwen3 `/generate_voice_design` respondió `Voice design generation completed successfully!`, y exportó `Qwen3_FactorDeGigantes_MasEnergia.mp3` en artefacto `12301563544`.
- Audio descargado, extraído y verificado: **MP3 mono, 24 kHz, 15,00 s, 300.525 bytes**. Entregado a través de ChatGPT como `FactorDeGigantes_Qwen3_MasEnergia.mp3`. URL evidencia: https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39503709220 .
- No hubo pagos, clave de Azure, clonación de voces ni cambios en `render.yml`. El generador Voice Design puede variar identidad vocal entre llamadas; mantener el narrador consistente a lo largo de un documental es aún una limitación arquitectónica por resolver.
- **Pendiente:** el propietario debe escuchar y decidir si la energía de esta versión se acerca al objetivo; no asumir aprobación a partir del éxito técnico ni incorporar la voz al canal hasta validar calidad y sostenibilidad gratuita.

## 2026-10-20 - Audicion Qwen v3: claridad y pronunciacion

- Evaluacion del propietario de v2: voz poco profesional, vaga, sin la claridad y pronunciacion exigidas.
- Cambio de prioridad: narrador masculino profesional de documentales, articulacion precisa, palabras completas, consonantes y vocales nitidas, ritmo medio con proyeccion firme, voz no arrastrada.
- Archivo actualizado en main: tools/audition_qwen.py. Misma frase sobre BlackBerry para comparar versiones. Nuevo MP3 Qwen3_FactorDeGigantes_DiccionProfesional.mp3.
- Postprocesamiento: filtro de graves por debajo de 70 Hz y loudnorm EBU R128 -17 LUFS, sin modificar el tono. No se afirma que estos filtros arreglen la diccion sintetizada.
- Prueba real GitHub Actions run 39504363557: SUCCESS, artefacto 12301594283. El ZIP contiene MP3 y audicion.json; MP3 verificado con ffprobe: 11.688 s, mono, 48 kHz, 234285 bytes.
- Archivo entregado al propietario para revision auditiva; voz NO aprobada aun. No hubo pagos, no se modifico el render de produccion ni se publico en YouTube.
- Pendiente: evaluar pronunciacion, timbre, autoridad y consistencia de voz entre fragmentos antes de integrar.

## 2026-10-20 · Primer timbre Qwen bien valorado; pronunciación de BlackBerry corregida en prueba de continuidad

- El propietario valoró la **tercera muestra Qwen3 Voice Design v3** como «Excelente, mucho mejor», especialmente por profesionalidad y dicción. Señaló una falla concreta: el nombre **BlackBerry** se escuchaba como «beri y berri», pronunciación inestable/repetida.
- Decisión técnica: mantener Qwen v3 **como timbre candidato preferido** y no rediseñar otra voz por ese error. La aprobación completa sigue pendiente de corregir el nombre y asegurar continuidad vocal.
- Se añadieron en la rama **`main`** los archivos `tools/voice_lexicon.py` (normalización solo para síntesis, `BlackBerry` → `Blákberi` sin afectar el texto visible), `tools/audition_qwen_clone.py` y el workflow `.github/workflows/voice-qwen-clone.yml`.
- El workflow recupera exclusivamente el audio sintético v3 desde GitHub Actions run **39504363557**, verifica SHA-256 `e03ee9359a0323d958279ea22ccb37f07aafd681dcd36667a0d318214c06e675` y usa `Qwen3-TTS Base 1.7B Voice Clone` (Space público oficial) para intentar mantener el mismo timbre al corregir el nombre. No se clona a ninguna persona real; se reutiliza un audio generado previamente para este canal.
- La ejecución **39505217153 finalizó con éxito**, artefacto **12302578597** `audicion-qwen-blackberry-con-voz-referencia`. El MP3 descargado fue examinado con ffprobe: **11.304 segundos, mono, 48 kHz, 226605 bytes**. Es una prueba verificable, no garantía de idéntica voz o pronunciación correcta; pendiente de escucha por el propietario.
- Muestra entregada como `FactorDeGigantes_BlackBerry_Corregido.mp3`. El audio v3 original permanece sin sobrescribir. Costo de proveedores TTS: **0**; no se activó Azure, no se modificó el renderizador principal y no se publicó en YouTube.
- **Riesgo de continuidad:** los artefactos GitHub Actions caducan (3 días en esta prueba); si se aprueba de forma definitiva el timbre, habrá que preservar una referencia vocal verificada y un léxico de marcas en almacenamiento persistente, sin depender de la disponibilidad del Space ni de su cuota de demo pública.
- Siguiente verificación del propietario: (1) BlackBerry como única palabra clara; (2) parecido de timbre con Qwen3 v3; (3) dicción firme. De aprobarse, diseñar preservación de identidad de marca para todo el canal.

## 2026-10-20 · Ajuste solicitado: r fuerte en Berry

- El propietario precisó que el sintetizador pronuncia «ri» con r simple en lugar de «rri» con vibrante fuerte. La corrección exacta es **r fuerte**, sin cambiar la voz Qwen v3 de dicción profesional ya considerada la mejor.
- El léxico de síntesis cambia sólo `BlackBerry` a `Blákberri` (doble `rr` entre vocales), manteniendo escritura comercial y subtítulos `BlackBerry`.
- Se actualizan a la vez el léxico, las pruebas del workflow y la salida `FactorDeGigantes_BlackBerry_RR_Fuerte.mp3`; se reutiliza como referencia la muestra sintética v3, sin introducir un locutor nuevo.
- La regla fonética y el éxito técnico **no equivalen a pronunciación garantizada**: comprobar auditivamente la vibrante fuerte y el timbre antes de aceptar para el motor definitivo.
- Coste cero, rama main; no se modifica `render.yml` ni se publica en YouTube.

- Resultado comprobado de la corrección con doble `rr`: GitHub Actions run **39506360433** terminó **success**, artefacto **12303606616** (`audicion-qwen-blackberry-rr-fuerte`). MP3 extraído y validado con `ffprobe`: 10,896 segundos, mono 48 kHz, 218.445 bytes. Enlace: https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39506360433 . Se entregó al propietario para que compruebe auditivamente la vibrante fuerte; **la generación correcta del archivo no acredita por sí sola que el fonema haya sido pronunciado como pidió**.

## 2026-10-20 · Estilo documental de naturaleza y ajuste localizado de «años»

- El propietario indicó que la versión BlackBerry con rr fuerte ya parece correcta, pero que el ritmo estaba algo rápido. Pidió una cadencia **similar al estilo de los documentales sobre animales de Discovery**, sin pedir la imitación de un narrador individual.
- Se preparó una audición basada **en el MP3 existente**, conservando voz e interpretación original: FFmpeg `atempo=0.94` y tres ampliaciones de pausa de 160 ms en silencios de final de frase. Resultado validado: `FactorDeGigantes_Documental_Naturaleza_Pausado.mp3`, MP3 de unos 12,07 s.
- El propietario valoró esta versión «Excelente», con una observación localizada: en **«Durante años»** suena «aaños», con la vocal inicial demasiado alargada.
- Se ajustó solamente la vocal inicial de ese término en el primer segundo, retirando **65 ms entre 0,5945 y 0,6595 s** y uniendo el audio con transición cruzada de 16 ms. **No se regeneró la voz**, no se alteraron los otros nombres ni el ritmo del resto de la locución.
- Nuevo archivo `FactorDeGigantes_Documental_Anos_Corregido.mp3`: validación con FFprobe, duración **12,00 s**, mono 48 kHz, **240 524 bytes**. Escucha pendiente de confirmación por el propietario: el archivo técnicamente correcto **no garantiza** la naturalidad del fonema.
- Scripts añadidos para reproducción en `main`: `tools/documentary_pacing.py` para controlar velocidad y pausas sin pagos; `tools/voice_fix_anos.py` para reparar exclusivamente la muestra aprobada, con comprobación de hash SHA-256 del audio fuente; y tests `tests/test_documentary_pacing.py`.
- No se modifica la voz provisional en `render.yml`, no se publica nada en YouTube y no se activa facturación.
- Siguiente tarea: evaluar auditivamente la vocal de «años», fijar referencia vocal persistente si queda aprobada, y comprobar capacidad y derechos de producción continuada sin coste.


## 2026-10-20 · Rechazo del recorte de «años»: efecto artificial (reversión inmediata)

- El propietario denunció que el archivo `FactorDeGigantes_Documental_Anos_Corregido.mp3` **estropeó la palabra «años»**, dejándola con un sonido similar a autotune. **Se rechaza esa muestra.**
- Causa concreta: la eliminación de 65 ms dentro de la vocal /a/ con crossfade de 16 ms creó una discontinuidad en la señal que el oído percibió como artificial. El archivo no debe servir como referencia para ningún documental.
- **Versión segura restaurada como referencia de audición**: `FactorDeGigantes_Documental_Naturaleza_Pausado.mp3`, que había recibido el calificativo «Excelente» antes de la reparación fallida; SHA-256 `9c608fe3d6c4a8280e14848a8fc3f3ac4d649ad403c727f2d833ea44cdf1c6bf`. Mantiene cadencia y el detalle original de pronunciación en «años», sin introducir autotune.
- Se **deshabilita** `tools/voice_fix_anos.py` de forma explícita, conservando aviso histórico para impedir cualquier reutilización involuntaria. No se aplicarán nuevos cortes intravocálicos ni clonaciones de una voz humana real.
- Se añadió `tools/audition_qwen_retake.py` y se cambió `.github/workflows/voice-qwen-clone.yml` para generar **una nueva toma íntegra** mediante Qwen3 y la referencia vocal de la muestra profesional v3. Sólo después se aplica ralentización global moderada `atempo=0.94` y pausas entre frases, sin modificar segmentos de la palabra.
- La corrección de «años» por regeneración queda **pendiente de audición humana**, ya que ejecutar el motor no demuestra que el fonema sea correcto o que la voz permanezca idéntica. No se modifica `render.yml`; política de cero pagos intacta.

## 2026-10-20 · Toma íntegra sin recortes — resultado de ejecución

- Ejecución real de GitHub Actions **39509095680**: **success**. La referencia Qwen v3 se descargó correctamente, el Space Qwen3 generó la locución completa y se aplicó la cadencia documental al audio entero, sin cirugía intravocálica.
- Artefacto `qwen-narrador-toma-natural-sin-cortes` ID **12303639971**. MP3 `FactorDeGigantes_Documental_TomaNatural.mp3` descargado y comprobado con FFprobe: **12,336 s**, mono, **48 kHz**, 247 245 bytes. URL: https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39509095680 .
- **Estado de calidad: pendiente de evaluación auditiva del propietario.** No se considera solucionada la articulación de «años» hasta su confirmación. La toma anterior `FactorDeGigantes_Documental_Naturaleza_Pausado.mp3` queda preservada como referencia segura y la reparación quirúrgica `voice_fix_anos.py` sigue deshabilitada.
- No se activaron servicios de pago ni se alteró el narrador del renderizador principal.

## 2026-10-20 · Aprobación auditiva de la toma documental natural

- El propietario escuchó `FactorDeGigantes_Documental_TomaNatural.mp3` y confirmó expresamente: **«Ahora está correcto»**. Se considera **muestra vocal aprobada para referencia editorial**: voz masculina profesional, clara, dicción entendible, ritmo pausado de documental de naturaleza, `BlackBerry` con doble erre según preferencia y «Durante años» natural.
- Muestra exacta aprobada: GitHub Actions [39509095680](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39509095680), artefacto `12303639971`, archivo `FactorDeGigantes_Documental_TomaNatural.mp3` (12,336 s, mono, 48 kHz).
- Se **rechaza y prohíbe reutilizar** el archivo `FactorDeGigantes_Documental_Anos_Corregido.mp3` y el método de recortar la vocal, porque generaron efecto autotune. La muestra anterior pausada queda solo como respaldo histórico.
- La aprobación corresponde **al audio escuchado**, no certifica todavía que nuevas generaciones con el mismo modelo conserven exactamente el timbre. No se ha sustituido el narrador técnico en el flujo de renderizado ni se ha configurado almacenamiento permanente de la referencia. Las grabaciones de GitHub Actions tienen retención temporal: evitar pérdida de la muestra aprobada.
- **Próximo paso prioritario:** conservar la muestra aprobada de forma persistente y verificable; diseñar un narrador reproducible con ese timbre y ese ritmo, validar derechos comerciales y ejecución sin pagos; después integrar al renderizador en `main` y probar narraciones largas sin publicar automáticamente.


## 2026-10-20 · Identidad vocal preservada y ensayo de continuidad en nuevos guiones

- **Persistencia comprobada en GitHub `main`**: `assets/voice/approved/narrador_documental_aprobado.mp3`, archivo binario real **247245 bytes**. El workflow `39510298815` de preservación terminó `success`: verificó SHA-256 `78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d` y guardó el MP3 aprobado. El audio ya no depende de la caducidad del artefacto.
- Manifiesto duradero `assets/voice/approved/reference.json` con el texto real pronunciado `Blákberri` y el texto editorial `BlackBerry`, modelo, ritmo `atempo=0.94`, pausas, aprobación del propietario y pendientes legales.
- `tools/approved_voice.py` permite recuperar sólo la referencia con aprobación y hash válidos, sin fallback silencioso. Tests en `tests/test_approved_voice.py`.
- **Paso siguiente implementado como audición**: `tools/qwen_consistency.py` usa el MP3 fijo aprobado, su transcripción y la demo Qwen3 Base para intentar generar una narración **nueva**, diferente de BlackBerry, sobre naturaleza y cambios empresariales. Mantiene la cadencia documental y rechaza entradas vacías o desmesuradas. `.github/workflows/voice-consistency.yml` lo prueba una vez en GitHub Actions; `tests/test_qwen_consistency.py` valida contratos sin hacer llamadas externas. **Pendiente de escuchar la muestra y de confirmar continuidad real**, no basta con la ejecución exitosa.
- El renderizador principal aún no utiliza este método. No habilitar como proveedor de publicación comercial mientras falte verificar derechos de output y viabilidad de ejecución local/coste cero. Las cuotas de Hugging Face ZeroGPU para usuarios sin autenticar son restringidas y no aptas como garantía de escalamiento.

## 2026-10-20 · Aprobada y almacenada la voz; continuidad verificada técnicamente

- La referencia de voz aprobada quedó almacenada **como binario permanente en la rama principal**: `assets/voice/approved/narrador_documental_aprobado.mp3`, de 247245 bytes, SHA-256 `78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d`. Ejecución de preservación `39510298815`: exitosa. Ya no depende de la caducidad del artifact.
- Manifest `assets/voice/approved/reference.json` y verificador `tools/approved_voice.py` fijan el audio aceptado, su transcripción, velocidad y checksum sin sustituirlo silenciosamente si falta o cambia.
- Prueba de **continuidad con otro guion** vía Qwen3-TTS Base 1.7B, partiendo de esa muestra fija y manteniendo la cadencia de documental: ejecución `39510650716`, exitosa. Artefacto `12304934427`; audio `FactorDeGigantes_Prueba_Continuidad_Voz.mp3` de **13,584 s**, mono y 48 kHz, checksum `7d34443491320c21b2167bafaf6591dce32303c6fa438014914bf5b6af2283af`. El usuario aún debe escuchar y confirmar identidad vocal, dicción y ritmo de esta nueva frase.
- El workflow de continuidad se ejecutó nuevamente en `39510770537` con éxito; no interpretar dos éxitos técnicos como validación auditiva de identidad.
- `tests/test_approved_voice.py` y `tests/test_qwen_consistency.py` pasaron en GitHub Actions `39510770438`; se corrigió la validación de saltos de línea del texto nuevo.
- La demo pública de Hugging Face ZeroGPU tiene cuota diaria limitada: **no se permite depender de ella para producir automáticamente documentales de larga duración**. El motor oficial actual `render.yml` no ha sido cambiado.
- Se puso en marcha una prueba controlada **sin API ni servicios facturables** del modelo Qwen3-TTS Base 0.6B en CPU del runner público gratuito GitHub Actions: script `tools/qwen_local_smoke.py`, workflow `.github/workflows/voice-qwen-cpu.yml`. El primer intento de workflow `39511250435` falló por expresión de contexto no permitida en `env`, corregida; ejecución `39511351086` iniciada y **resultado todavía pendiente de confirmar** al registrar esta nota. No anunciar éxito local antes de que entregue un MP3 real y métricas.
- GitHub documenta que el runner Linux de repositorios públicos incluye 4 CPU, 16 GB RAM, 14 GB SSD y es gratuito bajo la política vigente. Modelo 0.6B con licencia Apache-2.0. Persisten dudas de rendimiento, parecido auditivo y derechos de explotación de audios producidos en los flujos probados.


## 2026-10-20 · Qwen3-TTS Base 0.6B: síntesis **local CPU** lograda, sin API

- Resultado real: GitHub Actions run **39511351086** concluido `success`. Se instalaron PyTorch 2.8 CPU y `qwen-tts`, sin CUDA/GPU, cuenta de servicio ni API facturable; los pesos abiertos `Qwen/Qwen3-TTS-12Hz-0.6B-Base` fueron descargados y ejecutados en la VM del runner público de GitHub.
- Script ejecutado `tools/qwen_local_smoke.py`, que validó antes de inferir que el MP3 de referencia aprobado mantenía SHA-256 `78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d`.
- Muestra generada `FactorDeGigantes_Qwen_Local_CPU.mp3`: MP3 mono de 48kHz, **8,424 segundos**, 169005 bytes y SHA-256 `d9ff665031859c351acff5a781b3b73d8b914be2934c3b2bf748465bdb281fb1`. Artefacto GitHub Actions **12305867860**, adjunto `cpu-metrics.json`; source: https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39511351086 .
- Métricas observadas en una ejecución: **22,47 segundos de carga del modelo; 79,97 segundos de proceso total** (sin incluir la instalación inicial de paquetes); pico de memoria residente **6362008 KiB ≈ 6,07 GiB** (`/usr/bin/time -v`). No extrapolar linealmente estos tiempos sin benchmarking para documentos de 10 minutos.
- Se confirma técnicamente una opción **local gratuita** para síntesis con voz sintética de referencia, pero es el modelo **0.6B, diferente del 1.7B** que produjo la voz aprobada. El parecido audible, dicción y ritmo requieren nueva evaluación del propietario. **No reemplazar por el 0.6B automáticamente**.
- Qwen3-TTS Base 0.6B y paquete Qwen TTS publican licencia Apache-2.0. **Aún pendiente** la verificación legal completa de referencia/audios para usos comerciales, y la viabilidad/costo operativo de narraciones largas.
- Para evitar ejecuciones involuntarias de modelos pesados, se retira el disparo `push` del workflow CPU; queda **sólo manual `workflow_dispatch`** y restringido a repositorio público (evitar runners facturables si cambia a privado).
- Prioridades siguientes: aprobación auditiva del resultado CPU, persistencia a largo plazo de la voz ya conseguida (realizada), mediciones más extensas del narrador y, sólo con calidad/licencias/costos aptos, integración a `render.yml` y documentos completos; publicar en YouTube siempre bajo aprobación humana.

## 2026-10-20 · Evaluación del propietario del narrador local 0,6B

- Tras escuchar `FactorDeGigantes_Qwen_Local_CPU.mp3`, el propietario indicó **«Está bien el tono, como que ha cambiado un poco»**. El tono le parece aceptable, pero identifica una **variación perceptible de la identidad vocal** respecto a la toma de referencia aprobada. **Esto no equivale a aprobación del nuevo narrador** ni autoriza sustituir la voz definitiva.
- La referencia editorial aprobada (`assets/voice/approved/narrador_documental_aprobado.mp3`; SHA-256 `78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d`) permanece intacta. No alterar ni reemplazar.
- Se creó `tools/qwen17_local_smoke.py` y `.github/workflows/voice-qwen17-cpu.yml` para probar **Qwen3-TTS Base 1.7B en CPU**, el tamaño de modelo usado para generar la toma preferida, frente al 0,6B. El test usa **el mismo texto** que el experimento ligero, la misma referencia aprobada y los mismos parámetros de cadencia; limita la prueba a 12 min en runner de repositorio público, y la síntesis a 420s sin API o GPU de pago.
- **GitHub Actions run 39512992392** se inició; su resultado, consumo de memoria, duración y calidad **todavía están pendientes** en el momento de esta anotación. El éxito técnico no demuestra semejanza perceptual: el propietario decidirá al escuchar la nueva muestra.
- Mantener `render.yml` sin modificación y no publicar vídeos automáticamente; priorizar similitud con voz aprobada y recursos gratuitos verificables.


## 2026-10-20 · Resultado Qwen Base 1,7B CPU y comparación del ligero 0,6B

- La audición del modelo **`Qwen/Qwen3-TTS-12Hz-1.7B-Base` en CPU del runner GitHub Actions gratuito** fue exitosa: ejecución [39512992392](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39512992392), con voz de referencia aprobada intacta y validada por checksum, PyTorch CPU sin API pagada.
- MP3 realmente generado: `FactorDeGigantes_Qwen_17B_CPU_Voz.mp3` (7,680 segundos, mono, 48 kHz, **154 125 bytes**), SHA-256 **`29fdef191c8571f0d5a21adcd6e2202c1aed83c016385794f599320d0427255b`**; artefacto **12306875340**.
- Medición concreta: carga del modelo **20,44 segundos**, ejecución de Python hasta entrega de audio **88,62 segundos** y máximo de memoria residente **11 826 680 KiB (~11,28 GiB)**. No incluir la instalación de dependencias dentro de estos tiempos; no extrapolar directamente a documentales de larga duración.
- Se usó exactamente el mismo texto de comparación que con el modelo 0,6B. La diferencia de duración (1,7B: 7,680 s frente a 0,6B: 8,424 s) muestra que el ritmo generado puede cambiar; **la semejanza acústica real requiere que el propietario escuche ambas tomas.**
- **No se reemplaza la muestra Qwen aprobada**, en `assets/voice/approved/narrador_documental_aprobado.mp3`. El 1,7B local es candidato a preservar mejor la voz porque coincide en tamaño de modelo con el que generó la referencia, pero esto **no equivale a prueba de igualdad de timbre**.
- `.github/workflows/voice-qwen17-cpu.yml` queda **solo con lanzamiento manual** y condición `github.event.repository.private == false`, para no consumir recursos de GPU/CPU innecesariamente ni generar cobros por minutos de runners privados. No se modifica `render.yml`, no se activa publicación de YouTube ni facturación.
- **Siguiente tarea:** comparación auditiva por propietario entre el archivo local 1,7B y 0,6B; posteriormente probar trozos más extensos del elegido y fijar un proveedor/flujo con derechos comprobados, coste cero y narración consistente.

## 2026-10-20 · Confirmación definitiva de la referencia vocal exacta adjuntada por el propietario

- El propietario interrumpió la comparación de candidatos locales 0,6B/1,7B y declaró: **«Noo, esta es correcta»**, adjuntando su propio archivo `FactorDeGigantes_Documental_TomaNatural.mp3`. Este es el **único audio de identidad vocal aprobado**. La preferencia no se refiere genéricamente a Qwen 1,7B, a un tono similar ni a las generaciones locales recientes.
- Se inspeccionó directamente el archivo adjuntado por el propietario: **12,336 segundos, MP3 mono de 48 kHz, 247 245 bytes, SHA-256 `78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d`**; coincide byte a byte por hash y tamaño con `assets/voice/approved/narrador_documental_aprobado.mp3` (muestra de la toma natural aprobada).
- **Decisión editorial vinculante:** fijar **exactamente ese timbre y esa toma** como patrón de voz; las audiciones locales `FactorDeGigantes_Qwen_Local_CPU.mp3` (0,6B) y `FactorDeGigantes_Qwen_17B_CPU_Voz.mp3` (1,7B), aunque técnicamente válidas, **no están aprobadas para reemplazar el narrador**. Que un modelo sea de 1,7B no significa que produzca la misma voz en otras tomas.
- No regenerar, remezclar, ralentizar ni sustituir el archivo canónico. Para contenido nuevo, emplear la referencia inmutable y verificar identidad vocal con pruebas auditivas separadas; rechazar cualquier muestra perceptiblemente diferente.
- **Estado técnico:** referencia persistida en `main` y validada; producción de nuevas frases con fidelidad exacta todavía **no demostrada ni aprobada**. `render.yml` sigue sin Qwen y no hay publicación automática. Mantener reglas de cero pagos y comprobar derechos comerciales/viabilidad.

## 2026-10-20 · Banco de continuidad vocal en dos fragmentos (CPU 1,7B)

**Objetivo del plan maestro:** avanzar en Fase 2 (voz profesional y QA) sin reemplazar la voz única aprobada, iniciar cobros ni activar YouTube.

**Código realizado y confirmado en la rama `main`:**
- `tools/qwen_voice_continuity_batch.py`: banco con dos textos editoriales nuevos, de longitud acotada y diferentes del patrón canónico; reutiliza UNA carga del modelo local `Qwen/Qwen3-TTS-12Hz-1.7B-Base` en CPU y la referencia de `assets/voice/approved/`, previamente validada por SHA-256. Genera cada MP3 con la cadencia parametrizada aprobada, comprueba duración/tamaño y vuelve a verificar el patrón exacto al finalizar.
- Artefactos previstos si se ejecuta: `00_referencia_aprobada.mp3` (copia idéntica, sin modificar la original), `01_decision.mp3`, `02_transformacion.mp3`, `reporte_audicion.json` y guía de escucha. El reporte fija explícitamente `production_ready=false`, `generated_clips_owner_approved=false`, `commercial_rights_verified=false` y `youtube_publication_enabled=false`.
- `.github/workflows/voice-continuity-cpu.yml`: **solo `workflow_dispatch` manual**, runner Linux de repositorio público, CPU sin CUDA/API de pago, tiempo máximo de trabajo, verificación de disco y artefactos retenidos tres días. Si el repositorio se hace privado, el job no se ejecuta.
- `tests/test_qwen_voice_continuity_batch.py`: pruebas de límites, seguridad de identificadores, no repetición de texto y ausencia de aprobación automática.

**Evidencia de integración de código:** commits `4d9da9b`, `5227af5`, `5fb0a40` y corrección de descubrimiento de tests `b5ff562`. CI general sobre `b5ff562`: [run 39515949183](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39515949183), resultado `success`. Este CI **sí ejecutó los tests locales**, pero **NO ejecutó inferencia de Qwen** ni creó las dos muestras; el workflow de audición es deliberadamente manual.

**Pendiente real y prioridad inmediata:**
1. Ejecutar manualmente el workflow [Continuidad Qwen 1.7B CPU - dos tomas sin pagos](https://github.com/eler30mr-star/FactordeGigantes/actions/workflows/voice-continuity-cpu.yml) desde la rama `main`, dentro de la capacidad gratuita disponible; revisar el resultado, consumo, artefacto MP3 e informe. No reportar audio generado hasta observar un run exitoso con muestras.
2. Audición humana comparando las dos tomas contra **el MP3 original exacto**. Cualquier deriva o artificio vocal bloquea integración. No inferir identidad por checksum de referencia ni por coincidencia del modelo.
3. Si ambas muestras son aceptadas, evaluar fragmentos de mayor duración y montaje editorial, con pruebas reales de coste, QA y licencia comercial; integrar `render.yml` **únicamente** cuando haya evidencia suficiente y autorización editorial. Mantener el narrador actual sin alteraciones hasta entonces.
4. Avanzar paralelamente la investigación con fuentes y la trazabilidad de derechos audiovisuales, y después pruebas de un documental original 8–14 min. YouTube sigue sin OAuth ni subida automática.

**Estado inequívoco:** código en GitHub y tests CI **confirmados**; ejecución manual de dos audios, escucha/identidad, licencia comercial y producción **pendientes**. No se ha desplegado otro Worker ni alterado el renderizador principal.

## 2026-10-20 · Audición REAL de continuidad Qwen 1,7B: dos tomas generadas y verificadas

**Hito ejecutado, no solo preparado.** Se activó **una sola vez** el workflow en `main` usando un disparador `push` temporal autorizado por el propietario para ejecutar su prueba. El workflow se devolvió inmediatamente a **solo `workflow_dispatch` manual** (commit `08b4357`). No quedan disparadores automáticos del ensayo intensivo.

- GitHub Actions: [run 39516609592](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39516609592), conclusión **`success`**. Ejecución de generación, verificación de SHA y carga del artefacto completadas. Commit del disparador único `83af430`.
- Artefacto [12307719223](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39516609592/artifacts/12307719223): `factor-gigantes-continuidad-cpu-dos-tomas` (ZIP, cinco archivos: patrón original sin retocar, dos nuevos MP3, JSON de métricas e instrucciones). **Caduca 2026-10-23 a las 23:45 UTC** por retención gratuita de tres días; guardar una copia local antes. Los MP3 se recuperaron y sus checksums/duraciones coinciden con el reporte.
- `00_referencia_aprobada.mp3`: 12,336 s y SHA-256 `78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d`. **Idéntica a la referencia canónica original, que continúa sin modificación**.
- `01_decision.mp3`: 8,496 s, SHA-256 `68b6437729fd085e65af3e35099bd9ebf97b088d399f479199839d9e3dea4c4f`; 70,82 s generación y procesamiento.
- `02_transformacion.mp3`: 9,960 s, SHA-256 `f7019bfe413165ec2dbdee7745f8306ffff51a4ba560508bbf3712592b4990b6`; 80,23 s generación y procesamiento.
- Informe del proceso: `elapsed_seconds_without_dependency_install=172.5`, tiempo externo del paso de síntesis `2:58.30` y **máximo RSS 11 826 580 KiB ≈ 11,28 GiB** (incluye carga y procesamiento; no incluye instalación inicial). CPU PyTorch, cuatro hilos, 1.7B Base, sin API pagada.
- El informe mantuvo explícitos `generated_clips_owner_approved=false`, `voice_identity_verified_by_human=false`, `commercial_rights_verified=false` y `production_ready=false`; **éxito técnico de los MP3 NO implica continuidad vocal validada al oído**.

**Próximo paso prioritario del plan:** el propietario escuchará la muestra canónica y las dos tomas nuevas, y evaluará por separado si ambas conservan exactamente la identidad, la dicción y la naturalidad. Si hay deriva, no integrar. Si ambas son aprobadas, medir continuidad de párrafos más extensos con límites CPU gratuitos, investigar licencias de voz y contenido, y avanzar a narración de un documental de 8–14 minutos con fuentes y recursos licenciados. Sin YouTube automático, sin cambios en `render.yml`, sin cobros. No ejecutar de nuevo este workflow pesado salvo necesidad editorial expresa.


## 2026-10-20 · Revisión auditiva humana de los dos clips Qwen CPU 1,7B

**Evaluación directa del propietario:** «Sí ambas, la 1 es más fiel». La interpretación registrada es que **ambas tomas son aceptables en esta audición corta**, y que la toma **`01_decision.mp3` conserva con mayor fidelidad** el timbre de `FactorDeGigantes_Documental_TomaNatural.mp3` que `02_transformacion.mp3`.

**Evidencia exacta:**
- Ensayo completado: [workflow 39516609592](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39516609592); ZIP temporal [artefacto 12307719223](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39516609592/artifacts/12307719223), caduca el 23-10-2026.
- **Preferida para estudiar continuidad:** `01_decision.mp3`, 8,496 s, SHA-256 `68b6437729fd085e65af3e35099bd9ebf97b088d399f479199839d9e3dea4c4f`.
- **También aceptada en esta audición, menos fiel:** `02_transformacion.mp3`, 9,960 s, SHA-256 `f7019bfe413165ec2dbdee7745f8306ffff51a4ba560508bbf3712592b4990b6`.
- **Única referencia canónica definitiva:** `assets/voice/approved/narrador_documental_aprobado.mp3`, SHA-256 `78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d`. Ni el clip 1 ni el 2 sustituyen esa referencia y **no debe copiarse el clip 1 sobre el MP3 aprobado**.

**Conclusión rigurosa:** se supera **la audición humana de estas dos muestras cortas**; **no** se ha demostrado fidelidad idéntica en múltiples párrafos, control estadístico del timbre, narración larga, licencia comercial integral ni integración final al render. Las próximas pruebas deben comparar cada fragmento nuevo con la voz canónica y utilizar la mayor fidelidad relativa del clip 1 como pauta de selección, no como autorización automática para producción.

**Próximas prioridades conforme al plan:** preparar un ensayo limitado de continuidad en varios párrafos (sin mezclar identidades), medir consumo CPU, registrar resultados por toma y aplicar validación humana; revisar derechos comerciales de modelo/referencia/audio y después integrar únicamente una narración que mantenga la identidad estable. No activar servicios pagos, triggers periódicos ni subida a YouTube. Rama única `main`.


## 2026-10-20 · Fase 2: continuidad narrativa de tres párrafos + trazabilidad documental

**Trabajo en `main` comprobado (sin ramas secundarias):**
- `tools/qwen_longform_probe.py` y `tests/test_qwen_longform_probe.py`: prueba real de una historia **hipotética** de 3 párrafos consecutivos con Qwen3-TTS Base 1.7B en CPU; cada párrafo mantiene referencia SHA-256 aprobada, usa semilla documentada, parámetros originales de cadencia y validación técnica MP3 mono 48 kHz. Produce pistas separadas, versión unida con silencios solo ENTRE frases, copia intacta del MP3 de referencia y reporte JSON. Ningún archivo experimental se publica ni sustituye a la referencia.
- `.github/workflows/voice-longform-cpu.yml`: quedó exclusivamente en `workflow_dispatch`. El disparador `push` **único** usado para ejecutar esta prueba fue revertido inmediatamente en commit `b1438b2`; no queda trabajo automático de síntesis pesada.
- **Ejecución real:** [GitHub Actions 39518606909](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39518606909), `success`. Artefacto [12311066207](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39518606909/artifacts/12311066207), retención hasta **2026-10-24 00:08:53 UTC** (23-10-2026 19:08 Perú).
- **Pistas obtenidas y verificadas** por checksum y FFprobe: `01_apertura.mp3` 13,944 s; `02_conflicto.mp3` 13,944 s; `03_cierre.mp3` 14,712 s; previsualización `04_previsualizacion_unida.mp3` **43,296 s**. La muestra `00_referencia_canónica.mp3` coincide SHA-256 `78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d` con la aprobada; **no sufrió cambios**.
- Síntesis y ensamblado `elapsed_seconds_excluding_install=401.42`, y `/usr/bin/time` reportó `6:48.24` para el proceso y `11 978 044 KiB` (~11,42 GiB) de RAM pico. No usar este dato para afirmar que un documental 8–14 min cabe en el runner gratuito: pendientes escalamiento y límites por duración.
- **Identidad vocal por audición humana: pendiente para estas tres nuevas tomas.** La aprobación previa del usuario («sí ambas, la 1 es más fiel») atañe solo a `01_decision.mp3` y `02_transformacion.mp3` de la prueba ANTERIOR, no al nuevo conjunto.
- El modelo se distribuye con licencia declarada Apache-2.0 en la ficha oficial; la referencia sintética, el servicio/demo de procedencia, sus términos y la autorización comercial completa siguen con revisión pendiente. Se creó `docs/LICENCIAS_NARRACION.md` con fuentes primarias y una puerta explícita contra publicaciones no autorizadas.
- `tools/editorial_evidence.py` y `tests/test_editorial_evidence.py`: auditoría **de estructura**, fuentes HTTPS, IDs por afirmación y estados de licencias; sus resultados no autorizan publicación ni prueban la veracidad por sí mismos. `docs/FLUJO_VERIFICACION.md` documenta uso e integración pendiente D1/panel. CI [39519271278](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39519271278) en `main`: `success`.

**Pendientes inmediatos y siguientes pasos del plan:**
1. El propietario debe escuchar la versión continua de 43,296 s y las 3 tomas por separado, compararlas con la voz canónica y decir si alguno de los párrafos varía de timbre; hasta entonces **no hay aprobación auditiva del ensayo nuevo**.
2. Investigar la reutilización documentada de `create_voice_clone_prompt` de Qwen para evitar recalcular la referencia, medir estabilidad y eficiencia en nuevas pruebas acotadas; validar memoria/tiempo y compatibilidad antes de adoptarla (NO implementada aún).
3. Conectar de manera segura las evidencias y derechos por afirmación al panel y D1 en una migración nueva, sin alterar el esquema histórico; preparar guion factual respaldado por fuentes originales.
4. Después de licencias, calidad y viabilidad verificadas, abordar 8–14 min y mejoras cinematográficas. **Sin servicios pagados, sin OAuth/YouTube ni integración a `render.yml` mientras falten controles.**

**Estado preciso:** código y pruebas CI efectuados; audios nuevos GENERADOS y verificados; evaluación de identidad de estos nuevos párrafos, derechos comerciales integrales, integración al panel y render productivo PENDIENTES.


## 2026-10-20 · Aceptación auditiva del montaje continuo de 43,296 segundos

**Respuesta del propietario al escuchar la previsualización de tres párrafos:** «Está bien». Se registra como **aceptación editorial del resultado de esta audición continua**: `04_previsualizacion_unida.mp3`, 43,296 s, producido por [GitHub Actions 39518606909](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39518606909). La observación no identifica defectos adicionales ni pide cambiar timbre o cadencia.

**Alcance exacto de la aprobación:** la narración continua corta puede tomarse como referencia de calidad de este ensayo. No supone que cada futura generación vaya a conservar la identidad ni convierte las muestras en sustitutas de la **única voz canónica**, `assets/voice/approved/narrador_documental_aprobado.mp3`, SHA-256 `78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d`. Tampoco verifica términos comerciales, permisos de las salidas, calidad de un documental completo o autorización de publicar.

**Siguiente hito conforme al plan maestro, Fase 2:** pasar a mejoras reproducibles del motor para narración segmentada de varios minutos con controles de memoria, tiempos y límites gratuitos; trabajar investigación factual y derechos por afirmación, conectar después estos controles al panel y a D1, y únicamente con validación editorial/legal evaluar el primer documental de 8–14 min. Mantener cero pagos, `main` exclusivamente y sin subir a YouTube.


## 2026-10-20 · Fase 2: expediente editorial conectado al panel, Worker y esquema D1

**Objetivo realizado:** pasar de pruebas aisladas de validación de fuentes a un flujo de investigación administrable por cada documental. Trabajo exclusivamente sobre **`main`** del repositorio `eler30mr-star/FactordeGigantes`, sin ramas secundarias.

### Código implementado y confirmado en GitHub

- `src/editorial.mjs`: validador de expedientes con fuentes HTTPS, IDs únicos, documentos asociados a afirmaciones, `locator` de evidencia y estado, persona revisora, recursos y derechos (la voz es obligatoria). Los URL de fuentes del guion deben figurar en el expediente. **No** afirma haber comprobado contenido real en sitios externos.
- `migrations/0002_editorial_dossiers.sql`: nueva tabla vinculada a `jobs` que guarda expediente JSON, revisión humana, identidad del revisor y fechas, sin alterar `0001_initial.sql`.
- `src/worker.js`: nuevas rutas autenticadas `GET/PUT /api/jobs/:id/dossier` y `POST /api/jobs/:id/dossier/attest`; el editor acredita únicamente durante `review`, cuando todas las afirmaciones y licencias declaradas han sido revisadas. **Bloqueo efectivo en código** de `approve` y `dispatch` si el expediente está ausente, incompleto o no acreditado. Cambiar guion, expediente o pedir cambios invalida la acreditación previa. Si falta la tabla D1 remota, HTTP **503**, y el guardado del guion no muta datos antes de detectar el bloqueo.
- `public/index.html` y `public/app.js`: nuevo panel «Fuentes y licencias», edición JSON de expediente por trabajo, visualización de conteos, guardado y confirmación expresa del revisor; administración sin persistir `ADMIN_TOKEN` en almacenamiento del navegador.
- `tests/test_editorial_gate.mjs`: pruebas de autenticación, fuentes, bloqueo antes de revisión, revocación por cambios, despacho y comportamiento seguro sin migración. `tests/test_editorial_migration.py`: restricciones SQL/foráneas con D1 emulada en SQLite local.
- `.github/workflows/check.yml`: ejecuta los tests del Worker y contrato editorial con Node `--test`, además de la batería Python y chequeos anteriores.
- `docs/DESPLIEGUE.md` y `docs/FLUJO_VERIFICACION.md`: instrucciones concretas de migración remota, despliegue seguro y operación del nuevo panel.

### Pruebas y estado real

- [CI GitHub Actions 39521914410](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39521914410) — **`success`**, incluye `node --test tests/test_editorial_gate.mjs`, `python -m unittest discover -s tests -v`, sintaxis Worker y panel, manifest de ejemplo; diagnósticos HTTP a Cloudflare no bloqueantes. Verificaciones incrementales posteriores sobre protección ante migración ausente también completadas correctamente en GitHub.
- El conector Cloudflare no respondió correctamente al intentar consultar el estado de la base; **NO se ha aplicado la migración 0002 en D1 remota desde esta sesión**. **NO se ha confirmado un nuevo despliegue del Worker ni del panel**. El código funciona en las pruebas de integración simuladas, pero la funcionalidad todavía **no debe declararse operativa en la instancia Cloudflare**.
- Ningún vídeo se publicó; no se introdujeron servicios de pago, claves, OAuth ni se modificó la identidad canónica del narrador, su checksum o `render.yml`.
- Un editor que marque manualmente una afirmación `verificada` sigue siendo responsable de comprobar el documento real. La aplicación verifica estructura y trazabilidad declarada, **no garantiza verdad material ni derechos legales por una marca en el expediente**.

### Próximo paso prioritario verificable

1. En Cloudflare, aplicar `npx wrangler d1 migrations apply factor-de-gigantes-db --remote` tras validar cuenta y hacer respaldo; comprobar `editorial_dossiers` en D1. El primer esquema fue aplicado originalmente por API y es idempotente.
2. Desplegar Worker y assets desde `main`, verificar acceso autenticado, guardar expediente de prueba, comprobar `attest`, y que `approve`/`dispatch` respondan 409 cuando falten fuentes/validaciones. No ejecutar vídeo comercial.
3. Incorporar investigación real con fuentes primarias, metraje/música/imágenes originales con derechos, aprobación humana y guion documental. Mantener bloqueo de publicación y revisión pendiente de licencia comercial de la referencia vocal hasta evidencia concluyente.
4. En paralelo medir viabilidad de narración local de varios minutos y optimizar el Qwen CPU sin cambiar la voz aprobada ni sobrepasar cuotas.

**Estado al terminar este avance:** commits y pruebas CI **realizados**, migración y despliegue remoto **pendientes**, calidad vocal de 43,296 s **aprobada previamente** por el propietario, comercialización/publicación **no autorizadas**.


### Cierre técnico del control por escenas — revisión del avance editorial (2026-10-20)

- Se reforzó `src/editorial.mjs`: **cada segmento del guion debe figurar en al menos una afirmación documentada** mediante `segment_index` (base 1). Fuentes, localizadores, estados de revisión y licencias de voz no desaparecen al ampliar el guion.
- El formulario de expediente en `public/app.js` ahora crea automáticamente afirmaciones **pendientes** por cada escena, evitando un único registro insuficiente. No genera ni declara como verificadas las fuentes de forma automática.
- `src/worker.js`: expedientes obsoletos por cambio de fuentes o escenas se devuelven con `validation_error` y nunca se acreditan; el panel permite corregirlos sin devolver error HTTP 500. La falta de tabla `editorial_dossiers` retorna HTTP 503 antes de mutar el borrador.
- `tests/test_editorial_gate.mjs` añadió cobertura de índices inexistentes, escenas sin evidencia, migración ausente y revocación por cambios. CI de [run 39522588126](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39522588126) completada **`success`** en commit `1a14039e`; dos ejecuciones intermedias fallaron mientras el contrato y los tests se adaptaban, pero se corrigieron y la batería final volvió a verde. `docs/FLUJO_VERIFICACION.md` refleja el contrato de escena y revisión.
- **Sin despliegue validado**. Sigue siendo el principal bloqueo práctico: aplicar D1 0002 en la cuenta Cloudflare correcta, verificar la tabla y probar panel/Worker reales; las herramientas de Cloudflare conectadas no pudieron completar esa operación aquí.


## 2026-10-20 · Panel de investigación visual, D1 local verificada y primer piloto documental

**Objetivo del plan:** mejorar la preparación editorial del canal, probar con D1 real (local) y preparar el primer episodio con investigación primaria; mantener voz original y política de cero pagos.

### Cambios reales en `main`

1. **Editor visual usable desde el panel**: `public/dossier-editor.js` y actualizaciones de `public/app.js`, `public/index.html`, `public/style.css`.
   - Formularios guiados de fuentes/documentos, afirmaciones agrupadas por escena, evidencia con fuente, sección/página y estado, responsables de la revisión, y derechos de voz/imágenes/música/video/gráficos.
   - Añadir/quitar evidencias, fuentes adicionales y afirmaciones manteniendo condiciones de integridad (cada escena al menos una; sin suprimir la última voz; fuente del guion no se borra desde el expediente).
   - Edición JSON relegada a opción avanzada; se importa explícitamente y no equivale a autorizar. Cambios sin guardar impiden acreditar; controles responsivos para móvil.
   - Pruebas de funciones editoriales en `tests/test_dossier_editor.mjs`; GitHub CI [39523541399](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39523541399) **success**. No hay despliegue de esta UI confirmado en Cloudflare.

2. **Prueba real del Worker con D1 local usando Wrangler**: `tests/e2e_worker_local.mjs` y workflow `.github/workflows/worker-d1-local-e2e.yml`.
   - [GitHub Actions 39523829006](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39523829006): **success**. Instala Wrangler, ejecuta **ambas migraciones solo en D1 local aislada**, confirma que la tabla `editorial_dossiers` existe, levanta el Worker y prueba por HTTP la autenticación, creación, expediente pendiente, bloqueo 409, acreditación, aprobación, ausencia de token de dispatch real, revocación y registro de eventos.
   - El disparador `push` fue **temporal de una única prueba**, eliminado después (commit `15be8962`), por lo que el workflow quedó solo manual. **No tocó D1 remota, no desplegó ni despachó videos**.

3. **Corrección de duplicados de render**: `src/worker.js` reserva atómicamente `approved → queued` en D1 antes de llamar a GitHub Actions; evita disparar el mismo trabajo dos veces en simultáneo. Ante rechazo explícito de GitHub, restaura `approved`; si falla la red y el resultado es incierto, conserva `queued` y exige inspección manual de Actions para evitar duplicados. Además, revoca la acreditación ANTES de actualizar un guion, evitando modificaciones parciales que dejen un antiguo visto bueno.
   - `tests/test_editorial_gate.mjs` cubre duplicados, rechazo HTTP, fallo de red. GitHub CI [39524141335](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39524141335) **success**; un commit intermedio falló por el simulador antiguo y se corrigió en el commit de pruebas siguiente.
   - `GET /dossier` tampoco muestra acreditación cuando el expediente no sigue estructuralmente completo.

4. **Primer piloto editorial basado en fuentes públicas originales**: `research/blackberry/brief_investigacion.md`, `research/blackberry/expediente_preliminar.json` y `tests/test_blackberry_research.py`.
   - Tema candidato: **«BlackBerry: el gigante que tuvo que cambiar de negocio»**; líneas narrativas desde RIM (fundada en 1984), la introducción del iPhone en 2007, App Store de 2008, transformación a software en 2016 y cierre de servicios heredados en 2022 hasta su negocio de software seguro.
   - **Seis fuentes primarias** de Apple y BlackBerry con URLs y localizadores concretos; **ocho afirmaciones** trazables y esquema de 8 bloques para futuro documental de ~12 min.
   - **Ninguna afirmación está falsamente marcada verificada por un editor**: todas siguen `pendiente`, igual que licencias de voz, imágenes y música. El material no es todavía un guion factual final, investigación exhaustiva, ni autorización de producir/publicar. El guion debe incorporar información financiera independiente, revisar causalidad y obtener recursos licenciados. CI [39524514168](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39524514168) **success**.

### Estado, bloqueos y próximos pasos

- **Confirmado:** código en `main`, CI Node/Python exitosa, prueba E2E con D1 **local** real; voz de 43,296 segundos previamente aceptada. Ningún token privado revelado, servicio pago activado ni canal YouTube publicado.
- **Pendiente:** aplicar `0002_editorial_dossiers.sql` a la base **remota** Cloudflare y confirmar despliegue Worker+panel. El conector Cloudflare continúa fallando al acceder a la cuenta, por lo que **no se hicieron cambios remotos ni se puede declarar producción actualizada**. Ruta segura documentada en `docs/DESPLIEGUE.md`.
- **Pendiente:** contrastar formalmente cada fuente del piloto BlackBerry con un editor humano, conseguir fuentes independientes y derechos completos de material/voz, escribir narración original total, storyboard, primera prueba de video 8–14 min y QA.
- **Pendiente:** preparar reconciliación segura de trabajos con `dispatch` de resultado incierto, sin reintentos automáticos ni duplicados; pulir los formularios con pruebas de usabilidad en móvil tras el despliegue.
- **Orden siguiente:** D1 remota → Worker y panel remoto → ensayo autenticado con expediente real no publicado → investigación/comprobación editorial → licencia de voz y recursos → producción piloto de video. Todas las operaciones directamente en `main`.


## 2026-10-20 · Avance real: motor autónomo de investigación con IA local (Fase 2)

**Pedido del propietario:** continuar el avance y que sea la IA quien investigue los documentales, no el usuario. Trabajado directamente en main y siguiendo AGENTS.md / PLAN_PROYECTO.md.

### Trabajo implementado

- **tools/research_engine.py**: modo dossier (visita URLs de fuentes registradas y extrae pasajes candidatos vinculados a afirmaciones) y modo tema libre (busca autónomamente en MediaWiki y lee artículos secundarios). Guardias HTTPS/DNS/hosts internos, redirecciones y tamaños máximos; hashes de contenido, URLs de origen y final, errores distinguibles, fragmentos breves. Archivos de salida: reporte_investigacion.json, LECTURA_PRELIMINAR.md y evidencia_para_ia.txt. Los estados siguen en "pending_human", aunque exista pasaje coincidente.
- **tools/local_research_ai.py**: genera un borrador original a partir de pasajes documentales mediante Qwen/Qwen3-0.6B CPU, sin API generativa facturable. Rechaza generación sin evidencia; metadatos indican modelo, hashes, citas y ausencia de aprobación. Se añadió control de cifras fuera de pasajes de la fuente citada para detectar alucinaciones numéricas (no certifica exactitud histórica).
- **.github/workflows/research-ai-cpu.yml**: workflow exclusivamente MANUAL (tras un disparo controlado único y reversible) que ejecuta pruebas, consulta documentos y usa Qwen local. Acepta un tema libre o, en blanco, dossier BlackBerry; artifacts de 3 días. **No activa publicación ni cambia narrador canónico.**
- **.github/workflows/research-topic-smoke.yml**: prueba de descubrimiento desde un único tema en GitHub; disparo puntual revertido a workflow_dispatch. Sin servicio de pago ni publicación.
- **tests/test_research_engine.py** y **tests/test_local_research_ai.py**: simulaciones offline de límites y fuentes, bloqueo por falta de evidencia, búsqueda genérica y fechas numéricas inventadas.
- Documentación técnica docs/MOTOR_INVESTIGACION.md y auditoría concreta research/blackberry/qa_primer_borrador_ia.md.

### Evidencia real (no confundir tests con investigación completa)

1. **[Run 39528648495](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39528648495)**, success: de seis URLs primarias del dossier BlackBerry, **tres legibles** (S01-S03), tres bloqueadas/no analizables (S04-S06), y **cinco pasajes candidatos** para ocho afirmaciones pendientes. El modelo Qwen local 0.6B generó un borrador de **722 caracteres**, cita detectada [S01], 1:08.66 de fase de IA (incluye carga/descarga del modelo) y memoria RSS máxima 4 781 824 KiB (~4.56 GiB). Artefacto [12314626338](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39528648495/artifacts/12314626338). Los resultados fueron descargados e inspeccionados, no solo verificado un workflow verde.
2. **Error factual real detectado:** el texto IA escribió que la IPO en Toronto fue **10 de octubre de 1997**; S01 recuperada decía **28 de octubre de 1997**. Se añadió guardia audit_numeric_support con pruebas posteriores, que alertaría por esa cifra 10 ausente en pasajes de S01. La ejecución inicial **es anterior a esa corrección** y sigue siendo un borrador defectuoso; no se declara guion verificado ni renderizable.
3. **[Run 39529286991](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39529286991)**, success: con solo el tema BlackBerry, buscó y descargó **3/3 artículos secundarios** sin dossier manual. Cero hechos verificados automáticamente; es etapa de descubrimiento, todavía no investigación con fuentes primarias de cualquier tema.
4. **CI [39529112648](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39529112648)**, success: pruebas de detección de una fecha inventada. Los commits posteriores ampliaron el modo tema libre y mantuvieron la batería en verde.

### Bloqueos y próxima secuencia

1. **Investigación autónoma más rigurosa:** descubrir fuentes primarias e independientes desde tema libre, resolver PDF/reportes anuales con referencias precisas, detectar contradicciones y hechos ausentes, en vez de confiar solo en Wikipedia o un pasaje similar.
2. **Guion completo:** convertir evidencia contrastada en historia de 8–14 minutos con citas por escena, control de duración y voz original aprobada, sin alucinar cifras/causalidad.
3. **Integración del panel de producción:** actualmente la investigación ya funciona por GitHub Actions manual, pero **NO** está conectada al botón del panel. Se debe aplicar la migración 0002 D1 **remota** y desplegar Worker/GUI; Cloudflare de esta sesión no responde y **no se afirma que esté hecho**.
4. **Licencias y QA:** referencia de voz canónica SHA-256 78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d sin cambios. Los derechos comerciales de la referencia, música y recursos siguen pendientes. El sistema no sube a YouTube.
5. **Costos:** modelo ejecutado localmente en GH Actions, sin API de pago, pero vigilar minutos y cuotas de GitHub; workflows intensivos quedan solo manuales.

**Estado correcto:** primer motor de investigación y propuesta por IA probado; calidad editorial insuficiente para publicar; investigación primaria universal, desarrollo completo de guiones, Cloudflare remoto y publicación siguen pendientes. Todo realizado en main y documentado.

## 2026-10-20 · Investigación IA activable desde el panel (Fase 2, main)

### Objetivo
Continuar el motor de Factor de Gigantes mientras la laptop HP de 12 GB está descargada: la investigación se ejecuta en GitHub Actions con CPU, sin exigir una GPU local, sin servicios de pago por API y sin producción/publicación automática.

### Desarrollo real en la rama principal
- src/research-control.mjs: nuevo módulo de despacho seguro hacia research-ai-cpu.yml, únicamente ref main. Valida el tema, verifica el consentimiento, repo fijado, secreto exclusivo de Worker, máximo nominal de 4 solicitudes por día UTC y bloqueo de mismo tema/día con unicidad SQL. GitHub HTTP 204 equivale a solicitud aceptada, **no** a investigación terminada. Los rechazos y resultados de red inciertos se registran y no se reenvían automáticamente.
- migrations/0003_research_requests.sql: tabla nueva de solicitudes; conserva migraciones y datos anteriores. Estado reserved, sent, unknown o rejected con timestamps; UNIQUE(topic_key, day_utc). La cuota se comprueba en D1 por fecha, y la deduplicación es atómica. No es un procesador de trabajos ni monitor de finalización.
- src/worker.js: nuevas rutas privadas GET y POST /api/research bajo ADMIN_TOKEN, sin llamadas a render.yml o YouTube. HTTP 503 específico cuando falta la migración o token GitHub. La ruta del renderizador no puede utilizar este endpoint.
- public/index.html, public/app.js: sección «Investigar con IA» con tema, confirmación del gasto de minutos GitHub Actions, historial, enlace a resultados y errores legibles. No guarda ADMIN_TOKEN en disco.
- .github/workflows/research-ai-cpu.yml: usa la carpeta de resultados genérica dist/investigacion y artefacto factor-investigacion-ia-cpu. Sigue siendo manual y de CPU, sin nuevas generaciones automáticas.
- tests/test_research_control.mjs, tests/test_editorial_migration.py: pruebas para autenticación, cuota, rechazo/no respuesta de GitHub, deduplicación, compatibilidad de las tres migraciones y protección de datos previos. .github/workflows/check.yml ejecuta las nuevas pruebas.

### Verificaciones realizadas
- [GitHub CI 39544634359](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39544634359) completó success con los nuevos tests de control y migración SQL.
- [GitHub Actions D1 local E2E 39544778750](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39544778750) completó success: ejecutó migraciones 0001, 0002 y 0003 en D1 local Wrangler y levantó un Worker real; verificó API autenticada y denegación de envíos cuando el token GitHub no está configurado. El disparador temporal de push fue retirado inmediatamente; el workflow volvió a ejecución manual.
- Se intentó consultar Cloudflare conectado pero su herramienta devolvió un error interno. Por tanto, NO se aplicaron tablas remotas, NO se ha verificado despliegue de la nueva interfaz, NO se ha enviado una investigación real desde el panel de producción.
- En esta entrega NO se ejecutó Qwen pesado, NO se consumió ninguna API pagada y NO se cambió la voz canónica del canal.

### Próximas tareas prioritarias
1. Resolver conexión de Cloudflare; respaldar D1, aplicar migraciones 0002 y 0003 remotas, verificar las dos tablas, desplegar Worker/public de main y probar una investigación voluntaria mediante el nuevo botón. No confundir E2E local con producción.
2. Conectar resultados reales de GitHub Actions al panel (estado de ejecución y enlaces directos comprobados) sin exponer secretos ni gastar minutos por reintentos.
3. Avanzar búsqueda automática de fuentes PRIMARIAS, documentos PDF, contraste de datos y guion de 8–14 minutos; el borrador Qwen anterior tiene un error factual documentado, por eso no se publica ni se considera investigación terminada.
4. Confirmar derechos comerciales de voz y audiovisuales; retomar guion y montaje cinematográfico con identidad vocal aprobada, sin necesitar comprar equipo hasta conocer GPU de la laptop.

**Estado:** código + pruebas CI + integración con D1 LOCAL confirmados en main; despliegue Cloudflare REMOTO, uso real del botón, investigación documental completa y publicación pendientes.

## 2026-10-21 · Fase 2: seguimiento del investigador + descubrimiento de webs oficiales

**Contexto del avance:** el propietario pidió continuar sin depender de la batería/GPU de su laptop. Se trabaja **exclusivamente en `main`** de `eler30mr-star/FactordeGigantes`. No se modificó la voz original ni `render.yml`, y no se publicaron videos.

### Implementación comprobable

1. **Seguimiento de investigaciones por ejecución real de Actions:** se añadió `request_id` opcional a `.github/workflows/research-ai-cpu.yml` y `run-name` específico. `src/research-control.mjs` despacha el UUID de cada investigación y permite consultar hasta 50 runs recientes por API GitHub autenticada; la correlación exige título, rama `main`, tipo de evento, ID numérico y URL oficial correctos. `GET /api/research?runs=1` devuelve el run y su estado/conclusión, o marca consulta no disponible. Un HTTP 204 de despacho no demuestra ejecución exitosa. El panel `public/app.js` diferencia cola, ejecución, éxito y fallo, con acceso a Actions; solo consulta el estado tras iniciar la investigación o pulsar «Actualizar».
2. **Pruebas de protección y trazabilidad:** `tests/test_research_control.mjs` cubre URLs falsas, ramas distintas, respuestas 403, timeouts, runs ajenos y ausencia de estados confirmados. GitHub CI [39587493924](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39587493924): `success`. El resultado de este test usa respuestas simuladas de GitHub: falta verificación del botón con Worker/D1 remotos.
3. **Descubrimiento independiente de posibles sitios corporativos:** `tools/primary_source_discovery.py` investiga páginas vinculadas al tema mediante la API MediaWiki y la propiedad `P856` de Wikidata. Rechaza hosts privados/no HTTPS mediante `tools/research_engine.py`, pone límites de documentos, solo guarda pasajes breves y jamás marca hechos o licencias verificados. `tests/test_primary_source_discovery.py` verifica descubrimiento, falta de enlaces, fallos de red y protección URL. Se integró al workflow de investigación en temas libres, con advertencias y ejecución no bloqueante.
4. **Pruebas externas y corrección:** primera [39587995688](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39587995688), `success` pero **0 sitios** al inspeccionar dos resultados. Se amplió la búsqueda para examinar hasta cinco entidades y se repitió [39588198172](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39588198172), `success`: **1 candidato de cinco artículos**: `BlackBerry Limited`, `https://blackberry.com` desde Wikidata. **La página no se pudo leer** (`ValueError`); hay URL candidata, NO evidencia factual. No se afirmó haber verificado un hecho. Artefacto [12340022602](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39588198172/artifacts/12340022602) con `fuentes_oficiales_candidatas.json`.
5. Los workflows usados para una prueba de fuente real fueron restaurados inmediatamente a `workflow_dispatch` manual: **sin nuevas ejecuciones continuas, proveedores de pago ni publicación automática**. `docs/MOTOR_INVESTIGACION.md` detalla contratos y limitaciones.

### Bloqueos y siguiente tarea prioritaria

- **Cloudflare remota sin acceso:** la herramienta de Cloudflare devolvió error interno otra vez. NO se ha aplicado D1 0002/0003 ni desplegado el panel nuevo, ni se ha comprobado correlación real entre solicitud y Actions desde el Worker publicado.
- **Primarias:** obtener contenido original efectivo de sitios oficiales o documentos reguladores/financieros, con fecha y página; `P856` es solo una pista de la entidad. Contrastar datos de fuentes independientes y corregir el borrador Qwen anterior con error IPO.
- **Investigación y guion:** generar narración completa de 8–14 minutos únicamente tras respaldar las afirmaciones, licencias de material visual y de voz. Mantener el flujo manual controlado de GitHub sin cobrar APIs y respetar `main`.

**Estado preciso:** código implementado y CI verde; descubrimiento de un sitio oficial candidato comprobado externamente; enlace no descargado; funcionalidad remota y documental de producción aún **pendientes**.


## 2026-10-21 · Investigación de PDF con evidencia y páginas reales (Fase 2, `main`)

**Pedido del propietario:** continuar avances de Factor de Gigantes, respetando exclusivamente la rama principal, historial y la meta de investigación automática sin APIs de pago ni dependencia de su laptop.

### Implementación efectuada

1. **Nuevo analizador PDF:** `tools/pdf_sources.py`, descarga pública HTTPS protegida por validación DNS/redirecciones, tamaño máximo 4 MB, máximo 35 páginas, límites de texto y cabecera `%PDF-`, extracción textual local mediante `pypdf==5.9.0`. Sin OCR ni extracción de fotos. Rechaza PDFs cifrados/corruptos/no válidos y formatos de red inesperados.
2. **Integración de extremo a extremo dentro del investigador por expediente:** `tools/research_engine.py` acepta ahora HTML y PDF sin modificar la lista de fuentes del usuario. Registra `document_type`, `pdf_total_pages`, SHA-256 del archivo y `locator: PDF página N` por evidencia localizada. También incorpora la página al contexto de Qwen y al informe de lectura; deja `facts_verified_automatically=0`, `rights_verified_automatically=0`, `production_ready=false`.
3. **Comprobación y CLI:** `tools/pdf_probe.py` permite consultar un documento PDF original por URL HTTPS y búsqueda; el informe es JSON de referencias, no una redistribución del PDF. `tests/test_pdf_sources.py` fabrica un PDF de dos páginas para comprobar correspondencia de localizador, compatibilidad HTML y rechazo de entradas peligrosas. Workflows `check.yml` y `research-ai-cpu.yml` instalan el parser CPU versionado.
4. **Ejecución real comprobada:** [GitHub Actions 39592681746](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39592681746), `success`: documento original `https://arxiv.org/pdf/1706.03762` sobre Transformer (Vaswani et al.), PDF de **15 páginas**, **328 bloques** y **2 pasajes candidatos** en **página 1 y página 2**. Cero afirmaciones aprobadas. Se conserva artifact temporal de resultados, no el PDF completo.
5. **Tests:** batería general [39592490158](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39592490158) `success`. Se detectó y corrigió un problema de literal UTF-8 en un fixture que hacía fallar un commit intermedio; no se declaró listo hasta la ejecución verde. Workflow real de prueba restaurado a `workflow_dispatch` manual después de una única ejecución.

### Estado y bloqueos verificados

- **Código y pruebas en `main`: listos para la siguiente fase de investigación**. No se creó rama secundaria ni PR; no se usó servicio TTS o IA de pago, no se alteró `render.yml` ni la voz original aprobada.
- **PDFs grandes/escaneados y tablas financieras:** sin resolver. No presentar el texto de un PDF reducido a los primeros 35 folios como análisis suficiente de un informe corporativo completo; se debe obtener sección/página relevante con controles de integridad y verificación independiente.
- **Descubrimiento autónomo de PDFs de emisores/reguladores:** pendiente. En este ensayo se proporcionó una URL primaría explícita; aún falta encontrarlas por tema sin intervención humana.
- **Cloudflare:** la herramienta conectada `whoami` respondió error interno nuevamente; no se ejecutaron migraciones D1 remotas 0002/0003 ni se verificó despliegue del nuevo panel. El bloqueo de producción sigue vigente.
- **Control humano y licencias:** la lectura automática no acredita fechas, decisiones, cifras ni derechos de contenido audiovisual y voz. Sigue prohibido publicar un documental sin verificaciones.

### Próximo trabajo

1. Descubrir fuentes originales financieras y PDF por entidad, clasificar documentos, preservar fecha, URL, versión y página sin inventar datos. Validar con una prueba de fuente corporativa y contraste secundario independiente.
2. Crear auditoría de contradicciones entre cifras y fuentes, apoyar guion original por escena y revisión humana sin convertir un borrador Qwen en vídeo publicable.
3. Tras resolver Cloudflare, migrar D1 remota, desplegar Worker/panel, probar investigación y lectura de estado reales en producción.
4. Mantener la continuidad vocal aprobada y presupuesto gratuito para la prueba de producción audiovisual más larga, con derechos comerciales pendientes.

## 2026-10-21 · Infraestructura real recuperada y desplegada (rama obligatoria `main`)

**Solicitud autorizada:** propietario confirmó que se deben aplicar migraciones 0002 y 0003 y continuar avanzando sin ramas aparte, pagos por API ni publicaciones automáticas.

### Verificaciones y operaciones efectivamente realizadas

1. **Conexión correcta de Cloudflare:** los errores anteriores surgieron porque había dos cuentas conectadas y la herramienta requería `link_id`. Se seleccionó expresamente `Factor`, no `Primary`. Cloudflare confirmó el Worker `factor-de-gigantes` y la D1 `factor-de-gigantes-db` enlazada con el identificador esperado.
2. **Resguardo de datos previo:** se obtuvo un bookmark de Time Travel de la D1 y se solicitó una exportación SQL de las tablas `jobs` y `events`. Cloudflare API respondió estado `complete` y URL firmada temporal. La copia **no fue descargada permanentemente fuera de Cloudflare**; el enlace firmado vence y cualquier recuperación depende de la retención del servicio. No se publicaron datos de usuarios ni secretos.
3. **Migraciones remotas auténticas:** `migrations/0002_editorial_dossiers.sql` y `migrations/0003_research_requests.sql` leídas desde `main` y comparadas con los blobs esperados; ambas aplicadas mediante API SQL de D1 con `success`. Se verificaron tablas `editorial_dossiers`/`research_requests` e índices, sin anomalías en `PRAGMA foreign_key_check`. La API denegó `PRAGMA integrity_check` (`SQLITE_AUTH`), por lo que **no** se certifica un chequeo de integridad profundo.
4. **Preservación comprobada después de migrar y desplegar:** `jobs=1`, `events=8`, `editorial_dossiers=0`, `research_requests=0`. Mismo conteo de trabajos y eventos antes/después de las operaciones. Estas migraciones se ejecutaron por Cloudflare SQL API, **no** por Wrangler migrations, y `d1_migrations` todavía no existe. No crear otra D1 ni repetir SQL por rutina.
5. **Primer redespliegue controlado:** Cloudflare Builds conectado a `eler30mr-star/FactordeGigantes`, `main` y `npx wrangler deploy`. Build `729fb21f-d1d9-4f2f-999e-7e6f8cbd47de` `success`, commit `79a2ba80b95022e90acb696c81ebaa610112fa55`. El origen Worker, ASSETS, DB y secretos se conservaron.
6. **Protección de gasto por concurrencia:** se corrigió `src/research-control.mjs` para reservar cuota usando una única sentencia `INSERT OR IGNORE ... SELECT ... WHERE COUNT(*) < 4`, en lugar de dos operaciones con carrera. Consulta posterior diferencia duplicados HTTP 409 de límite diario HTTP 429. `tests/test_research_control.mjs` incorpora caso de dos peticiones simultáneas con un solo hueco; la prueba no dispara GH Actions real.
7. **Calidad obligatoria en Cloudflare Builds:** se configuró el trigger de `main` para ejecutar `node --check` y `node --test` antes del deploy, bloqueando builds con test rojo. Build `720b0c1e-b0ac-4dda-92c3-4c7110f8f862` `success`, 21 tests JS aprobados, 0 fallidos y Worker publicado.
8. **Nuevo diagnóstico interno del panel:** `src/system-readiness.mjs`, ruta autenticada `GET /api/system/status`, panel `public/index.html`/`public/app.js` y `tests/test_system_readiness.mjs`. Comprueba por lectura de sqlite_master cuatro tablas y muestra banderas de presencia de configuración GitHub, siempre sin exponer el valor de ningún token, sin contactar GitHub ni inferir autorización para publicar. HTTP 401 sin ADMIN_TOKEN, HTTP 405 con método POST; no modifica datos.
9. **Despliegue final auditado:** Cloudflare build `17eaaf34-42eb-4427-859b-0f0b8d92b262`, `success`, commit `7ccc9d4e6cf224bbc22333722e0127c1f932b4e6` de `main`, **25 pruebas Node aprobadas y cero fallos**, 2 assets nuevos/modificados subidos, versión Worker `a7695b06-938e-402e-a4ba-809fc2f2ec02` activada al 100 %. Lectura remota posterior del bundle verificó la ruta `/api/system/status` y la reserva atómica; D1 volvió a responder con los mismos datos 1/8/0/0. El Worker mantiene `ADMIN_TOKEN`, `RENDERER_TOKEN`, `GITHUB_DISPATCH_TOKEN` y D1.
10. **Monitoreo posterior al deploy:** `tools/production_smoke.py` y una comprobación no bloqueante añadida a `.github/workflows/check.yml` permiten vigilar HTML público, `/app.js`, `/health` y barrera de autenticación; esta comprobación **no se ha acreditado como ejecutada satisfactoriamente en la última versión**. No hay simulación de usuario autenticado por ChatGPT ni falsa afirmación de que se generó un documental nuevo.

### Próximas tareas prioritarias

1. Comprobar desde navegador del propietario que el panel actualizado abre, admite su token administrativo y muestra «Estado del sistema» y «Investigar con IA». Sin compartir secretos en chat.
2. Disparar **una** investigación IA real desde el panel solo cuando el propietario indique el tema; cotejar Action vinculado, informe, fuentes y borrador. Los Qwen experimentales anteriores no son guiones completos y han mostrado alucinaciones factuales.
3. Mejorar investigación primaria autónoma a PDFs oficiales/regulatorios y números con páginas, contraste entre fuentes y rechazo de contradicciones antes de narrar.
4. Construir narración documental original de 8–14 min y montaje audiovisual dentro del presupuesto de GitHub Actions, con QA, verificación de derechos de voz/visual y autorización humana. Sin publicación automática en YouTube.

**Estado final:** recuperación del conector, SQL D1 remota, dos despliegues, prueba de cuota y diagnóstico privado **COMPLETADOS Y VERIFICADOS**; uso autenticado real del panel, generación IA desde nuevo botón y documental completo **PENDIENTES**. Todo commit en `main`.

## 2026-10-21 · Auditoría editorial automatizada y documentos originales SEC (rama `main`)

### Cambios realmente implementados

1. `tools/editorial_audit.py`: examen conservador de afirmaciones existentes, URLs de procedencia y posibles huecos de evidencia. Distingue falta de pasajes, falta de corroboración desde más de un dominio, fuentes secundarias, fechas y cifras no coincidentes. Produce `AUDITORIA_EDITORIAL.json` con **cero hechos confirmados** y sin permisos de render/publicación. Una alerta es una cuestión a revisar, no una contradicción confirmada.
2. Cada `save_report()` en `tools/research_engine.py`, tanto desde expediente como desde tema libre, genera también `ESCALETA_DOCUMENTAL_10MIN_NO_APROBADA.md`. Contiene **12 bloques con duración total 600 s**, ID de afirmaciones candidatas y tareas de narración/visuales pendientes. La escaleta NO es un guion final ni una grabación.
3. `tools/edgar_discovery.py`: investigación autónoma de identificadores candidatos desde el tema mediante MediaWiki → Wikidata P5531 → SEC EDGAR. Si se consigue `submissions/CIK*.json`, se listan como posibles originales formularios 10-K/10-Q/20-F/40-F/8-K/6-K, fechas, ID de archivo y enlaces oficiales de SEC. Protección de CIK/URLs, máximo ocho documentos por entidad y registro explícito de bloqueo HTTP. **No descarga ni verifica los informes y no inventa cifras**.
4. El workflow manual `.github/workflows/research-ai-cpu.yml` agrega los contratos y una etapa acotada de búsqueda SEC por tema; el investigador Qwen recibe solo el informe de pasajes previamente recopilado, sin usar la mera lista SEC como hechos. Nuevos artefactos esperados: `AUDITORIA_EDITORIAL.json`, `ESCALETA_DOCUMENTAL_10MIN_NO_APROBADA.md` y, en investigaciones de tema libre, `sec_edgar_documentos_candidatos.json`.
5. `tests/test_editorial_audit.py` contiene 5 pruebas sobre cifras, fechas, falta de fuentes y escaleta; `tests/test_edgar_discovery.py` contiene 6 pruebas sobre IDs, formato de archivos, SEC inaccesible y ausencia de pruebas falsas. Ninguna test usa API paga ni consume tokens de Qwen.

### Verificación efectiva y despliegue

- **Cloudflare Builds `c6bfd5a1-3cd9-4201-b945-8d653f58f5a3`: `success`.** Ejecutó 25 pruebas JavaScript y las **11 pruebas Python**, todas verdes, al compilar el commit `cc90a481878d9e2c7ddca7c75dd1a28a09b73d71` de `main`. Wrangler completó despliegue de la versión `c110910e-c4ac-4561-bb06-110c40be0fef`. Para futuras compilaciones Cloudflare tiene incorporado el chequeo Python junto con el control previo JavaScript.
- Se preparó prueba independiente `.github/workflows/edgar-smoke.yml` con tema real Apple Inc., sin Qwen ni render. **Aún no se verificó un resultado real de SEC de esa prueba**; no afirmar accesibilidad ni existencia de archivos regulatorios por un test simulado. Su disparador temporal de push fue retirado y quedó solo manual.
- No se modificaron D1, credenciales, voz canónica, licencias, publicaciones YouTube ni la rama de trabajo. Los resultados de extracción dependen de la disponibilidad remota del proveedor y de sus reglas de acceso.
- La implementación queda desplegada en el repositorio conectado y el pipeline manual; no se ha ejecutado Qwen pesado en este avance ni se ha hecho prueba autenticada del nuevo botón desde el navegador del propietario.

### Siguientes pasos que no deben omitirse

1. Comprobar acceso real a SEC o registrar su rechazo, obtener un filing original íntegro y extraer hechos por sección/página con límites CPU. Contrastar CIK con identidad del emisor y con datos de otros organismos.
2. Construir motor para comparar **métrica + unidad + empresa + periodo** sin llamar contradicción a cifras de años diferentes, antes de redactar narración.
3. Redactar y verificar documental original completo 8–14 min; auditar frases, visuales, subtítulos y licencias de locución. Los 12 bloques son solo estructura pendiente de desarrollar.
4. Validar acceso real desde el panel de producción y una investigación voluntaria elegida por el propietario, con seguimiento de ejecución. Mantener desactivada subida automática a YouTube.

**Estado:** código probado y desplegado, sin hechos verificados ni episodio final. La fase documental tiene avances de ingeniería, pero la producción audiovisual continúa pendiente.

## 2026-10-21 · Comparador SEC XBRL, expediente consolidado y enlaces corporativos (main)

### Hito técnico implementado y probado

1. **Datos financieros estructurados:** `tools/financial_facts.py` utiliza el endpoint público XBRL de SEC `data.sec.gov/api/xbrl/companyfacts/CIK*.json`, con límite estricto de 9 MB, HTTPS, validación DNS pública, CIK exacto y taxonomía `us-gaap`. Conservar solo métricas explícitas, unidad USD, número decimal finito, fechas inicial/final, año/periodo fiscal, formulario y accession; generar `SEC_XBRL_HECHOS_NO_VERIFICADOS.json`. No hay interpretación libre ni datos fabricados.
2. **Comparador seguro:** agrupa únicamente por CIK, etiqueta de métrica, moneda, tipo de periodo y fechas exactas. Nunca mezcla ejercicios distintos o métricas diferentes. Si dos valores difieren para el mismo periodo, emite alerta `same_period_different_reported_values_review_required`, no una contradicción verificada ni fraude. No prueba autoría ni derechos.
3. **Flujo real controlado:** `tools/financial_probe.py` toma un CIK candidato del descubrimiento EDGAR y prueba como máximo una consulta XBRL. Si SEC rechaza, registra estado `sec_unavailable_or_unreadable`, tipo/código HTTP y cero observaciones verificadas. El workflow `research-ai-cpu.yml` incorpora esta etapa solo para tema libre y sin obligar a que XBRL sea accesible; Qwen y render no toman decisiones editoriales automáticas.
4. **Paquete para revisor:** `tools/editorial_package.py` consolida pasajes del investigador, auditoría, documentos SEC candidatos y XBRL opcional. Escribe `EXPEDIENTE_EDITORIAL_PENDIENTE.json` y `EXPEDIENTE_PARA_REVISOR.md`, con localizadores, alertas, bloqueos y acciones pendientes por afirmación. `ready_for_narration`, `ready_for_render` y `ready_for_youtube` permanecen `false`.
5. **Fuentes alternativas cuando SEC no responde:** `tools/official_document_links.py` localiza, dentro de HTML corporativo previamente obtenido, hipervínculos realmente presentes hacia PDF, informes anuales y páginas de inversores. Sin crawling, suposiciones de URL ni descarga de archivos; hosts ajenos aparecen como candidatos externos. Integrado en `tools/primary_source_discovery.py`, con `linked_document_candidates` y conteo global.
6. **Pruebas y control antes de deploy:** `tools/production_preflight.sh` es ahora el comando de compilación de Cloudflare, con `node --check`, 25 pruebas JS y seis grupos de pruebas Python (34 casos). GitHub CI [39625136678](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39625136678) `success`; Cloudflare build `18d882b5-39f5-4524-aa13-1db876e3ebdb` `success` desplegó desde `main` commit `cb54813a158c957e4f3b57651c211fb57e53a572`, versión `1489175a-38ca-403a-9477-a2a466f39b4c`.
7. **Producción verificada tras desplegar:** lectura Cloudflare API confirmó la versión activa y D1 intacta: 1 trabajo, 8 eventos, 0 expedientes editoriales, 0 solicitudes de investigación. Se mantuvieron el Worker, la rama `main`, las credenciales originales y los bloqueos de publicación. No se inició una investigación pesada con Qwen ni un render.
8. **Pruebas externas SEC, límites reales registrados:** [39621724636](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39621724636) obtuvo 1 CIK candidato desde Wikidata para el tema Apple Inc. pero SEC `submissions` devolvió `HTTPError`, 0 filings recuperados. [39624310668](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39624310668) consultó XBRL con CIK de prueba conocido: `sec_unavailable_or_unreadable` por `HTTPError`, **0 hechos financieros reales**. Ambos workflows se dejaron solo manuales. Las cifras de las pruebas unitarias son datos artificiales, nunca referencias reales de Apple.

### Estado y próximos pasos no cerrados

- La etapa de comparación técnica está probada; **no se pudo contrastar un estado financiero real** porque la SEC bloqueó las solicitudes externas. No emplear intermediarios no autorizados ni falsear la fuente; buscar informes originales corporativos accesibles y conservar su URL/version/página.
- Los enlaces corporativos se detectan en HTML en pruebas; todavía no se comprobó un informe real de esa ruta ni se extrajeron sus tablas con unidad/período.
- Obtener al menos una pareja de cifras auténticas y comparables (empresa + métrica + periodo + unidad) y revisión humana de documentación primaria/secundaria.
- Convertir hallazgos validados en guion narrativo original de **8–14 minutos**, con contenido audiovisual legal y narrador cuya licencia comercial esté acreditada. Crear MP4 de prueba sin publicación a YouTube.
- Probar login y lectura autenticada del panel y ejecutar una investigación real desde el botón solo cuando el propietario elija tema explícito. Cero solicitudes consumidas de las cuatro diarias durante este trabajo.

**Resultado:** código, tests, documentación y despliegue del comparador / expediente en producción técnica completados, con datos de usuario preservados; acceso real SEC, hechos aprobados y documental completo todavía pendientes. Todo cambio en `main`, sin PR ni ramas secundarias.

## 2026-10-21 · Primer bloque narrativo documental con datos BlackBerry originales (main)

**Alcance:** el propietario pidió avanzar hacia contenido real, no seguir únicamente en infraestructura. Se mantuvo la regla obligatoria de modificar exclusivamente `main` y nunca publicar automáticamente a YouTube.

### Completado con evidencia

1. **Fuentes originales recuperadas:** `tools/blackberry_sources_pilot.py` descarga dos comunicados financieros PDF de BlackBerry Investor Relations (FY2024 y FY2025) y busca pasajes definidos con página física, SHA-256, URL y base contable. En [GitHub Actions 39630703040](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39630703040), prueba real `success`, descargó **2/2 PDF y localizó 5/5 datos**, en páginas 2 y 16. Datos localizados: ingresos FY2024 presentados entonces US$853 millones; US$218 millones vinculados a venta de patentes; ingresos FY2025 US$534,9 millones; QNX FY2025 US$236 millones; e ingresos FY2024 comparativos de US$759,1 millones incluidos en el comunicado de FY2025. Los PDF completos no se distribuyeron en los artefactos.
2. **Precaución esencial:** FY2024 US$853m reportados en 2024 y FY2024 US$759,1m como comparativo de 2025 no deben restarse ni utilizarse para tasas de crecimiento sin revisar cambios de alcance y operaciones discontinuadas. Una localización textual por máquina no equivale a verificación editorial.
3. **Paquete editorial actualizado:** `tools/editorial_package.py` puede sumar `HECHOS_BLACKBERRY_2024_2025_CON_PAGINAS.json` al expediente, conservando URL/página, base contable y banderas `pending_human`. `tests/test_editorial_package.py` cubre explícitamente los dos importes FY2024, su alerta de comparabilidad y la prohibición de aprobar automáticamente.
4. **Investigación Qwen piloto:** `.github/workflows/research-ai-cpu.yml` ejecutará el sondeo de estos PDF solo cuando el tema sea vacío (piloto BlackBerry), antes de consolidar el dossier. No significa que Qwen ya haya generado desde ese flujo un documental terminado.
5. **Primer texto narrativo real:** `research/blackberry/PRIMER_BLOQUE_NARRATIVO_FUENTES_REALES.md` contiene cuatro escenas originales (~3–4 minutos previstos), preguntas narrativas, cifras referenciadas, localizadores de documentos, ideas visuales sin licencia asumida y bloqueos específicos para revisión. Es un **borrador para evaluar**, no un guion de 8–14 minutos completo ni audio/MP4.
6. **Validación:** el workflow de prueba de PDF y las pruebas de contrato en `main` terminaron exitosamente; la comprobación de GitHub del commit narrativo fue [39631313656](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39631313656) `success`. La última ejecución CI observada [39631477093](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39631477093) también reportó `success`. Los cambios realizados en GitHub no demuestran por sí mismos la generación de un nuevo video ni la revisión comercial de medios.

### Pendiente prioritario

- Verificar de forma editorial las notas contables del 10-K completo, la clasificación de Cylance y las cifras complementarias de comunicaciones seguras y licencias antes de aprobar la narración.
- Obtener fuentes independientes para cronología BlackBerry, competencia, QNX y consecuencias; ampliar el borrador a un **guion original de 8–14 minutos** con cada dato vinculado a evidencia revisada.
- Auditar permisos comerciales del narrador y recursos visuales/musicales; luego generar un MP4 piloto como prueba, **sin subirlo automáticamente a YouTube**.
- Demostrar una investigación voluntaria desde el panel publicado, autenticada por el propietario; no consumir acciones pesadas sin su decisión explícita.

**Estado preciso:** dos documentos primarios efectivamente descargados y cinco pasajes localizados; primer bloque narrativo escrito y guardado en `main`; documental largo, grabación, render final y publicación todavía pendientes.

## 2026-10-21 · Primer guion documental LARGO BlackBerry y cronograma de 12 escenas (main)

### Objetivo de esta ejecución
El propietario pidió continuar el avance hacia un documental terminado, sin más pruebas aisladas de infraestructura. Se trabajó directamente en `main`, sin generar rama ni PR, sin ejecutar Qwen pesado, sin compras y sin publicar en YouTube.

### Entregables guardados en GitHub
- `research/blackberry/FUENTES_GUION_10MIN.json`: siete referencias directas/museísticas a los hechos narrados, con URL y alcance: Smithsonian sobre dispositivos tempranos, comunicados de 2016 de externalización de hardware, resultados FY2024/FY2025 de BlackBerry, 10-K FY2025 y circular corporativa FY2025. Una URL no acredita licencia audiovisual.
- `research/blackberry/GUION_DOCUMENTAL_11MIN_NO_APROBADO.md`: **12 escenas, 1.691 palabras de voz en off original y objetivo de montaje 11:50 (710 s)**. Desarrolla el origen y correo móvil, estrategia hardware 2016, QNX, Cylance y cuentas FY2024/FY2025. Utiliza identificadores de las siete fuentes al final de cada escena y propone visuales originales. La estimación de locución a 145 palabras/min es aprox. 11,7 min sin pausas; necesita medición de voz real y ajuste de escenas. No se presenta como audio grabado ni como video exportado.
- `tools/blackberry_script_quality.py` + `tests/test_blackberry_script_quality.py`: validación automática de 12 escenas, ritmo y tiempos contiguos, presencia de fuentes válidas y avisos de no aprobación. El reporte `QA_ESTRUCTURAL_GUION.json` marca explícitamente `factual_gate_passed=false`, `commercial_voice_license_verified=false` y `youtube_publication_authorized=false`.
- `tools/blackberry_edl.py` + `tests/test_blackberry_edl.py`: exporta `EDL_PREVIA_12_ESCENAS.json` con inicio, fin, duración, fuentes y propuesta de imágenes de cada escena. **No contiene pistas de voz, música ni imágenes**; `render_allowed=false` para todas las escenas. Sirve para planear el primer montaje futuro.
- `tools/production_preflight.sh` incluye los nuevos grupos de pruebas Python y la generación de ambos reportes de QA/EDL, de modo que una versión mal formada no pase al despliegue.
- El bloque financiero ya validado en [39630703040](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39630703040) aportó dos comunicados PDF verdaderamente descargados y cinco datos ubicados por página. El manuscrito conserva la advertencia esencial: **FY2024 US$853m reportado en 2024 ≠ FY2024 US$759,1m reformulado en 2025 para fines de comparación automática**.

### Estado de verificación
- CI del nuevo QA en GitHub [39634135450](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39634135450): `success`.
- CI del nuevo EDL en GitHub [39634462696](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39634462696): `success`.
- Al redactar este registro, el nuevo commit de actualización del plan `af604759` se había enviado a GitHub y su CI estaba en cola. **No confundir pruebas estáticas aprobadas con aprobación editorial, voz definitiva o MP4 verificado.**
- No se realizó una prueba de locución humana ni se cambió la voz canónica. No se verificaron derechos de imágenes/música, ni se modificaron tokens o D1. No se disparó una investigación pesada desde el panel.

### Siguientes prioridades de producción
1. Auditar escena por escena el manuscrito contra las fuentes, enfatizando historia de dispositivos, anuncio 2016, descripción QNX y reexpresión por Cylance; eliminar o reformular cualquier afirmación débil.
2. Crear visuales cinematográficos **originales y licenciables**, no copiar fotos del museo o capturas completas de documentos. Preparar assets versionados e identificación de permisos.
3. Acreditar derechos comerciales de narración aprobada. Producir un **audio real**, medir ritmo/duración, ajustar la EDL y generar un MP4 reproducible de prueba, **sin publicar automáticamente**.
4. Mantener el desarrollo en `main`, acompañar todo avance con esta bitácora y seguir dejando pendientes las pruebas reales de panel administrativo e investigación voluntaria.

**Estado:** existe un manuscrito narrativo de largo documental y una EDL preliminar estructurada. NO existe todavía MP4 final de 11:50, voz comercial validada ni visto bueno factual/licencias.

### Verificación final del guion y montaje — 2026-10-21

- **QA real GitHub Actions:** [39634858858](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39634858858), `success`. Se ejecutaron **5 pruebas de texto/citas + 2 de línea de tiempo**, cero fallos. El informe confirmó `ESCENAS=12`, `PALABRAS=1691`, `DURACION_SEGUNDOS=710`, `ALERTAS_ESTRUCTURALES=[]` y `AUTORIZACION_YOUTUBE=false`.
- Se generaron y archivaron **dos artefactos de control**: `QA_ESTRUCTURAL_GUION.json` y `EDL_PREVIA_12_ESCENAS.json`, disponibles en [artefacto 12359629466](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39634858858/artifacts/12359629466), sujeto a caducidad normal de GitHub Actions.
- `.github/workflows/blackberry-guion-qa.yml` volvió a **`workflow_dispatch` exclusivamente manual** inmediatamente después de la prueba; no se instaló un pipeline de publicación.
- En una consulta administrativa posterior a la prueba, la integración Cloudflare devolvió un bloqueo del servicio de herramientas; **no se afirmó haber comprobado o redeplegado una versión nueva del Worker desde ese conector**. La comprobación de GitHub y los commits a `main` sí son reales y están confirmados.
- Pendiente crítico: comprobación humana del texto íntegro y de la atribución de cada afirmación, validación de licencia de la voz canónica, creación de visuales de uso lícito y generación de audio + MP4 de prueba sin YouTube. Un QA estructural `success` no equivale a documental listo.

## 2026-10-21 · Primera previsual MP4 reproducible — BlackBerry, 12 escenas

**Meta de esta iteración:** obtener un archivo audiovisual real y comprobar su duración y codec, sin comprar APIs, usar la laptop descargada ni publicar contenido no aprobado.

### Código y archivos realmente producidos en `main`

- `tools/render_blackberry_animatic.py` lee el guion y la EDL verificable de doce escenas; dibuja 12 tarjetas originales de estilo documental mediante Pillow (fondo, rejilla, símbolos geométricos, títulos y progreso). No utiliza imágenes de archivo ni descargadas, no incluye música ni locución y mantiene rótulos visibles de uso interno. Empaqueta el resultado en H.264 MP4 sin audio con FFmpeg. Emite `ESTADO_PREVISUAL.json`.
- `.github/workflows/blackberry-previsual-mp4.yml` instala `Pillow==11.3.0` y `imageio-ffmpeg==0.6.0`, comprueba las siete pruebas de estructura/EDL, produce MP4, extrae sus metadatos y sube MP4+informes a GitHub Actions. La tarea queda `workflow_dispatch` manual, no vigilancia ni publicación recurrente.
- **Primera corrida [39635497277](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39635497277) fallida:** el runner no tenía `ffmpeg`. Se corrigió mediante FFmpeg empaquetado `imageio-ffmpeg` y un ejecutable accesible desde PATH, sin modificar el equipo físico.
- **Segunda corrida [39635649958](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39635649958) EXITOSA:** doce escenas convertidas en `BLACKBERRY_PREVISUAL_30S_SIN_VOZ.mp4`. Confirmación real: 30,04 segundos, 1280×720, codec H.264, 204.427 bytes; banderas `audio_present=false`, `youtube_publication_authorized=false`. El ZIP de [artefacto 12360967934](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39635649958/artifacts/12360967934) contiene MP4, `ESTADO_PREVISUAL.json` y `METADATOS_VIDEO.json`; caduca según política de Actions. Se descargó y se verificó con `ffprobe` local. El usuario recibió enlace de reproducción a la copia temporal de la conversación en `/mnt/data/blackberry_previsual/BLACKBERRY_PREVISUAL_30S_SIN_VOZ.mp4`.
- No se modificó D1, Cloudflare, secretos ni voz canónica; la integración Cloudflare no permitió verificar una compilación adicional en esta etapa. El pipeline de video funciona desde GitHub Actions en CPU, sin depender de la GPU/RAM de la laptop.

### Alcance preciso y próximos pasos

- **Hecho:** existe un MP4 real de previsualización **de 30 segundos** sobre la estructura de 12 escenas; gráficos originales con fondo, títulos y fuentes. **No** contiene la historia narrada ni sus escenas cinematográficas desarrolladas.
- **Pendiente:** confirmar/licenciar voz comercial, pasar narración de 1.691 palabras a audio, validar el ritmo real, producir visuales/animaciones originales por escena (sin copiar fotos de archivo), sincronizar 11:50 de montaje y generar MP4 completo de 8–14 minutos.
- **Pendiente:** auditoría factual de afirmaciones, evaluación editorial de materiales y aprobación de propietario antes de cualquier publicación en YouTube.
- Todo commit sigue en `main`, y el despliegue/pipeline automático de YouTube sigue deshabilitado.

**Resultado del turno:** GUION LARGO ✅ | FUENTES REGISTRADAS ✅ | QA + EDL ✅ | MP4 CORTO DE PRUEBA ✅ | AUDIO LICENCIADO ❌ | VIDEO DOCUMENTAL LARGO ❌ | PUBLICACIÓN YOUTUBE ❌.

## 2026-10-21 · Corrección audiovisual por comentario del propietario: movimiento Y audio

**Señalamiento recibido:** la previsual BlackBerry de 30 s solo mostraba textos y fondo casi fijo y carecía de audio. La crítica fue correcta: era una prueba de codificación, **no una muestra cinematográfica aceptable**.

### Implementación y resultados reales

1. **Identidad vocal recuperada sin sustituciones:** se leyó `assets/voice/approved/reference.json` y `tools/approved_voice.py`. La referencia exacta es `narrador_documental_aprobado.mp3` (12,336 segundos, SHA256 `78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d`). Su estatus es `approved_by_owner_for_editorial_reference`, **derechos comerciales pendientes**, no una nueva narración de 11 minutos. Se mantuvo sin tocar.
2. **Nuevo motor corto:** `tools/render_blackberry_motion_intro.py` dibuja fotogramas independientes con Pillow para cuatro actos de la introducción: teléfono con movimiento de cámara, red dinámica de mensajes, circuitos de software y aparición de título final. Cada frame usa una variación temporal; ya no son solo imágenes repetidas con texto. Usa audio MP3 aprobado con `-map 1:a:0` y lo codifica como AAC, H.264 720p a 24 fps, 297 frames. El resultado está marcado como `documentary_complete=false` y `commercial_rights_verified=false`.
3. **Pruebas:** `tests/test_blackberry_motion_intro.py` incluye cuatro casos de hash/duración de voz, diferencias reales entre fotogramas de una misma escena, identidad visual de los cuatro actos y rechazo de tiempos inválidos.
4. **Error identificado y corregido de CI:** primeras ejecuciones de `Comprobar base` [39636899012](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39636899012) y [39636975047](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39636975047) fallaron al importar Pillow. Se corrigió `.github/workflows/check.yml` para instalar `Pillow==11.3.0` junto con `pypdf`. **No ocultar fallos previos**.
5. **Prueba de generación auténtica:** GitHub Actions [39636975142](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39636975142) `success`; cuatro tests de movimiento y de voz aprobados, render MP4 `BLACKBERRY_INTRO_MOVIMIENTO_VOZ_REFERENCIA.mp4` de **12,33 segundos**, 1280×720, H.264 + **AAC**, 1 623 429 bytes. `PISTA_AUDIO_VERIFICADA=true`, `FOTOGRAMAS=297`, SHA de voz igual al canónico, `PUBLICACION_AUTORIZADA=false`. Descarga: [artefacto 12360694777](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39636975142/artifacts/12360694777).
6. **Verificación en contenedor:** ZIP descargado; FFprobe confirmó audio AAC, video H.264, 1280×720 y 12,3333 s. Se extrajeron imágenes en 0,8 / 3,8 / 6,9 / 10,4 s, que muestran diferentes actos visuales. El workflow `.github/workflows/blackberry-motion-voice.yml` quedó únicamente manual después de la corrida exitosa, sin publicación YouTube.
7. **Cuidado de interpretación:** esta muestra ahora **sí tiene movimiento y la voz original**, pero **sigue siendo animación gráfica conceptual**, no material cinematográfico realista ni el episodio narrado completo. El sonido es la muestra original de introducción de 12 s; todavía no existen once minutos de voz con aprobación ni pista de música comercial.

### Próxima acción no resuelta

- Desarrollar un lenguaje visual documental con planos originales de lugares/objetos reconstruidos o metraje licenciado y movimientos de cámara, no títulos flotantes como contenido principal.
- Construir la narración larga a partir de la identidad vocal canónica con pruebas independientes y derechos comerciales validados. No usar una voz sintética distinta sin evaluación del propietario; no mezclar audio de referencia y texto no coincidente.
- Sincronizar voz/visuales por escena con ritmo probado, revisar fuentes BlackBerry y exportar un primer montaje de 8–14 min; sin publicación automática ni pagos no aprobados.

**Estado:** OBSERVACIÓN DEL USUARIO ATENDIDA EN INTRO CORTA ✅ | PRUEBA MP4 CON AUDIO ✅ | DOCUMENTAL LARGO CINEMATOGRÁFICO ❌. Todo persistido en `main`.

## 2026-10-21 · Primera escena REAL del guion BlackBerry: voces nuevas y montaje sincronizado (main)

**Objetivo concreto del propietario:** continuar hacia el documental completo después de aprobar la introducción animada de 12,33 s con sonido. La introducción y el SHA de la voz canónica `78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d` se preservan sin edición ni sustitución.

### Avances guardados en `main`
- `tools/qwen_blackberry_scene01.py`: extrae **literalmente el texto narrado de la Escena 01** del manuscrito BlackBerry de 12 escenas; valida que los cuatro segmentos tengan de 150 a 260 caracteres y reconstruyan todas las palabras en el mismo orden. Qwen3-TTS Base 1.7B CPU recibe únicamente la referencia vocal aprobada; semilla fija; exporta 4 MP3, muestra combinada con silencios entre fragmentos, copia intacta de la referencia, checksums y reporte `ESTADO_ESCENA01_VOZ.json`. No cambia el guion o el MP3 canónico, no usa servicio TTS pagado.
- `tests/test_qwen_blackberry_scene01.py`: exactitud de los cuatro segmentos del guion, rechazo de cambios sin revisión, flags de aprobación falsa. GitHub CI [39639684664](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39639684664) `success`.
- `.github/workflows/blackberry-scene01-voice.yml`: ejecución única de investigación de voz desde `main`, Qwen 1.7B CPU en GitHub Actions. [Ejecución 39639684819](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39639684819) iniciada. El resultado queda **PENDIENTE DE FINALIZACIÓN Y AUDICIÓN** al escribir este asiento. Si falla, registrar error exacto y no afirmar que existen MP3 nuevos.
- `tools/render_blackberry_scene01.py`: compositor de montaje original H264/AAC. Comprueba el SHA de cada uno de los cuatro MP3 y que los textos coincidan literalmente con el guion. Mide el audio y crea planos originales en movimiento con cambios de toma cada cinco segundos y transiciones; produce MP4 del primer capítulo con exactamente la duración real del audio. El render continúa marcado como `new_voice_approved=false`, `rights_commercially_verified=false` y `youtube_publication_allowed=false`.
- `tests/test_render_blackberry_scene01.py`: cambios reales de fotogramas dentro de una toma, cambio de planos, límites de tiempo, texto original. CI [39640085857](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39640085857) `success`.
- `.github/workflows/blackberry-scene01-video.yml`: job de solo lectura del repositorio que, si el workflow de voz termina correctamente, recoge su artefacto `fdg-blackberry-escena01-voz-para-audicion`, verifica los cuatro archivos y crea MP4 H264/AAC con informe de fotogramas, duración y audio; no publica a YouTube ni toca Cloudflare o D1. Disparador de primera prueba `workflow_run` será retirado tras validar el primer render. También admite uso manual con ID de corrida.
- **No atribuir tiempos ni archivo de salida antes de ver los artefactos reales.** La síntesis Qwen de otros párrafos consumió minutos de CPU y casi 12 GiB RAM de runner en ensayos anteriores, por lo que esta ejecución está acotada a una sola escena y cuatro fragmentos, sin iniciar los otros once capítulos a ciegas.

### Pendientes
1. Revisar que finalice [39639684819](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39639684819) con cuatro MP3 reales y que `blackberry-scene01-video.yml` exporte un MP4 con audio decodificable, duración medida y cambios de planos; si falla, corregir en `main` y repetir solo el paso fallido.
2. Escuchar cada toma nueva y contrastar la identidad del narrador; **no confundir la voz original aprobada de 12 s con aprobación de estos nuevos minutos**.
3. Completar auditoría editorial y licencias; ampliar paso a paso a las 12 escenas sin sobrepasar cuotas CPU, generar audio/visual original y MP4 final de 8–14 min. No hay publicación automática ni derecho comercial confirmado.

**Estado de esta entrega:** nueva generación de voz y nuevo compositor implementados; CI de contratos verde; render del primer capítulo y aceptación vocal todavía en ejecución/pendientes. Todo en `main`.

### Resultado real Qwen para BlackBerry escena 01 — 2026-10-21, 17:10 UTC

- La generación con Qwen3-TTS Base 1.7B en CPU **sí concluyó**: [workflow 39639684819](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39639684819), `success`.
- Cuatro archivos MP3 generados **desde frases literales del manuscrito**, condicionados por la referencia vocal oficial **sin modificarla**:
  - `01_teclado.mp3`: **15,840 s** (245 caracteres).
  - `02_segunda_historia.mp3`: **13,632 s** (220 caracteres).
  - `03_pregunta.mp3`: **11,448 s** (166 caracteres).
  - `04_seguiremos.mp3`: **14,568 s** (236 caracteres).
- Unión `05_escena01_unida.mp3` de **56,520 s**; comprobado tanto por el reporte Qwen como con FFprobe tras descargar ZIP a la sesión. [Artefacto temporal 12365895069](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39639684819/artifacts/12365895069). Incluye 4 MP3, unión, copia del MP3 canónico y manifest de control. El SHA canónico sigue siendo `78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d`; los audios nuevos **no están aprobados auditivamente por el propietario**.
- Consumo observado: memoria máxima `11978384 KiB` (~11,42 GiB) en GitHub runner; generación desde aprox. 17:01 hasta 17:10 UTC. No se contrató API de pago ni se utilizó laptop propia.
- El propietario recibió enlace directo en conversación para escuchar `/mnt/data/BlackBerry_Escena01_Audio/05_escena01_unida.mp3`; el archivo fue descargado del artefacto, no inventado.
- Se inició automáticamente el render del tramo sincronizado [39641357257](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39641357257) tras concluir Qwen, respetando la verificación del estado `success`; al redactar este asiento el video estaba codificándose y no se afirmaba todavía MP4 finalizado.
- Añadido además `tools/blackberry_voice_schedule.py` y `tests/test_blackberry_voice_schedule.py` para planificar **12 escenas enteras** con división por oraciones/cláusulas y preservación textual; se conservan banderas de `generated_voice_clips=0` para el resto de escenas. Este planificador no sintetiza audio ni dispara cargas Qwen de otras escenas; está cubierto por CI `Comprobar base`.
- `.github/workflows/blackberry-scene01-voice.yml` volvió a modo `workflow_dispatch` **manual**, sin nueva generación pesada por push. El workflow de montaje quedará también solo manual después de comprobar la primera prueba.

**Conclusión del audio:** por primera vez existe casi un minuto de narración nueva del texto real de BlackBerry con referencia al timbre canónico; falta aceptación auditiva humana y licencia comercial. No aprobar ni publicar automáticamente.

### MP4 real de primer capítulo y programación de 12 escenas — 2026-10-21, 17:12 UTC

- **Render audiovisual completado:** GitHub Actions [39641357257](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39641357257) `success`. Descargó los cuatro MP3 de la corrida 39639684819, comprobó hashes y correspondencia literal con las cuatro partes del guion, y generó `BLACKBERRY_ESCENA01_CON_VOZ_NUEVA_REVISAR.mp4`. El propio workflow constató audio AAC, H.264 1280×720 y duración **56,500 s**, 679 fotogramas escritos; [artefacto 12364518448](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39641357257/artifacts/12364518448).
- **Inspección adicional realizada:** se descargó ZIP a conversación, se extrajo MP4 de **5.036.997 bytes**, FFprobe confirmó duración `56.500000`, H.264, 1280×720 y AAC. Se extrajeron cinco fotogramas en 2, 11, 23, 36 y 48 s, y se revisó una hoja de contacto: aparece movimiento y cambia de plano, pero **reutiliza escenas visuales abstractas**. No es todavía reconstrucción cinematográfica realista ni un producto apto para publicación.
- **Enlaces directos compartidos con el propietario:** `/mnt/data/BlackBerry_Escena01_Audio/05_escena01_unida.mp3` y `/mnt/data/BlackBerry_Capitulo01/BLACKBERRY_ESCENA01_CON_VOZ_NUEVA_REVISAR.mp4`. Son copias en la conversación y **no deben confundirse con publicación a YouTube**.
- Se retiró el disparador `workflow_run` temporal de `.github/workflows/blackberry-scene01-video.yml` y se había retirado el disparador `push` de voz. **Ambos siguen disponibles manualmente**, sin gasto automático de nueva IA.
- El nuevo `tools/blackberry_voice_schedule.py` + `tests/test_blackberry_voice_schedule.py` extrae texto íntegro por escenas y lo reparte en fragmentos de 120–260 caracteres, permitiendo cortes en oraciones y comas, sin omitir ni resumir material. `research/blackberry/LOTE_AUDIO_VISUAL_12_ESCENAS.json` está comprometido en `main`: **12 escenas, 56 partes programadas**, solo las **4 tomas de la escena 01** constan generadas; quedan **52 partes sin generar**, 11 escenas sin montaje. Estado editorial y derechos permanecen pendientes.
- La prueba del validador de video, de texto exacto y del planificador se ejecuta por `Comprobar base` en cada commit de `main`. No activar la síntesis masiva de 52 tomas sin comprobar primero calidad auditiva, cuotas CPU, legalidad y la correspondencia de las escenas.

### Próxima prioridad realmente bloqueante

1. Escuchar y valorar **los 56,52 segundos nuevos**: identidad de voz, dicción de BlackBerry, naturalidad y transiciones. La voz de referencia original de 12,336 s no se modificó, pero **ninguno de los cuatro clips nuevos tiene aprobación automática**.
2. Mejorar la imagen (actualmente abstracta y repetida) con B-roll original y movimiento cinematográfico coherente con historia y fuentes. El MP4 de prueba demuestra continuidad AV, no calidad de documental terminado.
3. Ejecutar escena 02 solo tras determinar si las nuevas tomas son aceptables; 11 escenas/52 tomas aún pendientes. Conservar plan y trazas auditivas y de derechos por cada escena.
4. Validar fuentes/historia, derechos de voz y visuales, montaje completo de 8–14 min y **cero publicación YouTube automática**.

**Estado actualizado y demostrado:** primera escena BLACKBERRY = audio real 56,52 s ✅, MP4 con ese audio 56,50 s ✅, render H.264/AAC QA verde ✅; guion de 12 escenas y plan 56 partes ✅; derechos, aprobación vocal y documental largo ❌.

## 2026-10-21 · Decisión arquitectónica definitiva: el sistema hace TODO, ChatGPT no fabrica cada episodio

**Corrección expresa del propietario:** «la meta final es que todo el trabajo lo haga el sistema, no tú», y mencionó **Qwen o Gemini para realizar las investigaciones**. Esto cambia la prioridad de desarrollo: el objetivo no es acumular escenas que el asistente elabora manualmente, sino terminar una plataforma automática reutilizable desde cualquier tema.

### Cambios realizados en este turno (solo `main`)

1. Documento nuevo `docs/ARQUITECTURA_AUTONOMA.md`: fija el criterio de aceptación `tema → descubrimiento y extracción de fuentes → investigador IA → contraste factual → guion original → planificación audiovisual → narración autorizada → montaje MP4 de 8–14 min → QA → revisión del propietario`, sin que ChatGPT escriba personalmente el próximo documental. YouTube queda deshabilitado por defecto y sujeto a autorización.
2. `docs/PLAN_PROYECTO.md`: prioridad **P0** añadida al principio y sección de reorientación al final. Se documenta que BlackBerry es solo una prueba, no la forma definitiva de producir cada episodio.
3. Investigador pluggable propuesto: **Gemini API gratuita** (modelos gratuitos disponibles dependiendo de cuenta/cuota y política de datos) y **Qwen3 LLM local** (investigación textual CPU). El actual Qwen3-TTS solo genera voz; no confundirlo con el investigador. La integración real de Gemini, clave, prueba de red, calidad y cuotas **NO se ha ejecutado ni configurado**. Qwen3-0.6B ya tuvo experimentos pero no avala una investigación autónoma robusta.
4. Reglas obligatorias: evidencia primaria con URL, SHA, periodo/unidad/citas; comparaciones automáticas no dan hechos humanos verificados; ninguna contratación/API pagada, secreto en GitHub/Cloudflare únicamente, fuentes públicas en modalidades gratuitas y ningún contenido comercial sin derechos.

### Estado y siguiente hito verificable

**Hecho:** documentos de arquitectura y plan actualizados en el repositorio, sin cambio de proveedor en producción. No se ha hecho investigación Gemini ni generado contenido nuevo; no afirmar lo contrario.

**P0.1 siguiente:** implementar un contrato de proveedores `gemini_free`/`qwen_local`, pruebas sin clave ni gasto, y hacer un **ensayo real de investigación completa de un tema nuevo** por la plataforma tras configurar Gemini de forma segura (si se selecciona) o usar un Qwen LLM viable. Registrar exactamente fuentes, respuestas, latencia, límites de coste y errores. Luego conectar las etapas hasta MP4. El propietario debe supervisar/aprobar resultados, no realizar tareas técnicas.

**Recordatorio:** mantener exclusivamente `main` y documentar cada implementación, CI y despliegue por separado. La dirección se considera acordada; no regresar a producción manual permanente del chat.

### Primer componente implementado de la reorientación — contrato Gemini/Qwen (2026-10-21)

**Código real comprometido en `main`:**
- `tools/research_providers.py`: contrato común que transforma únicamente pasajes documentales originales en entradas identificadas (hasta 24, con `source_id`, URL, fragmento y página), construye un prompt estructurado y exige salida JSON con afirmaciones candidatas y preguntas de investigación pendientes. Cada cita que devuelva un modelo debe apuntar a un ID real incluido en la solicitud; de lo contrario se rechaza. Ningún modelo marca hechos verificados por sí mismo.
- `run_gemini_free`: adaptador HTTP de `gemini-2.5-flash` o `gemini-2.5-flash-lite`, con clave `GEMINI_API_KEY` por secreto y **bloqueo hasta confirmar la modalidad gratuita**. No hay clave configurada/confirmada ni llamadas reales realizadas; el control evita que el código active el proveedor inadvertidamente. Esto **no puede garantizar por sí solo** que una clave ya facturable no genere cargos: el estado de la cuenta deberá comprobarse antes de utilizarla.
- `run_qwen_local`: adaptador de generación local inyectable que acepta respuestas del Qwen LLM en el mismo contrato de evidencia. Es interfaz y pruebas de contrato; el motor de texto Qwen experimental existente aún no se conecta directamente a esta interfaz en el workflow de producción.
- `tests/test_research_providers.py`: 5 pruebas offline con proveedor simulado sobre fuente original, salida JSON, citas inventadas, opción gratuita obligatoria, ausencia de claves, hash de prompt y bloqueo de aprobación/publicación; cero créditos/API usados.
- `tools/production_preflight.sh`: añadió la prueba de estos proveedores a las condiciones de despliegue; la comprobación general `.github/workflows/check.yml` ejecuta automáticamente todas las pruebas Python de `tests`.

**Verificación de este lote:** CI [39644919482](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39644919482) `success` con adaptadores y tests; después se actualizó el preflight (commit `528a4d0588254aee772d77432a805d67becf13b0`), cuya comprobación [39644991576](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39644991576) estaba en ejecución al registrar este punto. No se afirma que Gemini haya investigado o que el ciclo autónomo end-to-end ya funcione.

**Siguiente integración prioritaria:** añadir selección de investigador en workflow/panel y conectar los pasajes del propio motor al adaptador; configurar una clave Gemini solo a petición/mediante secretos y validación de cuota gratuita; realizar primera investigación automatizada de un tema *sin fuentes ni guion preparados por ChatGPT*, con una ruta Qwen viable para contingencias. Comparar calidad, evidencia, tiempos y límites antes de automatizar guion/producción.

## 2026-10-21 · Cambio de requisito: radar autónomo de mercado, selección, fabricación y publicación

**Instrucción expresa del propietario:** la IA responsable debe estudiar en tiempo cercano al real la demanda del mercado (con la frescura y cuotas que permiten las fuentes), descubrir temas sin esperar entrada manual, clasificarlos, investigar la mejor oportunidad, transferir resultados a los motores audiovisuales y, tras autorización, **subir/programar el episodio con el propio sistema en YouTube**. ChatGPT se limita al desarrollo de la plataforma, no escribe/procesa manualmente cada documental de manera permanente.

### Código y decisiones ya guardados en `main`

1. Se corrigió el principio de `docs/ARQUITECTURA_AUTONOMA.md` y la portada de `docs/PLAN_PROYECTO.md`: el disparador estándar es el radar, no un tema que escribe el propietario. El portal permite preferencias/nicho y un tema manual como excepción, no como requisito.
2. Documento nuevo `docs/INTELIGENCIA_MERCADO.md`: mercado, fuentes, variables, criterios, límites, selección de emergentes/evergreen, ciclo D1, guardas, analítica posterior y carga YouTube controlada. No confundir señales de Wikipedia con volumen de búsqueda ni datos YouTube con éxito garantizado.
3. `tools/market_radar.py`: primer selector determinista. Requiere, para cada candidato elegible, estadísticas de 3–30 videos públicos de YouTube de hasta 90 días, observadas hace menos de ocho días, una señal independiente de interés por Wikipedia con dos ventanas equivalentes de 7 días y al menos una URL de fuente original. Excluye duplicados publicados, datos fuera de fecha y ausencia de métricas. Puntaje heurístico documentado y desglosado; permite abstenerse de seleccionar.
4. `tools/market_sources.py`: primer colector con clave de YouTube Data API (2 llamadas como máximo, 10 videos por candidato, limitación regional configurada y validación de estadísticas), y Wikimedia Pageviews de 14 días completos. Si la clave o muestra falta, el colector falla explícitamente: no inventa datos ni simula tráfico. **Todavía recibe entidades/temas del siguiente descubridor por desarrollar, no los extrae por sí mismo desde señales generales del mercado.**
5. Pruebas `tests/test_market_radar.py` y `tests/test_market_sources.py` con datos totalmente **sintéticos como fixtures**. No se usaron claves de YouTube, Gemini, Google Trends ni datos de un mercado verdadero en estas pruebas. `tools/production_preflight.sh` añade ambas baterías como condición de compilación del proyecto.

### Verificación y límites

- CI [39648768592](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39648768592) `success` después de añadir los colectores y pruebas; otras comprobaciones intermedias también aprobadas.
- Se añadieron los tests al preflight en el commit `6f12a0938d86e6213480b751a6fddc08887bb1c7`. **No** declarar confirmación de deploy remoto Cloudflare basándose solo en CI.
- **Aún no existe** radar en vivo conectado a YouTube, Google Trends alfa, Analytics propio, feed de noticias, descubridor automático de empresas ni un ranking de mercado real. `market_radar.py` demuestra el contrato de selección pero **no que funcione end-to-end**.
- **No se ha habilitado publicación a YouTube**. El producto debe terminar actuando como productor y también como operador de carga/agenda después de que se autorice el episodio, con OAuth y derechos comerciales acreditados.

### Próximas tareas prioritarias

1. Conectar credenciales de YouTube Data API mediante secretos, solo con permisos/consentimiento y cuotas verificadas. Descubrir temas desde señales **reales** del nicho sin requerir nombres propuestos por ChatGPT/propietario; extraer entidades y evitar duplicados.
2. Validar primer ranking no simulado para varias empresas, con fuentes y puntuación guardada en D1 y canal de estado visible. Añadir API Trends exclusivamente si se aprueba acceso alfa.
3. Elegir automáticamente el candidato suficiente, investigar con Gemini/Qwen, citar, verificar y redactar guion por el sistema. Después generar voz/escenas, montar y controlar MP4 de 8–14 minutos de manera autónoma.
4. Realizar flujo YouTube OAuth → revisión/permiso editorial → upload/programación automática por sistema → analytics → siguiente ranking, sin activarlo antes de garantías y licencia.

**Estado de esta etapa:** prioridad y arquitectura corregidas, ranking/colección de muestras y pruebas incorporadas al repositorio. **Estudio en vivo, selección autónoma de temas y autopublicación todavía pendientes.** Todo en `main`, con historial y sin gastos.

## 2026-10-21 · Primer descubrimiento automático de una empresa REAL + serie de interés

**Objetivo del propietario:** avanzar hacia una plataforma que elija los mejores temas en base a mercado, sin que ChatGPT proporcione manualmente empresas, guiones o material. Se trabajó solo en `main`.

### Implementación nueva
1. `tools/topic_discovery.py`: lee Wikimedia Pageviews Top (es/en), verifica identidad/clase empresa en Wikidata mediante P31 y conserva candidato, QID, idioma, fecha, enlace/ranking. Es un **descubridor desde señales**, no una lista de empresas hardcodeada. Filtra personas, títulos especiales y URLs inseguras. Controla hasta 180 artículos por wiki y 12 lotes Wikidata como topes de código; las pruebas reales usaron 120 artículos por idioma y 8 lotes.
2. Se cambió en `tools/market_sources.py` el límite de respuesta JSON de 1 MB a 5 MB, aún acotado, con encabezado `User-Agent` identificable según política del proveedor. La primera prueba había demostrado que 1 MB no alcanzaba para el top diario.
3. Enriquecimiento opcional `--enrich-interest`: consulta Wikimedia Pageviews para **14 días completos** de una página detectada, separando 7 días recientes de 7 previos, máximo seis empresas por ejecución. Si falla un proveedor no inventa cifras.
4. `tests/test_topic_discovery.py`: siete casos unitarios para clasificación/ausencia de señal/fechas/idiomas/URLs/consulta real simulada de 14 días. Los tests fueron ejecutados por el CI general (Python unittest discover).
5. `.github/workflows/topic-discovery-smoke.yml`: primera prueba disparada temporalmente por `push` y posteriormente convertida en **workflow diario programado a las 10:17 UTC + manual**, con límites de solicitudes y sin Qwen, Gemini ni YouTube.

### Evidencia real de red (no simulada)
- [Primera ejecución 39650638377](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39650638377): **failure** al superar el tamaño de lectura original de 1 MB. Se corrigió y repitió, no se ocultó el fallo.
- [Ejecución 39650844704](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39650844704): **success**, 240 artículos en es/en, 8 lotes Wikidata, **1 empresa candidata Theranos** (Q16956307), con QID y enlace de Wikipedia. Ningún estudio completo ni tema seleccionado para video.
- [Ejecución 39651368713](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39651368713): **success**, los mismos 240 artículos y 8 lotes, con **1 serie real de 14 días** completada. El ZIP de artefacto `12370101388` fue descargado y JSON leído: `Theranos`, 291.435 visualizaciones del artículo en la semana 14–20 de octubre y 55.952 en la semana 7–13 de octubre, fuente `en.wikipedia.org`; `observed_at=2026-10-21`. Son visitas al artículo, NO búsquedas Google, demanda garantizada de YouTube ni retención del canal.
- Registro permanente editorial en `research/market/VALIDACION_RADAR_2026-10-21.md`. Informe operativo JSON permanece en artefacto GitHub de retención limitada y en ZIP de la conversación; falta almacenar series futuras en D1.

### Próximos pasos
1. Añadir otras fuentes de descubrimiento más inmediatas para no depender de Wikipedia con desfase de ~3 días y aumentar muestra a varias compañías.
2. Conectar YouTube Data API y obtener estadísticas observadas, saturación, formatos y crecimiento real del propio canal al tener OAuth; **no simular interés** ni publicar sin autorización.
3. Persistir candidatos/rankings en D1 y conectar el selector con Gemini/Qwen para que el sistema investigue, redacte, narre, monte y entregue un MP4 original de 8–14 minutos.
4. Mantener derechos y revisión editorial como puertas obligatorias antes de una subida/programación de YouTube hecha por el mismo sistema.

**Estado:** descubrió por sí mismo la primera empresa candidata y midió interés en Wikimedia ✅; estudio comparativo profesional de mercado, tema ganador, producción completa y autopublicación aún pendientes ❌. Todo en `main`, sin pagos ni publicación.

## 2026-10-21 · Segunda ronda de descubrimiento autónomo y almacenamiento probado

**Necesidad del propietario:** el propio sistema investiga mercado permanentemente, decide los mejores temas y posteriormente investiga, narra, monta y sube a YouTube después de garantías; no depender del chat. **Todo commit fue directo a `main`.**

### Resultado con fuentes externas verdaderas

1. `tools/topic_discovery.py` + workflow ampliados a **360 artículos Wikipedia es/en** y máximo **12 lotes Wikidata** por corrida, con enriquecimiento de hasta seis páginas mediante ventanas comparables de 14 días. [Ejecución 39652155079](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39652155079) `success`: **Theranos Q16956307** y **DuPont Corporation Q221062** identificadas sin que ChatGPT introdujera esos nombres; se obtuvieron dos series de interés, con días de referencia 18 y 21 octubre (top con 3 días de retraso). Visitas por semana: Theranos 291.435/55.952 y DuPont 3.512/338. **Solo interés Wikimedia**, ningún ranking validado de demanda YouTube.
2. Migración nueva `migrations/0004_market_intelligence.sql`: tablas aditivas `market_runs`, `market_entities`, `market_pageview_observations`, `market_interest_windows`, `market_selection_decisions`. No afecta `jobs`, `events`, `research_requests` ni `editorial_dossiers`; **NO se ejecutó en D1 remoto**.
3. `tools/market_persistence.py`: esquema SQLite compatible D1, transacciones idempotentes, verificación QID, fechas, host Wikimedia, métricas y ventanas completas; `tests/test_market_persistence.py` cubre historial multi-día, ausencia de duplicados y preservación de migraciones previas. CI [39652800696](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39652800696) `success`.
4. [Prueba real integrada 39652982369](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39652982369) `success`: descubrimiento externo y medición, seguida de escritura de **SQLite local**. Se descargó artifact 12369113919 y se leyó con SQLite: `market_runs=1`, `market_entities=2`, `market_pageview_observations=2`, `market_interest_windows=2`, `market_selection_decisions=0`. `D1_PRODUCCION_MODIFICADA: FALSE`. Archivo local nuevo por ejecución, **aún no historial remoto persistente**.
5. `tools/production_preflight.sh` agregó pruebas de `test_topic_discovery.py` y `test_market_persistence.py`. Se retiró el disparador `push` temporal de la prueba integrada y dejó el workflow de investigación pública **diario (10:17 UTC) + manual**, sin gasto de IA ni publicación.

### Documentación/evidencia

- `research/market/VALIDACION_RADAR_2026-10-21.md` recoge la primera prueba de 240 artículos.
- `research/market/VALIDACION_RADAR_360_2026-10-21.md` recoge la prueba ampliada a 360 artículos y validación de SQLite, ambos con enlaces a workflows.
- Los artefactos diarios GitHub caducan; solo la documentación y el código están conservados permanentemente en `main`.

### Próximas tareas prioritarias

- Identificar cuenta Factor en Cloudflare, confirmar respaldo y aplicar D1 0004 remoto sin sobrescribir trabajos existentes; crear vía autenticada para guardar el radar diario y visualizarlo en panel.
- Incorporar noticias/trends actuales y YouTube Data API para comparar interés de **varios** temas, audiencia hispanohablante, competencia relativa y fuentes primarias suficientes. No elegir por solo Wikipedia.
- Implementar elección automática + Gemini/Qwen investigador y control factual → guion → voz → escenas → MP4 8–14 min → revisión editorial/derechos → YouTube OAuth y publicación por el propio sistema.
- Mantener decisiones explicables, cuotas y logs; evitar IA de pago no autorizada y no atribuir al motor una investigación completa que todavía no realiza.

**Estado:** radar de descubrimiento real y primer almacenamiento SQLite verificados; persistencia D1 remota, selección de mejor tema YouTube y productora end-to-end pendientes.


## 2026-10-21 · API administrativa del radar de mercado (continuación)

### Código implementado en main
- Nuevo `src/market-radar.mjs`: consulta limitada y exclusivamente de lectura de `market_runs`, `market_entities` y `market_interest_windows`. No realiza escrituras, ni decisiones editoriales, ni publica videos.
- `src/worker.js`: ruta `GET /api/market/radar?limit=30`, ubicada después del guard de `ADMIN_TOKEN`. El token del renderizador no autoriza el endpoint; respuesta 405 para otros métodos, 400 para límites fuera de 1-100 y 503 si falta migración 0004.
- `tests/test_market_radar_api.mjs`: contratos de consultas de solo lectura, límites, banderas fail-closed y migración ausente.
- `.github/workflows/check.yml`: nueva prueba incluida en CI de rama main.

### Distinción de estados y riesgos
- Los cambios de código han sido enviados a GitHub en `main`; **no se ha aplicado migración 0004 en D1 remoto ni desplegado este nuevo Worker desde este avance**.
- El endpoint solo presentará filas reales cuando se configure persistencia remota; datos SQLite generados en runners siguen siendo efímeros.
- Una observación Wikimedia nunca equivale a demanda YouTube; `market_study_complete`, `youtube_data_verified` y `automatic_publication_allowed` permanecen falsos.
- Antes de aplicar D1 0004: identificar cuenta/DB real, revisar respaldo, confirmar conservación de tablas y filas antiguas y realizar migración aditiva controlada.

### Próximas tareas prioritarias
1. Confirmar CI incluido `tests/test_market_radar_api.mjs`.
2. Identificar cuenta Cloudflare Factor y respaldo D1, aplicar migración 0004 en la DB correcta y verificar las tablas sin alterar `jobs`, `events` ni expedientes.
3. Implementar ingesta autenticada con idempotencia y trazabilidad de procedencia desde workflow diario a D1; nunca incluir tokens en artifacts/logs.
4. Añadir proveedor de noticias y señales YouTube reales para comparar múltiples temas antes de cualquier selección.
5. Conectar selección fundamentada con investigación Gemini/Qwen, fact-check, guion, voz, visuales, QA y subida a YouTube solo tras aprobación.



## 2026-10-21 · HITO NUEVO: radar persistente REAL con GitHub OIDC, D1 y panel

### Auditoría previa y migración remota
- Cuenta conectada: Cloudflare **Factor**, no `Primary`. DB exacta `factor-de-gigantes-db` UUID `ef699e75-b50a-4e28-a665-69316d10cdaf`.
- Antes de alterar D1: se leyó `sqlite_master`, se verificaron tablas 0001–0003, se registró bookmark Time Travel y Cloudflare confirmó exportación SQL temporal. El punto de restauración no debe confundirse con copia externa permanente.
- Se aplicó **`migrations/0004_market_intelligence.sql`** directamente a D1 remota con su SQL aditivo original; resultado OK y cinco tablas presentes: `market_runs`, `market_entities`, `market_pageview_observations`, `market_interest_windows`, `market_selection_decisions`.
- Recuento conservado antes/después: `jobs=1`, `events=8`, `editorial_dossiers=0`, `research_requests=0`. Sin pérdida de registros previos.

### Backend y seguridad implementados
- `src/market-ingest.mjs`: validación de entidades QID, fechas, series completas, métricas enteras, dominio Wikimedia, presupuestos y estados no autorizados. Escribe con `DB.batch` transaccional e identificador derivado de SHA-256 canónico. Inserciones idempotentes para reportes repetidos; no activa render ni YouTube.
- `src/github-oidc.mjs`: verificación de firma RS256 con claves públicas GitHub y claims de audiencia, `repository_id`, `workflow_ref`, rama, evento y tiempo. **No se utiliza un token de ingesta de larga duración**.
- `src/worker.js`: ruta `POST /api/market/ingest` únicamente mediante OIDC y ruta `GET /api/market/radar` únicamente con `ADMIN_TOKEN`.
- `tools/push_market_radar.py`: obtiene credencial efímera de GitHub Actions y reporta éxito solo cuando la API confirma escritura D1.
- `.github/workflows/topic-discovery-smoke.yml`: descubrimiento diario + manual, `id-token: write`, envía reporte a Worker sin almacenar el JWT; después de prueba temporal de integración se **retiraron tanto `push` como la concesión OIDC para evento `push`**.
- `tests/test_market_ingest.mjs`, `tests/test_github_oidc.mjs`, `tests/test_push_market_radar.py` y CI Node/Python añadidos y validados.

### Evidencia de funcionamiento real
- La primera ejecución de integración falló con 401 durante el despliegue/ajuste de credenciales efímeras. No se contó como éxito y se revisó.
- **[GitHub Actions 39658991775](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39658991775): `success`**. Recopilación pública real, prueba SQLite, autenticación OIDC, HTTP 201 y persistencia D1 confirmadas.
- Se leyó D1 remota *después* del éxito: `market_runs=1`; `market_entities=2`; `market_pageview_observations=2`; `market_interest_windows=2`; `market_selection_decisions=0`. Se comprobaron otra vez `jobs=1`, `events=8`.
- No se introdujeron manualmente nombres de empresas ni valores de mercado; la ejecución obtuvo entidades y cifras desde las fuentes públicas.
- Cloudflare API mostró versiones desplegadas del Worker que incluyen el verificador OIDC y la escritura D1; el build sigue sincronizándose desde `main`.

### Panel y presentación del histórico
- `public/index.html` incorpora sección «Radar de oportunidades» dentro del espacio autenticado.
- `public/app.js` consulta `/api/market/radar?limit=30` y presenta candidatos, ventanas y procedencia como **visitas a artículos Wikimedia**, nunca como demanda de YouTube; se usa `textContent` para evitar inyección HTML.
- Pendiente comprobación visual autenticada desde el navegador del propietario; el código y las comprobaciones CI no equivalen a navegación manual.

### Qué falta para la meta final
1. Añadir **descubrimiento oportuno de noticias y empresas** y guardar fuentes/time series en D1; ampliar variedad y continuidad de candidatos.
2. Conectar YouTube Data API (con cuota/credencial permitida) para observar videos recientes de cada mercado hispanohablante y comparar competencia y relevancia. Sin ello **no existe ranking YouTube real**.
3. Crear decisión explicable, auditada y basada en múltiples fuentes: motivo de elección, exclusión, conflictos y certeza, no elegir por popularidad de Wikipedia.
4. Conectar mejor tema → dossier investigador Gemini/Qwen → fact-check y citas → guion 8–14 min → voz/escenas originales → QA audiovisual real.
5. Añadir autorización editorial, derechos y OAuth oficial de YouTube; publicar solo con aprobación y sin contenido reutilizado.
6. Validar experiencia completa del panel y plan de restauración/coste operativos.

**Resultado inequívoco de esta sesión:** persiste autónomamente el radar en D1 con OIDC probado. **No** está concluida la investigación integral de mercado ni la producción/publicación automática. Historial y código en `main`.



## 2026-10-21 · P0: noticias actuales, preselección temática y D1 remota

### Nuevas funciones implementadas, no solo auditadas
- `tools/news_discovery.py`: colector ejecutable de **Google Noticias RSS** en cuatro consultas generales de empresas, innovación, tecnología e industria (ES/EN, PE/MX/US). Las consultas NO contienen nombres de empresas preseleccionadas. Conserva titulares, fecha UTC, URL del agregador, medio atribuido y categoría, con límites de tamaño, 72 horas de frescura, deduplicación y fallos explícitos.
- `migrations/0005_news_leads.sql`: nuevas tablas `market_news_runs` y `market_news_leads`; los registros nuevos quedan `unverified`, sin autorización editorial ni demanda YouTube calificada. Migración **aplicada y tablas verificadas en Cloudflare D1 REMOTA**, cuenta `Factor`. Se registró bookmark Time Travel antes de aplicarla.
- `src/news-ingest.mjs`, `tools/push_news_radar.py` y `src/worker.js`: ingesta vía `POST /api/market/news/ingest` con **GitHub OIDC** y validación estricta del payload. Escrituras por lote de D1, IDs estables para deduplicar y bloqueo explícito de autorización de videos. `GET /api/market/news` lee las noticias con `ADMIN_TOKEN`.
- `.github/workflows/topic-discovery-smoke.yml`: se amplió el radar diario para buscar noticias, preservar el reporte original y almacenarlo mediante identidad OIDC temporal en la misma base, sin APIs pagadas. **Se retiró el disparador temporal `push` al finalizar la prueba**; programación diaria 10:17 UTC y activación manual permanecen.
- `src/news-triage.mjs`: preselección **heurística y explicable** de relevancia documental; puntúa señales del titular (innovación, cambio empresarial, disrupción, industria) y penaliza material promocional, guías para invertir y noticias de mera cotización. Puntuación ≠ demanda YouTube ni aprobación editorial.
- `public/index.html` y `public/app.js`: sección privada «Noticias empresariales recientes» con medio atribuido, fecha, vínculo original del agregador y relevancia exploratoria. Uso de `textContent` para titulares ajenos.
- `tests/test_news_discovery.py`, `tests/test_news_ingest.mjs`, `tests/test_news_triage.mjs`: comprobación de fuentes, no simulación de resultados, deduplicación, frescura, seguridad, clasificación y prohibición de calificar temas sin señales externas; integradas en CI.

### Prueba integrada con fuentes y D1 verdaderas
- **[GitHub Actions 39668778079](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39668778079) `success`**: Wikimedia siguió funcionando, el nuevo colector RSS consultó sus fuentes y el Worker persistió sus resultados con OIDC real.
- Lectura de **Cloudflare D1 remota** posterior a ejecución: `market_news_runs=1` y `market_news_leads=100`, recortado al límite configurado. `market_runs=1`, `market_entities=2`, `jobs=1`, `events=8`: lo existente se preservó. Los titulares provenían de distintas fuentes atribuidas por el agregador, como Perú 21, AFR y Banca y Negocios. No se debe asumir que cada uno es editorialmente útil o verdadero.
- La **primera** prueba integral de noticias falló por HTTP 401 mientras la nueva versión del verificador OIDC se desplegaba; se diagnosticó, y la repetición tras el despliegue terminó `success`. La caída inicial no se declara éxito.
- Los permisos de `push` incorporados SOLO para la prueba se retiraron tanto del workflow como del validador OIDC, con CI posterior exitosa. No hay publicación YouTube.

### Limitaciones y siguiente fase
- Los 100 artículos almacenados son **titulares RSS de agregador**, no 100 temas verificados ni datos competitivos YouTube; puede haber noticias no pertinentes. No se han leído automáticamente los artículos originales.
- La puntuación de relevancia del título es un **filtro preliminar**, no puntuación de oportunidad de mercado; no se promueve automáticamente una noticia a investigación ni a guion.
- **Próximo P0**: obtener estadísticas observadas de YouTube Data API para temas/candidatos (con credenciales/cuotas permitidas), detectar y agrupar narrativas de varias noticias y contraste de fuentes primarias, computar competencia y crecimiento por región, y persistir una selección fundamentada. Solo después conectar Gemini/Qwen y el motor profesional de documental con revisión editorial.
- El navegador privado del propietario sigue pendiente de prueba visual autenticada. La lectura de D1 y el despliegue de código no equivalen a login probado.

**Estado final del bloque:** radar de empresas + radar de noticias con persistencia diaria D1 real ✅; preselección editorial sin IA y lectura desde panel implementadas ✅; estudio de mercado YouTube / mejor tema / documental integral / autopublicación autorizada pendientes ❌.


## 2026-10-21 · Hito P0: YouTube Data API por empresa y región, persistencia D1 y cuota sin pagos

### Desarrollo real en `main`
- Reutilizado `tools/market_sources.py` (cliente oficial YouTube Data API v3 `search.list` + `videos.list`) y agregado `channel_id` público solo si viene en la respuesta; jamás se estima retención o CTR ajenos.
- Nuevo `tools/youtube_market_study.py`: elige **únicamente las empresas descubiertas por Wikimedia/Wikidata**, hasta 2 y dos mercados hispanohablantes `MX` / `ES`, sin temas escritos manualmente por ChatGPT. Máximo **4 pares empresa-región, 4 búsquedas y 4 solicitudes de estadísticas** por ejecución; calcula muestras de videos recientes, mediana observada de vistas/día de antigüedad, canales identificados, región y fecha. Es **comparación exploratoria**, no prueba de demanda global.
- **Actualización documentada de cuota octubre de 2026:** el método `search.list` dispone ahora de bucket independiente por llamadas (hasta 100 al día por defecto, 1 unidad por llamada); `videos.list` cuesta 1 unidad en su cuota respectiva. Límite de este workflow: **4 llamadas de búsqueda + 4 de videos = 8 unidades solicitadas entre ambos buckets** por corrida, nunca 404 unidades de la fórmula antigua. Referencia oficial: https://developers.google.com/youtube/data/determine_quota_cost (actualizada 2026-10-15). La cuota real del proyecto debe comprobarse en Google Cloud antes de habilitarla.
- **Bloqueo de coste por defecto**: el workflow solo realiza llamadas si GitHub tiene `YOUTUBE_DATA_API_KEY` y la variable `YOUTUBE_MARKET_BUDGET_ENABLED=1`. Sin ambas, registra omisión explícita: ninguna llamada YouTube, ninguna muestra ni dato inventado, ningún proveedor cobrable alternativo.
- Migración aditiva `migrations/0006_youtube_observations.sql`: `market_youtube_runs`, `market_youtube_queries`, `market_youtube_videos`. **Aplicada a D1 remota Factor** tras verificar tablas previas, bookmark Time Travel y exportación temporal; se conservaron `jobs=1`, `events=8` y `market_news_leads=100`. **La restricción SQL de cuota es deliberadamente un límite superior amplio; la validación aplicativa impone el presupuesto real de 8 unidades.**
- `src/youtube-market.mjs`: valida procedencia, presupuestos, fechas, IDs, conteo de videos/canales y **recalcula la mediana sobre los valores de cada video**, rechazando métricas incoherentes. Persiste lotes D1 idempotentes con IDs SHA-256. No aprueba investigación, guiones ni YouTube.
- `src/worker.js`: nuevo `POST /api/market/youtube/ingest` protegido por GitHub OIDC, y `GET /api/market/youtube` con el `ADMIN_TOKEN` existente. No requiere token de ingesta adicional.
- `tools/push_youtube_study.py` envía los resultados solo a Worker Factor, con OIDC efímero, ocultando secretos. `.github/workflows/topic-discovery-smoke.yml` lo ejecuta condicionalmente después del radar real Wikimedia/RSS.
- Sección de **Comparación YouTube** agregada a `public/index.html` y `public/app.js`: muestran empresas, países, tamaño muestral, mediana por video y canales identificados cuando existan datos; con 0 datos, se muestra estado de insuficiencia sin ranking falso.
- Pruebas nuevas `tests/test_youtube_market_study.py`, `tests/test_youtube_market.mjs`, `tests/test_youtube_schema.py`; actualizadas `tests/test_market_sources.py` indirectamente por campos adicionales. Validan límite de llamadas, modo sin clave, fallos, fuentes, firma/lógica administrativa, FK y conservación del esquema.

### Evidencia y estado operativo
- Cloudflare API verificó **tres tablas nuevas presentes** en la D1 real y el Worker desplegado con endpoints/INSERT de YouTube.
- Recuento observado tras migración: `market_youtube_runs=0`, `market_youtube_queries=0`, `market_youtube_videos=0`. Esto **NO** significa que se haya medido competencia: el servicio espera las condiciones de cuota/API. No se configuraron secretos ni facturación en esta intervención.
- GitHub Actions CI incluye pruebas JS/Python reales de contrato. Los videos de las pruebas son **fixtures**, no métricas de mercado.
- Respetadas las reglas: cero pagos, ninguna búsqueda con clave en logs, cero publicaciones, cero cambios destructivos, únicamente rama `main`.

### Próximo hito funcional sin desviar prioridad
1. Confirmar con la cuenta de Google si existe proyecto YouTube Data API con cuota gratuita disponible y **sin facturación activada**; registrar de forma segura clave GitHub `YOUTUBE_DATA_API_KEY` y activar `YOUTUBE_MARKET_BUDGET_ENABLED=1` únicamente si se autoriza el consumo de cuota gratuita. Probar la ingesta pública y verificar filas remotas, sin inventar estadísticas.
2. Automatizar obtención de **fuentes primarias verificables** sobre empresas/eventos detectados y vincular titulares RSS con entidades canónicas (Wikidata) y fuentes originales, conservando procedencia.
3. Generar ranking comparable multiseñal y persistir `market_selection_decisions`, con estado `sin_datos_suficientes` cuando falten fuentes o YouTube. No usar la mediana de videos como pronóstico de crecimiento propio.
4. Encadenar investigación Gemini gratuita o Qwen local, evidencias, guion, voz oficial aprobada y MP4 profesional de 8–14 min con QA; publicación en YouTube siempre condicionada a revisión y permisos.

**No declarar completada fase P0:** el colector y su almacenamiento están implementados, pero falta primera ejecución con estadísticas YouTube auténticas y conexión de evidencia primaria para selección fundamentada.


## 2026-10-21 · P0 — Continuación: cotejo automático de fuentes y prueba integral (migración 0007)

### Código en main
- `tools/market_news_join.py`: asocia empresas realmente descubiertas por Wikimedia con titulares realmente obtenidos por RSS, por coincidencia textual normalizada y límites de palabra, quitando sufijos societarios genéricos. No utiliza lista fija de compañías, LLM, datos inventados ni adivina identidades. Excluye nombres ambiguos/cortos, fechas dispares y dominios fuera del agregador. Conserva evidencia de ambos extremos.
- `migrations/0007_entity_news_links.sql`: tablas aditivas `market_entity_news_runs` y `market_entity_news_links`. FK a `market_entities` y `market_news_leads`, estado `candidate_needs_entity_confirmation`, sin aprobación ni datos de YouTube.
- `src/market-cross-signals.mjs`: valida procedencia, tamaño, fechas, IDs, titular que contiene la mención y estados editoriales pendientes; persistencia por lote D1 idempotente, sin alterar manualmente un enlace confirmado/rechazado. API administrativa de lectura `GET /api/market/cross` y entrada OIDC `POST /api/market/cross/ingest` integrada en el Worker.
- `tools/push_market_cross.py`: transporte desde GitHub Actions a Cloudflare con JWT OIDC efímero, sin compartir ni imprimir tokens. `.github/workflows/topic-discovery-smoke.yml`: correlación + persistencia después de RSS y antes del sondeo YouTube condicional.
- `public/index.html`, `public/app.js`: sección de coincidencias con noticia y empresa y estado explícito de no verificación; interfaz sin HTML inyectado a partir de titulares externos.
- `tests/test_market_news_join.py` y `tests/test_market_cross_signals.mjs`: false positive tests, deduplicación, rechazo de aprobaciones falsas, datos de prueba marcados como fixtures, integración CI.

### Despliegue y prueba real
- Antes de alterar D1 se comprobó la base `factor-de-gigantes-db` en la cuenta Cloudflare Factor, obtuvo bookmark Time Travel y Cloudflare completó una exportación SQL temporal (no una copia externa permanente). Se verificó conservación inicial de registros.
- **Migración 0007 aplicada directamente en D1 REMOTA**: dos tablas presentes; las anteriores conservadas.
- Para lanzar una única prueba real se habilitó temporalmente `push` en el workflow y verificador OIDC, exclusivamente en `main`. El guardado del nuevo paso funcionó mediante el circuito Cloudflare autenticado.
- **[GitHub Actions 39673977211](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39673977211): `success`.** Pasaron descubrimiento Wikimedia, SQLite local, ingesta D1, RSS real, correlación, ingesta del cruce y paso de YouTube bajo presupuesto.
- Lectura independiente posterior a D1: `market_entity_news_runs=1`, `market_entity_news_links=0`; `market_entities=2`, `market_news_leads=106`, `jobs=1`, `events=8`. El sistema examinó 100 noticias en esa corrida, pero no halló ninguna mención textual confiable de las 2 empresas. **0 coincidencias es una observación real, no un fallo ni una licencia para inventar entidades.**
- YouTube: `market_youtube_runs=0`, `market_youtube_queries=0`, `market_youtube_videos=0`. La fase está **implementada pero no validada contra la API pública con credenciales reales**. No se ha consumido cuota de Google ni activado facturación desde aquí.
- **Cierre del modo prueba:** se eliminaron de nuevo tanto el evento `push` del workflow como su autorización en `src/github-oidc.mjs`. Las únicas entradas conservadas son `schedule` y `workflow_dispatch`. Se restauró el test que rechaza `push`.

### Próxima prioridad P0
1. Verificar que existe un proyecto YouTube Data API con cuota gratis **sin facturación**, y que están disponibles credencial `YOUTUBE_DATA_API_KEY` y permiso explícito `YOUTUBE_MARKET_BUDGET_ENABLED=1`; no pedir ni introducir clave en chat. Sin esos requisitos el módulo no llama a YouTube, informa el bloqueo sin inventar métricas.
2. Incorporar más candidatos desde noticias actuales a entidades Wikidata, con precisión medible y verificación de fuentes primarias; ampliar la cobertura de temas sin aumentar pagos.
3. Tras obtener muestras reales de competencia YouTube, comparar oportunidad de varios temas, justificar descartes, registrar `market_selection_decisions` en D1 y asignar `sin_datos_suficientes` cuando corresponda. Vincular sólo elegibles a investigador Gemini gratuito / Qwen local.
4. Después guion con evidencias, voz canónica aprobada, visuales originales/licenciados, documental 8–14 min, QA, autorización editorial y subida a YouTube con OAuth permitido.

**Conclusión técnica:** se han integrado y probado dos nuevos módulos en producción (ingesta informativa y cotejo), y se preparó YouTube condicionado a cuota. No confundir infraestructura lista con inteligencia de mercado competitiva completada.


## 2026-10-21 · P0 FUNCIONAL: entidades de noticias, páginas corporativas y evaluaciones D1 automáticas (0008–0009)

### Construcción integrada en main
- **`tools/news_entity_discovery.py`**: extrae hasta dos términos corporativos potenciales de cada uno de ocho titulares públicos recientes de medios distintos; consulta Wikidata `wbsearchentities` y confirma **clasificación P31 de empresa + etiqueta exacta**, en hasta 16 búsquedas y una obtención de atributos. Sin nombres precargados por ChatGPT. Las relaciones siguen siendo hipótesis hasta leer y contrastar los artículos originales.
- `migrations/0008_news_entities_assessments.sql`, `src/news-entity-ingest.mjs` y `src/worker.js`: guarda entidades sugeridas y sus titulares, fuente Wikidata, posibles dominios oficiales, errores y estado editorial sin aprobar. Ruta OIDC de escritura `POST /api/market/entities/ingest`.
- **`src/market-assessment.mjs`**: evaluador directo del historial REAL en D1, reúne empresas descubiertas Wikimedia y noticias Wikidata, cuenta ventanas Wikipedia, noticias y **regiones YouTube realmente medidas**, escribe snapshots explicables `market_assessment_runs` y `market_assessments` (evaluación diaria idempotente); registra faltantes y bloquea selección/guion/publicación si faltan datos YouTube o fuentes primarias verificadas. Endpoint OIDC `POST /api/market/assess/run` y lectura privada `GET /api/market/opportunities`. No se crea «ganador» ficticio.
- **`tools/market_official_evidence.py`** reutiliza seguridad del descargador del investigador (`fetch_public`, HTTPS, verificación de DNS público y redirecciones, límite de bytes/tiempo). Recupera hasta **3 sitios P856** hallados en Wikidata y conserva URL/resolución, SHA-256 del HTML, cantidad de bloques y enlaces candidatos a documentos. Ningún artículo original, comunicado, derecho o afirmación empresarial se aprueba automáticamente.
- `migrations/0009_official_evidence.sql`, `src/market-official-ingest.mjs`, `tools/push_news_entity_assess.py`: persisten evidencia oficial como **candidata no contrastada** en D1 real por GitHub OIDC efímero; lectura administrativa `GET /api/market/official`.
- Workflow diario `.github/workflows/topic-discovery-smoke.yml`: ahora ejecuta **Wikimedia → RSS → identificación de empresas Wikidata → páginas oficiales seguras → cruce de titulares → YouTube condicional por cuota → evaluación y persistencia de bloqueos**. Se añadieron tests Python/Node y controles de presupuestos. No requiere que ChatGPT introduzca un tema ni escriba un episodio.
- Panel administrativo `public/index.html` y `public/app.js` expone evaluación auditable de oportunidades y lista de fuentes oficiales, con mensajes claros de falta de datos. Los contenidos no se inyectan como HTML.

### Pruebas y producción verificadas
- GitHub CI de nuevas pruebas Python/JS (incluido `test_news_entity_discovery.py`, `test_news_entity_ingest.mjs`, `test_market_assessment.mjs`, `test_market_official_evidence.py` y `test_market_official_ingest.mjs`) resultó `success`; hubo un error de sintaxis inicial en el colector y fue corregido antes de declarar éxito.
- **E2E primera tanda:** [Actions 39676935229](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39676935229), `success` con resolución Wikidata y evaluación D1. Lectura directa posterior: `market_news_entity_runs=1`, **2 relaciones noticia–empresa** (Q482267 América Móvil y Q53268 Toyota), `market_assessment_runs=1`, **4 empresas evaluadas**, `qualified_count=0`, `selected_wikidata_id=NULL`.
- **E2E segunda tanda:** [Actions 39678008994](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39678008994), `success` incluyendo descarga segura de páginas P856 y persistencia por OIDC. D1 confirmó `market_official_source_runs=1`, `market_official_source_items=2` (Toyota: 3 bloques, DuPont: 21 bloques, ambos con hash SHA-256). **0 hechos/propiedad intelectual verificados**. Hay 114 titulares RSS acumulados, 1 trabajo y 8 eventos intactos.
- Cloudflare cuenta Factor, DB `factor-de-gigantes-db`: migrations **0008 y 0009 aplicadas directamente a D1 remota** tras verificar esquema, bookmark Time Travel y exportación SQL temporal. Los trabajos existentes y las señales anteriores se conservaron. Las páginas oficiales y la evaluación **son resultados del sistema, no de generación manual de contenido por ChatGPT**.
- Los `push` temporales usados para dos pruebas integrales se retiraron del workflow **y de la lista de eventos permitidos por el verificador OIDC**. Permanecen `schedule` diario y `workflow_dispatch` manual.
- No se activó facturación ni cuota YouTube; `market_youtube_runs=0` al final de las pruebas, sin estadísticas inventadas. No se ejecutó un render documental final ni publicación.

### Prioridades siguientes, sin reiniciar auditorías
1. **P0 sin resolver:** clave y presupuesto *gratuito autorizado* de YouTube Data API, sin facturación. Conectar muestras reales de videos/canales en regiones hispanohablantes; comprobar que no se agota cuota y no se imprimen secretos. Si falta autorización, seguir otros módulos sin costo.
2. **P0/P1:** usar los documentos P856 recuperados como puertas de investigación, descargar originales oficiales y extraer afirmaciones comprobables con fechas/páginas, cotejar independientemente con medios y reguladores. Actualmente `primary_sources_verified=0`; no activar selección automática todavía.
3. Tras completar evidencia real multifuente, ampliar el evaluador para poder pasar de `awaiting_evidence` a candidatura seleccionable/cola persistente, con auditoría y autorización editorial separada.
4. Integrar `gemini_free` o `qwen_local` investigador y guionista, voz oficial, visuales y MP4 profesional 8–14 minutos; asegurar QA derechos, y solo luego OAuth/publicación aprobada.

**Estado honesto:** P0 ha avanzado en integración y persistencia real. El proyecto total aún está lejos de su final; no se asigna porcentaje inventado ni se confunden dos páginas descargadas con un documental autónomo.


## 2026-10-21 · P0/P1: PDF primarios rastreables y puente a investigador autónomo con coste bloqueado

### Código integrado en `main`
- `tools/market_pdf_evidence.py`: extrae **solo PDFs encontrados realmente** desde enlaces identificados en páginas P856 del radar. Reutiliza `tools/pdf_sources.py` y seguridad de `tools/research_engine.py` (HTTPS, DNS público, redirecciones, límites de descarga y tiempos). Hasta 2 documentos por ejecución, exclusivamente del **mismo hostname** que la página corporativa candidata; nunca adivina rutas ni rastrea todo un sitio. Si el PDF tiene texto legible, registra SHA-256, página física, índice de bloque y hasta 5 extractos breves por documento. No autoriza derechos ni verifica afirmaciones.
- Migración aditiva `migrations/0010_pdf_evidence.sql`: `market_pdf_evidence_runs`, `market_pdf_evidence_documents`, `market_pdf_evidence_fragments`. Aplicada directamente a Cloudflare D1 remota **tras bookmark Time Travel y export SQL temporal**; sin DROP ni cambios sobre jobs.
- `src/market-pdf-ingest.mjs` valida informe, origen, dominio de documentos, página dentro de páginas totales, hashes, orden y estado `uncorroborated`, antes de escribir con D1.batch e ID de ejecución idempotente. Worker: `POST /api/market/pdf/ingest` con GitHub OIDC efímero; `GET /api/market/pdf` solo con credencial administrativa.
- `tools/push_news_entity_assess.py` admite `--mode pdf`, manteniendo OIDC y bloqueo de permisos, y `.github/workflows/topic-discovery-smoke.yml` ejecuta automáticamente extracción/almacenamiento luego de la identificación de sitios corporativos; las nuevas salidas se conservan en artefactos temporales.
- `public/index.html` y `public/app.js`: sección privada «Informes corporativos y citas» con PDF, estado, hash, páginas y fragmentos cuando realmente existan. En ausencia de datos, informa vacío en vez de dibujar material simulado.
- `tools/market_investigator.py`: enlaza estos pasajes con el **proveedor real existente** de `tools/research_providers.py` (Gemini 2.5 Flash Lite) y conserva página/URL/hash/identidad Wikidata y citas E001… El puente también puede tomar fragmentos de **páginas web corporativas P856 realmente descargadas** cuando el PDF falla; estas páginas son candidatas a fuentes primarias, no hechos verificados. Si no hay pasajes no llama al modelo; si faltan `GEMINI_API_KEY` **o** `GEMINI_RESEARCH_FREE_CONFIRMED=1`, entrega estado `skipped_*` sin consumir tokens ni cuota. Nunca envía secretos en el informe. Las respuestas siguen `candidate_unverified` y `ready_for_script=false`.
- Tests Python `tests/test_market_pdf_evidence.py`, `tests/test_market_investigator.py`, Node `tests/test_market_pdf_ingest.mjs`, incorporados al CI existente: errores de red, PDF fuera de dominio, páginas, hashes, rechazos de derechos falsos, persistencia idempotente, pasajes web fallback, y omisión de llamadas Gemini por defecto.

### Resultado real — distinguirlo del contrato
- [GitHub Actions 39696304954](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39696304954), `success`: radar autónomo completo, fuentes corporativas → búsqueda PDF → persistencia por OIDC → evaluación D1.
- D1 remota tras ejecución: **1 corrida PDF**, **1 documento PDF corporativo candidato DuPont** y **0 extractos/páginas**. La URL del informe PDF fue descubierta realmente en HTML corporativo, pero su descarga quedó con `state=fetch_failed`. **No afirmar que se leyó ni se extrajeron hechos del documento**; se deben probar alternativas de recuperación autorizadas o buscar otros documentos públicos.
- Permanecen `jobs=1` y `events=8`; `market_youtube_runs=0`. Base conservada, sin llamadas YouTube ni publicaciones.
- Se retiró el permiso OIDC de evento `push` y el disparador temporal del radar después de E2E. La validación Cloudflare confirmó que Worker rechaza `push` y tiene módulo PDF desplegado.
- **Prueba del puente Gemini:** fixtures de proveedor y CI exitosos con fuente web y PDF **sin llamadas reales al modelo**. No se aseguró existencia de proyecto gratuito, ni se almacenaron claves, ni se activó facturación, ni se ejecutó una síntesis final.
- CI regresó a las reglas de seguridad estándar; se conserva workflow diario y manual. Las pruebas se ejecutan sobre `main`, no sobre una rama secundaria.

### Próximo trabajo desbloqueado
1. En P0, conectar cuota gratuita **autorizada** YouTube para muestras reales MX/ES y ranking respaldado por mercado, o conservar `insufficient_evidence`. No abrir facturación ni solicitar secretos por chat.
2. En P1, recuperar PDF alternativos verificables cuando el servidor bloquea descargas, mejorar localización de documentos originales (informes financieros/reguladores), contrastar pasajes y persistir **claims** con fuente, locator y estado; no verificar hechos por coincidencia textual.
3. Persistir resultados de investigación y preguntas pendientes en D1 y orquestar selección elegible → investigador Gemini/Qwen bajo coste limitado → guion 8–14 min. Gemini solo tras comprobación externa de uso sin facturación.
4. Producción audiovisual y YouTube continúan sin autorización de publicación ni derechos; no sustituir la voz canónica.

**Balance:** infraestructura PDF y handoff IA integrados, probado E2E el rastreo/registro; extracción de páginas PDF reales **aún no lograda** en la primera fuente observada. Investigación autónoma con Gemini **aún no activada**. No es un documental completo.


## 2026-10-21 · P1: expediente investigador persistente y conexión E2E al radar (migración 0011)

### Desarrollo ejecutado en `main`
- `migrations/0011_market_research.sql`: cinco tablas aditivas `market_research_runs`, `market_research_evidence`, `market_research_claims`, `market_research_claim_evidence`, `market_research_questions`. Cada fragmento conserva Wikidata QID, URL HTTPS, SHA-256, empresa, tipo de fuente (web/PDF), página PDF cuando existe y extracto. Las afirmaciones referencian IDs E001… existentes, con estado `candidate_unverified` y puerta de aprobación cerrada por CHECK SQL; las preguntas y sus estados quedan trazables. Nunca presenta modelo como fuente primaria.
- `tools/market_investigator.py`: refactorizado para conservar **manifiesto documental aun cuando no pueda ejecutarse Gemini**, con fechas, fuentes, extractos y estados explícitos. El resultado `candidate_claims_generated` con modelo autorizado también lleva evidencias para persistir; conserva el contrato previo `input_evidence` sin extractos por compatibilidad. Sin permiso expreso de modalidad gratis o sin clave, omite llamada, no inventa afirmaciones ni preguntas.
- `src/market-research-ingest.mjs`: valida tamaño, dominio HTTPS, Wikidata QID, hash, localizadores PDF, esquema de afirmaciones, evidencia IDs, fechas, flags no publicados. Recalcula **alertas numéricas**: cifras en una afirmación que no aparecen en los extractos citados se marcan `unsupported_numbers_need_review` y siguen no verificadas. Inserciones D1.batch idempotentes (sha del informe) con FK entre declaraciones y evidencias.
- `src/worker.js`: `POST /api/market/research/ingest` reservado al GitHub OIDC del workflow del radar y `GET /api/market/research` solo ADMIN_TOKEN. `tools/push_news_entity_assess.py --mode research` transmite expediente mediante JWT efímero sin volcar credenciales. `.github/workflows/topic-discovery-smoke.yml` encadena esta ingesta después del investigador, no como prototipo aislado.
- Panel `public/index.html`, `public/app.js`: sección privada «Investigación autónoma y evidencia», con estado del último expediente, fuentes y hashes, citas numéricas, afirmaciones sin aprobar y preguntas abiertas; no inyecta HTML de sitios externos.
- **Arreglo de bloqueo real** en `tools/market_official_evidence.py`: la primera etiqueta HTML de Toyota/DuPont podía contener 60–72 caracteres de menú. Ahora busca un pasaje sustantivo de al menos 90 caracteres antes del fallback, sin modificar fuentes ni fabricar texto. Añadida prueba `test_substantive_excerpt_beats_navigation_from_realistic_html`.
- `tests/test_market_research_ingest.mjs`: contrato sin IA y con modelo simulado, citas inválidas, páginas incoherentes, números no respaldados, URLs internas y derechos falsos; integrado en el CI. `tests/test_market_investigator.py` y la suite anterior preservadas. Primer CI detectó ruptura del campo `input_evidence`, corregida; el CI definitivo pasó.

### Operación real confirmada
- Pre-migración se confirmó que no había tablas 0011, hubo bookmark Time Travel y se solicitó exportación SQL sin operaciones destructivas; **aplicación remota D1 verificada**, cinco tablas presentes y `PRAGMA foreign_key_check` sin filas de error.
- **[GitHub Actions E2E 39698459949](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39698459949) = `success`**: ejecutó el radar completo y el nuevo paso **Persistir evidencias, preguntas y afirmaciones del investigador en D1** con autenticación real. La ejecución del modelo no ocurrió por falta de aprobación del nivel gratis, que es el comportamiento seguro esperado.
- Lectura independiente posterior de Cloudflare D1: `market_research_runs=1`, `market_research_evidence=1`, `market_research_claims=0`, `market_research_claim_evidence=0`, `market_research_questions=0`; ejecución `skipped_free_tier_not_authorized`, proveedor NULL, `verified_claim_count=0`. Primer fragmento procede de una página candidata de **Google, Q95**, 95 caracteres, con SHA-256 persistido. **Es un fragmento promocional web y NO demuestra una tesis documental ni hechos originales**.
- `market_official_source_items=7` acumulados y trabajos anteriores `jobs=1`, `events=8` preservados. Última verificación Cloudflare: Worker con módulo y rutas de investigación desplegados; `push` rechazado por OIDC. El trigger `push` temporal de E2E fue retirado; solo ejecución diaria y manual.
- Se verificó estado verde del CI tras restaurar políticas. El modo E2E no constituye investigación Gemini exitosa ni prueba de documental íntegro.

### Prioridad próxima
1. **Elevar calidad del contexto antes del LLM**: detectar y descartar promos y avisos genéricos, conservar varios fragmentos sustantivos ligados a un mismo episodio con integridad/hash/URL, rastrear documentos corporativos originales o reguladores SEC sin forzar accesos bloqueados; exigir evidencias diversas e independientes por empresa y verificación contextual, no una web comercial de 95 caracteres.
2. YouTube Data API sigue sin clave y autorización de cuota gratuita/no facturación, por lo que `market_youtube_runs=0`. No sustituir con visitas Wikipedia o titulares RSS; hay que medir mercado real y persistir elección razonada solo cuando exista.
3. Al tener evidencias suficientes, activar un **investigador real Gemini gratis** mediante aprobación del propietario en Github o **Qwen local** con presupuesto CPU adecuado; comparar y registrar preguntas/afirmaciones/citas en D1. Luego producir original guion largo, voz canónica, escenas y MP4 con QA. Nunca publicar sin derechos y autorización editorial.

**Conclusión:** P1 ha pasado de reportes efímeros a historial D1 de investigación en producción. Solo se guardó una evidencia corporativa no aprobada; 0 afirmaciones generadas, 0 verificadas. No se indica ningún porcentaje global de avance hasta cumplir criterios funcionales de la productora.


## 2026-10-21 · P1 · Correcciones funcionales del investigador y ampliación documental

**Código en `main`, no auditoría general.** El puente `tools/market_investigator.py` ahora usa `select_one_company`: agrupa pasajes por identificador Wikidata, prefiere páginas PDF/cobertura documental real, numera E001… solo dentro de **una** empresa, registra las entidades diferidas y evita generar un tema mixto de varias compañías. `src/market-research-ingest.mjs` impide que D1 reciba citas de diferentes empresas en un mismo expediente y valida la identidad declarada. También se impide combinar capturas de páginas y PDFs de fechas discordantes cuando ambas tienen fecha.

**Mejor selección de pasajes:** `tools/market_official_evidence.py` puntúa únicamente texto ya extraído y prioriza menciones documentales/operativas o fechas, penalizando cookies, avisos de privacidad, menús, newsletters y eslóganes. No reescribe ni afirma hechos. Corrige asimismo el patrón que detecta años. Los fragmentos marcados `generic_candidate` o `insufficient_context` dejan de enviarse al modelo; las páginas continúan rastreadas en sus informes de origen.

**Nueva fuente real, sin claves ni tablas duplicadas:** `tools/market_primary_pages.py` identifica páginas HTML sobre inversión, resultados y reportes **enlazadas por los sitios P856 que el radar descargó**, limita a tres páginas adicionales por corrida, usa el mismo descargador HTTPS/DNS seguro y vuelve a verificar el hostname tras la redirección. Registra URL, hash SHA-256, error o pasaje breve y nivel de calidad; no atribuye autenticidad, derechos o verificación. Se incorporó al workflow diario antes del investigador mediante `PAGINAS_INVERSORES_NO_CORROBORADAS.json`. `tools/market_investigator.py` admite `--primary-pages-report` y convierte solo los extractos sustantivos, pertenecientes a la compañía elegida, en evidencias. Se reutiliza la tabla D1 de investigación 0011, sin migraciones innecesarias.

**Pruebas ejecutadas:** la suite de GitHub Actions confirmó los contratos previos después de corregir una aserción de fixture que daba por elegida una empresa concreta, aunque el algoritmo prioriza según el material; nuevas pruebas `test_market_primary_pages.py` para mismo hostname, redirecciones de otro dominio y errores, tests de aislamiento por Wikidata, banners publicitarios y evidencia web entregada al investigador sin llamada Gemini. CI: [39700694100](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39700694100) `success`; cambios posteriores quedan sujetos a su CI. No se hizo publicación ni se habilitaron APIs cobrables.

**Distinción operacional:** los controles de calidad y la captura de inversores están codificados e integrados al workflow; **aún no hay comprobación E2E de nuevas páginas de inversión en D1**, ni investigación real con Gemini/Qwen ni selección basada en YouTube. El sistema continuará guardando estados de bloqueo si faltan fuentes de calidad y permisos gratuitos.

**Siguiente objetivo (sin desvíos):** verificar una ejecución diaria real que encuentre documentos corporativos distintos, conectar contraste independiente de afirmaciones, ejecutar Gemini gratuito o Qwen local solo con permisos y coste controlados; obtener datos YouTube reales con clave/cuota autorizadas, seleccionar candidato elegible y activar borrador-guion → voz canónica → montaje MP4 bajo QA/editorial. No proclamar porcentaje o autonomía completa prematuramente.

## 2026-10-22 · Investigación CPU conectada al radar y recuperación documental ampliada

- Verificación independiente inicial: `main` en `dee090d`, CI 39700855653 exitoso. Consulta de producción D1: un expediente, una evidencia, cero afirmaciones; modelo omitido por falta de autorización de Gemini. La consulta de Actions por `event=schedule` no devolvió ejecuciones: escribir un cron no acredita su funcionamiento.
- Corregida dependencia ausente: el radar instala `pypdf==5.9.0` antes de analizar documentos. Ahora las páginas de inversores conservan enlaces realmente observados, y el recolector PDF puede seguirlos manteniendo fecha, empresa, mismo hostname, límites de dos PDF y seguridad DNS/redirecciones. No adivina rutas ni atribuye derechos.
- El contexto conserva hasta tres fragmentos distintos de cada página admitida, con hash del documento e índice de bloque cuando está disponible. Se descarta texto genérico largo y banners promocionales; agrupar por una sola empresa y el máximo de diez evidencias siguen vigentes.
- `tools/qwen_research_cpu.py` conecta Qwen3-0.6B de texto al contrato común: una inferencia CPU, sin API de pago, 3700 tokens de entrada, 640 de salida, límite de generación, JSON estricto, citas existentes y métricas. No sustituye la voz canónica. El radar usa `qwen_local` por defecto; `RESEARCH_PROVIDER=disabled` lo detiene y `gemini_free` sigue exigiendo clave y confirmación gratuita. Solo corre en repositorio público, una ejecución diaria programada, sin cargar modelo cuando no hay contexto. La calidad editorial del modelo pequeño sigue por demostrar.
- La base de procedencia ya no puede ser reemplazada por metadatos devueltos por el proveedor. Las afirmaciones siguen candidatas no corroboradas, sin aprobar guion ni publicar.
- `check.yml` incorpora petición explícita de radar con `run_radar` manual o marcador `[radar-e2e]` en un commit de main. Solo tras pasar CI, solicita `workflow_dispatch` con token efímero de Actions; **no** cambia el verificador OIDC ni permite ingestas por evento push. Facilita validar el sistema conectado sin credenciales en el chat.
- Pruebas locales ejecutadas: **196 pruebas Python**, **16 archivos de pruebas Node** y YAML de ambos workflows válidos; `git diff --check` sin errores. Incluye nueve pruebas nuevas de integración documental, aislamiento de empresa/fecha/dominio, cita inventada, JSON inválido y ausencia de contexto. No son evidencia de inferencia real ni de un documental terminado.

**Estado al preparar esta entrega:** cambios probados localmente, pendientes de commit remoto y prueba real de radar/modelo/D1. No se modificó el Worker ni el esquema remoto. La siguiente anotación registrará el resultado real de Actions, incluso si falla o no encuentra fuentes.

**Para terminar el producto:** quedan estudio YouTube con clave/cuota gratuita configuradas, contraste independiente, selección elegible, guionista largo integrado, planificación audiovisual genérica, continuidad/licencias de voz, QA del MP4 completo y revisión editorial. OAuth/subida siguen sujetos al consentimiento del canal. Ninguno de esos requisitos se marca completo por estas pruebas.

### Resultado real y corrección posterior

- Commit remoto `69b38428f0ff1e0669520b4cc0cca0a1574725ae`. [Radar 39794507558](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39794507558) terminó `success`: ocho candidatas, seis series Wikimedia y cuatro feeds RSS. Ingesta OIDC real a D1. **Cero contexto documental útil, cero inferencias Qwen, cero afirmaciones.** Consulta independiente D1 confirmó el expediente `research-49e84d8899b4264f126b83dfd40e`, estado `skipped_no_documentary_evidence`.
- Causa observada: Google entregaba un fragmento promocional y un enlace de inversores externo (Alphabet); las otras primeras candidatas no eran recuperables. No atribuir cifras de Alphabet a Google ni cruzar dominios sin comprobar relación. La ausencia de datos no equivale a éxito del investigador.
- Corrección funcional: deduplicar sitios compartidos y probar **una sola segunda tanda de hasta tres compañías ya descubiertas**, solo si la primera no contiene texto documental ni enlaces recuperables del mismo dominio. Cada tanda se guarda separadamente en el contrato D1 vigente; la consolidación de hasta seis registros es local y no se envía como una ingesta incompatible. Presupuesto máximo explícito: seis portadas, tres páginas de informes, dos PDF y una inferencia; sin rastreo ilimitado.
- Se conserva la categoría del enlace observado para admitir rutas de inversores como `/ir/`. Los informes anuales de hasta 350 páginas no se rechazan solo por superar 35: se extraen **únicamente las primeras doce páginas**, con el total físico y el límite de lectura declarados; continúan límites de bytes/texto, sin fingir lectura completa.
- Pruebas locales posteriores: **200 pruebas Python** exitosas, YAML válido y sin errores de whitespace. Nuevas pruebas: segunda tanda sin repetir hosts, omisión cuando ya hay contexto, índices de pasajes, enlaces `/ir/` y total físico de un PDF anual con lectura parcial. La nueva corrida real debe registrarse por separado.
- El propietario confirmó que necesita configurar YouTube Data API. Se indicaron `YOUTUBE_DATA_API_KEY` en secretos Actions y `YOUTUBE_MARKET_BUDGET_ENABLED=1` en variables, con facturación desactivada; no se solicitaron ni recibieron claves por chat.

### Primera inferencia del radar y persistencia comprobada

- Commit `38ecd61e1caa88918d1d8c8fcccb8cdfbc89fc68`; [radar real 39797804872](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39797804872). Los logs muestran seis portadas consultadas (dos tandas de tres), tres legibles, cero páginas hijas elegibles y cero PDF. La segunda tanda recuperó BBVA México; Amazon y Mercado Libre no dieron texto utilizable.
- **Qwen3-0.6B de texto ejecutado realmente en CPU**: 383 tokens de entrada, 84 de salida, 20,94 segundos medidos de carga/inferencia, cero llamadas a API de pago. Produjo una afirmación candidata y una pregunta, con identificadores de evidencia existentes; no se usaron frases redactadas por ChatGPT para alimentar esta prueba.
- **Consulta independiente de D1 confirmó** `research-ade84000696ad4a516a611895d81`, proveedor `qwen_local`, modelo `Qwen/Qwen3-0.6B`, una evidencia, una afirmación, una pregunta y cero hechos verificados. `jobs=1` y `events=8` permanecieron intactos. No hubo migración ni nuevo despliegue Worker.
- **Limitación editorial concreta:** el único pasaje dice que la app y los canales digitales de BBVA están disponibles 24/7. La afirmación del modelo repite esa disponibilidad y pregunta qué operaciones permiten. Es contexto comercial superficial, no investigación histórica, contraste independiente, tesis documental ni guion de ocho minutos. La próxima mejora de investigación debe obtener documentación sustantiva y diversa, no ampliar esta frase artificialmente.
- La lectura de logs confirma ingesta real y finalización de pasos, pero el estado global de Actions aún se consultaba como `in_progress` al redactar este registro; no se confunde esa observación con aprobación editorial. YouTube sigue omitido por falta de clave y variable de cuota; la evaluación conservó selección NULL y publicación bloqueada.

**Qué está resuelto:** alternativa CPU conectada y primera inferencia con citas guardada en producción. **Qué sigue abierto:** fuentes primarias útiles e independientes, estudio YouTube, selección de tema elegible, guion autónomo largo y producción audiovisual completa con QA y derechos. El proyecto no está terminado.

## 2026-10-22 · Conexión autorizada de la clave YouTube y primera comprobación

- El propietario informó que creó y guardó la clave YouTube en GitHub. Se toma como autorización para el estudio público gratuito ya acordado, no para publicar ni activar facturación. `YOUTUBE_MARKET_BUDGET_ENABLED` ausente usa ahora `1`; un valor explícito `0` mantiene la pausa. La clave sigue siendo obligatoria y nunca se muestra.
- La prueba conserva dos empresas descubiertas × MX/ES, como máximo cuatro `search.list` y cuatro `videos.list`. Referencia de cuota comprobada el 2026-10-22: https://developers.google.com/youtube/data/determine_quota_cost (actualizada 2026-10-15): search tiene depósito separado, costo uno por llamada; el límite de ocho representa cuatro búsquedas y cuatro lecturas en sus depósitos, no una cuota global garantizada de la cuenta.
- Diagnóstico HTTP: se preservan únicamente código y motivo permitido (`accessNotConfigured`, cuota, permisos, etc.). Nunca se guarda la URL con clave ni mensajes remotos arbitrarios. Ante el primer fallo de credencial/cuota se detienen ambas iteraciones de empresas.
- Se añadieron pruebas de ausencia de filtración del secreto en errores y detención después del primer HTTP rechazado. **Pendiente al preparar el commit:** probar la clave real desde Actions y verificar estadísticas en D1. La declaración del propietario por sí sola no acredita permisos ni muestras válidas.

### Clave probada y estudio YouTube real

- Commit `b0197937ebc84edcecd804e0c4185acbec8ad29a`; CI [39802674332](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39802674332) y [radar 39802726509](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39802726509) terminaron `success`. Los logs confirman clave presente y permiso de cuota, sin mostrar la clave.
- **Cuatro muestras observadas**: Google MX/ES y Theranos MX/ES, diez videos por muestra, sin errores de API. Ingesta OIDC confirmada e inspección independiente de D1: `ytrun-1174e425e43ca0efbc626e8aa68f`, estado `measured`, cuatro consultas y **cuarenta observaciones**. No son necesariamente cuarenta videos distintos: un video puede aparecer en ambas regiones.
- Medianas de vistas por día de antigüedad observadas: Google MX 22.915,64 / ES 15.664,85; Theranos MX 11.257,38 / ES 53.799,74. Son muestras de resultados, no volumen total de demanda ni vistas geolocalizadas. No se obtuvieron CTR, retención privada ni autorización de publicación.

## 2026-10-22 · Selección para investigar y cola persistente (0012)

- Se detectó una dependencia circular: el evaluador histórico nunca seleccionaba porque fijaba `primary_sources_verified=0` y exigía hechos contrastados antes de permitir investigar. Ese evaluador sigue protegiendo preparación editorial; la nueva selección decide **qué investigar**, manteniendo bloqueados guion/video/publicación.
- `src/market-research-selection.mjs` calcula prioridad desde D1, sin aceptar puntuaciones del runner. Requiere muestras recientes de MX/ES, al menos tres videos distintos, dos canales y una ventana independiente completa de catorce días. Deduplica videos compartidos entre regiones, conserva IDs de ejecuciones y videos, y compara velocidad observada, cambio de interés Wikimedia y diversidad de canales. Es una heurística entre las empresas medidas, sin promesa de audiencia ni revisión factual automática.
- Migración **aditiva 0012** aplicada a D1 remota: historial `market_research_selection_runs` y `market_research_queue`. Índice único parcial y reserva SQL impiden dos investigaciones activas simultáneas; reintentos del mismo snapshot son idempotentes. Una investigación abierta se conserva aunque cambie la prioridad diaria. Ambas tablas bloquean autorización de publicación; la cola también bloquea guion.
- Worker desplegado conservando `ADMIN_TOKEN`, `RENDERER_TOKEN`, `GITHUB_DISPATCH_TOKEN`, D1, variables y assets existentes. Nuevo `POST /api/market/research-selection/run` solo con OIDC del radar; `GET /api/market/research-queue` solo ADMIN. Confirmados después los bindings, `jobs=1`, `events=8` y `foreign_key_check` sin errores. Se obtuvo bookmark Time Travel previo; la exportación SQL solicitada no llegó a confirmarse como descarga completa, por lo que no se declara backup exportado.
- Workflow: YouTube/persistencia pasan antes de la búsqueda documental; la selección D1 se guarda en archivo y restringe al recolector/investigador a esa empresa. Si no hay fuentes para la elegida, se conserva el bloqueo y **no se sustituye por otra compañía** simplemente porque tenga un texto fácil de recuperar. El modo exploratorio previo se mantiene cuando no existe selección.
- Panel: sección privada «Próxima investigación», tema activo, estado, puntuación comparativa y datos de muestra. Diferencia búsqueda de fuentes de aprobación editorial; no expone secretos ni inserta HTML de terceros. Su despliegue de assets debe comprobarse tras el build de main.
- Verificación local: **203 pruebas Python**, suite Node completa sin fallos (incluidas cuatro nuevas pruebas de selección), YAML y Python embebido válidos. Las pruebas nuevas usan SQLite real con todas las migraciones, verifican idempotencia/una cola activa, rechazo de datos ausentes/caducados, deduplicación y autenticación. **Pendiente al preparar el commit:** publicar código en main y ejecutar de extremo a extremo selección → empresa elegida → búsqueda/expediente.

**Límites que siguen abiertos:** documentos históricos sustantivos e independientes para el tema elegido, contraste de afirmaciones, guionista largo, voz y montaje genéricos con QA/derechos. La clave y el primer estudio ya están comprobados; el documental completo aún no existe.

### Selección E2E comprobada y panel desplegado

- Commit `4f71af2a2850165c25f125e8a1a7c8126b5f0be8` en main. [CI 39805253904](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39805253904) y [radar E2E 39805302397](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39805302397) = `success`. GitHub confirmó 203 pruebas Python y 70 pruebas Node, todas exitosas. También apareció una ejecución `schedule` real [39803634070](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39803634070), exitosa: ya no se trata solamente de un cron escrito.
- El sistema seleccionó **Theranos, Q16956307**, entre **dos empresas con muestras comparables**. Consulta directa D1: cola `rq-4ddc49f3094f2d350bec704cc1bd`, estado `awaiting_sources`, puntaje heurístico 91,86; Google quedó en 84,27. Theranos: trece videos distintos/doce canales; Google: dieciséis/quince. Es prioridad de investigación entre dos muestras, no el estudio completo de tres a diez candidatos del plan ni una aprobación documental.
- Snapshot `selection-4ddc49f3094f2d350bec704cc1bd` conserva método, componentes, IDs de videos y ejecución YouTube `ytrun-4815a3a84ef5b0a1c57d10e34965`. La selección procede de D1 y estadísticas recuperadas por el sistema; no de un tema introducido manualmente por ChatGPT.
- El flujo respetó la selección: **cero sitios corporativos recuperables para Theranos**, cero fuentes útiles y cero llamadas Qwen para inventar contenido. Expediente `research-b3b745d616223e08221c455b0b03` guardado con `skipped_no_documentary_evidence`. No cambió automáticamente el episodio a BBVA/Google para aprovechar un texto promocional.
- Build Cloudflare **`b61593e7-c8ce-4536-92ae-65372ca05e8a` = success**, commit exacto `4f71af2...`, comando preflight y `npx wrangler deploy`; backend y assets del panel publicados por la integración GitHub existente. La lectura visual autenticada del panel no se realizó desde este entorno; el fetch web del dominio no estuvo disponible para esta herramienta.
- `script_authorized=0`, `publication_authorized=0`; `jobs=1` y `events=8` conservados. El evaluador editorial histórico todavía devuelve selección NULL por ausencia de hechos primarios contrastados; la cola nueva es la fuente de la **selección para investigar**, visible por `/api/market/research-queue`.

**Siguiente bloqueo concreto:** el recolector necesita localizar documentación regulatoria/judicial o referencias primarias de una empresa cerrada, sin depender de una portada P856 activa. Después debe contrastarla, producir el guion autónomo y conectar voz/montaje largo. No se requiere otra clave YouTube: esa integración ya funciona.



## 2026-10-22 · Equipo de investigación por funciones y cuotas persistentes (0013)

**Solicitud del propietario:** implementar cada proveedor según su capacidad, conservar Qwen y mantener cero pagos. Confirmó que por ahora **solo está guardada la clave de YouTube**. No se afirma activación de otras cuentas.

- `tools/ai_clients.py`: clientes HTTP sin SDK pesado para Tavily, Exa, Gemini 3.8 Flash, Groq GPT-OSS-120B, Mistral Small y OpenRouter `openrouter/free`. Clave + declaración explícita de modalidad gratuita + reserva D1 previa; sin redirecciones de credenciales, reintentos automáticos, plugins de búsqueda pagados ni upgrades. Errores sanitizados. Los límites son propios del proyecto, no una auditoría de facturación de cuentas externas.
- `tools/ai_source_discovery.py`: referencias externas observadas de Wikipedia como descubrimiento (no evidencia), dos búsquedas Tavily y dos Exa cuando estén configurados. Recupera hasta cuatro documentos originales públicos, prioriza autoridades/reguladores, valida HTTPS/DNS/redirecciones/bytes y conserva pasajes con hash/localizador. No convierte snippets del buscador en evidencia ni contiene compañías o rutas preparadas. Amplía el caso de empresas cerradas sin P856 vigente; todavía requiere E2E real.
- `tools/ai_research_pipeline.py`: Qwen3-0.6B CPU realiza una extracción preliminar acotada y respaldo; Gemini analiza el expediente; Mistral y OpenRouter solo se invocan como alternativas; Groq revisa citas, contradicciones y falta de contexto. Cloudflare clasifica pasajes mediante binding, sin eliminarlos automáticamente. Cada etapa registra éxito/omisión/error; ninguna coincidencia entre modelos acredita corroboración independiente.
- `src/ai-research-team.mjs`: reserva SQL atómica y de un solo uso con topes diarios/mensuales. Escrituras solo con OIDC exacto del radar; lectura administrativa. Validación de empresa única, fechas, SHA-256, fuentes, citas E###, categorías, revisión completa y flags sin autorización. Recalcula alertas numéricas; mantiene aprobaciones en cero. Una cola con pasajes pasa de `awaiting_sources` a `researching`, no a aprobada.
- `0013_ai_research_team.sql` **aplicada a D1 remota**, aditiva, sin reconstruir tablas. Bookmark previo `000000b2-00000000-0000510c-955864cf441ae28448e422e28e9f758d`; no se declara exportación SQL completa. Antes del cambio: `jobs=1`, `events=8`, `foreign_key_check` vacío. Historial nuevo de reportes JSON y reservas, con CHECK de autorización cerrada.
- El radar diario integra el flujo después de la selección y las fuentes corporativas, sin cambiar OIDC a eventos push. Qwen solo se descarga con pasajes. `RESEARCH_PROVIDER=disabled` detiene IA/buscadores autenticados; `qwen_local` conserva inferencias exclusivamente locales. El nuevo panel muestra equipo, fuentes, afirmaciones y revisiones, conservando aparte el historial anterior.
- `wrangler.jsonc` incorpora binding `AI` y `CLOUDFLARE_AI_FREE_CONFIRMED=0`. Consulta OAuth de suscripciones rechazada con 403 por falta de cobertura de scope; **no se verificó el plan**, no se activa inferencia Cloudflare ni se cambia facturación. Los otros proveedores esperan claves/variables. Guía exacta: `docs/CONFIGURACION_EQUIPO_IA.md`.
- Actualizado el adaptador Gemini anterior a 3.8 Flash por defecto; 2.5 conserva compatibilidad, pero Google restringe acceso de proyectos nuevos a esa familia.

**Validación local realizada:** 218 pruebas Python exitosas; 76 casos Node ejecutados individualmente con `--test-isolation=none` para obtener conteo real en este entorno; sintaxis JS, YAML y diff sin errores. Pruebas nuevas usan transportes simulados y SQLite real con todas las migraciones: no equivalen a llamadas reales de Gemini/Groq/Tavily/Exa/Mistral/OpenRouter/Cloudflare ni prueban calidad documental.

**Pendiente en esta entrega:** commit remoto, CI, build Cloudflare y un radar real con las credenciales disponibles; registrar sus resultados y bloqueos. No se ha generado un documental completo ni iniciado publicación. La identidad vocal canónica permanece íntegra.


### Aceptación técnica remota inicial del equipo IA

- Código remoto `4e9f39e24be254da89e94c40fa63f3d329ac7670` en `main`.
- CI [39811165131](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39811165131) exitoso: 218 Python y 76 Node; health/archivos públicos/autenticación del renderer comprobados por CI (esto no prueba investigación).
- Build automático Cloudflare `2395af30-9db0-4097-ad96-29600619287a` seguía en inicialización; se publicó el backend mediante API Cloudflare con los 18 módulos del commit probado. Despliegue directo `e08cdec754064b5799f8bc9138655654`, HTTP 200. Se conservan assets previos mientras finaliza el build automático, por lo que todavía no se declara panel nuevo publicado.
- Migración 0013 confirmada posteriormente: ambas tablas nuevas existen; `jobs=1`, `events=8` y sin violaciones FK. Ninguna inferencia externa nueva activada.
- Se solicita una única ejecución manual real del radar con el disparador operacional existente `[radar-e2e]`, para comprobar fuentes y Qwen con las credenciales disponibles. Resultado pendiente.


### Primer radar real del equipo y corrección de cobertura

- [Radar 39811587987](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39811587987), commit `16a82db6f15abcedfff7ec1b0e31de29b2a026b9`, terminó exitoso. OIDC e ingesta del nuevo informe en D1 confirmados independientemente: `ai-e6ff2a9f092e760a41f851098473`, Theranos Q16956307, **cero pasajes, cero inferencias, cero afirmaciones y cero reservas externas**. No se presenta el estado success del workflow como éxito de investigación.
- Se intentaron cuatro documentos; un PDF FDA fue descargado, pero sin texto relevante extraíble, y tres páginas no se recuperaron. Tavily/Exa reportaron `missing_key`; las inferencias se omitieron por falta de evidencia.
- Diagnóstico: se recortaban los enlaces externos a 160 **antes** de priorizar autoridades. La página posee referencias regulatorias posteriores. Se amplía la lectura de la lista a 800 enlaces dentro del mismo límite de bytes; se conservan cuatro descargas y diez pasajes máximos. Regresión nueva con una referencia pública después del enlace 200; no se agregan rutas de Theranos al código.
- Mayor robustez frente a JSON de proveedor malformado (commit `2e5028e18e69ce67250e0e0dc7bf5b35981cff73`) y errores locales sanitizados por tipo. Validación local actual: **219 Python** y 76 Node previos sin cambios de JS en esta corrección.
- Build Cloudflare `2395af30-9db0-4097-ad96-29600619287a` terminó `success` para `4e9f39e24be254da89e94c40fa63f3d329ac7670`: backend y assets del nuevo panel publicados por el build. No se declara revisión visual autenticada.
- Segunda ejecución acotada para validar la corrección de cobertura: pendiente.


### Recuperación real: bloqueo de contenido y diversidad de fuentes

- Segunda corrida [39812041195](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39812041195) localizó las referencias SEC/Justice antes perdidas, pero conservó cero pasajes (`ai-83d6cb8a8e64ef831a5b2a5c86d0`). Tercera corrida diagnóstica [39812615865](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39812615865) guardó `ai-007c49484aafa3bdec6bf42a7a04`: respuesta Justice de solo 2554 bytes, cero bloques legibles; PDF FDA de cuatro páginas con texto extraído sin pasajes de entidad utilizables; SEC rechazó HTTP. Sin inferencias ni reservas externas. No se sortean desafíos de acceso ni se declara leído el artículo por recibir HTTP 200.
- Diagnóstico persiste únicamente longitud, MIME, primeros cuatro bytes en hexadecimal, conteo de bloques y vista breve de texto público; nunca cabeceras de autenticación. Se limita a dos autoridades y dos fuentes independientes cuando ambas clases existen, máximo una por hostname y cuatro descargas totales. La cobertura oficial bloqueada ya no agota todos los intentos. `full_document_text_read` es falso cuando no se extrajeron pasajes relevantes.
- Regresión de diversidad: dos autoridades devuelven un HTML sin contenido y la fuente independiente todavía se descarga. Suite Python actual: **220 pruebas**, sin fallos. No cambió JS respecto a los 76 casos verificados.


### Aceptación real: Qwen extrajo afirmaciones sobre Theranos

- Código `e041d3b7f2ca56ac7ee39c022ba0bdb76b37d247`; CI [39813020893](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39813020893) exitoso (**220 Python, 76 Node**).
- Radar [39813067162](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39813067162), job `119944253232`, terminó `success`. La recuperación diversificada produjo **tres pasajes de una sola noticia secundaria original de Ars Technica (2016)** sobre el cierre de laboratorios y giro a dispositivos. SEC siguió rechazando acceso; Justice y un archivo web no aportaron contenido legible. No hay corroboración independiente suficiente ni se presenta esa noticia como fuente primaria.
- Qwen3-0.6B CPU fue invocado realmente: **905 tokens de entrada, 144 de salida, 42,9 s** de carga/inferencia, cero llamadas API pagadas en sus métricas. Extrajo dos afirmaciones candidatas con citas existentes y dos preguntas (una redundante con lo ya citado); la salida fue en inglés. Se refuerza después la instrucción explícita de español latinoamericano en investigador, sistema Qwen y revisor; la obediencia lingüística posterior sigue pendiente de otra inferencia, no se declara resuelta solo por cambiar el prompt.
- Lectura independiente D1 confirmó `ai-256da8832ba3984d7e0e3ee8cfd0`, `candidate_claims_generated`, tres pasajes, dos afirmaciones no verificadas, dos preguntas y cero revisiones Groq. La cola Theranos pasó a **`researching`**, con `script_authorized=0` y `publication_authorized=0`. `jobs=1`, `events=8`, **cero reservas de APIs externas** y `foreign_key_check` vacío.
- Estado real de configuración observado: Tavily/Exa/Mistral/OpenRouter `missing_key`; **Gemini y Groq detectaron valores configurados pero `free_mode_unconfirmed`**, por lo que no se invocaron ni se probó que las claves fueran válidas. Cloudflare también `free_mode_unconfirmed`. Se consulta al propietario por la modalidad de las dos cuentas; no se solicitan claves por chat ni se presumen permisos/facturación.
- La integración funcional del equipo y la inferencia local están comprobadas. **Pendientes:** activación/prueba real de las APIs con cuentas gratuitas confirmadas, calidad y contraste documental suficiente, respuesta en español demostrada y producción audiovisual completa. No se genera guion aprobado, render ni publicación.


**Cierre de entrega del equipo IA:** CI final de código [39813779576](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39813779576), commit `9cd905478952aee10fac69d6d1c078f5119024b7`, terminó `success` (220 Python/76 Node). Build Cloudflare `fcae8627-064a-4166-964f-b04cbafc2082` terminó `success` para `e041d3b7f2ca56ac7ee39c022ba0bdb76b37d247`; los cambios posteriores de código son instrucciones del investigador ejecutado en Actions, sin cambios adicionales del Worker/panel. Integraciones implementadas, panel publicado e inferencia Qwen real comprobada. Modalidad de Gemini/Groq consultada al propietario, aún sin respuesta en este cierre; no se activa por transcurso del tiempo. Tavily/Exa y alternativas mantienen sus requisitos de configuración. La fábrica documental completa sigue abierta.


## 2026-10-22 · P1 · Configuración gratuita confirmada y corroboración de evidencia por fuente

**Contexto validado por propietario:** Captura Google AI Studio del proyecto `factor-de-gigantes` presenta clave Gemini y texto **Nivel gratuito**, con opción para configurar facturación, no activada. Captura GroqCloud presenta **Gratis**, importe **$0** y **Plan actual**. No se han compartido claves ni agregado tarjeta. Aun así, la captura no prueba que una clave específica funcione contra un modelo específico: debe comprobarse en ejecución real sin facturación.

**Cambios realizados directamente en `main`:**
- `tools/ai_clients.py`: el identificador `gemini-3.8-flash` fue sustituido por `gemini-3.5-flash-lite`, modelo que la página de precios Gemini Developer API documenta con nivel gratuito. Es solo API de generación de texto con JSON, sin tools, búsqueda facturable, Batch, Priority ni Flex. Groq continúa con `openai/gpt-oss-120b` documentado en los límites del Free Plan.
- `.github/workflows/topic-discovery-smoke.yml`: tras confirmación visual de ambas cuentas gratuitas, Gemini y Groq disponen de bandera por defecto `1` en el workflow; **si el propietario define la variable de Actions con valor explícito `0`, la desactiva**. Conserva secretos de Actions, OIDC, las reservas D1 `ai_budget_reservations`, máximo una inferencia por proveedor y ejecución y límites diarios/mensuales. No se tocan las cuentas ni la configuración de facturación.
- `tools/ai_research_pipeline.py` añade `evidence_gaps`: compara URLs y hosts REALES por afirmación y detecta cuando varias citas proceden de **un solo documento o medio**, y si falta autoridad regulatoria. Añade `source_quality` y una matriz `claim_gaps`, siempre `requires_corroboration`, sin declarar hechos verificados, sin aprobar investigación o publicación.
- `src/ai-research-team.mjs` verifica opcionalmente esa matriz antes de persistir en D1. Recalcula fuentes y dominios de los mismos pasajes; impide que un modelo/cliente marque `all_claims_verified=true`, invente más fuentes o falsee la diversidad. Se conserva el esquema histórico D1 0013, no necesita nueva migración.
- Tests `tests/test_ai_free_model_gate.py`, `tests/test_ai_source_corroboration.py` y nueva regresión JS `tests/test_ai_research_team.mjs`: modelos gratuitos, una inferencia por proveedor, múltiples extractos de una sola URL no equivalen a corroboración, verificación no autorizada siempre false. Permanecen todos los tests anteriores.

**Fuentes públicas usadas para elegir el modelo:** `https://ai.google.dev/gemini-api/docs/pricing` documenta `gemini-3.5-flash-lite` con nivel gratuito; `https://console.groq.com/docs/rate-limits` incluye `openai/gpt-oss-120b` en el Free Plan. Este cambio no constituye por sí mismo llamada remota ni prueba de validez de la clave.

**Evidencia actual al inicio de esta entrega:** D1 muestra la cola Theranos en `researching`; expediente previo Qwen con 3 pasajes, 2 afirmaciones candidatas y 0 verificados; ninguna reserva IA externa anterior. El siguiente paso operativo es ejecutar el radar mediante el mecanismo `[radar-e2e]` aprobado del propio repositorio, comprobar Gemini/Groq reales con límites, inspeccionar matrices D1 y registrar fallos de proveedor sin repetir solicitudes ni gastar fuera del plan gratis. No hay autorización para producir/publicar un video todavía.


## 2026-10-22 · P1 — integración REAL Qwen → Gemini Free → Groq Free, calidad multifuente

### Evidencia confirmada (no confundir con prototipo)
- Capturas del propietario verifican GroqCloud en **Gratis ($0), Plan actual**, y proyecto `factor-de-gigantes` de Google AI Studio con **Nivel gratuito**, sin facturación activada visible. No se pidió acceso a secretos ni se habilitaron pagos.
- Modelos admitidos por el flujo: Gemini `gemini-3.5-flash-lite` (documentado Free Tier en `https://ai.google.dev/gemini-api/docs/pricing`); Groq `openai/gpt-oss-120b` (Free Plan en `https://console.groq.com/docs/rate-limits`). Se sustituyó el anterior `gemini-3.8-flash` para no arriesgar llamadas a una modalidad con tarifas de pago. La cuenta gratuita no equivale a garantía perpetua: se conservan cuotas y las variables de apagado.
- `.github/workflows/topic-discovery-smoke.yml` configura por defecto `GEMINI_RESEARCH_FREE_CONFIRMED=1` y `GROQ_RESEARCH_FREE_CONFIRMED=1` conforme a las capturas; cualquier variable de GitHub Actions con valor explícito `0` anula ese permiso. Las claves permanecen en Actions Secrets. Las reservas siguen limitadas en D1 a 4/día y 100/mes por proveedor según `src/ai-research-team.mjs`, y una generación por proveedor por ejecución según `FreeClients`.
- `tools/ai_research_pipeline.py`: añadió matriz `source_quality` por empresa/afirmación con cantidad de documentos, dominios independientes y respaldo de autoridad regulatoria; `claim_gaps` se mantiene `requires_corroboration` aunque dos modelos coincidan. `src/ai-research-team.mjs` valida que el cliente no infle cantidad de URLs/dominios ni declare `all_claims_verified=true`. `public/app.js` expone la matriz en panel privado. No fue necesaria migración D1 adicional.
- Nuevas pruebas `tests/test_ai_free_model_gate.py`, `tests/test_ai_source_corroboration.py` y extensión de `tests/test_ai_research_team.mjs` pasaron en CI. CI final para panel [39823265737](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39823265737): `success`.
- Ejecución de integración [GitHub Actions 39823284838](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39823284838) finalizó `success`, en `main` y mediante `workflow_dispatch` disparado por la puerta existente en `check.yml`; NO se permitió evento push en el OIDC ni se modificaron claves. Acreditó 4 de 4 muestras YouTube (dos compañías × dos regiones), selección `Q16956307` Theranos y descarga de tres extractos reales de Ars Technica.
- Logs E2E: `qwen extract success`, `gemini analyze success`, `groq review success`; Mistral/OpenRouter `not_needed`, Cloudflare `free_mode_unconfirmed`, Tavily/Exa `free_mode_unconfirmed`; Gemini modelo `gemini-3.5-flash-lite`, Groq `openai/gpt-oss-120b`. No hay prueba de consumo monetario: no se activó facturación ni pasarela de pago.
- Lectura **independiente de Cloudflare D1**: `ai_budget_reservations` con 1 Gemini + 1 Groq (2026-10-22). Expediente `ai-c03cb83a12585e6e76a4f8facbb8`, Q16956307 Theranos, estado `candidate_claims_generated`, `analysis_provider=gemini`, 3 extractos, **7 afirmaciones en español** y **7 revisiones Groq** (`supported_by_excerpt`, no `human_verified`), 1 pregunta de investigación. Matriz `source_quality` calculó **1 documento único / 1 dominio / 0 autoridades regulatorias**. Los 7 ítems tienen `only_one_document`, `no_independent_domain` y `no_regulatory_primary_document`, siguen `requires_corroboration`. Ninguna afirmación obtuvo verificación independiente, nadie autorizó guion o publicación. Estas afirmaciones provienen de **un solo artículo de Ars Technica 2016**; son hipótesis y no equivalen a un dossier contrastado.
- Workers de Cloudflare: GET del script confirmó presencia del validador multifuente y de la ruta del equipo IA; despliegue confirmado a las 17:31:17Z de 2026-10-22. Los datos históricos D1 y la cola `researching` de Theranos se conservaron.

### Siguiente trabajo sin desvíos
1. Resolver cobertura factual de Theranos con referencias regulatorias/juicios, archivo original y fuentes independientes que permitan evaluar las 7 afirmaciones; no acreditar veracidad por puntuación de Groq ni por artículos repetidos. Descargar originales respetando accesos y licencias.
2. Constrastar discrepancias y periodos; volver a pasar Gemini/Groq dentro de límites y generar nuevas preguntas basadas en `source_quality.claim_gaps`, sin depender de un episodio preparado manualmente.
3. Pasar a **guionista autónomo de 8–14 min** con trazabilidad de cada afirmación narrada, solo cuando haya dossier multifuente suficiente; conectar voz canónica, escenas y MP4 a la cola D1 con QA legal/editorial. No publicación automática sin aprobación.

**Estado final de este bloque:** integración real de dos APIs gratuitas, revisión y persistencia D1 CONFIRMADAS; calidad documental todavía insuficiente y no existe un documental final autónomo de 8–14 min.


### Seguimiento del mismo bloque — cola automática de fuentes pendientes

- Se corrigió `src/ai-research-team.mjs` en `main`: al persistir un expediente con `source_quality.claim_gaps` y cobertura insuficiente, el sistema devuelve la cola activa a `awaiting_sources` en lugar de mantener `researching`. Si el expediente cuenta con varias fuentes pero aún requiere revisión, permanece `researching`. No altera filas que ya tengan estado `review` o `closed`, ni concede permisos de guion o publicación.
- Se incorporó prueba de regresión D1 con SQLite real en `tests/test_ai_research_team.mjs`, incluyendo la condición de NO retroceder una decisión humana `review`.
- **Corrección remota verificada inmediatamente sobre la evidencia real ya almacenada:** se obtuvo bookmark Time Travel de D1 `000000c0-00000000-0000510c-4232f05a8fc72a60a4845f41cf652980`, se comprobó el expediente `ai-c03cb83a12585e6e76a4f8facbb8` con `independent_domains=1`, siete afirmaciones aún pendientes, `all_claims_verified=false`, y se actualizó **una única fila** de `market_research_queue` para Theranos Q16956307 desde `researching` a `awaiting_sources`. Verificación posterior D1: `script_authorized=0`, `publication_authorized=0`, `PRAGMA foreign_key_check` sin violaciones. No se borraron citas, trabajos ni eventos.
- Se revisó despliegue Cloudflare tras el cambio: el Worker servía el nuevo validador documental pero **todavía no el cambio posterior de transición `independent_sources_required`**. Distinguir código escrito/commit de despliegue; esperar build autorizado o ejecutar el despliegue de forma segura cuando las verificaciones estén verdes. No declarar que el siguiente ciclo remoto aplica por sí solo la nueva transición hasta confirmar la versión desplegada.
- **Pendiente:** CI del commit de transición, actualización confirmada del Worker y comprobar en un nuevo ciclo que `awaiting_sources` no repite inferencias innecesarias sobre exactamente la misma noticia. Evitar otro consumo de Gemini/Groq únicamente para validar el cambio de estado.


### Endurecimiento de QA documental posterior

- `src/ai-research-team.mjs` valida ahora la causa exacta de cada bloqueo (`only_one_document`, `no_independent_domain`, `no_regulatory_primary_document`) recalculándola del conjunto efectivo de citas. No acepta que un proveedor omita avisos de fuente única o declare falsamente la existencia de fuentes regulatorias. No se añaden permisos ni gasto.
- `tests/test_ai_research_team.mjs` añade regresión contra omisión artificial de las causas de bloqueo. Las comprobaciones previas del ciclo Qwen/Gemini/Groq permanecen integradas en `main`.
- **No atribuir despliegue ni CI final a estos últimos dos commits** hasta confirmar sus jobs; la última ejecución integral `39823284838` anterior a la nueva lógica de cola sigue siendo la prueba operativa de inferencia real. La corrección puntual del estado D1 sí fue ejecutada y verificada directamente.


## 2026-10-22 · P1 — continuidad real de investigación, nuevas fuentes y no repetir inferencias

### Causa operacional (observada directamente en D1, no asumida)
- En el E2E Gemini/Groq `39823284838` el descubridor encontró **324 enlaces externos** desde el artículo Wikipedia de Theranos, pero detuvo la descarga después de **4 URL**: una denuncia SEC en PDF falló con HTTP, una página del DOJ se descargó pero sin bloques de texto, un espejo histórico tampoco ofreció texto, y Ars Technica 2016 fue la única fuente legible (**3 extractos de 1 dominio**). No había evidencia suficiente para el guionista; la cola se mantiene `awaiting_sources`.
- El resultado demuestra un fallo de presupuesto y priorización de documentos, no una falta de temas ni una verificación factual exitosa. No se deben elegir documentos manualmente en ChatGPT para producir cada episodio.

### Código integrado en la rama `main`
1. `tools/ai_source_discovery.py`: máximo **8 descargas HTTP documentales** por corrida y como máximo **5 por clase** (autoridades / medios), una URL por hostname; alterna ambos grupos para no agotarse con portales oficiales bloqueados. Penaliza espejos archivados que responden con HTML de bloqueo y prioriza rutas referentes a la entidad, conservando la URL observada y su procedencia. Se detiene antes si ya consiguió dos URL de dos dominios y al menos una autoridad pública con texto; **no equivale a corroboración de hechos**.
2. La selección de investigación `src/market-research-selection.mjs` recupera del último expediente D1 de la misma empresa, dentro de siete días, las URL que ya se intentaron y hasta 4 pasajes públicos con SHA-256; entrega este historial al colector mediante el resultado OIDC. El colector evita volver a descargar esas URL. **El contexto histórico solo se reutiliza cuando la nueva corrida consigue al menos una fuente textual realmente nueva**. Si no hay nuevas fuentes, deja cero pasajes y omite Qwen/Gemini/Groq, no gastando la misma consulta gratuita de IA otra vez.
3. Compatibilidad hacia atrás con Worker desplegado: el HTTP extractor puede intentar **8 fuentes**, pero conserva un máximo de **4 informes de documento**, priorizando los que sí se pudieron leer, en `source_documents`. En `retrieval_budget` deja las **8 URLs intentadas**, cantidad total, documentos utilizables, dominios independientes y límite agotado. El futuro seleccionador usa `retrieval_budget.attempted_urls` para no perder los descartes. Esta medida impide que el Worker actual, cuyo validador publicado aún limita a cuatro documentos, rechace la ingesta.
4. `tools/ai_research_pipeline.py` envía el presupuesto de recuperación al expediente JSON; `src/ai-research-team.mjs` verifica que los contadores y URLs no superen el máximo o contradigan la evidencia. Se mantienen bloqueadas verificaciones de hechos, permisos de guion y publicación. No se alteró D1 con nuevas tablas.
5. Regresiones Python en `tests/test_ai_research_team.py`: ampliar búsquedas tras fuentes oficiales fallidas, conservar historial, evitar la segunda llamada de IA sin documentos nuevos y mantener cuatro registros compatibles. Pruebas SQLite reales `tests/test_market_research_selection.mjs`: selección D1 aporta la lista exhaustiva de URL agotadas y fragmentos anteriores. Regresiones en `tests/test_ai_research_team.mjs`: recalcular límites por fuente real y detectar falsa ampliación de documentos.

### Pruebas, integración y bloqueo externo
- Commits de código y pruebas guardados directamente en `main`; una ejecución CI para el commit `9ff0ccfd` figura `success` (Actions `39827953415`), pero ese commit NO contiene todavía todas las regresiones posteriores. La suite y un E2E de la versión más reciente deben confirmarse por separado.
- Cloudflare D1 y Worker siguen sirviendo expedientes y métricas anteriores sin cambios destructivos. El Worker publicado fue verificado como versión anterior al cambio de transición `awaiting_sources`. **Cloudflare Workers Builds no tiene configuración de proyecto ni triggers asociados**; sus minutos no están agotados. No fingir que el nuevo Worker se desplegó; requiere un procedimiento de deploy seguro que conserve bindings/secretos y CI.
- Se solicita **una sola nueva ejecución E2E** con el marcador `[radar-e2e]` del workflow `check.yml`, ya autorizado por el repositorio. Verificar tras la corrida las URLs nuevas, dominios y estado de D1; si no hay mejor evidencia, no declarar P1 terminada.
- **Próximo hito funcional**: conseguir en las fuentes realmente accesibles dos editoriales independientes y, cuando proceda, regulador o documentación primaria; contrastar uno por uno los hechos, sólo entonces habilitar el borrador del guionista autónomo de 8–14 minutos, vinculado a citas y QA. No generar ni publicar un video sólo por detectar el mercado.


## 2026-10-22 · P1 funcional — fuentes independientes e investigación incremental sin recobro de IA

**Motivo:** el radar seleccionó Theranos con datos reales YouTube; Gemini y Groq produjeron siete afirmaciones, pero **todas dependían de Ars Technica 2016**. Una revisión de modelos no equivale a hechos corroborados. El histórico del sistema tenía cuatro fuentes intentadas, tres con problemas de lectura. No se justifica generar voz ni MP4 comercial de un dossier así.

### Bloque implementado directamente en main
- **`tools/ai_source_discovery.py`**: búsqueda mixta por autoridad/medio, máximo ocho URLs públicas realmente descubiertas, máximo cinco intentos de cada categoría, una URL por hostname y hasta diez fragmentos. Se priorizan documentos legibles en las cuatro entradas `source_documents` para mantener compatibilidad con Worker anterior; `retrieval_budget.attempted_urls` conserva **todas las URLs realmente intentadas** y razones de bloqueo, sin aumentar D1 ni esconder consumo. Dos dominios con texto y autoridad pública detienen antes la búsqueda, pero siguen sin verificar afirmaciones.
- **Fuentes gratuitas adicionales sin API cobrable:** búsqueda documental `gdelt_articles` de `tools/ai_source_discovery.py` utiliza **una solicitud** a GDELT DOC 2.0 `artlist`, máximo veinte resultados y ventana `1y`; trae URL y titular, *nunca* se trata el título como prueba. Las páginas candidatas deben descargarse por el lector seguro que valida DNS/HTTPS/redirecciones, después producir textos auténticos y hashes. Documentación: `https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/`. En caso de limitación o error, conserva las demás fuentes. Se inyecta fetcher en pruebas sin tráfico externo; el workflow usa `fetch_public`. No usa tarjeta ni clave GDELT.
- **`src/market-research-selection.mjs`**: ahora consulta hasta cinco expedientes previos de D1 por compañía y dentro de siete días, recupera hasta ocho URLs agotadas + cuatro fragmentos auténticos y deduplica documentos por URL/hash. Una corrida sin fuentes ya no borra el último dossier útil. Solo lee información persistida del mismo Wikidata QID, no usa memoria manual de ChatGPT.
- **`tools/ai_research_pipeline.py`**: después de consolidar evidencia de fuentes originales, PDF y páginas corporativas, ejecuta `gate_duplicate_research`. No vuelve a invocar Qwen/Gemini/Groq cuando los pasajes proceden de URLs y hashes **idénticos** a la investigación anterior, incluso si se extrae otra frase del mismo archivo. Ante nuevo documento conserva todas las citas admisibles dentro del límite. Guarda `research_freshness` y `retrieval_budget` en el informe para trazabilidad.
- **`src/ai-research-team.mjs`** valida el presupuesto de ocho URLs observadas y el máximo compacto de cuatro documentos; cruza `attempted_urls` con las URL de la ingesta y evita conteos artificiales. No autoriza producción, hechos ni guiones. El expediente de un único dominio seguirá `awaiting_sources`.
- **Regresiones añadidas/actualizadas:** `tests/test_ai_news_and_freshness.py` prueba GDELT JSON realista sin pago, rechazo de enlaces privados, integración de dos artículos independientes tras fallar Wikipedia y APIs opcionales, y anti-duplicación por URL/hash. `tests/test_ai_research_team.py` prueba ocho intentos, preferencia de documentos legibles, conservación de cuatro entradas y lista completa de URLs. `tests/test_market_research_selection.mjs` prueba D1 SQLite real con última corrida vacía sin perder la anterior. `tests/test_ai_research_team.mjs` verifica presupuesto incoherente.
- No se habilitó ninguna API paga, no se modificaron secretos ni se publicaron videos. No se requirió migración nueva; siguen aplicadas las existentes.

### Pruebas y estado operacional
- [GitHub Actions 39830039322](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39830039322) falló sobre una versión intermedia: una aserción antigua esperaba exactamente **2 URL de gobierno** cuando el nuevo presupuesto había probado **5**. Esa aserción y otra que asumía que el primer documento compacto era un bloqueo fueron corregidas en commits posteriores.
- **No declarar CI verde ni despliegue remoto del bloque actual** hasta una ejecución real del HEAD. Última CI anterior aprobada `39827953415` sólo cubría un commit más antiguo. Worker Cloudflare aún no se ha confirmado con las nuevas rutas/transiciones. Sin recrear datos falsos.
- La cola Theranos sigue `awaiting_sources`, `script_authorized=0`, `publication_authorized=0` verificados previamente, y el último investigador en D1 no acredita fuentes independientes. Mantener ese bloqueo hasta próxima captura auténtica.
- **Siguiente trabajo inmediato:** verificar una corrida E2E `[radar-e2e]` de la nueva búsqueda libre + acumulación D1 + puertas anti-gasto, corregir los resultados que fallen; si hay varias fuentes primarias, contrastar el contenido, generar propuesta original de guion 8–14 min, enlazar la voz canónica y producción audiovisual con controles de derechos. Si GDELT no devuelve artículos, no inventar lecturas ni cuotas consumidas.

**Estado final honesto:** desarrollo conectado a radar diario y pruebas en `main`, pendiente verificación E2E de sus últimas revisiones; no se confunde el avance del código con un documental autónomo final.

## 2026-10-22 · Vía local Wrangler tras fallo OAuth del conector

- Wrangler 4.152.0 instalado localmente mediante npm, sin cambiar package.json ni generar package-lock. Instalación: 37 paquetes, auditoría sin vulnerabilidades reportadas.
- `wrangler whoami` ejecutado: no existe una sesión local autenticada. No se desplegó el Worker ni se modificó D1.
- Intento de abrir OAuth con almacén seguro de Windows y scopes `account:read`, `user:read`, `workers:write`, `d1:write`, `offline_access` bloqueado por revisión automática antes de ejecutar: requiere autorización expresa del propietario para escritura y sesión persistente. No se eludió el bloqueo ni se obtuvieron credenciales.
- Próximo paso: obtener esa autorización concreta, iniciar login oficial en navegador y verificar cuenta/Worker/D1 antes de cualquier despliegue. Este registro es local; no se creó commit ni se sincronizó con GitHub en esta intervención.

### Autorización del propietario y login Wrangler iniciado
- El propietario autorizó expresamente el acceso a Cloudflare en el chat. Se instaló `@napi-rs/keyring@1.3.0`, complemento requerido por Wrangler para el almacén seguro de Windows.
- Se corrigió la invocación: `offline_access` no es un argumento admitido por `--scopes` en Wrangler 4.152.0. Se inició OAuth con `account:read`, `user:read`, `workers:write`, `d1:write` y `--use-keyring`.
- Wrangler abrió el enlace de autorización en navegador y espera el consentimiento allí. No consta aún login exitoso ni verificación de cuenta, Worker o D1. No se ejecutó despliegue.

### Wrangler autenticado y D1 remoto verificado
- OAuth de Wrangler finalizó `Successfully logged in`; `whoami` confirmó la cuenta del propietario y credenciales cifradas con clave en Windows Credential Manager. No se copiaron tokens al repositorio.
- `d1 info factor-de-gigantes-db` funcionó: base existente con 34 tablas. SELECT remoto de la cola confirmó Theranos Q16956307 en `awaiting_sources`, `script_authorized=0`, `publication_authorized=0`; consulta con cero filas escritas.
- `deployments list` fue rechazado por acceso insuficiente a Workers. La sesión inicial tiene `workers:write` pero no el permiso granular `workers_scripts:write`. Se inició una nueva autorización oficial añadiendo ese permiso, dentro del acceso expresamente autorizado. Pendiente consentimiento del navegador y nueva comprobación del Worker. No se ejecutó despliegue ni cambio de datos.

### Conexión Wrangler completa verificada
- La espera OAuth adicional venció; se abrió un enlace nuevo y Wrangler confirmó `Successfully logged in` tras el consentimiento del propietario.
- `wrangler deployments list` ahora finalizó correctamente y devolvió el historial del Worker `factor-de-gigantes`, incluida la versión `51211b17-7176-4dea-9f9b-9dad1192fb17` (despliegue 2026-10-22T19:05:17.210Z). Acceso al Worker confirmado mediante consulta real.
- D1 remoto ya fue verificado por `info` y SELECT sin escrituras en la comprobación anterior. Vía local de administración operativa independientemente del conector MCP. No se desplegó código en este bloque.
- Próximo paso: contrastar la versión remota con main, corregir y probar el contrato entre descubridor e ingesta IA, conservar bindings y secretos, y verificar E2E antes de acreditar avance documental.

## 2026-10-22 · Corrección local del contrato integral de investigación

- Causa reproducida: `ai_source_discovery.py` emite `gdelt/discover` y `d1_history/avoid_duplicate_sources`, pero el validador JS rechazaba ambos. Se admiten esas etapas con roles restringidos; no se habilitan nuevos proveedores de inferencia ni reservas.
- `tools/ai_research_pipeline.py` ejecuta ahora el validador real JS antes de cargar Qwen/reservar APIs y otra vez antes de persistir. El JSON viaja por stdin y los errores no imprimen contenido remoto ni credenciales. Conserva `research_freshness` en el informe final.
- El validador comprueba la auditoría de fuentes nuevas. La cantidad de fragmentos extraídos se limita al presupuesto HTTP real (tres por documento), sin confundirla con los diez pasajes finales ni rechazar una corrida que descartó documentos repetidos antes de inferir.
- Regresiones nuevas: descubrimiento Python -> análisis local simulado -> contrato JS -> SQLite real; metadatos de búsqueda no pueden actuar como analistas ni reservar inferencias; corrida repetida sin carga del modelo; CLI rechaza contrato inválido antes de análisis/persistencia.
- Pruebas locales: 249 Python y 81 Node aprobadas; sintaxis Worker/panel y manifest de ejemplo correctos. La suite Python usa pypdf 5.9.0 en `.cache/python`, temporales dentro del proyecto y sustitución de fuentes del sistema sólo en el proceso de pruebas Windows (Arial); no se cambió el render ni la voz. La primera ejecución completa falló por temporales del sandbox; la ejecución ajustada pasó.
- `.cache/` excluido de Git. Carpeta local sin `.git`: sincronización mediante API GitHub sobre el HEAD de main, preservando el árbol remoto y sin crear ramas. Comparación de hashes src/public/tools/migrations/workflows contra main: únicamente difieren los dos módulos modificados en esta entrega.
- Pendiente al escribir este bloque: commit remoto, CI, despliegue del Worker y una ejecución E2E real. P1 factual continúa abierta; no hay documental final ni autorización de publicación.

### Integración de esta corrección
- Commit remoto directo a `main`: `01214bac31e609a708e669a82cc25f6e603386c9`, sin ramas adicionales. CI [39849460979](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39849460979): `success`.
- `wrangler deploy --dry-run` aprobado. Despliegue real con `--keep-vars` completado: Worker versión `6e149bc5-0c89-4aa1-ae90-4836d45ae572`. Se comprobaron nombres/tipos de bindings anteriores; no se copiaron valores de secretos al repositorio. El intento inicial de guardar metadata completa fue bloqueado por revisión automática antes de ejecutarse; se usó sólo un resumen filtrado sin valores.
- Smoke HTTP de producción pasó: `/health`, `/`, `/app.js` HTTP 200; `/api/research` sin credenciales HTTP 401. Esta comprobación acredita disponibilidad y barrera de autenticación, no investigación final.
- Una sola corrida real del radar [39849511998](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39849511998) fue disparada por la puerta existente `[radar-e2e]` después de CI. Pendiente resultado final y lectura independiente D1.

### Resultado real E2E y corrección de clasificación documental
- Radar [39849511998](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39849511998) finalizó `success` sobre `01214bac`. Qwen CPU, Gemini y Groq terminaron correctamente; Mistral/OpenRouter no fueron necesarios y no se habilitaron otros proveedores.
- Lectura independiente de D1: expediente `ai-26a72b2ba548c552054d3d14f2af`, 10 extractos, 4 URL documentales, 3 hostnames, 8 afirmaciones. Auditoría persistida `new_documentary_sources`, 3 documentos nuevos; 6 URL intentadas, 3 con texto relevante. GDELT respondió `source_unavailable`; no se inventaron resultados.
- Límites observados al terminar: 3 reservas Gemini y 3 Groq del día (cada proveedor con máximo 4). Esta corrida añadió una por proveedor. No se dispara otra corrida pesada para probar la corrección siguiente.
- Theranos continúa `awaiting_sources`, `script_authorized=0`, `publication_authorized=0`. `PRAGMA foreign_key_check` sin violaciones. El plan documental informó `blocked_insufficient_corroboration`, cero escenas, porque las ocho afirmaciones citaron cada una un solo documento. E2E técnico exitoso NO acredita contraste factual ni documental final.
- **Error descubierto en esta evidencia:** el contador histórico de 1 dominio regulatorio proviene de un artículo alojado en NCBI (`.gov`), no de una denuncia/sentencia regulatoria verificada. No atribuir respaldo regulatorio a esa corrida. El expediente original no se reescribió.
- Corrección posterior local: `src/regulatory-authorities.json` es la lista compartida por Python/JS de dominios de autoridades candidatas conocidas. El descubridor conserva prioridad de búsqueda pública, pero no clasifica PubMed/NCBI ni identificadores de biblioteca como reguladores; reclasifica las citas históricas al reutilizarlas. El Worker rechaza ingestas que intenten asignar esa clase a repositorios u hostnames que imiten autoridades. Una autoridad candidata sigue sin verificar hechos automáticamente.
- El workflow fija Node 24 y valida el contrato ANTES de instalar Qwen, para fallar rápido ante incompatibilidades. Ya se validaba también antes de inferir y de persistir.
- Verificación de esta revisión: 250 pruebas Python y 82 Node aprobadas, incluida descarga/reutilización simulada de NCBI sin autoridad regulatoria y rechazo de dominios parecidos; compilación Wrangler aprobada. Pendientes al registrar: sincronizar esta revisión adicional, CI y desplegarla. No repetir consumo IA de la corrida anterior.
- Próxima prioridad factual: mejorar el contraste por afirmación sobre documentos de emisores independientes y documentos regulatorios reales cuando sean necesarios; el guionista permanece bloqueado. No inferir corroboración por número de dominios ni por acuerdo entre modelos.

### Cierre verificado de esta entrega
- Revisión adicional sincronizada en `main`: `49998235758bb69f01ec9c780d03a1544fbb9f0c`. CI [39850413475](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39850413475): `success`.
- Despliegue final confirmado con `--keep-vars`: versión Worker `f58748ce-e95d-4c7f-97f7-02a3b2355380`, mensaje referido a `49998235`. Configuración D1/AI/ASSETS conservada y sin migraciones ni modificación de datos en este despliegue.
- QA adicional sin llamadas a IA: se leyó desde D1 el expediente público real `ai-26a72b2ba548c552054d3d14f2af`, se reclasificaron localmente los extractos NCBI, se recalculó la matriz y pasó el contrato JS corregido. Resultado efectivo: **0 dominios regulatorios, 8 afirmaciones pendientes, all_claims_verified=false**. El JSON histórico D1 permanece inalterado; su contador regulatorio anterior no debe interpretarse como válido.
- Smoke HTTP posterior al despliegue final aprobado. Código, tests, CI, despliegue y ejecución E2E técnica acreditados con las salvedades señaladas. Se mantiene abierta la aceptación documental/factual: aún no hay guion autónomo aprobado ni MP4 final de 8–14 minutos.
- Siguiente avance: investigación dirigida por cada vacío factual, citas de emisores independientes para la misma afirmación, cronología y documentos regulatorios auténticos cuando corresponda; conservar límites gratuitos y no volver a inferir sólo sobre archivos idénticos.

## 2026-10-22 · Continuación factual por afirmación y guionista reanudable

### Implementación y pruebas locales
- Selección D1: recupera hasta 40 URL de cinco expedientes recientes de la misma entidad, conserva ocho objetivos factuales y sus citas/vacíos, e identifica hasta dos artículos pendientes de extraer referencias originales. No se crean ramas ni se cambia el tema manualmente.
- Descubridor: sigue enlaces regulatorios observados dentro de documentos, con URL de procedencia y la misma descarga HTTPS/DNS/redirecciones segura. Todas las descargas, incluidas expansiones históricas, cuentan dentro de ocho intentos. La auditoría de escaneo evita reabrir los mismos artículos en cada ciclo. Reabrir un artículo para extraer enlaces NO justifica inferencia, aunque cambie el hash por HTML dinámico.
- Prompt de investigación: utiliza los objetivos anteriores en vez de cambiar de hechos en cada corrida; solicita dos referencias sólo cuando ambas respaldan la misma afirmación y exige distinguir acusación/condena, acuerdo/pago ejecutado y fechas. No acredita corroboración por simples coincidencias de modelos.
- Matriz `claim_source_policy_v2` compartida Python/JS: preserva la exigencia regulatoria en hechos legales; los hechos no legales requieren original primario y contraste, sin imponer un regulador irrelevante a toda innovación. La falta de documento regulatorio sigue visible como aviso. El Worker recalcula los requisitos y rechaza omisiones. Los expedientes históricos no se reescriben.
- `tools/documentary_script.py`: guionista autónomo de borradores con citas por párrafo, correspondencia con el plan de escenas, límites de 8–14 minutos estimados y bloqueo de permisos inventados. La calidad y la veracidad del contenido siguen sujetas a revisión humana. La prueba de 1200 palabras es un fixture, no el documental final.
- Fase `script` independiente dentro del mismo workflow autorizado, con contexto D1 por OIDC restringido al repo/workflow/main y consulta de expedientes activos. No repite radar ni Qwen ni consume otra inferencia de investigación. Comparte cuotas D1; una generación por proveedor/ejecución. No hay nuevas claves, migraciones ni apertura de publicación.
- Nueva ruta POST `/api/market/ai-pipeline/script-context`: sólo OIDC de radar; rechaza ADMIN/RENDERER y parámetros inválidos. Devuelve contexto sin modificar filas ni permisos. Se añade puerta de prueba explícita `run_script`/marcador `[script-e2e]` en el workflow de comprobación.
- Pruebas locales: 263 Python y 84 Node aprobadas, sintaxis y manifest válidos; compilación Wrangler aprobada. Las pruebas Windows usan temporales del proyecto, pypdf local y fuentes Arial sólo en el proceso de tests, sin alterar la voz ni el render.

### Evidencia real sin consumir IA
- El historial activo de Theranos se leyó directamente desde D1. Una prueba local con el descubridor siguió desde el artículo citado de Ars Technica 2017 la URL original del fiscal general de Arizona, sin que ChatGPT proporcionara la URL. El sitio original no ofreció texto utilizable. SEC/FDA/DOJ siguieron sin evidencia textual utilizable en ese presupuesto.
- La ampliación de referencias hizo ocho descargas máximas; recuperó los mismos artículos ya citados y dejó cero pasajes para nueva inferencia. `validate_report_locally` aceptó ese informe y la puerta anti-duplicación omitió IA. No se fabricó una fuente primaria ni se gastó otra consulta Gemini/Groq para repetir el dossier.
- Se comprobó la API pública documentada del DOJ como diagnóstico; respondió contenido no JSON utilizable en esta red. No se integró un resultado inexistente ni se eludieron restricciones.
- CLI del guionista sobre el expediente D1 real devolvió `blocked_source_contract`, cero escenas y render/publicación falsos: el histórico conserva la clasificación antigua NCBI que requiere revalidación. No se alteró el expediente para aparentar aceptación.

### Estado al registrar
- Código local y pruebas ejecutados. Pendiente sincronización, CI, despliegue y una prueba real de la fase script. El proyecto NO está terminado: falta un dossier realmente contrastado, un guion documental real aceptable, integración/QA de voz canónica, activos con derechos y MP4 final de 8–14 minutos. Instrucciones operativas en `docs/OPERACION_PIPELINE.md`.

### Revalidación histórica sin repetir IA
- Se añadió revalidación determinista de metadata antes del guionista: recalcula clasificación y matriz sobre una copia, conserva el hash del expediente original y no modifica D1 ni citas ni decisiones humanas. Así una etiqueta histórica NCBI no exige gastar una nueva inferencia para corregirse.
- CLI sobre el expediente real, después de esa revalidación: `blocked_insufficient_research`, cero escenas, con motivos por cada una de las ocho afirmaciones y falta de documento primario. Esto sustituye el bloqueo técnico `blocked_source_contract` de la comprobación anterior por el bloqueo factual real. El JSON original de D1 sigue intacto.

### Integración y encadenado hacia guion
- Commit `930d2fe843ed73a41795ab0e9b17addcce0f5561` sincronizado directamente en main. CI [39854241274](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39854241274) `success`.
- Backend desplegado con `--keep-vars`, versión `b33ded64-db7b-41f7-bf15-4429fa23631c`. No se aplicó migración ni se alteraron registros editoriales.
- Se añadió recibo local de persistencia D1 con el run_id exacto confirmado y encadenado automático hacia la fase script sólo si el plan documental supera la puerta. La fase script usa otra ejecución, no repite la investigación ni supera el límite de una generación por proveedor/ejecución. Su aceptación con dossier real suficiente sigue pendiente.
- La suite final incorpora revalidación histórica y recibo D1: 265 pruebas Python previstas tras la última regresión añadida; la regresión específica de recibo pasó y la suite anterior de 264 + 84 Node pasó completa. Confirmar la ejecución CI siguiente para la revisión de encadenado. Reservas D1 antes de la prueba script: Gemini 3 y Groq 3; no se añadió consumo en las comprobaciones locales.

### Prueba real de reanudación del guionista
- Commit `f1bb9bf5a66b09588c3a74b4e66fc48f7fd7e352` en main; CI [39854730005](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39854730005) `success`. Suite de esa revisión: 265 Python y 84 Node.
- Ejecución real de fase script [39854835936](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39854835936): `success`, job `documentary-script` aprobado; radar y encadenador de investigación `skipped`. OIDC pudo leer el contexto activo de D1 y revalidarlo. El guionista devolvió `blocked_insufficient_research`, cero escenas. No se produjo narración ficticia ni se consumió una inferencia para un dossier insuficiente. Esto acredita reanudación y bloqueo, no un guion final aceptado.
- No hay navegador conectado a las sesiones existentes de los buscadores. Para no exigir otra conexión humana se añadió una consulta de perfil a `GET https://api.tavily.com/usage`, conforme a la documentación oficial `https://docs.tavily.com/documentation/api-reference/endpoint/usage`. La fase `profile` sólo lee plan/cuotas, no busca ni activa facturación, y filtra campos antes de guardar logs/artefactos. No se habilitan búsquedas con esa entrega. Pruebas cubren plan pagado, PAYG, cuota insuficiente, apagado explícito y redacción de campos sensibles.
- Pendiente: CI y ejecución real del perfil configurado; no afirmar plan gratuito hasta obtener evidencia de la cuenta concreta. Exa permanece desactivada sin confirmación de modalidad gratuita.

### Verificación de la modalidad Tavily
- Perfil ejecutado de forma real en [39855421638](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39855421638), `success`, sobre commit `4fbe98ca9aa83aac581960d05b21e162f0917b90`; CI [39855323094](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39855323094) aprobada. La lectura devolvió `invalid_profile`: no se afirmó modalidad gratuita, no se hicieron búsquedas y no cambió facturación.
- Se endureció el diagnóstico para guardar sólo los tipos de campos de plan/cuotas que faltan, sin valores arbitrarios, correos ni credenciales. Acepta contadores enteros representados como números enteros o cadenas decimales; los valores ausentes, fraccionarios o límites PAYG desconocidos nunca habilitan búsquedas. Nueva regresión específica aprobada. No se sustituye la política de cero pagos por una suposición.
- Suites de la revisión anterior: 269 Python y 84 Node aprobadas. Pendiente lectura final de diagnóstico con ese ajuste; no usar Tavily ni Exa mientras no exista confirmación válida.

### Estado final verificado de este bloque
- Revisión de diagnóstico `fbeec00a233a42fae4ab9d6974a603ccb82e4bbd` en main. CI [39855702268](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39855702268): `success`. Lectura real de perfil [39855751132](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39855751132): `success`.
- La cuenta Tavily responde `current_plan=Researcher`, pero `account.paygo_limit` es nulo. Los otros contadores tienen tipo entero. Esto acredita la existencia del plan, NO que PAYGO esté desactivado. Se mantiene `free_search_confirmed=false`, cero búsquedas y cero cambios de facturación. Se solicitó al propietario confirmar sólo ese estado del panel; no se pidieron claves por chat.
- Pruebas finales completas ejecutadas localmente: 270 Python y 84 Node aprobadas. Producción HTTP saludable y API protegida. D1: Theranos `awaiting_sources`, `script_authorized=0`, `publication_authorized=0`; integridad referencial sin errores. Reservas del día permanecen Gemini 3 y Groq 3: este bloque no añadió inferencias.
- Guionista y continuación están implementados, sincronizados, probados y el backend desplegado. El camino positivo de guion largo fue probado con fixtures; el dossier real fue correctamente bloqueado y no generó escenas. No se acredita todavía guion real aceptable ni documental final, voz/visuales completos o integración comercial.
- Próximo avance: confirmar PAYGO desactivado o mantener Tavily apagado; ejecutar continuación dirigida dentro de cuotas sólo con nuevas fuentes, lograr contraste real y generar el borrador por el encadenado implementado; después revisión editorial, voz canónica, activos con derechos y render 8–14 minutos. No abrir publicación automática.

## 2026-10-22 — Tavily habilitado con confirmación del propietario

- El propietario confirmó expresamente que «Pay as you go» está desactivado en su panel. Se habilitan búsquedas básicas Tavily en main; un apagado explícito por variable sigue prevaleciendo. No se modifica facturación ni se activa Exa.
- Antes de buscar se lee el perfil y se exige plan Researcher/Free, límite de 1000, consumo PAYGO cero y al menos dos créditos disponibles. Un `paygo_limit` nulo sólo admite la confirmación humana explícita; se conserva nulo en el registro y se distingue de la verificación por API. Plan pagado, PAYGO positivo, cuota agotada o perfil ilegible no habilitan búsquedas.
- Se mantienen las reservas D1: máximo dos búsquedas por ejecución, ocho diarias y doscientas mensuales. Las búsquedas aportan URL candidatas; la evidencia exige descargar documentos y contrastarlos.
- Pruebas locales: 271 Python y 84 Node aprobadas; comprobación sintáctica Worker/interfaz aprobada. Nuevas regresiones cubren confirmación humana para dato nulo y rechazo de planes, límites o consumo incompatibles incluso con esa confirmación.
- Pendiente en esta entrega: sincronizar commit a main, verificar CI y ejecutar la investigación real con Tavily. No se declara todavía contraste completo, guion aceptado, render ni publicación.

### Ejecución Tavily real y corrección de prioridad documental
- Commit `4cd8ab55f3a1561a4ebaf506e1f523f24d7e0794` sincronizado en main. CI [39857001640](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39857001640) y radar [39857051989](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39857051989): `success`.
- Perfil real: Researcher, 0/1000 créditos antes de buscar, consumo PAYGO 0, límite PAYGO nulo y confirmación humana registrada como `owner_confirmed_no_paygo`; límite de clave 1000. Tavily discovery, Qwen extraction, Gemini analysis y Groq review finalizaron correctamente. Exa y Cloudflare AI permanecen sin modalidad gratuita confirmada.
- D1 confirmó expediente `ai-68c81e2c178164794d3c573474d0`: diez pasajes, ocho afirmaciones y ocho revisiones. El artefacto real muestra ocho descargas intentadas, tres URL con texto y ningún regulador legible. El guion quedó `blocked_insufficient_corroboration`, cero escenas; las ocho afirmaciones siguen citando un solo documento. Dos hashes de un mismo artículo no son dos fuentes independientes.
- Se detectó la causa que impedía aprovechar Tavily: la clasificación de pistas descargaba enlaces generales antes que las búsquedas dirigidas, y una URL compartida con Wikipedia perdía la procedencia de búsqueda. Se priorizan las pistas Tavily/Exa sólo cuando existen objetivos pendientes, conservando esa prioridad al deduplicar y al compactar el registro de documentos. No se amplían cuotas ni permisos.
- Regresión reproduce doce enlaces generales que habrían desplazado el resultado dirigido y verifica orden, procedencia, deduplicación y límite de cinco secundarios. Suite local completa: 272 Python aprobadas. Pendiente CI y nueva ejecución real de esta corrección. Gemini/Groq conservan su máximo diario; no se fuerzan inferencias después de agotarlo.
- Wrangler tuvo un fallo de renovación por conectividad con el servidor de autorización. No se borraron credenciales ni se repitió login: se recuperó el artefacto firmado desde GitHub y la ingesta D1 se confirmó en los logs OIDC. No fue necesario desplegar Worker para cambios Python/workflow.

### Contraste: conservación de contexto y exclusión de enciclopedias
- Corrección de prioridad en commit `f30497e1683c19370512fd2cff526970fb49d190`, CI [39857975838](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39857975838) y radar [39858023531](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39858023531): `success`. Expediente D1 `ai-3ddd59df67619c0d60947f11ce3a`.
- El artefacto confirmó que los resultados dirigidos de Tavily ya se descargan: seis intentos, cuatro páginas con texto. También acreditó los bloqueos de cuota diaria: Gemini y Groq devolvieron `budget_denied`, sin superar los límites. Qwen extrajo dos afirmaciones; cero revisiones Groq, ningún original regulatorio y guion bloqueado. No confundir éxito técnico del radar con aceptación documental.
- La inspección detectó dos fallos adicionales: Tavily podía devolver Wikipedia y el lector la trataba como documento; doce pasajes nuevos llenaban los diez espacios disponibles antes de recuperar el historial. Se excluyen Wikipedia/Wikimedia/Wikidata de pistas, redirecciones e históricos reutilizados. Los documentos D1 históricos permanecen intactos.
- Se reserva espacio dentro de los diez pasajes para hasta cuatro citas históricas de URL distintas de las recién leídas. Los pasajes nuevos se reparten por documento antes de tomar segundos/terceros fragmentos. Un cambio de hash del HTML no duplica el mismo texto como fuente independiente.
- Pruebas locales completas: 274 Python aprobadas. Nuevas regresiones cubren enciclopedia recibida del buscador, redirección, histórico y doce pasajes nuevos frente a cuatro históricos. El contrato JS real del Worker valida ambos escenarios.
- Lectura pública real adicional, sin Tavily ni inferencias: tres descargas originales legibles (University of Texas, KJZZ y Fox Business), nueve pasajes nuevos observados; el manifiesto final conserva diez pasajes de seis URL, incluyendo los tres documentos históricos de Ars, Fortune y Observer. Wikipedia ausente. El contrato actual del Worker fue aprobado. Resultado local: `.wrangler/corroboration-replay-real.json`; no se presenta como nuevo expediente D1 ni como corroboración semántica aprobada.
- Estado real: integración Tavily gratuita probada y prioridades corregidas; dos expedientes reales nuevos persistidos. Sigue pendiente obtener originales primarios legibles, contrastar las afirmaciones y completar la revisión cuando haya cuota; después guion real, voz canónica, derechos y MP4 de 8–14 minutos. No se ha autorizado ni iniciado publicación.

## 2026-10-22 — Avance independiente de cuotas: control audiovisual real

- Se continuó el frente de producción mientras Gemini/Groq permanecen en su límite diario. Nuevo `tools/av_quality.py`: ffprobe inspecciona pistas reales y FFmpeg decodifica el archivo completo, sin modificarlo ni sintetizar voz. Perfiles diferenciados de preview, documental 8–14 minutos y Short vertical; límites de resolución, fps, códecs, tiempos de pistas y duración esperada.
- Detecta congelamiento y silencio prolongados (2 s), negro prolongado (0,8 s), ausencia de audio, cabeceras incompatibles y errores de decodificación/truncamiento. Reporta intervalos y niveles medios/pico de audio; un pico cercano a escala completa solicita audición, sin afirmar clipping ni normalizar. Los umbrales pueden señalar pausas/planos intencionales; no reemplazan revisión editorial o auditiva.
- El reporte enlaza archivo/tamaño/SHA256 y mantiene identidad vocal, derechos, hechos y publicación sin aprobar. No mide sincronía labial ni contenido semántico. Las credenciales y metadatos arbitrarios del medio no se copian al reporte.
- `render.yml` ejecuta la puerta antes de subir la vista previa y reportar `ready`, y conserva diagnóstico aunque falle; `blackberry-scene01-video.yml` añade QA al montaje y a su artefacto. No se ejecutó un nuevo trabajo editorial/D1 ni se inició publicación. La aceptación de estos dos workflows con un nuevo render autorizado queda pendiente; su código no se confunde con integración real ejecutada.
- `check.yml` incorpora un job independiente con FFmpeg: codifica movimiento+audio, congelamiento+silencio, negro+audio, ausencia de audio y archivo truncado. El validador bloquea los casos defectuosos y admite el positivo sin conceder derechos/aprobación. No usa APIs de IA ni Qwen.
- Pruebas locales completas: 282 Python (incluida integración FFmpeg explícita) y 84 Node aprobadas; sintaxis JS y manifest de ejemplo aprobados.
- Comprobación con medio real del producto: se regeneró la intro técnica existente con la referencia canónica intacta y gráficos propios, sin nueva locución. Archivo local `dist/qa-audiovisual/INTRO_REFERENCIA_PRUEBA_TECNICA.mp4`, 1.639.396 bytes, 12,333333 s, 1280×720, H.264/yuv420p 24 fps y AAC mono/48 kHz. SHA256 `3e362ac5652a5ac2c68e3e158fe877768e89b0ae54da8e477ddc8ebf8d65c7a0`; decodificación completa y puerta técnica aprobadas, sin intervalos negros/congelados/silenciosos detectados. Audio medio −18,3 dBFS y pico −2,4 dBFS. Se extrajo e inspeccionó un fotograma. Reporte `dist/qa-audiovisual/QA_INTRO_REAL.json`. Es la intro de referencia, no un documental nuevo ni narración larga aceptada.
- Documentación operativa en `docs/QA_AUDIOVISUAL.md`, enlazada desde `docs/OPERACION_PIPELINE.md`. Pendiente sincronización/CI de esta entrega. Próximos frentes independientes: preparar el paso del guion autónomo a tomas de voz y recursos por escena, con revisión/licencias explícitas; continuar el contraste al recuperar cuota. El MP4 final de 8–14 minutos sigue pendiente.

### Cierre comprobado del control audiovisual
- Entrega sincronizada en main, commit `b1fb007acc907ddceb10cb872db0a7231ff871f5`. CI [39859983653](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39859983653) aprobada: jobs `checks` y `audiovisual-quality` en `success`; radar, guionista y perfil no se ejecutaron. La integración FFmpeg sobre archivos codificados también pasó en Linux.
- Se compararon hashes Git de los ocho archivos de la entrega entre la copia local normalizada y el árbol remoto: coincidencia en todos. Esto acredita sincronización del contenido entregado; no se afirma un working tree Git limpio porque esta copia no contiene `.git`.
- No se desplegó Worker ni se modificó D1, ya que el cambio afecta a herramientas y workflows de producción. Los próximos renders autorizados ejecutarán la nueva puerta; no se declara una nueva corrida editorial completa por la prueba de CI.

## 2026-10-23 · Preparación de producción desde el guion autónomo

- Se sincronizó `e2c0f69a511fb84506093fa86e6b8c96351ec017` antes de implementar. Los fallos GDELT/historial y conservación de frescura de la copia antigua ya estaban corregidos allí; se preservaron esas mejoras.
- Radar programado [39975550972](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39975550972), `success`: Tavily, Qwen, Gemini y Groq exitosos; recibo OIDC `ai-5b69d4ef80887cf5b512171e16f1`, diez pasajes, siete documentos y plan `blocked_insufficient_corroboration`, cero escenas. Evidencia del log de Actions, no lectura D1 independiente. GDELT no disponible; Exa y Workers AI sin modalidad gratuita confirmada.
- Nuevo `tools/documentary_production_plan.py`: convierte el borrador del guionista en tareas de voz y solicitudes visuales por escena/párrafo. Las tomas conservan todos los caracteres, posiciones, citas y hashes, máximo 260 caracteres/toma y 128 tomas. Recalcula palabras y tiempos estimados; rechaza referencias malformadas, alteraciones y permisos inconsistentes. No hace red, descargas ni carga modelos.
- La referencia requerida procede de `tools/approved_voice.py`, sin modificar el MP3 ni sustituir la voz. Registrar el hash no acredita inspección del archivo ni licencia comercial. Los recursos visuales siguen pendientes y las aprobaciones falsas. Un guion bloqueado conserva sus motivos con cero escenas/tomas.
- La fase `script` encadena el plan y guarda `PLAN_PRODUCCION_NO_APROBADO.json` junto al guion/bloqueo en su artefacto. Operación documentada en `docs/OPERACION_PIPELINE.md`. Sin cambios de Worker, D1, secretos, cuotas o publicación.
- Cinco regresiones nuevas recorren el guionista con transporte de prueba hasta el paquete, conservación exacta del texto/citas, referencia canónica, bloqueos y alteraciones. Suite local completa con integración FFmpeg activada: **287 Python y 84 Node aprobadas**; sintaxis JS y manifest válidos. El positivo es un fixture, no un documental real aceptado.
- Pendiente CI y una prueba `[script-e2e]` del nuevo paso contra el contexto real, sin repetir radar. Si el dossier continúa insuficiente, debe quedar bloqueado sin generación de guion.
- Acceso Cloudflare: la conexión negó la cuenta de producción con HTTP 403 e informó una cuenta diferente. No se cambiaron cuentas ni datos. La descarga del artefacto firmado al entorno no se completó; no se atribuye inspección íntegra del expediente.
- **Para terminar:** originales legibles y contraste de afirmaciones reales, guion real aceptable, revisión factual/derechos, voz canónica auditada, visuales con licencia, montaje y QA del MP4 de 8–14 minutos. El puente implementado no acredita esas aceptaciones.


### Integración comprobada del puente de producción

- Commit `802eb10537f6347b8239dbd78b6a2defb4154196` sincronizado directamente en main. CI [40008940033](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40008940033): `success`, incluidos `checks`, QA audiovisual FFmpeg y disparador `live-script`. Smoke HTTP y autenticación del renderizador aprobados en CI.
- Prueba real [40008990029](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40008990029): `success`, sólo job `documentary-script`; radar, perfil e investigación no se repitieron. Logs: `GUION_DOCUMENTAL: blocked_insufficient_research ESCENAS: 0`; `PLAN_PRODUCCION: blocked_script_unavailable TOMAS_PLANIFICADAS: 0 TOMAS_GENERADAS: 0`. El camino bloqueado quedó verificado con contexto real OIDC; no acredita el camino positivo con dossier suficiente ni un documental terminado.
- Artefacto de revisión confirmado: `fdg-guion-documental-revision`, ID `12524489941`, 1446 bytes, SHA256 `3e638e5c6b3d8677d40c1b49e7e955d431fb4dcd3ef54417dd4c05037816b637`, caduca el 2026-10-28. CLI local también conserva bloqueos. El fixture positivo planifica 48 tomas en seis escenas y 522 segundos estimados, sin generar audio ni validar contenido real.
- No hizo falta despliegue Worker ni migración D1: herramientas Python y workflow se ejecutaron desde el commit exacto. Pendiente principal sin cambios: evidencia suficiente del episodio real y aceptación factual antes de guion/voz/visuales/render.

## 2026-10-23 · Recuperación dirigida a los vacíos factuales

- Se confirmó main `2b711b91bdea719392f6bdcc30f659d567427222` antes de continuar. Se ataca la falta de respaldo del dossier, sin cambiar el tema elegido por el radar ni escribir el episodio manualmente.
- `tools/research_source_plan.py` prepara dos consultas por proveedor: original regulatorio/primario del hecho pendiente prioritario y contraste con un emisor distinto del ya citado. Tavily recibe filtros `include_domains`/`exclude_domains`, contrastados con su SDK oficial. Exa mantiene su puerta de activación y recibe los nombres equivalentes cuando se configure. Filtros inválidos se rechazan antes de reservar presupuesto; continúan basic, dos consultas, sin respuestas/raw content/auto_parameters ni cambios de pagos.
- El lector deja de tomar sólo los tres primeros bloques que mencionan la empresa: prioriza pasajes de los objetivos, conserva ventanas literales de 90–320 caracteres, página/bloque, y contexto cercano de entidad cuando corresponde. No une frases, no añade cifras y no cruza páginas PDF para atribuir contexto. La selección lexical no acredita verdad ni contraste semántico.
- El expediente conserva `discovery_plan`; diagnóstico acotado en JSON/Actions relaciona documentos, fallos de lectura, citas, afirmaciones, revisión y vacíos. La fase script puede guardar el diagnóstico del contexto OIDC revalidado sin repetir búsqueda ni inferencia. Se filtran campos; no se vuelcan tokens, entorno ni mensajes remotos de error.
- Ocho regresiones nuevas: filtros/consumo real del cliente, dominios inválidos, párrafo decisivo tardío, cifra al final de bloque, contexto de entidad y separación de páginas, descubridor completo aceptado por el contrato JS, y exclusión de campos secretos en diagnósticos. Suite local completa con FFmpeg: **295 Python y 84 Node aprobadas**, sintaxis y manifest válidos.
- Pendiente al registrar: sincronización/CI y una sola corrida `[radar-e2e]` dentro de las cuotas existentes. Se inspeccionará el diagnóstico público para comprobar si hay originales legibles y apoyo efectivo; no se declaran fuentes obtenidas por escribir el código. Worker/D1 no requieren despliegue/migración para estos cambios de runner.

### Resultado real y siguiente corrección de recuperación

- Entrega `8ba82228a0ddcc00f6c1b435e12662282001364f` en main. Radar [40010820927](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40010820927): `success`. CI [40010779089](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40010779089) figura `cancelled`; no se atribuye CI completa aprobada a esa revisión aunque el disparador ejecutó el radar. Suites locales sí pasaron.
- Recibo OIDC `ai-cf689a064823eea9d7d24b9d578d`: nueve pasajes efectivos, cinco URL/documentos y cinco afirmaciones. Qwen/Gemini/Groq exitosos; dos páginas nuevas con texto, seis descargas, cero autoridades originales. El diagnóstico permite inspeccionar citas y vacíos. Plan bloqueado, cero escenas; dos fuentes candidatas sobre fundación no suplen un original primario.
- Se observaron errores concretos: consulta legal española extensa produjo DOJ 2008/BOE ajenos al tema; una bibliografía del PDF universitario entró como pasaje; el descubridor no seguía anotaciones/URLs regulatorias de PDFs. La consulta oficial ahora usa entidad canónica, conceptos legales y años observados; mantiene filtro, cuotas y segunda consulta de contraste.
- `pdf_link_annotations` extrae sólo Link/URI de las primeras doce páginas bajo los límites PDF existentes, con cantidades acotadas; no ejecuta acciones. Descubridor filtra referencias por HTTPS/autoridad conocida y conserva documento/página de origen; admite también URLs literales en el texto. Una anotación inválida no borra el texto ya extraído. Máximo doce referencias por documento y ocho descargas totales.
- Cuando la primera URL observada de una autoridad no aporta texto, se puede intentar una segunda distinta del mismo hostname dentro de los mismos cinco intentos primarios; no se vuelve a descargar la misma URL ni se amplía el presupuesto. Se mantienen restricciones de DNS, redirecciones y tipo de contenido.
- La selección de pasajes excluye bibliografías con varias URLs. El blueprint bloquea copias con hash idéntico en dominios distintos como si fueran originales independientes, incluso por afirmación. No presume que hashes distintos acrediten veracidad.
- Seis regresiones adicionales cubren PDF real con anotaciones, rechazo de hosts privados/simulados/HTTP, lectura de referencias y presupuesto en el colector, bibliografía separada de hechos, segunda URL de autoridad y copias idénticas. Suite local completa final: **301 Python y 84 Node aprobadas**, incluido FFmpeg. Pendientes CI y E2E de esta corrección antes de atribuir recuperación real de originales.

### Primer original judicial recuperado y mejora de consolidación

- Main `508c6a1f1355df58a5baef7a2359465bf3de4978`; radar [40012093107](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40012093107) `success`. Recibo OIDC `ai-9ce68254a8ec6b9f63de93142166`: nueve pasajes, cinco documentos, ocho afirmaciones/revisiones; **una fuente primaria judicial candidata** realmente descargada y leída.
- Original: GovInfo `USCOURTS-cand-5_18-cr-00258-13.pdf`, 276077 bytes, SHA256 `658110e0f7d6c59436a8624cadda6e9a41db78cd0e6836323d112e1d3ccbf3d0`; páginas 2/3 citadas. Es una orden de instrucciones preliminares al jurado, no una sentencia. La búsqueda oficial inglesa encontró el documento sin que ChatGPT suministrara su URL. El PDF universitario también se reabrió y escaneó; se intentaron referencias SEC observadas, sin acreditar extracción de esos documentos. Seis descargas totales, dos con texto útil; Qwen/Gemini/Groq exitosos. Datos confirmados en diagnóstico/recibo de Actions; sin lectura D1 administrativa independiente.
- El plan sigue bloqueado: cada afirmación cita una sola URL; dos repiten la fundación, y ninguna está verificada por un humano. No hay guion real aceptable ni audio/video nuevos. No presentar la mera existencia del PDF como corroboración de todas las afirmaciones.
- Se refuerza el prompt para agrupar el mismo hecho con sus citas, admitir menos hechos distintos y distinguir instrucciones/cargos de condena. El parser consolida sólo repeticiones textualmente idénticas (salvo puntuación/mayúsculas), conservando todos sus IDs y estado no verificado; no fusiona por parecido semántico automáticamente.
- Extracción PDF limpia únicamente secuencias marginales ascendentes de al menos ocho números 1–28 y pies judiciales completos. Conserva cifras/fechas sueltas y texto sustantivo. Diagnóstico añade referencias y procedencia de páginas, sin nuevos secretos ni campos arbitrarios. Dos regresiones adicionales; suite Python completa **303 aprobadas**, con FFmpeg. Las 84 Node anteriores permanecen aprobadas; estos últimos cambios son Python/workflow.
- CI [40012055875](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40012055875): `checks` y `live-radar` aprobados; QA audiovisual cancelado al agotar cinco minutos instalando 99 paquetes/94 MB desde el espejo APT. Se sustituye sólo la preparación CI por build mensual BtbN fijado y validado con SHA256, descarga acotada y caché; conserva las pruebas reales y el límite del job. `bash -n` aprobado; pendiente CI Linux de este ajuste. No se desactivó QA ni se amplió la cuota IA.
- No se solicita otra corrida de investigación únicamente por cambios de prompt/formato sobre los mismos archivos. Próximo ciclo necesita nuevas fuentes/contraste; queda pendiente completar corroboración, guion real, revisión y derechos, tomas canónicas, visuales y MP4 8–14 minutos.


### Cierre verificado de esta entrega

- Main `2d23fa8a27afcf4ce28eef4e08b4bd4e431a340a` contiene la consolidación, limpieza y preparación CI corregidas. CI [40013365270](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40013365270): **success**, incluidos checks y QA audiovisual; los disparadores de radar/guion/perfil quedaron omitidos y no se repitieron inferencias.
- Se compararon hashes Git de **19 archivos** entregados entre copia local y árbol remoto: todos coinciden. Suite local final: 303 Python con integración FFmpeg y 84 Node; sintaxis Bash/JS y manifest comprobados. El cambio de FFmpeg se verificó además en el runner Linux real, no sólo por sintaxis local.
- Resultado factual acreditado: primer original judicial candidato legible en el dossier actual de Theranos, con fuente/página/hash y persistencia confirmada por recibo OIDC. Sigue sin corroboración suficiente por afirmación, guion aceptable o documental final. No se verificaron hechos automáticamente, no se cambió la voz, no se renderizó ni publicó un episodio.
- Próxima aceptación: obtener/relacionar soporte de emisores distintos para los mismos hechos, consolidar duplicados en la siguiente investigación con evidencia nueva y pasar la puerta del guionista. Después revisión factual/derechos, tomas canónicas, recursos visuales y montaje/QA de 8–14 minutos. Se conservan las cuotas y la reanudación sin repetir archivos idénticos.

## 2026-10-24 · Recuperar el radar y conectar el apoyo del revisor

- Verificación remota: main `12c0a97cee740382f2e6911cd15ee9de35eabf60`, CI `40013567455` aprobada. El radar programado [40100661992](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40100661992) falló antes de medir YouTube/investigar: Wikidata devolvió más de cinco MB para un lote de entidades y se lanzó ValueError. No se presenta esa ejecución como avance factual.
- `SourcePayloadTooLarge` distingue ese fallo sin incluir cuerpos/URLs/secretos. `topic_discovery.py` restringe sitelinks al idioma, divide lotes demasiado grandes y cuenta todos los intentos dentro del mismo máximo; un título individual demasiado grande se omite explícitamente. Registra consultas, títulos procesados/omitidos/pendientes y cobertura. No aumenta el límite de cinco MB ni las doce consultas del workflow.
- Se conectan las citas adicionales del revisor con las afirmaciones candidatas. `parse_review` valida una matriz por pasaje, IDs conocidos/únicos, cobertura de referencias y coherencia del veredicto. Sólo amplía citas cuando cada pasaje figura como apoyo completo y siguen presentes las citas iniciales; conserva estas últimas en `analysis_evidence_ids`, no reescribe el hecho y recalcula `source_quality`. Contradicción/contexto insuficiente/metadata histórica no amplían citas. Todos los hechos siguen no verificados y sin permisos.
- El contraste cabe en una generación Groq por ejecución, salida acotada a 3200 tokens; conserva reserva D1, límites diarios/mensuales y apagado gratuito explícito. No hay reintento, escalado ni activación de pago.
- Nueva fase `review` del workflow y `tools/review_research.py`: reanuda únicamente Groq sobre el expediente activo obtenido por OIDC; no descarga documentos ni Qwen y no repite Gemini/YouTube. Conserva el cálculo antes de la escritura, el ID/hash de procedencia, fecha documental original y fecha de revisión. Un expediente ya revisado bajo el mismo contrato se omite sin consumir otra reserva ni persistir duplicados. Si queda soporte suficiente encadena el guionista existente; no renderiza ni publica.
- Quince regresiones nuevas cubren el fallo de bytes real, división/omisión/presupuesto, apoyo completo/negativo/incompleto/falso, contrato JS real y reanudación idempotente, cuota denegada y conservación ante fallo D1. Suite local completa: **318 Python y 84 Node aprobadas**, integración FFmpeg, sintaxis JS/manifest y YAML válidos. Sin cambios Worker/migraciones.
- Pendiente al registrar: sincronizar, CI y prueba real `[review-e2e]` del nuevo contraste; después una ejecución del radar corregido. No se declara aún corroboración factual de las afirmaciones ni guion real/MP4 final. Las pruebas positivas usan fixtures; el historial judicial real permanece sin modificar.

### Prueba real y cobertura explícita de comparaciones

- Código `948203ade796ecde639f170fb8e7ac0392a464c6`, CI [40129744193](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40129744193) aprobada. Fase review real [40129775506](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40129775506): `success`, sólo `review-existing`; radar, perfil, guion y encadenado omitidos. Recibo OIDC `ai-02240ffddd1f46cee22c467b0527`. Groq ejecutó la matriz sin repetir Qwen/Gemini/descargas, pero no amplió ninguna cita: cada afirmación siguió con el único pasaje original. No se presenta esto como contraste conseguido.
- Se identificó la limitación operacional: el revisor elegía por sí mismo qué comparar y devolvía sólo los IDs iniciales. `review_candidates.py` fija ahora tareas con las citas originales y hasta dos alternativas de dominios/contenidos distintos, ordenadas por coincidencias de palabras/fechas y equivalencias de recuperación; no contiene una compañía predeterminada. Cada pasaje solicitado debe evaluarse, incluso si resulta insuficiente. La matriz rechaza omisiones, falsos IDs y contradicciones del veredicto.
- Contrato `per_excerpt_support_v2`: `evidence_ids` sólo incluye apoyo completo; los pasajes insuficientes quedan en la matriz sin añadirse como citas, y una contradicción bloquea la ampliación. Se preservan el hecho, citas iniciales y estado no verificado. Una revisión v1 no acredita cobertura v2; una v2 completa se omite al repetirla.
- Tres regresiones adicionales cubren comparación omitida, alternativa insuficiente que no contamina apoyo y presupuesto con ocho citas originales. Suite local Python completa de esta revisión: **321 aprobadas**, con FFmpeg; los 84 Node previos corresponden al mismo código Worker sin cambios. Pendiente CI y una prueba review v2; después radar corregido, siempre dentro de cuotas. No hay render, publicación ni aprobación factual automática.


### Revisión por pasaje confirmada con el expediente real

- Main `42a5881134f90cce9ba688f34944370efc0522f5`, CI [40130149873](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40130149873) `success`. Revisión v2 [40130175486](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40130175486): `success`, radar/guion/perfil omitidos; cero descargas y sin repetir Qwen/Gemini. Recibo OIDC `ai-31ef6ae07e1b19173625e4477830`.
- Resultado efectivo del revisor: las afirmaciones 1 y 2 (variantes del mismo hecho de fundación) pasan de una cita a **tres documentos/dominios**: PDF universitario, EBSCO y CNET. Se conservan IDs originales y matriz de cada pasaje. Esto no son dos hechos distintos ni verificación humana. Ambas siguen con vacío de original primario. Las otras seis afirmaciones mantienen una única URL; los pasajes insuficientes no fueron añadidos como apoyo.
- El guionista no se encadenó: persisten vacíos documentales. No se modificó el texto de los hechos, el expediente previo ni permisos. La evolución real puede inspeccionarse en `INVESTIGACION_DIAGNOSTICO` del job y en su artefacto.
- Pendiente una ejecución completa `[radar-e2e]` para verificar la corrección de tamaño Wikidata y continuar recuperación de fuentes; no se considera el fallo diario resuelto en producción sólo por el test offline. Las cuotas permanecen vigentes.

### Radar recuperado y fuentes nuevas; revisión pendiente del expediente nuevo

- Main `1c6179268de5e87318b5c6730f763cd2d790e8ba`, CI [40130319807](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40130319807) `success`. Radar [40130358108](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40130358108) completado con `success`: **360 títulos considerados, 12 consultas Wikidata y seis compañías detectadas**. La consulta que detenía el radar volvió a funcionar; las pruebas offline cubren también división/omisión. No se afirma que todos los títulos hayan quedado resueltos; la cobertura se registra aparte.
- Recibo OIDC `ai-5b5c8ff036820980d532e502444c`: seis documentos, dos dominios primarios candidatos y cinco hechos propuestos distintos. La búsqueda recuperó texto de la página DOJ `us-v-elizabeth-holmes-et-al` además del original GovInfo histórico y contexto independiente. Un hecho sobre la acusación de junio de 2018 ya cita dos documentos y no tiene vacío estructural de fuentes; sigue sin revisión aceptada ni verificación humana. Otros hechos continúan con fuente única o sin original.
- Qwen y Gemini exitosos; Groq registró `invalid_output`. El reporte fue persistido y el guion quedó bloqueado, sin escenas. La salida rechazada no se conservó, por lo que no se atribuye una causa exacta a ese caso. No se confunde éxito técnico del workflow con aceptación del revisor.
- Se añaden códigos de fallo de contrato y normalización conservadora: una declaración global positiva se reduce si la matriz contiene contradicción o carece de apoyo; sólo se usan IDs con evaluación de apoyo completo. No se eleva un veredicto negativo, no se rellenan evaluaciones ausentes, no se aceptan IDs falsos y no se verifica ningún hecho automáticamente. Las declaraciones originales se conservan al ajustar metadata.
- Dos regresiones nuevas prueban que un resumen positivo no oculta contradicción y que un pasaje insuficiente sale de las citas de apoyo pero permanece en la matriz. Suite local Python completa: **323 aprobadas**, con FFmpeg; mismos 84 Node aprobados del Worker sin cambios. Pendiente CI y una revisión reanudable del expediente nuevo, con una sola solicitud Groq y sin repetir radar/búsquedas/Gemini/Qwen. No se amplía la cuota diaria para esa prueba.

### Contraste del expediente nuevo y corrección de citas activas

- Main `6c2f12af3b28fb906cf5a58fc75fbd9abb517fb3`, CI [40130927788](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40130927788) `success`. Revisión [40130965881](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40130965881) `success`, recibo `ai-c734d1c5225d5ac8af93c20988c8`. Se aceptó la matriz de cinco hechos: el de acusación formal de junio de 2018 tiene dos apoyos completos, incluido DOJ; otros hechos siguen sin contraste suficiente y no hay guion/render/publicación.
- La inspección real descubrió que los hechos compuestos 3 y 5 seguían contando como cita activa un pasaje que Groq había considerado insuficiente. Se corrige la asignación: sólo los pasajes con apoyo completo quedan en `evidence_ids`; las citas iniciales permanecen en `analysis_evidence_ids` y las retiradas en `removed_support_evidence_ids`. La matriz se recalcula, por lo que un pasaje insuficiente ya no aumenta los dominios de apoyo.
- `review_existing` puede reconciliar ese metadata ya revisado y persistir la corrección sin invocar Groq ni reservar cuota. Una segunda reconciliación idéntica se omite. Una regresión adicional demuestra reducción a fuente única, trazabilidad y cero inferencias; suite local Python completa **324 aprobadas**, con FFmpeg. Las 84 Node previas corresponden al mismo Worker sin cambios. Se requiere CI y prueba de reconciliación real antes de declarar esa corrección aplicada a D1.
- El prompt de futura extracción pide hechos atómicos para evitar mezclar edad, año, tecnología y resultados legales con soporte parcial. Este ajuste no se usa como motivo para repetir Gemini sobre los mismos archivos. Se actualiza el encabezado del plan maestro con el estado real; siguen pendientes dossier suficiente, guion, revisión/derechos y producción audiovisual.


### Cierre verificado: radar operativo y apoyo sin inflación de citas

- Código final `5b2ac6bae55c3c3c7dd51f8e4f2b704cd778e9f2`, CI [40131370275](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40131370275) **success**, incluidos contratos y QA audiovisual. Pruebas locales: 324 Python con FFmpeg y 84 Node, YAML/sintaxis/manifest válidos. Comparación de hashes Git de **16 archivos** locales frente a main: todos coinciden.
- Reconciliación real [40131393585](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40131393585), `success`; recibo OIDC `ai-225176fc3823f126c31f8f885413`. Log: `support_reconciled_without_inference`, **GROQ_SOLICITUDES: 0**, descargas 0, Qwen/Gemini no repetidos. El código publicado se ejecutó realmente; no fue sólo una prueba con fixtures.
- Dossier actual: cinco afirmaciones propuestas, seis documentos y dos dominios primarios candidatos. La acusación formal de junio de 2018 conserva dos apoyos, incluidos original DOJ y contexto independiente, y no tiene vacíos estructurales de fuentes. Las otras cuatro tienen vacíos. Los hechos compuestos 3 y 5 quedaron correctamente reducidos a una cita activa; los pasajes insuficientes retirados se conservan como procedencia. Cero hechos verificados por humano, cero guiones/render/publicaciones autorizados.
- Se confirmó la recuperación completa del radar mediante `40130358108`, después de su fallo diario. Nuevos flujos de revisión usan sólo OIDC/rutas D1 existentes; no hubo migración ni despliegue Worker, modificación de claves, cambio de voz o incremento de cuotas. Los recibos/logs de Actions acreditan persistencia; no se atribuye lectura D1 administrativa independiente.
- Próximo criterio de aceptación: completar contraste y originales de las afirmaciones pendientes, mantener hechos atómicos/distintos y obtener un dossier suficiente para el guionista; después revisión factual/derechos y producción canónica/visual del MP4 8–14 minutos. El proyecto continúa incompleto; esta entrega deja radar reparado, comparación por pasaje operativa y conteo de apoyo corregido.


### 2026-10-24 — Guion automático conectado al expediente editorial (código probado)

- Se implementa `/api/market/ai-pipeline/script-ingest`, sólo con OIDC del workflow oficial en main. El guion queda ligado a su expediente D1, QID y huella SHA-256 de documentos, extractos y citas activas. Se recalculan contraste por hecho, revisiones, párrafos, duración y permisos antes de guardar. No se importa investigación insuficiente.
- Migración aditiva `0014_autonomous_script_drafts.sql`: origen/auditoría del guion, tres permisos automáticos fijados a cero. Trabajo `draft`, expediente sin atestación y evidencias/licencias pendientes. D1 batch conserva atomicidad: error => cero trabajos huérfanos; concurrencia y reintentos => un trabajo/evento; revisión humana existente nunca se sobrescribe. La voz declarada conserva exactamente el hash canónico.
- El guionista ahora conserva el run_id original y la huella de evidencias. `tools.push_documentary_draft` importa un artefacto existente sin regenerarlo ni consumir IA, valida recibo D1 y conserva el original ante fallo. La conexión Actions está preparada bajo `AUTONOMOUS_SCRIPT_INGEST_ENABLED=1`; permanece desactivada hasta comprobar el despliegue.
- Estos trabajos no pueden entrar al renderizador heredado que utiliza voz de previsualización. La producción canónica por escena sigue pendiente; guardar un guion no equivale a renderizar ni publicar.
- Segundo horario del workflow: 00:20 UTC (19:20 Lima), sólo revisión reanudable; radar a las 10:17 UTC sin duplicarse. No se aumentan cuotas ni se añaden proveedores cobrables.
- Validación local: **327 Python aprobadas, con integración FFmpeg activada; 90 casos Node aprobados**, incluidos seis contratos Python→JS→SQLite real, concurrencia, rollback, permisos y conservación de edición humana. El doble de pruebas editorial se actualiza para reconocer la nueva consulta de origen; trabajos anteriores conservan sus pruebas.
- Conexión de producción finalmente verificada con `martin30.eler@gmail.com`: lectura real de Worker/settings y D1 correcta. Respaldo Time Travel previo: `000000ee-00000000-0000510e-847c51789e199a19f91a0960c76bcbff`. Versión Worker anterior: `c306704e-d6b6-4c14-b1ca-6d39e06b02d9`. Antes de esta entrega no se ha aplicado 0014 ni desplegado el código nuevo; se registrará la aceptación real aparte.
- Lectura D1 independiente confirma expediente `ai-225176fc3823f126c31f8f885413`, cinco candidatos y cola `awaiting_sources`; un trabajo previo. Reservas de hoy: Gemini 1, Groq 4, Tavily 2. Groq llegó al límite del proyecto: no se repite la inferencia ni se aumenta el tope. Falta dossier suficiente, guion real aceptable, derechos/tomas/visuales y MP4 profesional de 8–14 minutos; proyecto incompleto.


### Evitar regeneración al reintentar guion importado

- CI del primer bloque `476c67a877a5a5dd8609b19fe57ae677d7f4736b`: [40132985120](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40132985120), success. Se completa la reanudación: `script-context` devuelve el guion original ya importado; el CLI lo reutiliza antes de construir clientes o reservar cuota. Ediciones humanas siguen en su expediente y no se sustituyen.
- Una regresión Python adicional confirma cero generación/reservas en reintento; el contrato SQLite comprueba recuperación exacta del guion y job_id original. Suite local: **328 Python con FFmpeg y 90 Node aprobadas**. Despliegue de 0014 y del Worker aún pendiente en este punto del historial.


### Despliegue real de integración guion → panel

- Código `068ffeee71536394e71d15d9be52698814bea7c6`, CI [40133084536](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40133084536) **success**. Suite final local: 328 Python con FFmpeg; 90 casos Node aprobados.
- Aplicada migración aditiva 0014 en D1 de producción mediante API Cloudflare autenticada. Tabla e índice creados sin borrar ni reconstruir tablas. D1 anterior no utiliza `d1_migrations`; no se inventa un registro Wrangler. Verificación posterior de tabla, conteos y claves foráneas.
- PUT Worker oficial aceptado HTTP 200 a las 21:11:35 UTC. Entrada `src/worker.js`; 22 módulos, JSON empaquetado como módulos constantes, sin cambiar lógica. Se conservaron todos los bindings mediante `inherit` estricto y los assets con `keep_assets:true`; tres secretos permanecen en Cloudflare, sin leer ni copiar valores. Fecha de compatibilidad permanece 2026-10-20; clasificación Cloudflare mantiene bandera 0.
- ID devuelto de despliegue: `d1b3f05edffa4718a4eb3760eef8397a`; etag `0302fa889df844e661ebcdf70604623650d60730ec161555fc19ba5103269932`. La migración no crea documentales de prueba en producción. Se habilita por defecto la importación Actions; un 0 explícito en `AUTONOMOUS_SCRIPT_INGEST_ENABLED` la desactiva.
- Se solicita prueba real `[script-e2e]` desde el expediente activo para comprobar contexto, guardas OIDC y rechazo de investigación insuficiente, sin nuevas inferencias. Un rechazo correcto no acredita importación positiva de un documental real; esa aceptación requiere dossier suficiente. Aún no hay MP4 autónomo aceptable.


### Ajuste de activación ausente en Actions

- CI [40133182729](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40133182729), success; guionista real [40133208758](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40133208758), success, expediente insuficiente sin generación, cero tomas. La inspección de pasos muestra que la importación se omitió: no se declara probada la nueva ruta.
- Se cambia la condición a `(vars.AUTONOMOUS_SCRIPT_INGEST_ENABLED || '1') == '1'` para expresar un valor por defecto explícito sin comparación numérica implícita. Un 0 configurado se sigue respetando. Se repite exclusivamente la prueba de script, sin radar ni IA. La lectura del código Worker servido ya contiene la nueva ruta y la reutilización de contexto; bindings y D1 verificados.


### Aceptación real del endpoint y cierre de esta integración

- Main de código/activación `13c506f1a904266e9be11011d2193985957484d8`; CI [40133300880](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40133300880) **success**. Prueba real de script [40133322890](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40133322890) **success**. Ahora el paso de importación sí se ejecutó y registró `GUION_PANEL_OIDC: rechazo 400 confirmado; sin guion aceptable`. OIDC y nueva ruta comprobados; el expediente real insuficiente no creó ningún trabajo ni tomó cuota IA.
- QA de producción en Actions: `/health`, panel y `/app.js` HTTP 200; API de investigación sin credenciales 401; consulta del renderizador con token a UUID inexistente 404, autorización correcta. Los tres pasos diagnósticos tienen conclusión success.
- Verificación D1 posterior: sigue un trabajo previo, cero filas en `autonomous_script_drafts`, cero infracciones de claves foráneas; reservas idénticas a las anteriores (Gemini 1, Groq 4, Tavily 2). No se publicó contenido ni se concedieron aprobaciones.
- Comparación local con árbol main: **14 archivos críticos idénticos por hash Git**, incluido el MP3 original. `reference.json` tiene sólo diferencias de formato del snapshot local: contenido JSON semánticamente idéntico al remoto, misma identidad, SHA y política. `python -m tools.approved_voice --check` pasó con la referencia exacta.
- Acceso Cloudflare de producción ya operativo para lectura/escritura; el bloqueo de conexión de este turno está resuelto. Tabla, Worker y flujo Actions están desplegados y probados. La importación positiva de un documental real queda pendiente de un dossier suficiente; la prueba positiva completa hasta SQLite usa fixtures y no se presenta como episodio real.
- Estado de producto: cinco hechos candidatos Theranos; uno con original e independiente, otros cuatro con vacíos. Guion real sigue bloqueado, cero tomas generadas y cero MP4 final. Próximo criterio: completar contraste y obtener hechos distintos suficientes; después revisar guion/derechos y ejecutar producción con voz canónica y recursos por escena. **El proyecto todavía no está terminado.**


### 2026-10-24 — Continuación factual sin repetir radar ni investigadores

- Se añade `tools/corroborate_research.py` y fase `corroborate` del workflow oficial. Lee el expediente activo por OIDC, deriva objetivos de sus vacíos reales, rota al próximo hecho pendiente y busca documentos nuevos con los límites existentes: dos búsquedas por proveedor configurado, hasta ocho descargas y una revisión Groq. No carga Qwen ni invoca Gemini/Mistral/OpenRouter; no vuelve a medir mercado.
- Conserva todas las citas activas antes de incorporar pasajes nuevos, distribuye espacios entre documentos y respeta el máximo de diez evidencias. IDs y afirmaciones se remapean juntos; matrices anteriores quedan en el expediente padre. El descubridor nunca agrega por sí solo citas de apoyo. Sólo una revisión completa por pasaje puede hacerlo; un pasaje insuficiente sigue fuera del apoyo activo.
- Si Groq no tiene cuota, las nuevas lecturas quedan persistidas con revisión pendiente y un recibo D1. El cron de revisión puede retomarlas sin descargas ni análisis repetidos. Una lectura fallida queda en historial para no gastarla de nuevo; no se aumenta la cuota diaria. Una revisión editorial abierta no se toca.
- Nuevo horario a las 00:40 UTC (19:40 Lima), tras la revisión de las 00:20. El radar principal mantiene 10:17 UTC. El guionista se encadena únicamente si el dossier ampliado supera todas sus puertas; no se habilita render ni publicación.
- Seis pruebas nuevas cubren conservación de citas/linaje, rechazo de apoyo parcial, revisión diferida por cuota, reanudación sin descargas, rotación/capacidad y artefacto guardado antes de un fallo D1. Suite Python completa local **334 aprobadas con FFmpeg**, YAML y diff válidos. Los 90 contratos Node anteriores corresponden al mismo Worker, sin cambios en este bloque. Pendiente CI y ejecución real de contraste; no se presenta todavía como nuevo apoyo factual ni guion aceptado.


### Contraste real persistido y protección de las lecturas pendientes

- Main `cbf3efb1e5e31e831086bd2c1798476a49b016ba`, CI [40134045789](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40134045789) success. Contraste real [40134078185](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40134078185), success: ocho intentos de descarga, dos documentos nuevos legibles, **cuatro pasajes nuevos retenidos**, recibo D1 `ai-6eba409cc681623b49ce3452361f`. Lectura administrativa independiente confirma expediente de diez evidencias y cinco hechos candidatos; todas las citas activas previas se conservaron/remapearon. Los documentos nuevos son El CEO y una página Ethics Unwrapped/University of Texas; no se presentan como fuentes primarias. El original DOJ activo permanece; otros documentos históricos sin cita activa están en el expediente padre.
- Groq tuvo reserva denegada por el tope diario: **cero llamadas Groq**, cero inferencias Qwen/Gemini y cero radar repetido. Los pasajes quedaron `sources_saved_pending_review`, no como nuevo apoyo aceptado. Cuotas D1 verificadas: Gemini 1, Groq 4, Tavily 4; se usaron dos búsquedas Tavily adicionales dentro del límite de ocho. Guion/render/publicación siguen cerrados.
- Se protege la siguiente continuación: si hay pasajes guardados pendientes, no se buscan otros ni se descartan antes de que el revisor los evalúe. La regresión reproduce denegación de cuota, nueva lectura preservada y revisión posterior sin descargas.
- Se corrige otro obstáculo del descubrimiento: la extracción de referencias ahora recoge y ordena hasta 800 enlaces observados antes de devolver doce, priorizando el tema y rutas documentales. Los primeros doce enlaces de un menú oficial ya no desplazan automáticamente documentos posteriores. Metodología `ranked_regulatory_links_v2`, sin inventar URLs ni aumentar descargas. Los barridos antiguos pueden reabrirse una vez; un barrido con el nuevo método se conserva en historial y no se repite.
- Dos pruebas adicionales cubren un documento después de cincuenta enlaces de menú y el cambio de versión de barrido. Suite local completa: **336 Python con FFmpeg aprobadas**, diff válido. Worker/D1 sin cambios de esquema ni despliegue en este bloque. Pendiente CI final y prueba de reintento sin nuevas búsquedas. El cron 00:20 UTC debe revisar los pasajes guardados al renovarse la cuota; no se finge que ya se revisaron.


### Cierre verificado de continuación factual

- Código final `7cbc40b671ee6645d7d5ecc2e4571e017d8e00df`, CI [40134568673](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40134568673) **success**. Reintento real [40134605776](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40134605776), **success**: `awaiting_saved_passage_review`, descargas 0, Groq 0 y radar/Qwen/Gemini no repetidos. No se perdieron los cuatro pasajes descargados.
- D1 después del reintento conserva como último expediente `ai-6eba409cc681623b49ce3452361f`, cinco candidatos. Las reservas permanecen Gemini 1 / Groq 4 / Tavily 4; el reintento no gastó nuevas búsquedas ni inferencias. Sigue un trabajo previo y cero guiones autónomos importados. La validación local del MP3 canónico pasó con su SHA original.
- Ocho regresiones nuevas en este bloque; suite Python completa **336 aprobadas con FFmpeg**, más los contratos Node y QA de CI. Cambios publicados sólo en main; ningún secreto, voz, permiso factual, derecho audiovisual o autorización de publicación fue sustituido.
- Siguiente ejecución programada: revisión a las 00:20 UTC (19:20 America/Lima), tras reinicio UTC de cuota; continuación de fuentes a las 00:40 UTC. GitHub puede demorar los cron. La revisión pendiente aún no ocurrió: cuatro pasajes nuevos no equivalen a cuatro hechos corroborados. Sigue pendiente dossier suficiente, guion real, narración/visuales y MP4 de 8–14 minutos.


### 2026-10-24 — Cambio explícito de estrategia ordenado por el propietario

- El propietario indica que Codex realice directamente investigaciones y búsquedas de prueba; las demás IA se probarán en la versión final integrada. Esta instrucción reemplaza la secuencia previa de disparar revisiones y búsquedas reales durante cada avance.
- Todos los jobs de proveedores del workflow oficial requieren ahora `FINAL_AI_INTEGRATION_ENABLED=1`; sin esa variable quedan desactivados, incluidos cron, análisis, revisiones, búsquedas y guionista. Se conservan implementación, secretos y cuotas para la prueba final. No se incrementa ningún límite ni se invoca un proveedor para validar este cambio.
- La meta de desarrollo es cerrar el motor genérico de episodio completo con material de prueba investigado directamente por Codex. No se presentará ese material como resultado autónomo de las IA ni como autorización comercial/publicación. La voz canónica permanece intacta.


### 2026-10-25 — Motor genérico de episodio completo y material investigado directamente

- Por instrucción del propietario, Codex consultó directamente nueve fuentes de SEC, Justicia, FDA y análisis contextual. Entrega revisable `research/theranos-development/GUION_PRUEBA_CITADO.md`: 1.600 palabras, ocho escenas, fuentes por párrafo y corte histórico 2022-12-07. Su origen es `codex_development_research`; no es salida de las otras IA ni reemplaza el expediente autónomo D1.
- Se implementan contrato de episodio, adaptación de guion autónomo validado, narración Qwen CPU reanudable por toma, gráficos originales por escena, subtítulos SRT/VTT, capítulos, créditos, MP4 y página de revisión. Referencia vocal y cadencia aprobadas se conservan. Los checkpoints evitan repetir tomas válidas y bloquean una voz de prueba como narrador real.
- Exportación técnica local real: **696 segundos (11:36), 1280×720, 12 fps, H.264/AAC**, SHA del MP4 `e1f8fea06dd94db8ccb7210a1ed870982cc75b573cdac748a55f9c97072f4f4b`. QA sobre archivo real aprobada. Contiene una señal técnica expresamente identificada, **no locución**; cero tomas Qwen y cero llamadas a proveedores. Se corrigió movimiento que el primer render comprimido detectaba como planos congelados, sin rebajar umbrales QA.
- Worker/panel conectan trabajo autónomo aprobado al motor canónico, recuperan contexto con trazabilidad, reciben informes idempotentes y ofrecen reintento con tomas anteriores/enlace al artefacto. No se fabrica aprobación humana en D1. Una señal técnica, manifiesto cambiado, referencia incorrecta, QA fallida o permisos inventados no marca un episodio narrado como listo.
- Workflow `development-episode.yml`: modo técnico sin IA y modo final canónico con habilitación explícita por ejecución, matriz de escenas, checkpoints y artefactos recuperables. La habilitación individual no enciende búsquedas ni cron de proveedores. Puente `tools.production_job` no llama IA ni expone claves. Sin migraciones nuevas, sin publicación YouTube.
- Verificación local: suite Python completa anterior a añadir las cuatro pruebas del puente **343 aprobadas con FFmpeg**; las **cuatro pruebas adicionales del puente aprobaron**. **95 contratos Node aprobados**, incluidos despacho Worker→workflow→adaptador Python, seguridad, callback y reintento. Voz original verificada por SHA. Esto acredita implementación y pruebas locales; **CI, artefacto remoto y despliegue de este bloque se registrarán después de comprobarlos**.
- Operación y límites documentados en `docs/PRODUCCION_EPISODIOS.md`. Próximo paso exacto: publicar en main, comprobar CI y montaje técnico en Actions, desplegar Worker/panel y después ejecutar una prueba final canónica con el material preparado. El documental narrado, la audición y la aceptación profesional siguen pendientes; no se declara terminado el proyecto.


### Ajuste de CI y comprobación de despliegue automático

- Commit principal `a4383ecd32f6d6f0de5a5b1e5e41ca8b727a634b`, CI `40163236319`: contratos generales success (347 casos Python, cinco omitidos en ese job por requerir FFmpeg explícito, y 95 Node). El job audiovisual falló por ruta de importación de fixtures al ejecutar módulos específicos, no por montaje; se corrige `PYTHONPATH=.:tests`. Los quince casos audiovisuales pasan localmente con el mismo comando. El disparador de episodio ahora exige tanto contratos como QA audiovisual.
- Workflow técnico real `40163254722`: preparación correcta y montaje en curso; todavía no se declara artefacto remoto aceptado.
- Cloudflare desplegó automáticamente la integración en versión `a9325812-3831-446c-a88f-947cf949cf59`, deployment `6fe6b559-ac0b-45a8-81ff-0e3b40124850`. La lectura del Worker servido confirma rutas de episodio, workflow canónico, reintento y SHA de voz. La verificación HTTP pública desde el conector es 403 externo; no se presenta como fallo del Worker. Se amplía el smoke de Actions para comprobar el panel nuevo y registrar su hash sin credenciales.
- Se incorpora disparador explícito `[final-episode-e2e]` para una ejecución final canónica después de todos los checks. Este commit de corrección **no lo activa** y no reactiva proveedores ni cron de investigación. La voz final permanece pendiente.


### Candidato integrado verificado; prueba final canónica acotada

- CI corregido `40163372125`, commit `eb04986c04f172694bd58a49899563dec79c5b0c`: **success** en contratos y los **quince casos audiovisuales con FFmpeg**. Job general: 347 casos Python, cinco omitidos cubiertos en la suite audiovisual; 95 Node. La incidencia de importación quedó resuelta.
- Smoke desde Actions confirma HTTP 200 de `/health`, panel y JavaScript nuevo. SHA `/app.js` `7f664433c0b3e4968fe587dae1efcce3740a9e8fcbf0f34e3f6288f5ab546415`, idéntico al archivo implementado. API de investigación y nueva ruta de episodio sin token: 401. Renderizador autenticado a UUID inexistente: 404. Despliegue Worker y panel verificado sin revelar claves.
- Cron real `40163370338` quedó **skipped** por la pausa del propietario: no reactivó búsquedas ni investigadores. El montaje técnico `40163254722` sigue exportando el episodio; aún no se declara terminado ese run.
- Tras comprobar el candidato y el MP4 técnico local, se solicita **una prueba final de narración y montaje** mediante `[final-episode-e2e]`. Usa exclusivamente Qwen TTS 1.7B en CPU y el material preparado por Codex; no invoca Gemini, Groq, Tavily, Exa ni radar. Conserva referencia/cadencia y checkpoints de cada toma. Esta solicitud no acredita éxito de generación, audición ni calidad profesional: se registrará su resultado real. No aumenta cuotas de proveedores ni autoriza publicar.


### Pausa completa desde el panel y prueba final solicitada

- Se cierra también la vía manual de investigación `research-ai-cpu.yml`: exige la habilitación final y el Worker rechaza lanzamientos con HTTP 409 antes de reservar cuota D1 o contactar GitHub. El panel muestra la pausa y desactiva el botón; los informes históricos siguen consultables. `wrangler.jsonc` fija `FINAL_AI_INTEGRATION_ENABLED=0`; habilitar la investigación futura requiere cambio explícito tanto en Worker como en Actions. No se modifican secretos ni se llama a un proveedor para comprobar esta puerta.
- Regresión nueva prueba pausa por defecto, valores no habilitantes, cero reserva y cero despacho; conserva los diez casos anteriores de control. Se actualiza el contrato D1 local para el valor predeterminado pausado. Las pruebas locales de control pasan (11); el conjunto completo suma **96 casos Node aprobados**.
- Candidato `c07cf783d9372a2d740ea9944eba0bee054b28fa`, CI `40163527331` success. Prueba final canónica solicitada `40163555937` (en cola al registrar). Sin ejecución final aceptada todavía; no se presenta como narración completa ni se reactivan las IA de investigación. Montaje técnico remoto `40163254722` aún en curso.


### Montaje completo aceptado en Actions; narración final en ejecución

- Workflow técnico **40163254722 success**: exportó **696 s (11:36)**, sin locución y sin modelos; pasó QA del MP4 real. Artefacto `fdg-episode-technical-review`, ID **12587492309**, **30.530.632 bytes**, digest ZIP `sha256:24742c5ce35b9e1de3e201cff93372adc299468232579f3554a7a2d743abd8ff`. Descarga: https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40163254722/artifacts/12587492309 . Incluye video, subtítulos, fuentes, guion e informes; no se sube el WAV de la señal. Retención siete días. No se confunde con documental narrado ni aprobado para publicar.
- Pausa del panel/API publicada en main **e614d752d6d498e94f02fd1ac2b63b94dcfb2385**; CI **40163689370 success**, 347 casos Python (cinco integraciones cubiertas por la suite audiovisual separada), quince audiovisuales y **96 Node**. Cloudflare deployment **96665e23-38ec-450c-8729-98dbf893ed66**, versión **8a90d5d6-c00f-4beb-b15e-047775dc8356**, confirma código de rechazo y variable `FINAL_AI_INTEGRATION_ENABLED=0`. El smoke de ese run precedió por siete segundos al despliegue nuevo: su hash corresponde al panel anterior ya validado; no se atribuye falsamente al panel de pausa.
- Prueba final **40163555937**: preparación success, dos escenas generando con Qwen CPU y seis en cola al registrar. Nada acredita todavía narración completa, identidad auditiva ni MP4 narrado. No se repite investigación y no se habilita publicación. El README ahora enlaza entregables actuales y describe el motor canónico, sin seguir presentando Piper como narrador del producto.


### Seguimiento fiable y panel de pausa comprobado

- CI documental **40163851401 success** y smoke de producción confirman el JavaScript del panel de pausa SHA `9db138451afe88ae5dd64c477950698148a8350bd2bf73f6fdcbc987f95a1905`, idéntico al publicado. HTTP 200 de panel/salud y 401 sin credenciales de investigación/episodio. El Worker mantiene investigación deshabilitada; referencia vocal original intacta y workspace local limpio antes de este ajuste.
- Se corrige un caso concreto del callback: un fallo retrasado ya no puede sobrescribir un episodio que pasó a `ready` después de leerse su estado. Fallo y ejecución recuperable se guardan condicionalmente en un batch D1; se conserva la revisión. Regresión SQLite reproduce estado leído atrasado y comprueba cero cambios sobre el resultado listo. Se exigen también cadenas reales para hashes/run IDs, evitando coerción de arrays.
- **97 casos Node locales aprobados** tras el ajuste; seis corresponden a la integración canónica. Python/render sin cambios. CI/despliegue del ajuste se comprobarán después de publicar. Prueba final `40163555937` sigue generando las dos primeras escenas en CPU; no se repite ni interrumpe para estos cambios de seguimiento. Ningún proveedor de investigación se ha reactivado.


### Cierre verificado del bloque de implementación — 2026-10-25 05:11 UTC

- Main de código **01e4da04d658499381db3a04f4a711731b1b463a**, CI **40164274158 success** en contratos y QA audiovisual. Total Node: **97 aprobados**. Los 347 casos Python quedan cubiertos por el job general y los casos FFmpeg del job audiovisual. Cloudflare deployment **b043cfc7-a46b-438b-a611-a57bf1d1e42e**, versión **b1f9b79e-dab4-466a-8531-a47d4ccee19c**, confirma la protección condicional del fallo tardío servida en producción. Worker/panel mantienen los secretos, D1 y la pausa del propietario.
- Se descargó el ZIP técnico real de Actions y se comprobó su digest `24742c5ce35b9e1de3e201cff93372adc299468232579f3554a7a2d743abd8ff`, sus diez archivos, SHA del MP4 coincidente con el informe, 696 segundos, QA aprobada sin fallos, referencia canónica exacta y `contains_narration=false`. La comprobación no depende sólo del estado success del workflow.
- Narración final **40163555937** en ejecución: **SC01 y SC02 success**, artefactos **12587528554** y **12587712030**. Se descargaron y validaron las **14 tomas Qwen** contra texto, modelo, cadencia, referencia y hash real del audio: **80,300 s** y **86,826 s**, total **167,126 s**. No son dobles de prueba; son nuevas generaciones CPU, todavía pendientes de audición. No se concede aprobación de identidad ni licencia comercial. SC03/SC04 siguen procesándose y las cuatro restantes están en cola. No se reinicia el run ni se regeneran esas catorce tomas.
- El flujo continuará automáticamente con las escenas restantes, ensamblado y QA del episodio narrado. Resultado y artefactos: https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40163555937 . **Este registro no declara terminado ese flujo:** no existe aún una exportación narrada completa verificada. Si falla, conservar sus artefactos y usar `resume_run_id=40163555937` para continuar las tomas faltantes; no repetir investigación.
- Bloque de software implementado, probado y desplegado; guion investigado directamente y montaje técnico completo entregados. Quedan el resultado de la prueba final canónica, audición/aceptación profesional, prueba integrada del equipo de investigación cuando se habilite expresamente y OAuth/subida YouTube con sus permisos. No se declara terminado el proyecto ni se solicita al propietario investigar o redactar el material de desarrollo.


### 2026-10-25 — Avance de producción y descarga dentro del panel

- Se implementa seguimiento de las ocho ejecuciones más recientes: preparación, narración por escena, montaje y archivos de revisión. API privada `/api/production/runs` y detalle numérico, sólo ADMIN y GET. No escribe D1, no despacha workflows, no reserva cuota ni invoca IA. Consulta manual al conectar/actualizar, sin sondeo permanente.
- La API verifica repositorio oficial, rama main y workflow canónico antes de consultar jobs/artefactos. Respuestas y tiempos acotados, redirecciones rechazadas y errores sin cuerpo remoto ni claves. Reintentos conservan éxitos anteriores y cada escena se cuenta una vez. No convierte escenas completadas en porcentaje global del proyecto.
- Panel muestra estados y descarga sólo tras montaje correcto y artefacto no caducado. Distingue señal técnica de video narrado pendiente de revisión, construye enlaces oficiales y muestra caducidad. Resultados parciales/fallidos no se ofrecen como MP4 terminado. Se añade identificación de trabajo en nombres de las futuras ejecuciones.
- Seis pruebas nuevas cubren avance real y reintentos, distinción de audio, expiración/URL oficial, filtros, consultas acotadas, fallos sin filtraciones y ADMIN/renderer/métodos. Conjunto Node local **103 aprobados**, sintaxis, YAML y diff correctos. CI añade lectura real contra Actions con permiso de lectura; no inicia trabajos. Smoke de producción comprueba el panel y la barrera nueva. CI/despliegue aún pendientes de verificar al publicar este bloque.
- Narración real `40163555937`: SC01/02/03 success, SC04 y SC05 en proceso al registrar. No se reinicia ni se vuelve a investigar. El video narrado completo sigue pendiente del resto de escenas, montaje y QA. La pausa del equipo investigador y la referencia vocal aprobada permanecen.


### Lectura real de producción y comprobación de despliegue sin repetir IA

- Código **67a28e535b70daf6450f09dd27e064fd86757165**, CI **40165204728**: contratos y QA audiovisual success, **103 Node** y cobertura Python anterior conservada. La lectura real del nuevo módulo registró `run_id=40163555937`, **3/8 escenas**, cero fallos, cero exportaciones y **ai_calls=0**. No es un contador simulado ni una nueva ejecución de modelos.
- Cloudflare deployment **7e6627cf-2023-4f4c-9a56-701fe5493b04**, versión **8fb056ba-0e75-4895-a04e-b404d7311c67**, código de seguimiento comprobado servido. El smoke de ese CI leyó el panel anterior ocho segundos antes del despliegue: HTTP 200 no se presenta como validación del JavaScript nuevo.
- Se añade comprobación posterior de producción independiente de las pruebas: lee el panel, exige el SHA exacto de `public/app.js` y las barreras privadas; admite seis consultas breves para sincronización. No repite suite/modelos ni despacha producción. La prueba final futura espera este job. Pendiente resultado de esta comprobación posterior al publicar el ajuste.


### 2026-10-25 — Conexión oficial del canal preparada, sin publicar

- El seguimiento por escenas ya está desplegado y aceptado: código `2d608d4a938172db9fa80347ef49c0bd2ad8d574`, CI **40165476276 success**, incluido `production-smoke`. Panel servido SHA `622207cc7511e6c591f10ed18e033e332e7948055932e6e847755f360b7f0614`, idéntico al código; salud/panel HTTP 200 y rutas privadas 401 sin credenciales. Se descargaron y validaron 29 tomas de las cuatro primeras escenas, **339,552 s**, sin regenerarlas ni conceder aprobación auditiva.
- Se prepara el siguiente bloque de conexión OAuth: API ADMIN de estado/inicio/desconexión y callback público controlado. State y cookie de un solo uso, PKCE, caducidad, verificación del ID exacto del canal, cifrado AES-GCM de credenciales en D1, renovación interna y revocación. Ninguna ruta devuelve access/refresh tokens. La conexión no contiene una operación de subida ni publicación.
- Panel incluye «Canal YouTube», configuración pendiente y botón de consentimiento Google desactivado si faltan credenciales. La clave Data API existente no se presenta como OAuth. Documentación concreta `docs/CONEXION_YOUTUBE.md` con retorno exacto y tres secretos del propietario; la clave de cifrado se configura automáticamente y no se revela.
- Migración aditiva **0015 aplicada realmente en D1**: dos tablas y un índice, tres sentencias success. Antes había un trabajo y ninguna tabla OAuth; no se modificaron tablas anteriores. `YOUTUBE_TOKEN_ENCRYPTION_KEY` creada como secreto Cloudflare (HTTP 201), sin imprimirla ni escribirla en archivos. Aún faltan `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET` y `YOUTUBE_CHANNEL_ID`; **no hay cuenta Google conectada ni consentimiento concedido**.
- Nueve contratos nuevos prueban consentimiento/PKCE/cifrado, cookie/state/expiry/replay, canal equivocado, permisos incompletos y errores, carrera con desconexión, aislamiento ADMIN/renderer, cancelación y renovación interna sin restaurar una conexión borrada. Suite Python local completa **347 aprobadas con FFmpeg**. Node completo **112 aprobados**, incluidos los nueve casos OAuth y renovación; se volvieron a aprobar tras vincular credenciales al cliente/canal exactos. CI/despliegue del bloque OAuth pendientes de publicar/verificar.
- La narración `40163555937` conserva sus escenas y continúa sin reinicios; seis escenas success y las dos finales procesándose al registrar. El equipo de investigación permanece pausado y no se usa ningún proveedor para desarrollar OAuth. Pendientes: MP4 narrado/QA/escucha, configuración y consentimiento reales de Google, subidor privado con revisión por episodio y habilitación explícita de investigación para su aceptación final.


### 2026-10-25 — Primer episodio de desarrollo completo con narración real y QA

- Prueba final **40163555937 completed/success**: las ocho escenas de voz terminaron y el job de montaje **121090344893 success**. **56 tomas Qwen Base 1.7B CPU**, referencia y cadencia originales, sin reemplazo por otra voz. Se exportó el documental completo con **671,483 s de audio (11:11)**; contenedor MP4 **671,500 s**, H.264 1280×720 a 12 fps y AAC mono 48 kHz, ocho capítulos, subtítulos SRT/VTT, guion, fuentes y página de revisión. `technical_gate_passed=true`, fallos QA `[]`.
- Artefacto **12588892336**, `fdg-episode-narrated-review`, **30.130.903 bytes**. ZIP SHA256 **b4f68867dd3989776b08b2af756b59bfb40b67f3755e9f7704c34ee6fc8df4bd**. Descarga: https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40163555937/artifacts/12588892336 . Retención siete días; conviene descargar el paquete. MP4 SHA256 **398d5963d25f35f2c1bccb2b7c759e25ec224758243d99e250bccf000f3991ad**.
- Se descargó y extrajo realmente el ZIP: digest, conjunto de archivos, SHA del video, huella del episodio y de la referencia, las 56 tomas declaradas y todas las banderas de aprobación verificadas. FFprobe confirma duración/codecs y una imagen extraída del MP4 confirma el montaje con texto, identidad y subtítulos. La primera comprobación local esperaba un archivo adicional: se corrigió el recuento y pasó. **Corrección del historial:** estos paquetes contienen **nueve archivos**, no diez como se anotó antes; no se alteró el video para corregir el conteo.
- Reporte mantiene `contains_narration=true`, `voice_kind=canonical_qwen_pending_audition`, `human_factual_approval=false`, `commercial_rights_verified=false` y `publication_authorized=false`. No se inventa audición humana ni licencia comercial. El episodio parte del guion de desarrollo investigado por Codex; no prueba que el equipo investigador autónomo haya terminado su dossier real D1. No se han reactivado Gemini/Groq/Tavily/Exa ni repetido búsquedas para este avance.
- OAuth de código **42fb42469c49dafcecd73b2a1bb524f56f2792d6**, CI **40166762056 success** en contratos, QA audiovisual y comprobación posterior de producción. Panel SHA **c943ed7f083477a1b498e13c40f3d291e86f950276cb3e6fc32318a64cc9ef8f** coincide con el código servido. Salud/panel HTTP 200; investigación/progreso/OAuth 401 sin token; callback inválido 303 sin conectar ni llamar a Google. Cloudflare deployment **2835ac0c-fc4f-4a8b-87e2-f7e0b6fc6932**, versión **e6f65de4-1c5d-40e1-9c0c-f61503f6e691**, módulo OAuth servido y secreto de cifrado presente.
- D1 conserva el trabajo anterior, incorpora las dos tablas OAuth vacías y no tiene infracciones FK. El propietario respondió que **necesita crear el cliente OAuth**; se entregó guía concreta con tipo Aplicación web, URI de retorno y secretos Cloudflare. No hay cuenta Google conectada ni subida YouTube. Próximos pasos: revisión audible/visual del episodio, configuración y consentimiento Google, implementar el subidor privado con autorización por episodio y aceptar el equipo investigador cuando se habilite expresamente. No se confunde el cierre técnico del motor con el proyecto terminado.


### 2026-10-25 — Canal OAuth conectado y entrega privada implementada

- Conexión real comprobada en D1: canal **Factor de Gigantes**, ID **UC61mComG9XD-RwoWhXFv1Lg**, último resultado OAuth `connected`. No se leyeron ni mostraron credenciales. Queda resuelta la configuración del cliente/canal y el consentimiento, sin confundirlo con autorización del episodio.
- Se implementa registro de exportaciones canónicas terminadas, borrador de metadatos y revisión final en el panel. Cada aprobación se vincula al SHA del MP4 y exige voz, fuentes, derechos, gráficos/subtítulos, metadatos, audiencia y responsable. Casillas inicialmente sin marcar; el material Codex conserva su origen de desarrollo.
- Subida privada separada: reserva atómica, workflow sólo manual por solicitud autorizada, paquete/SHA verificados, una sesión reanudable cifrada y transferencias de hasta 4 MiB a través del Worker. Los tokens Google y la URL de sesión no se entregan al runner ni al navegador. Privacidad `private` y notificaciones desactivadas por código. Reintentos consultan rango y conservan solicitud/sesión; un inicio incierto no se duplica.
- Confirmación final consulta a Google el ID, canal y privacidad antes de marcar `uploaded`; callback repetido es idempotente. La desconexión o cambio de canal bloquea nuevas transferencias. No hay publicación pública automática ni invocaciones de IA en estos workflows.
- Migración nueva `0016_youtube_exports.sql`: dos tablas y un índice aditivos. Operación documentada en `docs/SUBIDA_PRIVADA.md`. Siete contratos Node de exportaciones/roles/aprobación/protocolo y cuatro Python de transporte/reanudación; conjunto local **119 Node** y **351 Python con FFmpeg aprobados**, YAML y sintaxis válidos. Pruebas Google simuladas: no se atribuye una subida real.
- Próximo paso de este mismo bloque: desplegar, ejecutar CI y registrar el episodio existente `40163555937` para revisión, sin repetir montaje, investigación o voz. La subida real queda pendiente de autorización por episodio del propietario; no se fabrica esa aprobación durante el registro.


### Cierre comprobado: subida privada desplegada y episodio en revisión

- Código **0b5776261e7f9da085474a6bb8a829bfb74e6ba4**, CI **40172097549 success**, incluidos contratos, QA audiovisual, comprobación del panel y despacho de registro. **119 Node y 351 Python** cubiertos por la suite general y los casos FFmpeg separados. No se invocaron investigadores ni se regeneró la voz.
- Smoke posterior confirma panel HTTP 200, JavaScript servido SHA **3b3f58bee40e7cf1bd137cf98352616227bd7d0dd83af5dd16f5e45ec3e28ec2**, módulo `youtube-review.js` HTTP 200 y barreras de conexión/exportaciones 401 sin credenciales. Callback inválido continúa 303. El resultado prueba el código desplegado, no sólo una solicitud de despliegue.
- Registro real **40172138117 success**, job **121105036167**: recuperó el paquete narrado existente y registró la exportación **398d5963d25f35f2c1bccb2b7c759e25ec224758243d99e250bccf000f3991ad**. Consulta D1 independiente confirma `state=review`, procedencia run **40163555937** / artefacto **12588892336**, revisión `{}`, audiencia sin declarar, privacidad borrador `private`, cero sesión y video ID vacío. Único evento `registered_for_review`; **no se aprobó ni subió el episodio**.
- Migración 0016 aplicada con tres sentencias success, trabajo anterior preservado, claves foráneas sin infracciones. La cola muestra el video con título, descripción/capítulos/fuentes preparados y origen Codex de desarrollo. El canal Factor de Gigantes está realmente conectado. El propietario puede revisar el archivo y sus derechos, guardar su aprobación y solicitar «Subir como privado» como acción independiente.
- La transferencia Google está implementada y probada con respuestas simuladas; **primera subida real pendiente de revisión y autorización del propietario**. No se declara ya probada en Google ni se publica contenido para validarla. El equipo investigador permanece pausado y la aceptación profesional del episodio sigue pendiente. El proyecto completo no se marca terminado.
