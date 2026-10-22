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

Gemini/Groq mantienen sus límites D1 de cuatro solicitudes diarias y cien
mensuales, además de una generación por proveedor y ejecución. Guion e
investigación se reanudan en ejecuciones separadas; comparten el presupuesto
diario. La falta de cuota o configuración produce un bloqueo explícito.

El borrador no marca hechos aprobados, no sustituye la voz canónica, no
autoriza recursos visuales ni música, y no llama al renderizador. La aprobación
editorial y los derechos deben resolverse antes de producir el MP4; la
publicación en YouTube continúa requiriendo autorización humana explícita.
