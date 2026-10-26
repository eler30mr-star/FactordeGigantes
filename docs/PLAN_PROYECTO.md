# Plan maestro — Factor de Gigantes

> **Dirección vigente del propietario — 2026-10-25.** Este bloque define el producto y el orden de trabajo. Prevalece sobre prioridades, secuencias y propuestas incompatibles del historial conservado al final y de los documentos técnicos anteriores. Los hitos históricos acreditan componentes, no la aceptación del sistema completo. Se mantienen las reglas de seguridad, veracidad, licencias, voz canónica, cero pagos y trabajo exclusivo en `main`.

**Corrección del propietario — 2026-10-26:** primero elegir un tema y una empresa según las políticas ya implementadas; después investigar únicamente lo necesario para ese video. Se retira la aceptación de empresa fija BlackBerry y no se presenta como selección del mercado ni como encargo del propietario. Las pruebas de contratos se ejecutan sin APIs reales. Una prueba integrada con proveedores debe recorrer una selección real y trazable del estudio o del chat.

## 1. Objetivo del producto

Construir un **sistema de automatización de producción y publicación del canal de YouTube Factor de Gigantes**, con IA y supervisión del propietario. El resultado operativo es un video del canal que avanza desde una elección editorial hasta su reproducción en el panel y su publicación autorizada.

El nicho del canal ya está definido: empresas, tecnología, innovación, modelos de negocio y decisiones que cambiaron su trayectoria; contenido original en español latinoamericano. La identidad documental, la voz canónica y el formato principal de 8–14 minutos se conservan. No volver a pedir al propietario que defina el nicho en cada ciclo.

La unidad de trabajo es **un episodio con un tema, una empresa y un enfoque elegidos**. El volumen de compañías almacenadas, fuentes recogidas o llamadas a IA no mide el éxito del producto.

## 2. Dos formas de iniciar el mismo episodio

### Modo automático: búsqueda y selección del día

1. En el ciclo diario, buscar oportunidades recientes **en YouTube**, dentro del nicho y del público del canal.
2. Las IA comparan un conjunto acotado de candidatos con señales observadas: videos, fechas, evolución cuando haya observaciones comparables, visitas, rendimiento relativo y competencia temática. Considerar el historial propio para evitar repeticiones.
3. Elegir **un tema y una empresa**, con una pregunta/enfoque para el video, y registrar brevemente por qué conviene producirlo ese día.
4. Solo después de persistir esa selección, comenzar la investigación factual y documental del episodio.

Esta búsqueda busca potencial de viralización en YouTube; no promete viralidad. Wikipedia, Wikidata, RSS y noticias pueden aportar contexto o desambiguación, pero no sustituyen la búsqueda en YouTube ni sus señales. No atribuir a muestras públicas CTR, retención ni crecimiento que no se haya medido. Si faltan señales suficientes, mostrar el motivo y permitir reintento o elección por chat; no inventar un ganador ni investigar indiscriminadamente todas las opciones.

El ciclo diario define la oportunidad del día; no impone publicar un video incompleto por cumplir una fecha. La duración real de producción, los límites gratuitos y las aprobaciones siguen siendo visibles.

### Estudio de mercado obligatorio antes de elegir

La IA debe realizar un estudio suficiente para justificar la elección; no elegir por completar el ciclo ni por el primer resultado. El presupuesto acotado evita gasto indiscriminado, pero no permite llamar «estudio de mercado» a una muestra insuficiente.

- Buscar con varias consultas del nicho y del enfoque, comparar alternativas de tema y empresa, y registrar consultas, fechas, videos y canales observados. Declarar cobertura, antigüedad y límites de la muestra.
- Evaluar afinidad con el público hispanohablante, actualidad, interés sostenido o emergente, competencia y saturación, ángulo diferenciador y antecedentes del canal. Separar Shorts de videos largos y comparar duraciones y edades semejantes.
- Contextualizar las visitas por edad del video y rendimiento habitual del canal cuando haya datos suficientes. No equiparar el éxito de un canal grande con una oportunidad para este canal ni decidir por visitas absolutas, una noticia o un único video excepcional.
- Medir evolución solo con observaciones fechadas comparables; visitas divididas por días es un promedio, no crecimiento demostrado. Identificar datos faltantes y no inventar demanda, CTR o retención de terceros.
- Comparar candidatos mediante criterios y ponderaciones documentados y versionados, calidad de evidencia e incertidumbre. Antes de activar el selector, definir y validar mínimos de cobertura, frescura y suficiencia con muestras reales; no ajustar umbrales para forzar un ganador.
- Entregar una decisión explicable: tema, empresa, enfoque, oportunidad detectada, evidencia enlazada, comparación con alternativas, motivos de descarte y límites. El panel muestra un resumen y permite abrir el detalle.
- Si la evidencia no alcanza los mínimos, registrar **«sin selección: estudio insuficiente»**, explicar qué falta y esperar nueva búsqueda o instrucción del propietario. Solo el ganador habilita investigación profunda.

**Aceptación:** una revisión de muestras reales debe poder reconstruir por qué se eligió ese episodio frente a alternativas. Las pruebas cubren muestra insuficiente, datos caducados, duplicados, sesgo por tamaño de canal y ausencia de tendencia medida; todos deben impedir conclusiones no sustentadas.

### Botón del panel: Automático encendido / apagado

El propietario controla un botón visible con estado inequívoco **«Automático: encendido» / «Automático: apagado»**, persistido en el servidor por canal y conservado al recargar.

- **Encendido:** habilita el ciclo diario de búsqueda, estudio de mercado y selección por IA dentro del nicho. No garantiza un ganador cuando el estudio sea insuficiente.
- **Apagado:** no se inician nuevas búsquedas de oportunidades, estudios ni selecciones automáticas, tampoco desde cron, tareas en cola o reintentos. El sistema espera los temas y empresas que el propietario indique por chat.
- Apagado no desactiva los investigadores ni la producción de episodios pedidos por el propietario: estos recorren investigación → video → revisión y publicación autorizada con las mismas IA.
- Al apagar durante una búsqueda, cancelar o descartar su resultado automático antes de crear un episodio. Un episodio ya seleccionado/en producción se conserva y se muestra como tal; el botón no lo borra ni cancela silenciosamente.
- Verificar el modo en el servidor al iniciar la búsqueda y antes de confirmar una selección; cubrir carreras con el apagado e impedir que una tarea antigua lo reactive.
- Confirmar al usuario el estado realmente guardado; si falla el cambio, mostrar el error sin aparentar otro modo. Configuración ausente implica apagado hasta activación expresa. Registrar quién cambió el modo y cuándo.
- El modo automático no concede autorización de publicación ni elimina presupuestos, derechos o revisiones vigentes. Su implementación futura no levanta por sí sola la pausa de investigadores existente.

**Aceptación:** tras apagar y recargar, cron/colas no generan búsquedas ni episodios automáticos; una instrucción válida por chat sí crea el episodio dirigido. Al encender se recupera el ciclo sin duplicados. Probar también apagado concurrente con la selección y fallos al guardar.

### Modo dirigido: chat del propietario

El panel debe tener **un chat operativo** para indicar tema y empresa, por ejemplo: «Haz un video sobre BlackBerry y por qué perdió el mercado».

- Interpretar la instrucción, mostrar tema, empresa y enfoque entendidos, y crear o dirigir el episodio correspondiente.
- Si la instrucción es suficiente, pasar a investigación del tema elegido sin exigir selección por radar ni formularios de fuentes, guion o JSON.
- Pedir una aclaración breve solo si falta información imprescindible; no cambiar la empresa o el enfoque en silencio.
- La selección explícita del propietario sustituye la búsqueda automática de ese episodio. Guardar origen `chat` o `automático`, instrucción y decisión.
- Si hay un episodio en curso, mostrar el efecto de una nueva instrucción y conservar su trabajo; no iniciar producciones duplicadas ni descartar material silenciosamente.
- El chat da instrucciones al sistema real y muestra su ejecución; no debe limitarse a responder texto sin crear o actualizar el episodio.

## 3. Flujo obligatorio después de seleccionar

**Búsqueda YouTube → selección de tema y empresa**, o **instrucción por chat → selección del propietario**.

Ambas entradas convergen en:

**Investigación del elegido → guion → narración y escenas → montaje y QA → video reproducible en el panel → revisión/aprobación → subida y publicación/programación autorizadas → resultados del canal.**

- El investigador busca exclusivamente la información necesaria para la pregunta y las escenas del episodio seleccionado. Puede investigar otras empresas cuando sean parte necesaria de esa explicación, sin abrir expedientes independientes de cada candidata.
- Las IA obtienen fuentes, contrastan afirmaciones y redactan el guion. El propietario supervisa; no tiene que investigar o escribir cada episodio ni depender de Codex como productor recurrente.
- La selección de oportunidad no exige tener antes un expediente factual completo. El contraste de hechos pertenece a la investigación posterior y debe completarse antes de usar afirmaciones en el video.
- Los módulos de voz, visuales, montaje y QA reciben el mismo episodio y conservan trazabilidad. Reintentar desde el fallo sin repetir búsqueda, investigación o tomas ya válidas.
- Mantener los controles editoriales y de derechos existentes, incluida la autorización de render donde corresponda. La autorización de publicación es una acción explícita: elegir por chat, conectar OAuth, aprobar un guion o superar QA no la concede.
- La publicación/programación es parte del objetivo final del producto. La entrega actual de subida privada es un componente intermedio, no el cierre del proyecto.
- La analítica propia retroalimenta futuras decisiones cuando esté disponible y autorizada. No presentar métricas ajenas como resultados del canal.

## 4. Qué debe mostrar el panel

La portada debe responder: **qué video se está haciendo, por qué se eligió, en qué etapa está y cuál es la siguiente acción**.

1. Episodio actual: tema, empresa, enfoque, origen de la elección y motivo resumido.
2. Botón persistente «Automático: encendido/apagado» y chat para dar instrucciones de tema y empresa. Apagado, se espera la elección del propietario.
3. Avance comprensible: investigación, guion, voz, montaje, revisión y publicación; bloqueo concreto y posibilidad de reanudar cuando proceda.
4. **Reproductor de video dentro del panel**, con audio, pausa y desplazamiento, vinculado al MP4 real de ese episodio. La descarga o un enlace a GitHub Actions no reemplazan este requisito.
5. Revisión y acciones autorizadas de subida/publicación/programación, con estado y enlace YouTube cuando exista.
6. Historial de episodios en un apartado secundario. Fuentes, citas, logs, comparativas y diagnósticos accesibles bajo demanda y asociados al episodio.

Resolver entrega autenticada del MP4, permisos, reproducción parcial y conservación suficiente para la revisión. Mostrar disponibilidad y caducidad reales y un error recuperable cuando falte el archivo. No mostrar un montaje técnico como video final aceptado.

## 5. Límites que corrigen el desvío

- No investigar, extraer PDFs o armar expedientes de todas las empresas antes de elegir el episodio.
- No desarrollar una enciclopedia de empresas ni un catálogo de monografías como objetivo operativo.
- No usar acumulación de titulares, visitas Wikimedia o entidades como sustituto de una decisión editorial basada en YouTube.
- No convertir el panel principal en un listado simultáneo de todas las etapas, candidatos y datos históricos.
- La comparación previa puede conservar una evidencia mínima y acotada para explicar la selección; la investigación profunda queda vinculada al ganador.
- Preservar registros anteriores como historial. Revisar las tareas programadas al implementar el nuevo flujo para retirar la recolección indiscriminada; esta actualización documental no borra datos ni modifica cron.
- Reutilizar módulos útiles. No reiniciar el proyecto ni regenerar el episodio de desarrollo para simular cumplimiento.

## 6. Prioridades de implementación y aceptación

## Estado verificado al 2026-10-26

| Bloque | Implementación comprobada | Aceptación pendiente |
| --- | --- | --- |
| P0 | Modo persistente, chat, episodio único, reservas, estudio YouTube y conexión a investigación del elegido | Calibrar cobertura real; todavía ninguna selección automática validada |
| P1 | Panel con seis etapas y acciones del episodio, lectura/revisión del guion, reproductor vinculado por SHA/run y extracción del MP4 real verificados | Revisión humana en navegador de audio, desplazamiento y experiencia completa |
| P2 | Conexión episodio → investigación → guion y registro del video; reanudación diferenciada de análisis, contraste, revisión y guion desde resultados guardados; cierre por publicación confirmada implementado | La prueba fija queda archivada; aceptar el recorrido de un episodio elegido por estudio o chat, desde selección hasta video |
| P3 | Subida privada y autorización separada de publicación/programación implementadas | Consentimiento Google ampliado y primera publicación/programación autorizadas |

La [aceptación real del mercado](ACEPTACION_MERCADO_REAL.md) ejecutó YouTube y Gemini y confirmó una muestra insuficiente: no se eligió una empresa ni se habilitó el selector. Las casillas de aceptación integral continúan abiertas; este estado distingue implementación de cierre operativo.


Todo lo siguiente queda **pendiente de implementación o validación integral**, salvo componentes acreditados en AVANCE. Una casilla histórica completada no completa estos criterios nuevos.

### P0 — Corregir la entrada y el orden de ejecución

- [x] Implementar el botón de modo persistente y su control efectivo en servidor, cron y colas; apagado permite solo episodios dirigidos por el propietario.
- [ ] Definir y validar criterios de estudio de mercado, mínimos de suficiencia y decisión comparativa explicable; no elegir si faltan evidencias.
- [x] Modelar el ciclo diario y el episodio único con tema, empresa, enfoque, origen, decisión y estado persistentes.
- [ ] Hacer que el descubrimiento comience por búsqueda YouTube del nicho; comparar candidatos de forma acotada y seleccionar uno antes de disparar investigación.
- [x] Impedir investigación profunda de candidatos no seleccionados y revisar los cron/colectores existentes.
- [x] Implementar chat conectado al orquestador para elegir tema y empresa sin radar obligatorio.
- [x] Evitar duplicados en el ciclo, doble envío del chat y reintentos; una nueva instrucción no destruye un episodio en curso.

**Aceptación:** con proveedores simulados, comprobar ambos recorridos y el orden de llamadas; ningún investigador profundo se invoca antes de existir una selección ni para candidatos descartados. Validar después búsqueda real y decisión explicada, respetando la pausa vigente de investigadores hasta habilitación expresa.

### P1 — Panel centrado en el video

- [x] Presentar episodio actual, botón automático encendido/apagado, chat, avance, bloqueo y siguiente acción como vista principal; permitir consultar el estudio que sustenta la selección.
- [ ] Entregar y reproducir el MP4 real dentro del panel autenticado; probar audio, desplazamiento, permisos y caducidad.
- [x] Relegar datos técnicos, fuentes e historial a vistas secundarias asociadas al episodio.

**Aceptación:** el propietario puede indicar una empresa y tema por chat, seguir el episodio y ver el video en el panel sin preparar investigación, guion ni descargar un ZIP para reproducirlo.

### P2 — Integrar las IA y cerrar producción

- [ ] Unir selección → investigación enfocada → guion → voz canónica → escenas → MP4 y QA bajo la misma identidad de episodio.
- [ ] Reanudar desde fallos conservando fuentes y resultados válidos; respetar presupuestos gratuitos y controles editoriales.
- [ ] Validar un episodio automático y uno dirigido por chat; distinguir pruebas simuladas, ejecución real y aprobación humana.

**Aceptación:** producción por el propio sistema, sin que Codex suministre manualmente fuentes o prosa para acreditar autonomía; video real reproducible y evidencias suficientes para revisión.

### P3 — Publicación del canal y aprendizaje

- [x] Integrar metadatos, subtítulos, revisión, subida y publicación/programación con OAuth del canal y autorización explícita. Código y contratos implementados; primer recorrido real de publicación pendiente.
- [ ] Confirmar resultado en YouTube, evitar duplicados y mostrar errores recuperables.
- [ ] Incorporar resultados propios del canal a futuras búsquedas cuando exista acceso.

**Aceptación final:** los dos modos de inicio llegan al mismo flujo; el propietario ve y revisa el video en el panel y el sistema publica/programa el episodio autorizado en el canal correcto. Una subida privada de prueba no acredita por sí sola publicación completa.

## 7. Estado y reglas de continuidad

La infraestructura existente —Worker, D1, proveedores IA, narrador, montaje, OAuth y subidor privado— se reutiliza según su estado verificado en [AVANCE.md](AVANCE.md). Hay un episodio narrado de desarrollo registrado, no una demostración del nuevo flujo autónomo. El modo persistente, el chat de selección y el reproductor embebido están implementados. El reproductor se desplegó y verificó con el MP4 real; su aceptación auditiva y visual humana sigue pendiente. El estudio YouTube v2 conserva una puerta de calibración; el episodio elegido por chat o estudio ya conecta con investigación enfocada y guion editorial trazable, y reutiliza la aprobación/render canónico existentes. La aceptación real con proveedores y del recorrido completo sigue pendiente. Avance/descarga por sí solos no equivalen a reproducción.

La pausa de investigadores registrada previamente se conserva. La conexión implementada no levanta por sí sola la pausa ni concede autorización de publicación. Se mantienen cero pagos, voz canónica, fuentes verificables, recursos con derechos, secretos protegidos y `main` exclusiva.

**Siguiente bloque de desarrollo:** validar el estudio y la selección única de P0 con las políticas vigentes; después enlazar ese episodio persistido con investigación enfocada → guion → aprobación → render y registro del MP4. Aceptar ambos inicios. La prueba fija de BlackBerry queda archivada y no debe retomarse como sustituto de selección real. El runner ya puede avanzar hasta tres rondas persistidas, sin repetir fallos de cuota; un análisis pendiente no reemplaza los candidatos anteriores ni permite crear un borrador. La publicación/programación autorizada ya tiene código y pruebas con Google simulado; aceptar su primer recorrido real tras consentimiento ampliado, revisión del video y autorización. El control, el reproductor y el estudio v2 ya tienen código y pruebas; no ampliar el radar antiguo. Registrar separadamente código, pruebas, despliegue y aceptación real.

## Anexo — Plan e hitos anteriores, conservados como historial

Las prioridades y los textos de estado dentro de este anexo reflejan decisiones pasadas. Ante incompatibilidad, rige la dirección del propietario y las prioridades P0–P3 de arriba. Los documentos técnicos enlazados se deben adecuar durante la implementación y no pueden reintroducir investigación masiva previa.

<details>
<summary>Consultar plan anterior e historial técnico (2026-10-20 a 2026-10-25)</summary>

## Plan anterior — registro histórico

> **Aceptación técnica 2026-10-25:** primera exportación de desarrollo completa **con narración real**, 11:11 y 56 tomas canónicas, workflow `40163555937` success y MP4 descargado/verificado. Panel con avance/descargas y conexión OAuth desplegados; cliente Google/consentimiento pendientes del propietario. Se mantiene revisión humana, licencia comercial y calidad profesional pendientes; la investigación de prueba fue preparada por Codex. Próximo bloque: subidor privado con autorización por episodio y aceptación integrada de investigadores cuando corresponda. Estado actual y enlaces en [`AVANCE.md`](AVANCE.md).

> **Motor integrado 2026-10-25:** implementado montaje genérico con narrador canónico CPU reanudable, fuentes por párrafo, gráficos por escena, subtítulos, exportación y QA. Montaje técnico completo de 11:36 aprobado en Actions `40163254722` (señal técnica, sin locución). Panel y Worker desplegados; CI corregido aprobado. Investigación manual y programada pausadas por el propietario. Prueba final canónica `40163555937` en ejecución al registrar; no acredita todavía documental narrado aceptado, calidad profesional ni OAuth/publicación. Operación en [`PRODUCCION_EPISODIOS.md`](PRODUCCION_EPISODIOS.md), aceptación en AVANCE.

> **Dirección del propietario 2026-10-24 (prevalece sobre la secuencia de pruebas anterior):** Codex realizará directamente las investigaciones y búsquedas necesarias para preparar datos y guiones de prueba. Se posponen las pruebas de Gemini/Groq/Tavily/Exa/Qwen hasta la versión final de prueba integrada. Prioridad: terminar el motor genérico de producción y demostrar montaje completo con datos de desarrollo; esos materiales no se presentarán como producción autónoma de las IA. El workflow de proveedores queda cerrado por `FINAL_AI_INTEGRATION_ENABLED` (por defecto desactivado). Se conserva la voz canónica y la publicación sigue bloqueada.

> **Continuación factual 2026-10-24 (ejecución real persistida):** nueva fase `corroborate` amplía fuentes y reanuda revisión desde D1, sin repetir radar/Qwen/Gemini. Conserva citas activas y guarda lecturas nuevas aunque Groq no tenga cuota. Programada a las 00:40 UTC, con los mismos límites. Ejecución 40134078185 guardó cuatro pasajes nuevos sin repetir investigadores; revisión Groq pendiente de cuota. Se conserva ese material y se priorizan enlaces documentales frente a menús. El dossier real todavía requiere corroboración y hechos suficientes; aceptación detallada al final de AVANCE.
> **Integración editorial 2026-10-24 (Worker/migración desplegados y guardas OIDC probadas):** el guionista conserva la identidad D1 y una huella de sus evidencias; una importación OIDC reanudable crea trabajo y expediente pendientes sin duplicados ni sobrescribir revisión humana. Migración aditiva 0014. El renderizador de previsualización queda cerrado para estos trabajos, hasta integrar voz canónica y recursos de escena. Revisión automática a las 00:20 UTC, sin repetir el radar de las 10:17 UTC. CI 40133300880 y prueba real 40133322890 exitosas: el expediente insuficiente fue rechazado sin crear trabajos. La importación positiva de un episodio real sigue pendiente de fuentes suficientes. Detalles al final de AVANCE.
> **Estado verificado 2026-10-24:** se recuperó el radar tras un lote Wikidata demasiado grande; la ejecución completa `40130358108` detectó seis compañías y mantuvo doce consultas. El dossier de Theranos contiene seis documentos y dos dominios primarios candidatos. La revisión reanudable evalúa pasajes alternativos sin repetir investigación; una acusación de junio de 2018 tiene apoyo candidato de original y fuente independiente. La revisión sigue sin verificar hechos automáticamente: faltan contraste de otros hechos, guion real aceptable, voz/visuales con derechos y MP4 de 8–14 minutos. Cambios, incidencias y aceptación se registran en `AVANCE.md`; los estados anteriores son históricos.

> **Estado operativo actualizado 2026-10-22:** radar YouTube, selección D1 e integración Qwen/Gemini/Groq probados en ejecución real `39849511998`. Worker administrado también por Wrangler autenticado. La investigación conserva objetivos pendientes y sigue referencias originales con presupuesto acotado. Se incorpora un guionista reanudable desde D1 para borradores citados de 8–14 minutos, con pruebas de contrato; su ejecución real y la aceptación documental se registran en `AVANCE.md`. El dossier actual de Theranos todavía no supera el contraste: no se acredita documental final ni autorización de render/publicación. Los bloques anteriores de este plan conservan hitos históricos.

> **Equipo IA 2026-10-22:** se implementa descubrimiento Tavily/Exa + documentos públicos, extracción Qwen, análisis Gemini, alternativas Mistral/OpenRouter, revisión Groq y clasificación Cloudflare. Las APIs requieren claves y modalidad gratuita confirmada; el propietario solo confirmó la clave YouTube. Cuotas persistentes D1 en migración 0013. Código/pruebas no acreditan activación de cuentas ni documental final. Configuración y funciones: [`CONFIGURACION_EQUIPO_IA.md`](CONFIGURACION_EQUIPO_IA.md); aceptación real en AVANCE.

> **Estado de implementación 2026-10-22:** se conecta el investigador Qwen de texto local al radar como alternativa sin clave Gemini, y se amplía recuperación de informes y contexto con varios fragmentos. Esta entrega debe validarse con ejecución real y persistencia D1; no acredita todavía selección de mercado YouTube, contraste factual ni documental autónomo completo. Detalles y resultados en `docs/AVANCE.md`.

> **Actualización posterior 2026-10-22:** clave YouTube probada en Actions y primer estudio persistido (cuatro muestras, cuarenta observaciones). Se incorpora una cola de **investigación** calculada desde muestras públicas y ventanas Wikimedia. La selección inicia búsqueda/contraste; no exige que los hechos ya estén aprobados antes de investigarlos y tampoco acredita guion, render o publicación. Mantener separadas estas puertas. Aceptación E2E y bloqueos en `docs/AVANCE.md`.

> **META FINAL INNEGOCIABLE — ACTUALIZACIÓN 2026-10-21:** Factor de Gigantes debe **estudiar el mercado, descubrir y clasificar autónomamente los mejores temas**, y convertir el seleccionado en un documental profesional, sin depender de que ChatGPT ni el propietario investiguen, escojan manualmente el tema, escriban el guion o monten cada episodio. El propio sistema descubrirá y contrastará fuentes, redactará, narrará con voz autorizada, construirá escenas y exportará MP4 de 8–14 minutos. El propietario supervisa/aprueba. YouTube queda sujeto a autorización humana. **Prioridad inmediata: radar de mercado con estadísticas observadas y selección propia, seguido de un investigador independiente con Gemini API gratuita o Qwen LLM local** (el Qwen-TTS de voz es otro componente). Arquitectura y aceptación en [`docs/ARQUITECTURA_AUTONOMA.md`](ARQUITECTURA_AUTONOMA.md). Este objetivo prevalece sobre seguir redactando BlackBerry a mano.


**Fecha inicial:** 2026-10-20 · **Repositorio:** `eler30mr-star/FactordeGigantes` · **rama:** `main`

## 1. Propósito y meta final

Crear y operar una productora documental autónoma con supervisión editorial y propia para el canal **Factor de Gigantes** (`@FactordeGigantes`), enfocada en grandes compañías, inventos, tecnología, modelos de negocio, decisiones decisivas y sus consecuencias. El objetivo de negocio es construir una audiencia sostenida y eventualmente solicitar monetización, **sin prometer resultados ni ingresos**.

El sistema debe permitir gestionar varios proyectos editoriales y, en un futuro, varios canales, con controles por cuenta y trazabilidad. Primero validar un canal y su calidad.

## 2. Identidad editorial

- Idioma: español latinoamericano comprensible internacionalmente.
- Estilo: documentales investigados, cinematográficos y accesibles.
- Promesa: descubrir el factor detrás de una gran transformación.
- Eslogan: *Las decisiones que cambiaron el mundo*.
- Formatos: documental 8–14 minutos (principal); Short 30–60 segundos (complementario).
- Cadencia orientativa al madurar: dos documentales y varios Shorts semanales, limitada por calidad/coste.
- Identidad visual: negro/charcoal, oro, elementos industriales y tecnológicos; no usar metraje ajeno sin derechos.

## 3. Reglas editoriales innegociables

1. Cada video parte de una pregunta o tesis específica, no de un guion genérico reescrito.
2. Investigación original con fuentes públicas comprobables. Registrar URL, fecha, atribución y afirmaciones a verificar.
3. Evitar datos inventados, exageraciones y acusaciones no sustentadas.
4. Licencias verificadas de música, imágenes, voces y video. No reutilizar videos de terceros para eludir copyright.
5. Separar claramente visualizaciones recreadas con IA de grabaciones reales cuando corresponda; respetar declaraciones de contenido sintético de YouTube.
6. Un humano autoriza antes de renderizar y de publicar. Nunca generar o publicar en masa sin revisión.
7. Guardar documentación editorial y técnica, sin exponer claves o datos personales.
8. Consultar las políticas vigentes de monetización de YouTube para contenido reutilizado e inauténtico antes de cada lanzamiento.

## 4. Arquitectura y componentes

### Plano de control (Cloudflare)

- Cloudflare Worker sirve API administrativa y archivos estáticos del panel.
- D1 guarda proyectos, guiones aprobados, estado y registro de cambios.
- `ADMIN_TOKEN` protege la API desde el panel en MVP; no persistir token en navegador.
- `RENDERER_TOKEN` protege rutas para el runner.
- `GITHUB_DISPATCH_TOKEN` permite al Worker solicitar una acción `workflow_dispatch`.
- Control de transición de estados: `draft → review → approved → queued → rendering → ready`; `failed` permite diagnóstico.
- Nunca incrustar credenciales o secretos en archivos estáticos.

### Plano de producción (GitHub Actions)

- Runner recibe `job_id` únicamente, obtiene el guion aprobado de la API segura.
- Genera voz preliminar sin servicios externos, tarjetas visuales propias y video H.264 usando FFmpeg.
- Entrega el MP4 como artefacto del workflow (no publica en YouTube).
- Reporta éxito/error a la API y conserva evidencia de ejecución.

### Futuro: producción de calidad y distribución

- Investigación asistida por IA con fuentes trazables y revisión de hechos.
- Voz neural con derechos de uso comercial, material visual original/licenciado, motion graphics y edición avanzada.
- Servicio de render escalable para documentales largos según coste real.
- R2 para recursos y previsualizaciones, con retención limitada.
- OAuth 2.0 YouTube Data API, subida como privado, revisión humana y publicación programada.
- YouTube Analytics para retención, CTR, horas, conversiones y pruebas de títulos.
- Opcional: herramientas AI de pago con límites de gasto por ejecución.

## 5. Modelo de datos inicial

`jobs`: `id`, `title`, `status`, `format`, `manifest_json`, `review_note`, `last_error`, `created_at`, `updated_at`. `events`: log auditable de acciones y transiciones. En el futuro separar entidades `channels`, `research_sources`, `assets`, `licenses`, `renders`, `publications` y `metrics`.

## 6. Hitos verificables

### Fase 0 — Fundamentos
- [x] Repositorio y rama principal identificados.
- [x] Plan y documento de avance.
- [x] Contrato de datos y diseño inicial de controles.
- [ ] Pruebas de seguridad y funcionamiento del primer despliegue.

### Fase 1 — MVP de guion a previsualización
- [x] API, D1, panel, controles de aprobación.
- [x] Workflow GitHub Actions para renders bajo demanda.
- [x] Script de render con escenas y narración provisional.
- [x] Configurar secretos reales y ejecutar de extremo a extremo con credenciales propias. Confirmado en run 39471906672 (MP4 v0.1) y D1 `ready`.
- [ ] Verificar costos, fallos y accesibilidad móvil.

### Fase 2 — Producción documental profesional
- [ ] Investigación con trazabilidad por afirmación.
- [ ] Generación asistida de guiones; verificación humana.
- [ ] Voz natural con licencia comercial.
- [ ] Motion graphics, recortes, cronologías, imágenes con derechos, música comercial autorizada.
- [ ] QA automático audiovisual y revisión humana completa.
- [ ] Pruebas de videos 8–14 min y Shorts.

### Fase 3 — Distribución
- [ ] Autenticación OAuth de canal YouTube (consentimiento explícito).
- [ ] Subida como privado/no listado y programación solo tras aprobación.
- [ ] Comprobar estado/verificación del proyecto de YouTube API, cuotas y políticas.
- [ ] Control de duplicados, errores, reintentos y auditoría de publicaciones.

### Fase 4 — Analítica, optimización y escala
- [ ] YouTube Analytics; panel KPIs por video y periodo.
- [ ] Optimización editorial con historial de decisiones.
- [ ] Presupuestos mensuales y alertas; expansión a varios canales sólo si hay retorno.

## 7. Reglas de desarrollo

- Todo trabajo directamente en `main` según la forma de sincronización de este proyecto.
- `docs/AVANCE.md` se actualiza en cada entrega con hecho, pendiente y siguiente acción.
- Código y visuales específicos del producto; no plantillas genéricas sin propósito.
- No marcar como terminado ningún punto sin prueba ejecutada.
- Sin secrets en Git, videos con copyright, ni publicación automática sin consentimiento.
- Cada cambio debe tener verificación, rutas claras de rollback y posibilidad de continuar después.

## 8. Aceptación final

Un documental puede investigarse, guionizarse, producirse con calidad, revisarse, publicarse con permiso y medirse desde una plataforma coherente; con flujo automatizado, evidencias de originalidad y coste controlado. Ningún simple video genérico prueba esa meta.
## 9. Entrega audiovisual v0.2 (2026-10-20)

- Motor de voz neuronal local Piper y modelo `es_MX-ald-medium` incorporados; smoke y generación de MP4 comprobados en GitHub Actions, sin API de IA de pago.
- Workflows de render usan voz Piper predeterminada, gráficas editoriales con movimiento Ken Burns, subtítulos quemados y archivos auxiliares `subtitulos.srt`, `ficha.json`, `creditos.txt`.
- Validación de códecs, resolución y duración mediante `ffprobe`. Se corrigió a partir de una revisión visual real la escala excesiva de subtítulos verticales.
- Requisitos no alcanzados: calidad editorial cinematográfica, metraje con licencias, verificaciones de fuentes/afirmaciones, validación de derechos de voz derivada, alineación fonética y OAuth YouTube. Este hito es una previsualización **técnica mejorada**, no producción final apta para monetización.

## 10. Identidad vocal del canal — decisión editorial

El propietario ha definido una voz objetivo más adulta, profesional, seria, natural, con autoridad y pronunciación clara para historias de empresas, innovaciones y decisiones. Idealmente español latinoamericano comprensible internacionalmente. No asumir una edad real ni género del locutor a partir de los nombres de modelos; se evaluarán auditivamente.

- Mantener una sola voz institucional estable para documentales y Shorts.
- Conservar voces alternativas como candidatas para audición, pruebas o narraciones especiales; nunca sustituir automáticamente al narrador oficial.
- El modelo actual, es_MX-ald-medium, queda como referencia técnica hasta aprobar una nueva identidad.
- Audición A/B/C preparada con es_MX-ald-medium, es_MX-claude-high y es_ES-davefx-medium; reproducir el mismo texto y revisar timbre, neutralidad, pausas, claridad, pronunciación de empresas y licencias.
- El panel necesitará configuración persistente de identidad vocal: modelo, velocidad, pausas, pronunciaciones especiales, prueba auditiva y control de versión.
- No activar publicación comercial de ningún modelo sin revisar términos del dataset, pesos y entrenamiento.

## Política económica definitiva — cero pagos (2026-10-20)

Decisión expresa del propietario: **no utilizar servicios de pago, suscripciones, saldos de prueba que luego se facturen, ni motores que requieran contratar un nivel pagado para explotar comercialmente los audios**.

- Descartar la contratación Azure Speech S0 y cualquier API TTS pagada. La voz Microsoft `es-EC-LuisNeural` se conserva **solo como referencia de estilo** (natural, formal, fluida), no como dependencia, proveedor ni voz oficial aprobada.
- Priorizar motores locales, de código abierto y modelos con derechos de uso comercial **verificados para cada voz/modelo**, no solo para el motor base.
- Antes de integrar un proveedor, comprobar licencia de pesos, dataset, referencias y restricciones de redistribución y uso comercial.
- No activar por defecto facturación, claves de servicios cobrables, upgrades de planes ni workflows que incurran en cargo sin autorización explícita posterior del propietario.
- **Gratis no significa ilimitado:** verificar cuotas de GitHub Actions/Cloudflare; establecer límites de duración, reintentos y frecuencia para mantener el proyecto dentro de las franquicias gratuitas. Ante agotamiento, detener/posponer en vez de generar cargos.
- No reducir calidad con filtros artificiales de pitch; la identidad vocal final será una voz natural seleccionada mediante audición real y fijada para todos los videos.
- Desarrollo y registro de avance directamente en `main`.

## Dirección vocal de referencia: documentales de naturaleza (20-10-2026)

El usuario elige **como referencia de ESTILO**, no como persona a imitar, el narrador masculino de documentales de animales de Discovery: cadencia más pausada, voz cálida, serena, inteligible y profesional, autoridad contenida y buen manejo de silencios. El canal continúa siendo sobre historia empresarial y decisiones influyentes.

- El narrador preferido sigue siendo la **tercera muestra Qwen3 de dicción profesional**, con BlackBerry pronunciado aproximadamente «Blákberri» (rr fuerte).
- La última versión de prueba se ralentizó con `atempo=0.94` (sin cambiar altura) y se añadieron tres pausas de 160 ms en silencios entre frases; los resultados se mantendrán sujetos a evaluación humana.
- La corrección de la «a» prolongada en **«Durante años»** es un ajuste puntual, no una modificación global del ritmo ni una voz nueva.
- Cero pagos, sin clonación de personas identificables, cambios solo en rama `main`; pendiente integración al render hasta que la voz y la arquitectura sean sostenibles.


## Hito alcanzado: referencia vocal guardada y motor CPU experimental funcional (2026-10-20)

- Patrón auditivo del narrador aprobado, inalterado en `assets/voice/approved/narrador_documental_aprobado.mp3`, con verificador SHA-256, manifest y protección frente a cambios accidentales.
- Qwen3 Base 1.7B ha generado correctamente nueva frase al usar la referencia en la **demo pública con cuota limitada**; no permite asumir producción masiva.
- Qwen3 Base 0.6B ya ha sintetizado por primera vez localmente en CPU de GitHub Actions, sin API ni GPU pagada; rendimiento medido para solo 8,424 segundos de audio. La **aprobación audible de la muestra 0.6B no existe todavía**.
- Para llegar a la meta final, falta: verificar calidad y consistencia de la voz en muchos fragmentos; medir coste temporal en documentales completos sin sobrepasar recursos gratuitos; comprobar derechos de uso comercial y eliminar la dependencia de demos con cuotas; integrar al motor/render y panel sólo después de esas verificaciones.
- Nada de pagar, no incorporar automáticamente voces peores, ni publicar audiovisuales sin revisión.


## Hito adicional — mismo modelo 1,7B funcionando en CPU (2026-10-20)

Tras detectar una ligera diferencia de timbre en la audición Qwen 0,6B, se ejecutó la versión `Qwen3-TTS Base 1,7B` en CPU gratuita, con salida MP3 verificable, mismos datos de referencia y mismo guion. La prueba terminó con éxito: 7,680 s de audio, ~88,62 s de ejecución del proceso Python y ~11,28 GiB de RAM pico; workflow 39512992392.

La variante local de mayor tamaño no reemplaza todavía la voz elegida ni supone autorización comercial. Faltan comparación auditiva humana, robustez en segmentos largos, cálculo real de throughput, licencias aplicables y conservación de la cadencia vocal. Las pruebas CPU pesadas son manuales y solo en repositorio público.

## Decisión editorial vinculante: una sola voz canónica

Confirmación expresa del propietario mediante nueva subida: `FactorDeGigantes_Documental_TomaNatural.mp3` **es la voz correcta**. Coincide exactamente con el MP3 versionado en `assets/voice/approved/narrador_documental_aprobado.mp3` (SHA-256 `78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d`).

No se acepta automáticamente el 0,6B ni el 1,7B local como sustituto, aunque sean ejecutables con CPU gratis. Ambos son ensayos sin aprobación vocal. Objetivo de ingeniería: producir nuevas frases que suenen como **esta identidad exacta**, sin modificar la referencia, sin usar servicios de pago y sin activar publicación en YouTube. Si no se demuestra continuidad, mantener bloqueada la integración de Qwen.

## Subhito de Fase 2 — continuidad vocal segmentada sin pagos (2026-10-20)

- [x] Crear banco de dos fragmentos para experimentar continuidad de la voz fija en Qwen Base 1,7B CPU (script, tests y workflow manual en `main`); CI de contratos [39515949183](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39515949183) exitosa.
- [x] Ejecutar una sola vez `voice-continuity-cpu.yml`, comprobar los dos MP3 nuevos y sus métricas: [GitHub Actions 39516609592](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39516609592) `success`; artefacto 12307719223, audios 8,496 y 9,960 s, memoria pico ~11,28 GiB. La prueba fue lanzada con disparador temporal y revertida a ejecución exclusivamente manual.
- [x] Obtener evaluación auditiva del propietario de ambas tomas: «Sí ambas, la 1 es más fiel»; `01_decision.mp3` es la más cercana a la referencia; `02_transformacion.mp3` también aceptable en esta prueba breve. **No implica equivalencia perfecta en textos futuros ni sustituye la voz canónica**. Evidencia: workflow 39516609592.
- [ ] Demostrar continuidad en narraciones largas, validar derechos comerciales de todos los componentes, implementar QA de voz/visual y recién entonces evaluar integración en `render.yml`.
- [ ] Continuar investigación con fuentes verificables, activos originales con licencia y producción de primer documental 8–14 min.

**Restricciones vigentes:** cero pagos, únicamente `main`, patrón vocal canónico único, experimentos no equivalen a aprobación, y ninguna publicación en YouTube sin consentimiento expreso. Fase 2 sigue **abierta**.

### Resultado editorial de escucha A/B (2026-10-20)

- **Ambas muestras cortas aceptadas por el propietario; preferencia por la primera por mayor fidelidad.** Mantener íntegra la muestra oficial ya aprobada.
- [ ] Siguiente hito: evaluar constancia vocal en varios párrafos y validar rendimiento sin pagos, licencias comerciales y QA editorial antes de conectar el motor Qwen al render.
- [ ] Primera producción documental completa 8–14 minutos, con guion investigado y recursos audiovisuales con derechos comprobados. No abrir OAuth ni publicación sin aprobación.


## Fase 2 — resultados técnicos incrementales de octubre (2026-10-20)

- [x] Probar continuidad de **tres párrafos de una misma historia** con Qwen Base 1.7B CPU sin servicios de pago, audios separados, previsualización de 43,296 s, metadatos y referencia canónica intacta: [run 39518606909](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39518606909) `success`.
- [x] Limitar nuevas pruebas intensivas al inicio manual; la activación excepcional por `push` fue retirada en `main` inmediatamente después de lanzar la ejecución.
- [x] **Audición humana de la previsualización continua de 43,296 s:** el propietario respondió «Está bien». Aceptación editorial limitada al montaje escuchado; no supone aprobación universal de nuevos fragmentos ni derechos de uso comercial.
- [x] Introducir comprobación estructural de fuentes enlazadas a afirmaciones y de derechos de recursos (`tools/editorial_evidence.py` + tests). CI `success`, **aún no conectada** al Worker/D1 ni a un guion factual real.
- [x] Documentar estado declarado Apache-2.0 del modelo y las lagunas de derechos de la voz en `docs/LICENCIAS_NARRACION.md`.
- [ ] Validar términos del audio de referencia y todos los materiales con derechos de uso comercial, optimizar la generación larga con presupuesto gratuito y pruebas de estabilidad, preparar fuentes originales y un primer documental completo.
- [ ] Integrar verificación editorial y licencias al panel, y la narración final al renderizador, **solo después** de aprobación técnica, humana y legal.

**Fase 2 aún abierta**. Ningún ensayo experimental se considera publicado, monetizable o idéntico a la identidad aprobada solo por superar FFprobe o CI.


### Hito de escucha aceptado (2026-10-20)

El montaje breve de tres párrafos (43,296 s) obtuvo conformidad editorial del propietario. Se mantiene intacta la voz canónica; siguiente etapa: optimización de narración segmentada para mayor duración, límites de CPU gratuito y trazabilidad de investigación y licencias. No se habilita aún narración para publicación ni YouTube.

## Fase 2 — integración editorial de fuentes y licencias (2026-10-20)

**Hito de desarrollo verificado en GitHub `main`:**

- [x] API Worker con expedientes de fuentes, afirmaciones y derechos vinculados a cada trabajo (`src/editorial.mjs` + rutas `/api/jobs/:id/dossier`).
- [x] Esquema D1 versionado `0002_editorial_dossiers.sql`; preserva tablas iniciales y referencia del trabajo, registra revisión editorial y la invalida ante modificaciones.
- [x] Panel administrativo con edición del expediente, estados y confirmación humana; el guardado por sí solo **no** permite renderear, y `approve`/`dispatch` se bloquean con HTTP 409 si no hay verificación acreditada.
- [x] Pruebas de seguridad y contratos con Node, pruebas de migración local SQLite y CI de GitHub Actions [39521914410](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39521914410) **exitosa**; también se cubrió el caso de migración remota ausente con HTTP 503.
- [ ] **Aplicar la migración 0002 a Cloudflare D1 real**. Las herramientas de Cloudflare de esta sesión no permitieron consultar/actualizar la base; no declarar aplicado el SQL remoto.
- [ ] **Desplegar el nuevo Worker y panel y validar el recorrido completo en la instancia real**. No confundir tests en CI con despliegue.
- [ ] Construir un expediente factual con fuentes originales comprobadas, revisión legal de voz y materiales, y primer documental investigado de 8–14 minutos. La narración de 43,296 s aprobada por el propietario permanece como ensayo, sin autorización comercial automática.

**Orden obligatorio del próximo avance:** migración D1 y confirmación → despliegue Worker/assets → prueba de acceso, expediente, bloqueo/atestado y aprobación → materiales con licencias y guion de un documental original → nueva validación de narración y montaje. Cero proveedores de pago, `main` exclusiva y YouTube sin subida automática.


## Fase 2 — integración probada con D1 local y primera investigación (2026-10-20)

- [x] Editor guiado de fuentes, afirmaciones y derechos por escena en el panel; JSON avanzado opcional. Permite registrar múltiples evidencias por afirmación y bloquea acreditaciones con cambios sin guardar. Pruebas de componentes: [CI 39523541399](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39523541399) `success`.
- [x] Validar migraciones y recorrido de edición/acreditación/aprobación con **Worker real + D1 local** mediante Wrangler: [Actions 39523829006](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39523829006) `success`. Sin credenciales remotas ni publicación.
- [x] Asegurar el despacho de renders frente a solicitudes duplicadas mediante reserva condicional en D1, con manejo explícito de rechazos y resultados de red inciertos; [CI 39524141335](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39524141335) `success`.
- [x] Crear el **primer piloto de investigación documental** (BlackBerry, tema provisional) con seis fuentes originales, ocho afirmaciones identificadas y estructura editorial de ~12 minutos: `research/blackberry/brief_investigacion.md` y `expediente_preliminar.json`. Las afirmaciones y licencias siguen en **estado pendiente de revisión humana**.
- [ ] Resolver acceso a Cloudflare y aplicar **D1 0002 en remoto** sin alterar trabajos existentes. Confirmar de forma verificable la nueva tabla.
- [ ] Desplegar y auditar panel/Worker en Cloudflare y recorrer un expediente auténtico con usuario autorizado, sin lanzar render si hay derechos no confirmados.
- [ ] Completar investigación del piloto con fuentes independientes y datos financieros originales, escribir narración verificada, obtener música/gráficos/visuales utilizables legalmente y aclarar los derechos de la voz canónica.
- [ ] Realizar el primer render documental de 8–14 minutos con el nivel editorial deseado, límites gratuitos de CPU y control de QA, **solo tras superar las verificaciones técnicas y comerciales**.

**Nota:** un ensayo local exitoso, un expediente preliminar o un clip de voz aprobado no significa que la productora ya publique automáticamente. La fase 2 está parcialmente implementada y sigue abierta; las fases 3 y 4 no han comenzado.


## Fase 2 — motor de investigación propia con IA local (2026-10-20)

**Meta final:** que Factor de Gigantes investigue y documente el episodio con IA, dejando al propietario principalmente el control editorial y la aprobación, y sin servicios facturables. Esta meta aún **no** está completa.

- [x] **Primera consulta automática de fuentes web con trazabilidad**: tools/research_engine.py visita URLs HTTPS declaradas, propone pasajes breves ligados a cada afirmación, y registra URL, hash, similitud y bloqueos. No marca datos verificados por coincidencia textual.
- [x] **Investigar cualquier tema sin expediente previo**: descubrimiento MediaWiki y lectura de fuentes secundarias. Probado en [run 39529286991](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39529286991), 3/3 páginas legibles, 0 afirmaciones aprobadas. La búsqueda de primarias independiente del usuario sigue pendiente.
- [x] **Redacción autónoma preliminar por IA local sin API paga**: tools/local_research_ai.py usa Qwen/Qwen3-0.6B CPU y propone una estructura con citas. [Run 39528648495](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39528648495) success: 3/6 fuentes BlackBerry legibles, 5 pasajes y borrador de 722 caracteres. No llegó a guion completo.
- [x] **Auditoría básica antiinvenciones**: comprueba referencias inventadas y señala cifras que no aparecen en pasajes citados; CI [39529112648](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39529112648) success. El primer borrador contiene un error real de fecha IPO BlackBerry; se documentó y **no se certifica** ni se elimina por una prueba verde posterior.
- [x] **Workflow manual y controlado** de investigación: .github/workflows/research-ai-cpu.yml; tema libre o dossier BlackBerry, artefactos no publicables y retención corta. Sin activación recurrente ni servicios de IA de pago.
- [ ] **Búsqueda autónoma de fuentes primarias e independientes**, extracción de reportes PDF/financieros y contrastes de afirmaciones con contexto y contradicciones; la herramienta aún no puede asumir que un texto secundario o una mención prueban un hecho.
- [ ] **Generación de guion original completo de 8–14 minutos** y plan escena-por-escena; los textos actuales son solo borradores de demostración y pueden contener errores.
- [ ] **Vincular investigación por tema y por episodio al panel Cloudflare**, respetando tokens aislados y revisión humana; D1 remota 0002 y despliegue todavía no confirmados.
- [ ] Validar derechos de voz canónica, música e imágenes, QA de narración y visuales, antes de render y publicación.

La nueva fase 2 tiene un motor experimental de consulta y redacción IA **ejecutado de verdad**, no un sistema de investigación autónomo completo ni una fábrica de videos finalizada. Mantener todas las tareas en main, sin gasto facturable ni publicación automática.

## Fase 2 — botón «Investigar con IA» en el panel (2026-10-20)

- [x] Crear formulario de investigación por tema en la interfaz administrativa, sin requerir potencia gráfica ni batería de la laptop (ejecución del motor IA local en GitHub Actions CPU). Requiere confirmación explícita.
- [x] API autenticada por ADMIN_TOKEN para despachar ÚNICAMENTE research-ai-cpu.yml a main, dejando el token GitHub en el Worker; no usa render.yml ni subida a YouTube.
- [x] Registro D1 versionado 0003_research_requests.sql, cuota nominal 4 solicitudes/día UTC, unicidad de tema/día, bloqueo de duplicados e incertidumbres de red, sin reintentos ni tareas automáticas.
- [x] Pruebas unitarias Node + integridad SQL; [CI 39544634359](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39544634359) success.
- [x] Ejecución real de integración con Worker/D1 aislada: [GitHub Actions 39544778750](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39544778750) success. Se aplicaron localmente las migraciones 0001–0003; no hubo llamadas a GitHub dispatch ni consumo de Qwen en esta prueba.
- [ ] Aplicar las migraciones 0002 y 0003 en la D1 **remota** Cloudflare, desplegar panel/Worker actualizado desde main y comprobar solicitudes reales, estado y cuota en producción. Conector Cloudflare indisponible desde la sesión: esto sigue PENDIENTE.
- [ ] Comprobar que las solicitudes aceptadas se vinculen automáticamente con un run_id real y un estado de finalización, sin suponer que un HTTP 204 implica resultado correcto.
- [ ] Ampliar investigación autónoma a fuentes primarias, contraste factual y guion de 8–14 min; el motor actual genera borradores no verificados. Material audiovisual y derechos de narrador aún bloquean producción comercial.

**Importante:** sin nuevas GPU o compras. La laptop HP con 12 GB RAM no participa en la inferencia de la fase 2, que se hace en GitHub Actions bajo ejecución manual y cuotas del servicio. ComfyUI/otros motores de video local quedan condicionados a identificar GPU/VRAM y derechos de uso, sin instalación automática.

## Fase 2 — resultados vinculados y fuentes oficiales desde el tema (2026-10-21)

- [x] Cada nueva solicitud del panel envía un `request_id` de correlación a `research-ai-cpu.yml` sin modificar `render.yml`; GitHub muestra dicho ID en el título de ejecución.
- [x] El panel puede consultar manualmente estado/conclusión y URL de una ejecución real por GET autenticado `/api/research?runs=1`, distinguiendo `queued`, `in_progress`, `completed` y fallas de lectura. CI [39587493924](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39587493924) `success`; estado real de ejecución con la D1 remota **todavía no probado**.
- [x] Motor auxiliar `tools/primary_source_discovery.py` para descubrir sitios oficiales candidatos desde MediaWiki/Wikidata P856. CI local de seguridad y contratos en `main` [39587923760](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39587923760), `success`.
- [x] Prueba de recuperación real por tema: [39588198172](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39588198172) `success`, identificó `https://blackberry.com` como **candidato** a sitio oficial de `BlackBerry Limited` entre cinco entidades examinadas. **No** se pudo leer esa web (ValueError) ni verificar hechos. El flujo de investigación con Qwen puede incluir ahora el reporte de candidatos.
- [ ] Mejorar recuperación de contenidos originales HTTPS y fuentes primarias financieras, archivos PDF con páginas/citas precisas, y contraste de cifras; ninguna fuente candidata constituye por sí sola prueba editorial.
- [ ] Resolver acceso Cloudflare, migraciones D1 0002/0003 y despliegue, y comprobar consultas de estado del panel contra Actions reales. Ningún cambio de esta sesión se considera operativo en producción.
- [ ] Pasar de borradores pequeños a guiones de 8–14 minutos respaldados por evidencias, licencias completas y montaje cinematográfico, manteniendo narrador canónico e intervención humana.

**Estado:** código y pruebas de correlación y descubrimiento implementados en `main`; búsqueda externa oficial probada como **localización de enlace**, no como extracción factual verificada. La productora aún no publica automáticamente ni ha completado la fase 2.


## Fase 2 — extracción PDF de fuentes originales con páginas (2026-10-21)

- [x] Soportar documentos públicos PDF en el investigador por expediente (además de HTML), con texto localizable por página, SHA-256, URL final, tipo PDF y límites explícitos de tamaño, páginas y tiempo. Código en `tools/pdf_sources.py` y `tools/research_engine.py`.
- [x] Incluir los localizadores PDF reales en el reporte editorial y en el contexto enviado a Qwen, sin confundir coincidencia textual con verificación. `tests/test_pdf_sources.py` prueba páginas diferentes y errores de documento.
- [x] **Validación externa real de un PDF de investigación primario**: [GitHub Actions 39592681746](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39592681746) `success`: artículo arXiv `Attention Is All You Need`, **15 páginas, 328 bloques, 2 pasajes candidatos en páginas 1 y 2**. No se aprobaron hechos; [CI 39592490158](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39592490158) `success` para la batería general.
- [ ] Buscar PDFs primarios de informes financieros y regulatorios **automáticamente a partir del tema**, no solo desde URL conocida. Ampliar extracción a documentos largos/escaneados y tablas contrastadas sin inventar valores ni sobrepasar recursos CPU.
- [ ] Integrar evidencia documental y fuentes verificadas al guion completo de 8–14 minutos; conservar aprobación editorial, licencias de voz/imágenes/música y QA antes de render final.
- [ ] Migración D1 0002/0003 y despliegue remoto Cloudflare siguen **pendientes**: el conector continúa con error interno, así que la mejora está en `main` y probada en GitHub, **no** confirmada en el panel web publicado.

**Decisión:** priorizar una cadena de investigación documental realmente reproducible y sus evidencias antes de ampliar modelos IA o instalar generadores locales de video. Las tareas de PDF y síntesis usan CPU en GitHub Actions, no dependen de la laptop.

## Hito 2026-10-21 — Cloudflare real, límites transaccionales y diagnóstico del panel

**Despliegue de fase 2 en la infraestructura real, verificado por API de Cloudflare:**

- [x] Recuperar conexión Cloudflare seleccionando explícitamente `Factor`, no `Primary`; cuenta y Worker correctos confirmados.
- [x] Preservar 1 trabajo y 8 eventos; generar exportación previa en Cloudflare y bookmark Time Travel. Aplicar **0002 editorial** y **0003 research** en D1 REMOTA por SQL API con archivos originales de `main`. Verificar tablas, índices y claves foráneas, sin borrar datos; nuevas tablas vacías (0 expedientes, 0 solicitudes). Los scripts se aplicaron por API y no generaron historial `d1_migrations` de Wrangler: revisar con cuidado cualquier reaplicación futura.
- [x] Desplegar desde `main` el Worker actualizado mediante el build conectado a GitHub y `npx wrangler deploy`. Ejecución `729fb21f-d1d9-4f2f-999e-7e6f8cbd47de`, `success`, commit `79a2ba80b95022e90acb696c81ebaa610112fa55`.
- [x] Endurecer la cuota diaria del investigador: reemplazar comprobación y reserva separadas por **un solo INSERT condicional atómico** en D1, con discriminación de duplicado HTTP 409 y cuota llena HTTP 429. Agregar prueba de solicitudes concurrentes.
- [x] Configurar Cloudflare Builds para ejecutar tests JavaScript antes de desplegar. Build `720b0c1e-b0ac-4dda-92c3-4c7110f8f862`: 21 pruebas aprobadas, 0 fallos, código desplegado.
- [x] Incorporar `GET /api/system/status` con `ADMIN_TOKEN`: presenta diagnóstico privado de tablas y requisitos de investigación sin exponer secretos ni asumir validez del token externo. Añadir sección «Estado del sistema» al panel y 4 pruebas de acceso y estado.
- [x] **Validación de versión final:** build `17eaaf34-42eb-4427-859b-0f0b8d92b262` (`success`), **25 pruebas Node, 0 fallos**, commit `7ccc9d4e6cf224bbc22333722e0127c1f932b4e6`; 2 assets de panel actualizados; Worker publicado versión `a7695b06-938e-402e-a4ba-809fc2f2ec02` con el 100% del tráfico. API de Cloudflare confirmó el código nuevo desplegado y D1 con 1 trabajo + 8 eventos intactos.
- [ ] **Prueba autenticada real desde navegador:** entrar al panel con ADMIN_TOKEN propio, revisar «Estado del sistema», consultar expedientes y lista de investigaciones. No usar tokens en chats ni registrar capturas sensibles.
- [ ] **Primer despacho real del investigador desde el panel actualizado:** únicamente tras solicitud explícita del propietario con tema concreto y cuota disponible; inspeccionar workflow, artifact y estado. Ninguna prueba técnica actual consumió ejecución pesada de Qwen.
- [ ] Desarrollar investigación de fuentes primarias independiente, contraste automático de contradicciones, y guion respaldado de 8–14 minutos con revisión factual y derechos editoriales. Las mejoras de infraestructura **NO** completan el motor de producción documental.
- [ ] Preparar narración comercial autorizada y visuales con licencia; respetar el narrador aprobado y no subir nada a YouTube automáticamente.

**Criterio de estado:** D1 y Worker en producción confirmados; browser login, workflow real de investigación desde el panel, contenido documental completo y publicación siguen pendientes.

## Hito de motor editorial 2026-10-21 — auditoría y documentos SEC

- [x] Incluir auditoría conservadora en cada investigación: falta de pasajes, falta de contraste en segundo dominio, dependencia de Wikipedia, números/años que no coinciden y nunca concluir automáticamente que una afirmación sea verdadera o falsa. `tools/editorial_audit.py`, `AUDITORIA_EDITORIAL.json`.
- [x] Producir primera **escaleta estructurada de 10:00** (12 bloques con duración conocida e identificadores de evidencias), sin redactar narración falsa ni aprobar voz/imagen o publicación. `ESCALETA_DOCUMENTAL_10MIN_NO_APROBADA.md`.
- [x] Descubrir metadatos candidatos de documentos corporativos originales de SEC EDGAR a partir del tema sin API paga: Wikidata P5531 → CIK → SEC `submissions/CIK*.json`. Admitir rechazos y datos incompletos sin inventar archivos, cifras ni referencias. `tools/edgar_discovery.py` integrado al workflow manual `research-ai-cpu.yml`.
- [x] Añadir tests para seguridad del identificador, URL y filtro de documentos, SEC inaccesible, cifras discordantes, falta de evidencia y cuota. Compilación Cloudflare `c6bfd5a1-3cd9-4201-b945-8d653f58f5a3`: **25 tests JS + 11 tests Python, 0 fallos**, desplegado el commit `cc90a481878d9e2c7ddca7c75dd1a28a09b73d71` de `main`. Cloudflare Builds requiere pasar pruebas Python además de las del Worker antes de publicar.
- [ ] Verificar resultado del smoke real `edgar-smoke.yml` para Apple Inc.; la existencia de un documento en SEC **no** se da por probada por una simulación offline. Dejar este workflow solo manual después de la ejecución de prueba.
- [ ] Descargar documentos regulatorios concretos con límites legales/técnicos y analizar contexto, periodo, moneda, unidades y tablas. Comparar contradicciones reales con fuentes múltiples antes de escribir la voz.
- [ ] Completar texto narrativo de 8–14 minutos, evidencia de cada escena, edición visual y locución comercial con licencia verificada. El bloque actual entrega una escaleta, NO un episodio terminado.
- [ ] Probar una investigación iniciada y revisada desde el panel de producción con `ADMIN_TOKEN` solo cuando el propietario elija el tema. No asumir permisos externos por la mera presencia del secreto.
- [ ] No publicar a YouTube ni contratar servicios; conservar rama `main` y documento `docs/AVANCE.md`.

**Nota:** el montaje y la narración no se consideran terminados; avanzar en ellos depende de evidencias, derechos y prueba de audio aprobado. La laptop de 12 GB RAM no es un requisito de este hito.

## Fase 2 — comparador financiero y expediente de revisión (2026-10-21)

- [x] Implementar extracción XBRL SEC candidate-only para un emisor con tag, unidad USD, fechas exactas, tipo de periodo, filing y accession; validar host SEC, CIK y topes de descarga. **No hay recolección real confirmada todavía.**
- [x] Comparar solo métricas y periodos homogéneos; señalar diferencias entre presentaciones del mismo periodo como **revisión humana**, nunca fraude/contradicción probada.
- [x] Integrar en investigación Qwen manual un paso condicional de datos XBRL, tolerante a SEC bloqueada. Mantener borradores y conteo de hechos verificados igual a cero.
- [x] Generar expedientes consolidados `EXPEDIENTE_EDITORIAL_PENDIENTE.json` y `EXPEDIENTE_PARA_REVISOR.md` con las carencias por afirmación, enlaces de fuentes, riesgos, cifras candidatas y bloqueos de derechos. No significa guion terminado.
- [x] Extender `primary_source_discovery.py` para registrar enlaces **realmente presentes** a informes anuales y PDF desde páginas corporativas, distinguiendo hosts externos. Cero links inventados y ninguna descarga/autoría automática.
- [x] Versionar chequeos de Cloudflare en `tools/production_preflight.sh`, evitando configuraciones de build difíciles de mantener. CI [39625136678](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39625136678) `success`.
- [x] Ejecutar prueba pública controlada de SEC: [registros 39621724636](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39621724636), [XBRL 39624310668](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39624310668): ambos endpoints rechazaron acceso (`HTTPError`). **0 datos SEC financieros reales obtenidos.**
- [ ] Validar una fuente financiera real accesible, con PDF/HTML, unidad/periodo/URL/página, y contrastar cifras de al menos dos documentos independientes.
- [ ] Completar prosa documental de 8–14 minutos con verificación frase a frase, fuentes originales y narrador con derechos comerciales acreditados; generar una prueba reproducible de audio/MP4 antes de hablar de producto listo.
- [ ] Verificar en el panel publicado el login privado y una solicitud manual real, sin exponer ADMIN_TOKEN ni activar publicación.
- [x] Desplegar y comprobar la versión del motor alternativo en Cloudflare. Build `18d882b5-39f5-4524-aa13-1db876e3ebdb` (`success`), commit `cb54813a158c957e4f3b57651c211fb57e53a572` de `main`, 25 pruebas JS + 34 Python aprobadas, versión Worker `1489175a-38ca-403a-9477-a2a466f39b4c` al 100 %. La D1 conserva 1 trabajo y 8 eventos; tablas editoriales e investigación siguen vacías.
- [ ] Conservar publicación YouTube deshabilitada, códigos en `main` y el historial en `docs/AVANCE.md`.

## Hito editorial 2026-10-21 — de simulaciones a evidencias reales de BlackBerry

- [x] Identificar desde el portal oficial de inversores de BlackBerry **dos PDF** de resultados FY2024 (16 páginas) y FY2025 (19 páginas), aptos para el presupuesto de procesamiento CPU.
- [x] Descargar y analizar ambos documentos en un GitHub Actions real: [39630703040](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39630703040), **success**, 2 fuentes leídas, 5 cifras/páginas ubicadas y hashes SHA-256 registrados. No hay hechos aprobados automáticamente; [artefacto JSON](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39630703040/artifacts/12359810175).
- [x] Diferenciar explícitamente los 853 millones FY2024 reportados en 2024 y los 759,1 millones FY2024 comparativos presentados en 2025; no deducir una variación sin revisar operaciones discontinuadas. Registrar también 218 millones por patentes, ingresos FY2025 534,9 millones y QNX 236,0 millones, con página de origen.
- [x] Integrar estos datos originales al expediente editorial del investigador en modo BlackBerry; la tabla original no se redistribuye, la IA sigue sin facultad de verificar/publicar. Mantener separada la investigación general por tema.
- [x] Crear primer bloque de narración interna con escenas, voz en off original y citas documentales, `research/blackberry/PRIMER_BLOQUE_NARRATIVO_FUENTES_REALES.md` (~3–4 minutos), **sin etiquetarlo como documental completo**.
- [ ] Ampliar la comprobación de la reformulación contable utilizando 10-K completo y otros documentos originales, incluyendo cifras con comparabilidad homogénea.
- [ ] Obtener fuentes independientes para la historia de dispositivos y decisiones, completar voz narrativa de 8–14 minutos, revisión editorial, licencias comerciales y un MP4 verificable.
- [ ] Demostrar desde panel un flujo autenticado en producción con una ejecución IA aprobada y artefactos vinculados. No consumir minutos Qwen sin tema/decisión del propietario.
- [ ] Conservar acciones de prueba en modo manual y cualquier despliegue en `main` con CI verde, sin publicación YouTube ni datos especulativos.

## Hito editorial 2026-10-21 — primer guion documental largo y plan de montaje, solo `main`

**Objetivo:** sustituir los borradores de pocos párrafos por un texto narrativo verdaderamente desarrollado, respaldado por documentos concretos, sin mentir sobre licencias o resultados de audio/video.

- [x] Redactar `research/blackberry/GUION_DOCUMENTAL_11MIN_NO_APROBADO.md`, **12 escenas y 1.691 palabras** de narración original; escaleta temporal continua de **11:50 (710 segundos)**. Los tiempos y ritmo de voz son objetivos técnicos, no prueba de audio real. A ~145 palabras/minuto el texto ocupa aproximadamente 11,7 min sin pausas, por tanto el cronometraje debe afinarse con el narrador real.
- [x] Registrar `research/blackberry/FUENTES_GUION_10MIN.json` con siete referencias rastreables: museística Smithsonian, declaración BlackBerry 2016 sobre externalización de hardware, registro corporativo 2016, comunicados FY2024/FY2025, 10-K FY2025 y circular corporativa FY2025. Las fuentes históricas y contables citadas siguen sujetas a **revisión humana afirmación por afirmación**.
- [x] Estructurar una narración desde los primeros dispositivos hasta el cambio de estrategia en 2016, QNX, Cylance y la composición financiera FY2025. Evitar inferir fracaso/éxito, fraude o rentabilidad mediante comparaciones inadecuadas.
- [x] Mantener explícita la **incomparabilidad directa** entre los ingresos FY2024 comunicados originalmente en 2024 (US$853m) y la cifra FY2024 reformulada en 2025 (US$759,1m), hasta una conciliación por operaciones discontinuadas.
- [x] Añadir `tools/blackberry_script_quality.py` + pruebas `tests/test_blackberry_script_quality.py`: continuidad de escenas, fuentes referenciadas, ritmo proyectado, duración, advertencias editoriales y ausencia de permisos de render/publicación.
- [x] Añadir `tools/blackberry_edl.py` + pruebas `tests/test_blackberry_edl.py`: produce `EDL_PREVIA_12_ESCENAS.json` con intervalos, duración, visual propuesto y estado de derechos NO resueltos. No crea un video y no usa imágenes de terceros. Ambas comprobaciones están incluidas en `tools/production_preflight.sh` de Cloudflare.
- [ ] Completar auditoría factual humana del manuscrito largo: verificar contexto, comparabilidad y atribución de todas las frases; respaldar datos históricos con más de una fuente cuando proceda.
- [ ] Medir la voz real por escena contra el guion; ajustar duración y ritmo a **8–14 minutos**. No aprobar automáticamente una muestra de voz sin licencia comercial.
- [ ] Crear ilustraciones y visuales originales, garantizar derechos de música/narrador e implementar montaje reproducible; obtener **primer MP4 real verificable**, sin subida automática.
- [ ] Realizar prueba de aceptación del guion/archivos y del panel conectado con el propietario. Los tests solo demuestran estructura y código, no que esté listo para publicación.

**Estado:** guion narrativo largo y cronograma de edición redactados e integrados en `main`; hechos/editorial/licencias/audio/MP4 siguen pendientes. `docs/AVANCE.md` debe conservar evidencias de las ejecuciones para la próxima sesión.

## Hito de render técnico 2026-10-21 — primer MP4 verificable sin narración

- [x] Desarrollar `tools/render_blackberry_animatic.py`, un renderizador de **gráficos y títulos 100 % propios** en Pillow, utilizando `blackberry_edl.py` para representar las doce escenas con barra de progreso, identificadores de fuentes y aviso de no publicación. No descarga imágenes, voces ni música ajena. Exporta H.264 MP4 1280×720 a 24 fps mediante FFmpeg, **sin pista de audio**.
- [x] Crear workflow `.github/workflows/blackberry-previsual-mp4.yml` que instala Pillow 11.3.0 e imageio-ffmpeg 0.6.0 (FFmpeg empacado, sin dependencia del portátil), ejecuta 7 pruebas de guion/EDL, produce el MP4 y revisa duración/tamaño con el lector de metadatos. Quedó solo manual tras la primera ejecución positiva.
- [x] **Verificar una exportación real:** [GitHub Actions 39635649958](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39635649958) `success`, [artefacto MP4 12360967934](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39635649958/artifacts/12360967934). Archivo `BLACKBERRY_PREVISUAL_30S_SIN_VOZ.mp4`: **30,04 s, 1280×720, H.264, 204.427 bytes, doce escenas**, sin voz, sin música ni subida a YouTube. El archivo se descargó y validó además con `ffprobe` en el entorno de trabajo.
- [x] Resolver una dependencia faltante de FFmpeg en el ejecutor Linux de GitHub: primera corrida [39635497277](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39635497277) falló porque `ffmpeg` no estaba instalado; fue corregido usando `imageio-ffmpeg` y la segunda corrida es válida. No esconder el primer fallo.
- [ ] **Siguiente hito de producto real:** reemplazar tarjetas estáticas por escenas audiovisuales originales con movimiento/cámara y gráficos basados en hechos, generar la voz narradora con derechos comerciales aclarados, sincronizar audio y obtener un MP4 **de 8–14 minutos**, no solo una muestra de 30 s.
- [ ] Revisar hechos/citas de guion con un editor, comprobar fuentes audiovisuales y licencia del narrador, ensayar un MP4 largo **sin publicarlo** a YouTube; medir calidad antes de automatización general.

**Distinción obligatoria:** este es el primer video técnico REAL, no un documental profesional terminado. La duración de 30 s no es la duración del episodio planificado de 11:50. Todo desarrollo persiste en `main`.

## Corrección a partir de evaluación audiovisual — 2026-10-21

**Comentario del propietario:** «en el video: se muestra los textos y un fondo firme, y sin audio». Se reconoce que la previsual anterior fue una animática de tarjetas estáticas. **No cumpliría el estándar cinematográfico del canal.**

- [x] Mantener intacta la voz canónica del propietario `assets/voice/approved/narrador_documental_aprobado.mp3`, SHA256 `78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d`, duración 12,336 s, **aprobada para referencia editorial**, con licencia comercial aún pendiente. No cambiar por Piper o eSpeak.
- [x] Crear `tools/render_blackberry_motion_intro.py`: render de **297 fotogramas únicos**, 1280×720 a 24 fps, cuatro secuencias con teléfono/cámara móvil, nodos de comunicación, circuitos y cierre; banda sonora de la voz canónica sin recrear sus palabras. No emplea imágenes ajenas ni API de pago.
- [x] Crear `tests/test_blackberry_motion_intro.py`, con cuatro contratos incluyendo diferencias dentro de cada secuencia y verificación de hash de la referencia.
- [x] Ejecutar GitHub Actions [39636975142](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39636975142) **success**. Archivo `BLACKBERRY_INTRO_MOVIMIENTO_VOZ_REFERENCIA.mp4`, 12,33 s, 1280×720, H.264 + AAC, 1 623 429 bytes; 297 frames escritos, pista de audio decodificable y SHA original confirmado. [Artefacto temporal 12360694777](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39636975142/artifacts/12360694777). Descargado y verificado también con FFprobe; las cuatro escenas fueron inspeccionadas visualmente.
- [x] Corregir `.github/workflows/check.yml` para instalar Pillow 11.3.0 en pruebas base (la primera ejecución con el nuevo test falló por `ModuleNotFoundError: PIL`). Volver `.github/workflows/blackberry-motion-voice.yml` a **modo únicamente manual** después de la corrida exitosa.
- [ ] Avanzar de gráficos abstractos en movimiento a **escenas cinematográficas originales** y montaje continuo por actos, sin tarjetas de títulos como contenido principal.
- [ ] Generar narración real coherente con las 1.691 palabras del manuscrito completo usando la identidad vocal aprobada y consentimiento/licencia verificables; evaluar segmento a segmento dicción, coherencia y derechos. El MP3 aprobado **solo contiene 12,336 s de texto introductorio, NO narra el guion completo**.
- [ ] Renderizar un documental **de 8–14 minutos** con metraje y voz sincronizados, sin subir automáticamente a YouTube y solo después de revisión factual, editorial y derechos.

**Estado preciso:** intro de 12,33 segundos con movimiento y audio real = prueba superada; documental de 11:50 con voz y escenas cinematográficas = aún pendiente.

## Siguiente etapa de producción: primer capítulo con voz nueva comprobable (2026-10-21)

**Objetivo:** ampliar la introducción aceptada de 12,33 segundos a un tramo del manuscrito BlackBerry real, con narración nueva de la misma identidad de referencia, animación original y archivos para audición. Mantener siempre la rama `main`, sin servicios TTS pagados ni publicación automática.

- [x] Implementar `tools/qwen_blackberry_scene01.py`, que obtiene literalmente el texto de la escena 01 del manuscrito largo y lo divide en **cuatro** tomas seguras; validez de nombres, límites de caracteres y texto sin pérdidas. Conservar la referencia Qwen 1.7B en SHA `78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d`. Nuevas tomas mantienen estado pendiente.
- [x] Añadir `tests/test_qwen_blackberry_scene01.py` y workflow `blackberry-scene01-voice.yml` CPU limitado a una escena. GitHub CI [39639684664](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39639684664) aprobada. Primera generación real [39639684819](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39639684819) en ejecución al escribir este punto. No marcar MP3 nuevos como realizados sin ver su artifact.
- [x] Implementar `tools/render_blackberry_scene01.py`, que exige 4 MP3 con SHA conforme a reportes, texto exacto, referencia original sin cambios y minutos de audio dentro de límites. Secuencia propia con cambios de planos cada 5 segundos y animación real por fotograma, H264 + AAC, reportes y bloqueo de publicación; tests `test_render_blackberry_scene01.py`. CI [39640085857](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39640085857) exitosa.
- [x] Agregar `blackberry-scene01-video.yml`: recupera los MP3 únicamente desde la ejecución Qwen correcta, genera video con su longitud real y comprueba pista AAC/duración y 1280×720, sin tocar D1 o YouTube. El primer disparador automático es un acoplamiento acotado al éxito de la voz; después volver a manual.
- [ ] **Verificar entregables reales:** cuatro MP3, unión audible y primer MP4 de **escena 01**, duración exacta de voz y fotogramas distintos entre tomas. Descargar y escuchar; corregir si la voz o video falla. No sustituir éxito de código por archivos auténticos.
- [ ] Audición humana del propietario de las cuatro tomas nuevas, confirmar parecido con la referencia, dicción y ritmo antes de declarar identidad vocal aprobada. Los derechos comerciales continúan sujetos a evaluación aparte.
- [ ] Planificar ensayos de escenas 02–12 por lotes controlados, sin exceder memoria/minutos de GitHub Actions; reutilizar material si pasa QA en vez de regenerar indiscriminadamente.
- [ ] Completar aprobación histórica y fuentes, assets cinematográficos originales/licenciados, final de 8–14 min y validación audiovisual. **No** subir automáticamente a YouTube.

**Situación:** infraestructura, guion largo y prueba de intro están verificados; la nueva escena narrada y el documental completo aún no lo están. Ver `docs/AVANCE.md` para estado de corridas.

### Entrega audiovisual real — BlackBerry escena 01 — 2026-10-21

- [x] **Audio nuevo del guion real:** Qwen3 Base 1.7B CPU generó 4 MP3 en [39639684819](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39639684819), todos con referencia canónica y sin sustituir la voz. Duraciones: 15,840 + 13,632 + 11,448 + 14,568 s; unión **56,520 s** con pausas. [Artefacto 12365895069](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39639684819/artifacts/12365895069). 0 APIs de pago. **Audición y licencia comercial pendientes.**
- [x] **Video con esa misma narración:** [39641357257](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39641357257) `success`, [artefacto 12364518448](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39641357257/artifacts/12364518448). `BLACKBERRY_ESCENA01_CON_VOZ_NUEVA_REVISAR.mp4`: 56,500 s, 679 fotogramas animados, 1280×720, video H.264 y **audio AAC decodificable**. La duración fue medida y se inspeccionaron fotogramas de 2, 11, 23, 36 y 48 segundos. Sigue siendo previsual gráfica con planos que se reutilizan; no llamarlo montaje cinematográfico definitivo.
- [x] Descargar y verificar MP3/MP4 en entorno de trabajo. Los enlaces temporales de conversación contienen el MP3 unido `05_escena01_unida.mp3` y el MP4 de 56,5 s; no depender de esos enlaces para almacenamiento a largo plazo. Los artefactos GH son temporales.
- [x] **Programación completa 12 escenas:** `tools/blackberry_voice_schedule.py` y `research/blackberry/LOTE_AUDIO_VISUAL_12_ESCENAS.json` registran **56 fragmentos planificados** para 12 escenas, con reconstrucción textual exacta, ID y estado. Solo 4 de 56 tienen audio generado, **52 faltan**. El resto es planificación, no audios producidos.
- [x] Retirar disparadores de prueba automática de voz y montaje después de la exportación; `blackberry-scene01-voice.yml` y `blackberry-scene01-video.yml` quedan **solo manuales**, sin ejecución Qwen por push ni publicación.
- [ ] Evaluar auditivamente las cuatro tomas de la escena 01 contra la referencia y decidir correcciones antes de extender generación CPU a las demás. Los tests no certifican timbre, pronunciación ni legalidad.
- [ ] Sustituir visuales gráficos repetidos por planos originales más diversos con coherencia narrativa; montar capítulos 02–12 con voz consistente y fuentes revisadas.
- [ ] Comprobar derechos comerciales de voz, música e imágenes, QA audiovisual final y publicar manualmente solo cuando se apruebe un documental completo de 8–14 minutos.

**Medición concreta:** 12 escenas planificadas / 1 con MP4 real de 56,5 s; 56 tomas proyectadas / 4 generadas. Ninguna aprobación comercial ni publicación.

## Reorientación prioritaria — 2026-10-21

**Aclaración del propietario:** la meta final nunca fue que el asistente produzca cada episodio, sino que el **sistema Factor de Gigantes** realice todo el trabajo repetible. El prototipo BlackBerry debe ser una prueba y fixture de aceptación, no un proceso de producción artesanal ni dependencia permanente del chat.

- [x] Especificar en `docs/ARQUITECTURA_AUTONOMA.md` contratos, etapas del orquestador, límites de fuentes, derechos, costes y criterio medible de independencia.
- [x] Definir investigación como función de un **LLM de texto** intercambiable, distinta de Qwen3-TTS (solo narración).
- [ ] Evaluar en la plataforma `gemini_free` (API, sin pago activado y con clave configurada por canal seguro) frente a `qwen_local` (LLM ejecutado en GitHub Actions/CPU), usando exactamente las mismas fuentes y criterios de evidencia; Gemini no está todavía conectado ni se ha probado en la infraestructura.
- [ ] Implementar proveedor investigador/guionista y ejecución automática de **tema arbitrario sin que ChatGPT suministre documentos o prosa**, con auditoría de cada cita.
- [ ] Construir orquestación persistente desde D1 de investigación→guion→voz→escenas→MP4, con reintentos seguros, presupuestos, guardas editoriales y estados operativos visibles en el panel.
- [ ] Validar un episodio completo de 8–14 minutos generado por el propio sistema, no por redacción manual del asistente, y entregarlo para revisión. Publicación en YouTube por defecto deshabilitada.

**Condiciones explícitas:** no contratar ni activar facturación para Gemini sin autorización; modalidad gratuita no es una capacidad ilimitada, y puede usar datos para mejora del proveedor; solo fuentes públicas. Mantener `main`, el historial y los controles de licencia y veracidad.

## Prioridad P0 superior: detectar oportunidades y elegir automáticamente el siguiente episodio (2026-10-21)

**Nueva definición inequívoca del propietario:** la IA debe vigilar el mercado, descubrir y clasificar oportunidades de empresas e innovación, **elegir los mejores temas según un estudio real de mercado**, investigar exhaustivamente el elegido y pasar el resultado por los motores de voz, video y publicación YouTube. El propietario no introducirá un tema por cada episodio. ChatGPT construye y corrige el sistema, **NO actúa como productor manual recurrente**.

- [x] Adaptar `docs/ARQUITECTURA_AUTONOMA.md`: iniciar ciclo en radar, no en tema introducido manualmente; definir decisión, evidencias, feedback YouTube y subida automatizada **tras autorización editorial/OAuth**.
- [x] Crear `docs/INTELIGENCIA_MERCADO.md`, que fija fuentes, frecuencia configurable, señales, limitaciones, categorías, algoritmo inicial, etapas y condiciones de publicación.
- [x] Implementar `tools/market_radar.py`: valida muestras reales fechadas YouTube/Wikipedia, documentación primaria y antecedentes del canal; clasifica por demanda, movimiento, competencia relativa, fuentes y novedad. Devuelve **sin candidato** si los datos son insuficientes o caducados. La puntuación es heurística, no una promesa de rendimiento.
- [x] Implementar `tools/market_sources.py`: dos consultas limitadas a YouTube Data API por consulta de candidato, únicamente si existe clave en secreto, y ventana de 14 días mediante Wikimedia Pageviews; no hay estadísticas ni noticias inventadas. Pruebas en `tests/test_market_radar.py` y `tests/test_market_sources.py` con fixtures artificiales, sin pedir APIs. Preflight verifica ambas.
- [ ] Conectar un **descubridor autónomo** de nombres de empresas, acontecimientos y ángulos surgidos de señales recientes del nicho, sin catálogo fijo ni entrada manual. Enlazar YouTube Data API con cuota autorizada y Wikipedia verificando entidad/idioma; Google Trends solo si se concede acceso alfa.
- [ ] Ejecutar el **primer estudio de mercado en vivo**, con registros auditables de al menos tres candidatos, ranking, fuentes, fechas y motivos de descarte; ningún test simulado equivale a ese hito.
- [ ] Orquestar en D1 revisión y ejecución por estados desde selección automática, evidencia/guion Gemini o Qwen, voz, escenas originales y MP4, con reintentos y costos controlados.
- [ ] Completar OAuth de canal, metadatos, subtítulos y programador YouTube. **El sistema hará también la subida y publicación** de cada episodio aprobado; queda bloqueada la publicación sin autorización editorial/comercial y derechos válidos.
- [ ] Aprender de Analytics del propio canal y retroalimentar selección; no atribuir CTR/retención ajenos ni prometer viralidad.

**Estado real:** documentos, clasificador y colectores de señales implementados/probados con mocks; todavía no hay campaña de mercado real, descubrimiento continuo activado, selección autónoma operativa ni publicación YouTube. El piloto BlackBerry sigue siendo prueba del motor audiovisual, no una tarea que ChatGPT deba repetir cada semana.

### Avance P0 — Radar público diario funcionando (21 octubre 2026)

- [x] Primer descubridor `tools/topic_discovery.py`: recibe **rankings públicos completos de Wikimedia**, extrae entidades de Wikidata por P31 de empresa sin nombres aportados por el propietario ni por ChatGPT, con tope por consulta, idioma, fecha y respuesta, sin ejecutar guion o render.
- [x] Medición independiente en 14 días del artículo candidato, obtenida en una segunda consulta Wikimedia; eventos y mediciones provenientes de un proveedor real, no de fixtures.
- [x] Primera validación de red y datos auténticos: [39650844704](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39650844704) detectó Theranos en 240 artículos y 8 consultas Wikidata; [39651368713](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39651368713) agregó 291.435/55.952 visitas del artículo de Wikipedia en dos ventanas consecutivas de 7 días. Ver `research/market/VALIDACION_RADAR_2026-10-21.md`. Estas visitas **no son estadísticas de YouTube**.
- [x] Programar la fase de descubrimiento público con `.github/workflows/topic-discovery-smoke.yml` **una vez diaria** (10:17 UTC aproximados), sin consumo de modelos de pago ni publicación. Se conservó opción manual y se retiraron eventos por `push`.
- [ ] Incorporar fuente más inmediata de noticias empresariales y otras observaciones para descubrir varias oportunidades de tecnología/negocios (no solo compañías que estén en los 120 artículos más leídos por wiki).
- [ ] Obtener cuota/credencial autorizada para YouTube Data API y análisis de competencia/mercado hispanohablante, y conectar esas señales al selector. Si la clave no está configurada, bloquear decisiones basadas en una muestra inexistente.
- [ ] Persistir el radar en D1 con historial multi-día y completar la primera selección verificable de **mejor tema según estudio de mercado**, no solo una empresa candidata.
- [ ] Conectar Gemini/Qwen investigador para producir desde esa selección un dossier, guion, voz, visuales, MP4 y ciclo de YouTube **solo tras aprobar derechos/editorial**.

**No declarar completo el sistema de producción por la existencia de una ejecución de radar.** El dato es real; la clasificación empresarial solo abre una puerta a investigación; el ranking de mercado completo sigue bloqueado hasta YouTube/competencia y fuentes originales.

### Hito 2026-10-21 · Radar ampliado, dos empresas y migración de historial probada

- [x] Ampliar descubrimiento automático de 240 a **360 artículos** Wikimedia es/en por corrida, limitando a **12 lotes Wikidata** y 6 enriquecimientos de 14 días, sin claves ni servicios pagados.
- [x] Validar con datos públicos verdaderos en [39652155079](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39652155079): 2 entidades empresariales, Theranos y DuPont Corporation, con 2 series de 14 días completas. Datos y enlaces en `research/market/VALIDACION_RADAR_360_2026-10-21.md`.
- [x] Crear esquema **D1 aditivo 0004** para ejecuciones, entidades, visitas diarias, interés 14 días y decisiones de mercado; escribir `tools/market_persistence.py` y pruebas idempotentes/retrocompatibles.
- [x] Ejecutar [39652982369](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39652982369) `success`: snapshot **SQLite local**, 2 entidades, 2 observaciones y 2 series; conservar ZIP en artefacto temporal GitHub y verificar las tablas reales. La migración **NO se ha aplicado aún a Cloudflare D1 remoto**.
- [x] `.github/workflows/topic-discovery-smoke.yml` quedó solo **diario programado** (10:17 UTC sujeto a retrasos GitHub) y manual. No se ejecuta por cada push ni publica videos.
- [ ] Aplicar migración 0004 en D1 remoto con identificación y copia de seguridad verificadas; implementar endpoint autenticado e idempotente para guardar en producción series diarias.
- [ ] Incorporar fuentes más inmediatas e información de YouTube mediante credenciales con presupuesto autorizado; obtener y comparar **varios temas con demanda real en YouTube** antes de seleccionar un ganador.
- [ ] Conectar ranking→investigador Gemini/Qwen→guionista autónomo→TTS/escenas/video→QA→publicación YouTube tras autorización; el pipeline todavía no es automático extremo a extremo.

**Aclaración:** Wikipedia muestra interés en un artículo, no oportunidades ya verificadas para el canal. No se han inventado datos YouTube ni se ha iniciado una producción automática por observar Theranos o DuPont.


### Hito cumplido 21 de octubre de 2026 — radar con persistencia remota real

- [x] Descubrimiento autónomo de empresas desde rankings reales Wikimedia/Wikidata y primera medición independiente de 14 días.
- [x] Ampliación de cobertura a 360 artículos / 12 consultas de entidades, sin introducir una lista fija de compañías.
- [x] Migración D1 remota 0004 aplicada, cinco tablas de mercado confirmadas y tablas editoriales previas conservadas.
- [x] Flujo programado GitHub Actions → token OIDC efímero verificable → Worker → D1, sin secreto de larga duración para ingesta.
- [x] Primera ejecución integral [39658991775](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39658991775): 2 empresas, 2 observaciones y 2 ventanas guardadas en D1 real; cero selección editorial automática.
- [x] Panel privado con lectura de radar D1; desplegado desde `main`, pendiente comprobación de navegación autenticada.
- [ ] Cobertura adicional de fuentes de noticias y tendencias recientes, con registro verificable de procedencia.
- [ ] Datos observados de YouTube Data API y competencia hispanohablante, comparados entre varios temas mediante criterios explicables.
- [ ] **Decidir automáticamente el mejor tema con evidencia suficiente** y persistir la decisión; Wikipedia sola no acredita demanda.
- [ ] Producción original autónoma de 8–14 minutos con fuentes, investigación Gemini/Qwen, voz, visuales y control de calidad.
- [ ] Autorización editorial/legal, OAuth oficial y publicación por el sistema solo con permisos correspondientes.

**Importante:** se completó la infraestructura de descubrimiento y almacenamiento, **no** la productora autónoma ni el estudio de mercado de YouTube. Las etapas pendientes mantienen sus criterios de aceptación.


### Hito P0 cumplido 2026-10-21: radar informativo e histórico D1

- [x] Colectar noticias recientes **sin nombres de compañías preparados** mediante cuatro búsquedas RSS industriales y tecnológicas es/en, con registros de URL agregadora, medio atribuido, fecha y categoría.
- [x] Mantener tabla D1 separada de señales informativas con migración aditiva `0005_news_leads.sql`; preservar trabajos y expedientes anteriores.
- [x] Integrar consulta de noticias en GitHub Actions → Worker autenticado por OIDC → D1, con prueba real [39668778079](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39668778079). Primera corrida persistió **100 titulares** (límite de muestra), **no 100 oportunidades cualificadas**.
- [x] Panel autenticado para leer titulares recientes y puntuación de *relevancia temática preliminar*, calculada sin datos falsos ni LLM y con explicaciones.
- [x] Eliminar trigger `push` de prueba y conservar ejecución **diaria y manual**.
- [ ] Resolver y cotejar URLs originales de las noticias; buscar múltiples fuentes independientes y confirmar datos regulatorios/corporativos.
- [ ] Implementar estudio de **demanda y competencia en YouTube** con estadísticas realmente observadas; no confundir noticias, visitas Wikipedia ni puntuación de relevancia con oportunidad definitiva.
- [ ] Agrupar candidatos por empresas y eventos, registrar hipótesis y decisión de prioridad con razones, descartes, calidad de datos y revisión editorial.
- [ ] Conectar la oportunidad suficientemente verificada al motor de investigación Gemini/Qwen, dossier, guion, voz y video 8–14 min.
- [ ] Programación/subida oficial a YouTube **solo con autorización humana, derechos comprobados y OAuth**.

**Aclaración del progreso:** está avanzado el código y la infraestructura REAL del radar; el producto final sigue condicionado a investigación, calidad audiovisual, licencias y automatización de publicación segura.


### P0 · Entrega técnica 2026-10-21 — YouTube preparado y correlación real sin inventar mercado

- [x] Colector reutilizable `YouTube Data API v3` integrado al workflow con dos candidatas descubiertas × dos regiones hispanohablantes, límite explícito de llamadas gratuitas y omisión sin clave/permiso; sin publicar automáticamente.
- [x] Observaciones YouTube: migración D1 `0006`, API OIDC para escritura, lectura administrativa, panel, comprobaciones y tests CI. **0 registros reales YouTube aún**: no se declara estudio competitivo terminado.
- [x] Unión conservadora de titulares RSS con compañías canónicas Wikidata, migración D1 `0007`, workflow de correlación, API y panel. **Prueba integral `39673977211` exitosa** con dos empresas, 100 noticias evaluadas y 0 coincidencias textuales. No se inventaron vínculos.
- [x] Rollback del disparador `push` provisional usado en pruebas; `schedule`/manual y OIDC limitado, cero pagos y sin credenciales expuestas.
- [ ] Ejecutar YouTube Data API con clave y presupuesto gratuito expresamente aprobados en proyecto **sin facturación** y registrar vídeos auténticos por región.
- [ ] Corroborar identidad de empresa y fuentes originales de noticias y comunicados, evaluar varias oportunidades, persistir razones/descartes y seleccionar solo cuando exista evidencia suficiente.
- [ ] Habilitar pipeline investigador/guionista Gemini gratuito o Qwen local, producción 8–14 minutos con voz canónica y permisos, QA y OAuth/publicación solo tras aprobaciones.

**Criterio de aceptación pendiente:** la infraestructura YouTube y las coincidencias entre fuentes NO equivalen aún a un radar profesional que selecciona el mejor documental. Priorizar evidencias, comparación y decisión autónoma por delante de nuevas mejoras estéticas.


</details>
