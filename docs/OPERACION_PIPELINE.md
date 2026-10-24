# Operación del pipeline de Factor de Gigantes

El workflow `FDG - radar diario empresas y noticias` separa investigación,
revisión, guion y comprobación de perfil en `main`.
La selección del episodio sigue procediendo de señales observadas y de D1.
No es necesario proporcionar fuentes o escribir un episodio manualmente.

## Investigación y continuación

La fase predeterminada `research` mantiene el radar diario y la ejecución manual.
Si un lote Wikidata supera el límite de cinco MB, se divide sin elevar ese
límite; cada intento fallido consume también el máximo de consultas. Una
entidad individual demasiado grande se omite y se registra; la cobertura
pendiente queda explícita. Las respuestas se filtran al sitelink del idioma
solicitado para evitar traer cientos de enlaces ajenos a esa clasificación.
Recupera de cinco expedientes de la misma entidad las URL intentadas, hasta
ocho afirmaciones pendientes y cuatro pasajes históricos. Conserva hasta 40 URL
de historial; el límite por corrida continúa siendo ocho descargas documentales.

Los artículos pueden aportar enlaces originales de autoridades. Cada descarga
de esas referencias consume el mismo presupuesto, conserva su procedencia y
pasa por validación HTTPS, DNS y redirecciones. Una URL o un titular nunca se
convierte en prueba de un hecho. Se permite revisar hasta dos artículos ya
citados para extraer referencias que antes no se habían registrado; esa lectura
por sí sola no habilita otra inferencia, aunque cambie el HTML dinámico.

La matriz distingue requisitos de fuentes por afirmación. Los hechos legales
exigen respaldo regulatorio candidato; otros hechos pueden apoyarse en
documentación corporativa original y contraste independiente. Ninguna de esas
condiciones constituye verificación factual automática ni concede aprobación.

La continuación prioriza los vacíos regulatorios y después los originales
primarios. Mantiene dos consultas básicas por buscador: la primera puede
restringirse a las autoridades registradas en `src/regulatory-authorities.json`;
la segunda excluye el emisor ya citado para buscar contraste. Ese registro no
es exhaustivo ni acredita jurisdicción o independencia editorial. Los filtros
no activan Exa ni cambian cuotas o facturación. Tavily documenta esos parámetros
en su [SDK oficial](https://github.com/tavily-ai/tavily-python/blob/main/tavily/tavily.py).

El lector elige hasta tres pasajes por documento según los hechos pendientes,
con ventanas literales de hasta 320 caracteres y página/bloque originales.
Puede usar contexto de los dos bloques anteriores de la misma página; conserva
ese contexto como cita aparte y no cruza páginas PDF para asignar entidad.
La coincidencia de palabras o cifras es recuperación, nunca verificación.

Los informes guardan el plan de búsqueda y un diagnóstico de fuentes, pasajes,
afirmaciones, revisión y vacíos. El resumen usa campos públicos seleccionados,
sin variables de entorno, credenciales ni cuerpos de errores remotos. Queda
en el artefacto y en la línea `INVESTIGACION_DIAGNOSTICO` de Actions para poder
explicar un bloqueo incluso si no hay acceso administrativo directo a D1.

Las referencias regulatorias también se extraen de anotaciones PDF Link/URI
y de URLs HTTPS literales en los bloques leídos, con página de procedencia.
No se ejecutan acciones del PDF, no se convierten enlaces HTTP en HTTPS y no
se adivinan rutas. Máximo doce referencias por documento; todas las descargas
siguen contando dentro de ocho. Se permite una segunda URL observada de una
autoridad registrada sólo si la primera no dio pasajes relevantes, sin superar
cinco intentos de categoría primaria ni dos del mismo hostname. Una lectura
útil cierra nuevos intentos del mismo hostname en ese ciclo.

El lector separa bibliografías con varias URLs de los pasajes factuales. El
plan documental exige también contenidos con hashes distintos: un PDF idéntico
en dos dominios no equivale a dos originales. Hashes distintos tampoco prueban
independencia editorial o respaldo semántico; esa revisión continúa pendiente.

## Guionista reanudable

### Revisión independiente por pasaje

La fase `review`, con `research_run_id=latest` o un ID activo, reutiliza el
contexto D1 por el mismo OIDC restringido. Hace como máximo una llamada Groq
con modalidad gratuita y reserva D1; no repite radar, búsquedas, Qwen ni Gemini.
Si ese expediente ya contiene el contrato vigente `per_excerpt_support_v2`, se omite
sin nueva reserva ni escritura. Un bloqueo de cuota/proveedor se conserva.

El sistema fija qué pasajes debe comparar Groq, buscando alternativas de otros
dominios/documentos por coincidencias textuales y de fechas. Ese orden es sólo
recuperación de candidatos. Una respuesta que omite comparaciones se rechaza.
Sólo se incorporan pasajes evaluados como apoyo completo, con matriz consistente
y conservando las citas iniciales. Los pasajes insuficientes quedan evaluados
sin convertirse en apoyo; una contradicción impide ampliar. El texto no cambia y las citas del
analizador quedan en `analysis_evidence_ids` y la matriz se recalcula. Una
contradicción, contexto insuficiente o revisión histórica sin matriz no amplía
citas. Esto es apoyo candidato evaluado por IA, nunca verificación humana.

Se conserva el cálculo antes de intentar persistir, y el recibo confirma el
nuevo expediente sin modificar el original. La fecha original de los documentos
se mantiene; la revisión registra su propia fecha y el hash de procedencia.
Sólo si el blueprint pasa su puerta se encadena el guionista. El artefacto
`fdg-revision-reanudable` conserva el informe o bloqueo durante cinco días.

### Redacción del borrador

Cuando la investigación supera la puerta documental, el workflow encadena
automáticamente una ejecución independiente de guion con el identificador
exacto confirmado por D1. Esta conexión queda pendiente de aceptación con un
dossier real suficiente; una prueba con un dossier bloqueado no la acredita.

En GitHub Actions, ejecutar el mismo workflow con `phase=script` y
`research_run_id=latest` (o el identificador `ai-...` de un expediente activo).
También existe una puerta de prueba en `Comprobar base`, con `run_script=true`.
Se recupera el contexto de D1 mediante OIDC del workflow exacto en `main`;
no se transmite el token administrativo al runner. Los expedientes cerrados,
ajenos o demasiado antiguos no se utilizan.

Esta fase no ejecuta el radar, ni descarga Qwen, ni repite el análisis factual.
Recalcula la puerta documental antes de reservar IA. Si faltan citas, revisión,
fuentes primarias o contraste, genera un informe de bloqueo sin narración.
Si el dossier supera esa puerta, hace una sola generación con un proveedor
gratuito confirmado y cuota D1 disponible. No hay reintentos automáticos.

El borrador debe cubrir el plan de escenas, citar afirmaciones y evidencias
existentes en cada párrafo y alcanzar una duración estimada de 8–14 minutos
a 138 palabras por minuto. La duración es una estimación de texto, no prueba
de una pista de audio. La veracidad y la calidad editorial requieren revisión.

El resultado se conserva como `GUION_DOCUMENTAL_NO_APROBADO.json` en el
artefacto `fdg-guion-documental-revision`, con retención de cinco días.
No se acredita la calidad de un documental real por pasar pruebas con fixtures.

### Del borrador a las tareas de producción

La misma fase `script` prepara `PLAN_PRODUCCION_NO_APROBADO.json` mediante
`tools/documentary_production_plan.py`. Si la investigación impide escribir
el guion, conserva ese bloqueo y deja cero escenas y cero tomas planificadas.
Para un borrador válido prepara tomas de hasta 260 caracteres y solicitudes
de recursos visuales por párrafo, con los identificadores de hechos y citas.
Los cortes conservan todos los caracteres, posiciones y hashes del texto;
el paquete queda ligado al hash del guion y del expediente investigador.

La referencia exigida procede de `tools/approved_voice.py`. Registrar su hash
no acredita que se haya inspeccionado el MP3 en esa ejecución ni su licencia.
No se carga Qwen-TTS ni se descargan imágenes; los recursos siguen pendientes
y no hay audio nuevo. Antes de ejecutar las tareas se requieren revisión
factual, derechos de voz y visuales y aprobación humana de render. Las
duraciones siguen siendo estimaciones hasta disponer de audio real.

```sh
python -m tools.documentary_production_plan \
  --script dist/script/GUION_DOCUMENTAL_NO_APROBADO.json \
  --out dist/script/PLAN_PRODUCCION_NO_APROBADO.json
```

## Cuotas y producción

El propietario confirmó el 2026-10-22 que PAYGO de Tavily está desactivado.
El workflow habilita sus búsquedas básicas con un máximo de dos por ejecución,
ocho al día y doscientas al mes mediante reservas D1. Un valor explícito `0`
en `TAVILY_RESEARCH_FREE_CONFIRMED` mantiene el servicio apagado.
Antes de buscar se consulta el plan: debe ser Researcher/Free, con límite de
mil créditos, consumo PAYGO cero y al menos dos créditos disponibles. Si
`paygo_limit` es nulo, se conserva ese valor y se registra la confirmación
del propietario; no se presenta como comprobación de facturación por API.
Un límite PAYGO positivo, plan pagado o perfil ilegible bloquean Tavily.
Exa permanece sin habilitar.

Gemini/Groq mantienen sus límites D1 de cuatro solicitudes diarias y cien
mensuales, además de una generación por proveedor y ejecución. Guion e
investigación se reanudan en ejecuciones separadas; comparten el presupuesto
diario. La falta de cuota o configuración produce un bloqueo explícito.

El borrador no marca hechos aprobados, no sustituye la voz canónica, no
autoriza recursos visuales ni música, y no llama al renderizador. La aprobación
editorial y los derechos deben resolverse antes de producir el MP4; la
publicación en YouTube continúa requiriendo autorización humana explícita.

## Calidad del archivo audiovisual

El control local `tools/av_quality.py` inspecciona y decodifica el MP4 real
antes de reportar un render como listo. Detecta problemas de pistas,
duración, congelamiento, negro y silencio prolongado. Es independiente de
las cuotas del investigador y mantiene separadas calidad técnica, revisión
editorial, identidad vocal y licencias. Perfiles, límites y operación en
[QA_AUDIOVISUAL.md](QA_AUDIOVISUAL.md).
