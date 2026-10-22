# Operación del pipeline de Factor de Gigantes

El workflow `FDG - radar diario empresas y noticias` tiene dos fases en `main`.
La selección del episodio sigue procediendo de señales observadas y de D1.
No es necesario proporcionar fuentes o escribir un episodio manualmente.

## Investigación y continuación

La fase predeterminada `research` mantiene el radar diario y la ejecución manual.
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

## Guionista reanudable

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
