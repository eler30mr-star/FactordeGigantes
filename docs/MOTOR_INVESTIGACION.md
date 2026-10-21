# Motor de investigación con IA — Factor de Gigantes

**20 de octubre de 2026. Estado técnico:** fuentes web, búsqueda autónoma por tema y Qwen 0.6B local en CPU **ejecutados y probados en GitHub**. Nunca debe confundirse un borrador con hechos o derechos verificados.

## Flujo técnico

1. **Tema libre:** python -m tools.research_engine --topic "Tema" --out dist/research. Busca artículos relevantes de Wikipedia, obtiene pasajes y plantea preguntas. Son fuentes SECUNDARIAS para orientación; luego deben localizarse y contrastarse fuentes primarias.
2. **Fuentes del episodio:** python -m tools.research_engine --dossier research/blackberry/expediente_preliminar.json --max-requests 6 --out dist/research. Visita HTTPS públicos con restricciones de DNS/redirección y captura fragmentos breves, URL original y final, hash SHA-256, índice y semejanza lexical con cada afirmación.
3. **Escritura por IA:** python -m tools.local_research_ai --report dist/research/reporte_investigacion.json --out dist/research --model Qwen/Qwen3-0.6B. Descarga el modelo abierto y lo ejecuta con PyTorch CPU en el propio runner (sin proveedor API de IA de pago). **Bloquea** la generación si no hay pasajes.
4. **Control de calidad:** redacta BORRADOR_IA_NO_VERIFICADO.md y metadatos_ia.json. Comprueba identificadores de fuentes, números ausentes en pasajes citados, duración y modelo. Las alertas son indicios: no certifican la verdad ni la licencia.
5. **Revisión:** un editor debe cotejar cada afirmación y cada recurso audiovisual antes de acreditarlos en el panel; jamás se aprueban fuentes o renderizaciones automáticamente.

## Cómo activarlo

En [Workflow del investigador IA](https://github.com/eler30mr-star/FactordeGigantes/actions/workflows/research-ai-cpu.yml), escoger la rama principal main y pulsar «Run workflow». Con el campo tema libre, investiga desde cero en fuentes secundarias. Campo vacío: usa el piloto de fuentes primarias BlackBerry. El ZIP de resultados se conserva tres días en GitHub Actions, sin publicación en YouTube.

El workflow es SOLO MANUAL para limitar minutos gratuitos. La integración al panel Cloudflare aún **no** está desplegada; D1 remota necesita migración 0002 y Cloudflare no respondió desde la conexión. No afirmar que este flujo se acciona ya desde el panel publicado.

## Prueba real de BlackBerry

- [GitHub Actions 39528648495](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39528648495): **success**.
- Resultado: **3 de 6 fuentes legibles**, otras 3 bloqueadas o no analizables; **5 pasajes candidatos** para 8 afirmaciones, todas aún pendientes de verificación humana; no inventó resultados para páginas bloqueadas.
- Qwen/Qwen3-0.6B (CPU) generó un borrador de 722 caracteres usando referencia [S01]. Paso de inferencia, incluida descarga del modelo: 1:08.66; memoria RSS máxima 4 781 824 KiB (~4,56 GiB). [Artefacto 12314626338](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39528648495/artifacts/12314626338).
- **Fallo editorial descubierto:** el borrador señaló que la salida a bolsa de RIM en Toronto fue el 10 de octubre de 1997, pero el texto de fuente S01 recuperado indicaba **28 de octubre de 1997**. El resultado NO es publicable y tampoco es un guion final.
- **Corrección en código posterior a esa prueba:** auditoría de números en tools/local_research_ai.py que alerta cuando una cifra no aparece en los pasajes de la fuente citada. [CI 39529112648](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39529112648) pasó pruebas unitarias con este caso concreto. El borrador ya generado es ANTERIOR al cambio, no se ha vuelto a sintetizar.

## Prueba real sin expediente manual

- [GitHub Actions 39529286991](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39529286991): **success**. Se introdujo únicamente el tema «BlackBerry» y el sistema recuperó 3 de 3 páginas secundarias, con **cero hechos verificados automáticamente**. Ninguna empresa, fecha, cifra o decisión se certifica por el hecho de encontrarse en Wikipedia.

## Restricciones y seguridad

- Hasta 12 URLs HTTPS y 750 KB por fuente; rechaza conexiones HTTP, hosts internos, credenciales en URL, IP privadas y redirecciones peligrosas. Respeta identificación del cliente para Wikimedia. No hay crawling masivo; páginas PDF, con sesión, JavaScript o protegidas se marcan como inaccesibles.
- Conserva únicamente fragmentos breves, metadatos y hashes; no distribuye textos de fuentes completos ni contenidos audiovisuales ajenos.
- Los reportes incluyen señales inequívocas: facts_verified_automatically=0, rights_verified_automatically=0, production_ready=false, youtube_publication_authorized=false.
- El modelo local puede alucinar incluso citando; su análisis NO sustituye verificación independiente, revisión humana, derechos de voz o evaluación de guion.

## Próximos hitos

1. Buscar fuentes primarias e independientes a partir del tema, incluida información financiera original, y extraer documentos PDF con citación de página.
2. Pasar del ensayo de investigación al flujo de un episodio dentro del panel y D1 una vez resuelto Cloudflare.
3. Ampliar calidad de síntesis de guion documental 8–14 min con datos verificados, voz única aprobada y derechos de material, antes del render.
4. Mantener sin proveedores pagos, sin OAuth ni subida automática.

## Integración desarrollada con panel y control de ejecución (2026-10-20)

- La nueva sección del panel en public/index.html y public/app.js ofrece un formulario «Investigar con IA» para escribir cualquier tema. Solicita una confirmación explícita antes de consumir minutos del runner y proporciona el enlace al workflow donde estarán los resultados.
- El Worker incluye GET y POST /api/research, protegidos por ADMIN_TOKEN. El módulo src/research-control.mjs valida temas, requiere GITHUB_DISPATCH_TOKEN exclusivamente en servidor, lanza ÚNICAMENTE research-ai-cpu.yml con ref main y entradas de tema. Nunca llama render.yml ni publica en YouTube.
- El esquema D1 0003_research_requests.sql registra cada solicitud, previene duplicados del mismo tema y día UTC mediante UNIQUE(topic_key,day_utc), y fija cuota nominal máxima de cuatro solicitudes/día. Los rechazos y resultados de red inciertos quedan registrados sin reintento automático. Un 204 de GitHub solo confirma aceptación de la solicitud.
- Pruebas Node: tests/test_research_control.mjs — límite, identidad de workflow, consentimiento, autenticación, deduplicación, fallo de red, 403, token ausente. Pruebas SQL: tests/test_editorial_migration.py valida el esquema 0003 y su unicidad.
- [E2E Worker+D1 local 39544778750](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39544778750): success. Migraciones 0001/0002/0003 aplicadas a D1 local aislada; rutas GET/POST verificadas sin PAT de GitHub para impedir gastos. CI Node/Python [39544634359](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39544634359): success.
- .github/workflows/research-ai-cpu.yml queda manual y usa el nombre de artefacto genérico factor-investigacion-ia-cpu; no se ejecuta automáticamente por el cambio.

**Pendiente operacional:** Cloudflare no proporcionó acceso a su API desde esta sesión, por lo que NO se aplicaron migraciones en producción ni se desplegó el panel. Consultar docs/DESPLIEGUE.md para migrar primero y probar allí la función. La investigación sigue siendo preliminar: las fuentes, guiones, licencias y voz requieren revisión antes del render.

## Consulta de ejecuciones y fuentes corporativas (2026-10-21)

### El panel puede localizar una ejecución real de GitHub

- El workflow `.github/workflows/research-ai-cpu.yml` admite `request_id` opcional y muestra ese identificador en `run-name`. El Worker envía el UUID original junto con el tema y la rama `main`.
- `src/research-control.mjs` consulta hasta 50 ejecuciones recientes del workflow al recibir `GET /api/research?runs=1`. Vincula **solo** `display_title` con UUID exactamente solicitado, `event=workflow_dispatch`, `head_branch=main` y URL oficial `https://github.com/eler30mr-star/FactordeGigantes/actions/runs/<id>`. Una solicitud `sent` nunca se interpreta automáticamente como terminada.
- El panel muestra `queued`, `in_progress` y `completed`, la conclusión de GitHub y el vínculo a la ejecución/artifacts. Sin permisos Actions:read, fallo HTTP o sin coincidencia, mantiene `run:null` e indica ausencia de confirmación. No se realizan consultas a GitHub sin acción del administrador sobre «Actualizar», salvo la revisión posterior a un envío expresamente confirmado.
- La lectura solo usa el token del Worker, no revela claves al navegador. Las ejecuciones muy antiguas pueden escapar de la ventana de 50 resultados; no está implementado un callback ni un estado persistente de finalización.
- Pruebas `tests/test_research_control.mjs`: correlación exacta, estados, fallos de API, URL falsa, rama equivocada y no confundir solicitudes con resultados. CI [39587493924](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39587493924) **success**. No se comprobó todavía esta función contra la D1 **remota** ni desde el panel publicado.

### Sitios oficiales desde el tema, sin URLs proporcionadas por el usuario

- `tools/primary_source_discovery.py` recorre resultados MediaWiki, consulta su `wikibase_item` y sigue la propiedad `P856` (sitio web oficial) de Wikidata, siempre por HTTPS y con comprobaciones de hosts públicos, tamaño de página y redirecciones usando el investigador existente. El objetivo es encontrar **candidatos** de fuente directa de organizaciones sin pedir al usuario sus enlaces.
- Tras un primer intento limitado a dos artículos sin resultados, se corrigió para inspeccionar hasta cinco entidades diferentes. [Prueba real 39588198172](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39588198172), `success`, encontró **1 candidato / 5 entidades** para el tema BlackBerry: artículo `BlackBerry Limited`, sitio Wikidata P856 `https://blackberry.com`.
- La página oficial quedó en `official_url_candidate` y su descarga **falló con ValueError**: NO se extrajo contenido de esa web. Los otros cuatro artículos no tenían P856 útil; la herramienta registró **cero hechos verificados**. [Artefacto 12340022602](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39588198172/artifacts/12340022602).
- La primera prueba [39587995688](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39587995688) comprobó que limitarse a dos entidades no bastaba. El workflow temporal fue restaurado a ejecución exclusivamente manual tras la segunda prueba.
- En el workflow normal `research-ai-cpu.yml`, los temas libres generan también `fuentes_oficiales_candidatas.json` si el servicio externo está disponible, sin marcar verificaciones y sin conceder permisos comerciales.
- No se supone que una página de Wikipedia pruebe qué web pertenece a una empresa, ni que un enlace P856 esté actualizado. Aún falta contraste de entidad, examen del contenido original y fuentes financieras independientes.

**Pendiente inmediato:** conseguir acceso fiable al sitio corporativo usando URL final HTTPS permitida o fuentes originales alternativas, enlazar páginas/archivos a afirmaciones concretas, y evaluar coincidencias y contradicciones sin otorgar permisos de publicación.


## Documentos PDF con evidencia por página — 2026-10-21

**Implementado en `main` y validado realmente.** La extracción de PDF se integró en el modo `--dossier` del investigador, no se limita a una utilidad aislada:

- `tools/pdf_sources.py` descarga documentos públicos HTTPS con los mismos controles DNS y redirecciones del motor original. Solo acepta HTML, texto, JSON o `application/pdf`; comprueba cabecera `%PDF-`, `Content-Length`, tamaño máximo **4 MB** para PDF, **35 páginas** por documento y presupuestos de texto/bloques. Usa `pypdf==5.9.0` en CPU, sin OCR, sin extraer imágenes ni redistribuir páginas completas. PDFs cifrados o demasiado grandes se rechazan.
- `tools/research_engine.py` usa el analizador conjunto de HTML/PDF. Cada fragmento candidato en PDF lleva `page` y `locator: PDF página N` junto con el SHA-256 del PDF, URL final e identificación del documento; esas ubicaciones aparecen también en `evidencia_para_ia.txt` para el borrador local Qwen y en `LECTURA_PRELIMINAR.md`. Las búsquedas en HTML conservan localizador de bloque web, no página inventada.
- `tools/pdf_probe.py`: `python -m tools.pdf_probe --url https://arxiv.org/pdf/1706.03762 --query "We propose a new simple network architecture the Transformer based solely on attention mechanisms dispensing with recurrence and convolutions entirely" --out dist/documento-pdf`. Genera `reporte_pdf_citado.json`, no descarga permanente del PDF.
- `tests/test_pdf_sources.py`: PDF simulado con **dos páginas** y texto diferente, verificando el localizador de página 2, compatibilidad con HTML, límites/errores y estados sin aprobación. CI general instala pypdf antes de la batería; el workflow de IA también lo instala antes de investigar.
- **Prueba real:** [Actions 39592681746](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39592681746), `success`. Descargó artículo original `Attention Is All You Need` de arXiv, extrajo **15 páginas, 328 bloques textuales y 2 fragmentos candidatos**, localizados en las **páginas 1 y 2** para la pregunta de prueba sobre Transformer/attention. Cero hechos marcados verificados. GitHub conserva temporalmente un artefacto de reporte, sin redistribuir el documento. [Referencia original](https://arxiv.org/abs/1706.03762).
- Prueba CI completa con el parser y sus contratos [39592490158](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39592490158): `success`. El workflow de ensayo externo volvió a **`workflow_dispatch` solamente** tras una corrida.

**Límites:** informes financieros de cientos de páginas, tablas complejas, PDFs escaneados o cifrados **NO** están resueltos. La versión actual detiene o limita ese contenido: no usar citas incompletas para aseverar cifras. Ni una coincidencia literal ni un SHA prueban verdad contextual, autoría o derechos comerciales. Cada afirmación aún requiere contraste independiente y revisión editorial.

**Siguiente mejora:** detección/descubrimiento autónomo de PDFs de organismos e inversores desde el tema, procesamiento acotado de grandes informes mediante selección de secciones y citas de tablas verificables, y comparación entre documentos primarios y secundarios. Sin APIs facturables.

## 2026-10-21 — Auditoría factual, escaleta 10 min y búsqueda SEC EDGAR

**Desarrollo incorporado en `main`:**

- `tools/editorial_audit.py`: el investigador genera automáticamente `AUDITORIA_EDITORIAL.json` y `ESCALETA_DOCUMENTAL_10MIN_NO_APROBADA.md` junto a `reporte_investigacion.json`, tanto en tema libre como en expediente. Señala ausencia de pasajes rastreables, único dominio de origen, dependencia de Wikipedia, cifras de la afirmación que no aparecen juntas en un extracto y años sin coincidencia. Detecta **posibles discrepancias**, no contradicciones demostradas. Revisión humana, veracidad y derechos siempre pendientes.
- La escaleta comprende **12 bloques y exactamente 600 segundos (10:00)**: apertura, contexto, ventaja, expansión, cambio, decisión, competencia, consecuencias, transformación y cierre. No redacta hechos ni inventa voz: coloca identificadores de afirmaciones candidatas y deja pendientes narración y visuales. No sustituye un guion de 8–14 min listo para locución.
- `tools/edgar_discovery.py`: camino de descubrimiento por tema `MediaWiki → Wikidata → P5531 (CIK) → SEC EDGAR submissions`. Extrae solo metadatos de formularios 10-K, 10-Q, 20-F, 40-F, 8-K y 6-K, con ID de archivo, formulario, fecha y URL de la SEC. Restringe CIK a diez dígitos, acccesion al formato regulatorio y nombre de archivo seguro; no descarga los informes ni reproduce páginas o gráficos. Wikidata P5531 es solo un candidato a identidad legal; cotejo de entidad/fecha/periodo y contenido sigue pendiente.
- Si SEC rechaza el acceso, el flujo guarda el CIK y un estado de consulta no disponible, **sin fabricar registros**. El flujo de Qwen desde panel continúa siendo manual/confirmado y `research-ai-cpu.yml` añade `sec_edgar_documentos_candidatos.json` solo cuando el tema libre lo permite. El experimento no emplea una API de IA de pago.
- Contratos `tests/test_editorial_audit.py` (5 casos) y `tests/test_edgar_discovery.py` (6 casos), incluidos en GitHub CI. Cloudflare Build `c6bfd5a1-3cd9-4201-b945-8d653f58f5a3` verificó **25 pruebas JS + 11 Python, 0 fallos**, desplegó el commit `cc90a481878d9e2c7ddca7c75dd1a28a09b73d71` desde `main` y reportó `success`, versión `c110910e-c4ac-4561-bb06-110c40be0fef`.
- Prueba externa SEC por tema `Apple Inc.` preparada en `.github/workflows/edgar-smoke.yml` sin carga de Qwen, video ni API de pago; **pendiente de revisar su ejecución**. No atribuir cifras ni documentos concretos a SEC sin obtener el resultado de esa ejecución.

**Límites deliberados:** actualmente SEC/Wikidata no devuelve pasajes citados de cada filing, solo posibles direcciones. El motor no comprueba filas de estados financieros ni coherencia entre ejercicios. Una advertencia de cifras no constituye desmentido. La investigación definitiva de un documental exige contrastar documentos auténticos y personas/identidades, cotejar sus extractos por página, completar 8–14 minutos y verificar derechos comerciales de narrador, música e imágenes.

**Próximo bloque:** leer de forma segura filings pertinentes e indexar párrafos y tablas por sección/periodo, crear comparador de cifras de una misma métrica con unidad y año, enlazar eventos a fuentes primarias y producir guion original completo bajo aprobación humana.

## 2026-10-21 — Métricas XBRL, discrepancias comparables y ruta alternativa a SEC

- `tools/financial_facts.py` incorpora lector de hechos de **SEC Companyfacts XBRL** para un CIK determinado. Descarga HTTPS solo del endpoint oficial `data.sec.gov/api/xbrl/companyfacts/CIK*.json`, con DNS/TLS y tamaño máximo 9 MB; no evade bloqueos HTTP. Filtra tags `us-gaap` explícitos, unidad USD, formularios admitidos, accession, fecha de presentación, fechas de inicio/fin y valores decimales finitos. Limita etiquetas/registros; guarda SHA-256. **No interpreta notas, tablas complejas ni cambia moneda.**
- La comparación solo agrupa por `entity_cik + metric + unit + period_kind + start + end`. Diferencias de años, trimestres, métricas o divisas **no** se catalogan como contradicciones. Dos valores para el mismo periodo generan `same_period_different_reported_values_review_required` y requieren verificar reexpresiones, entidad, alcance y documentos; nunca se infiere fraude, falsedad o aprobación.
- `tools/financial_probe.py` recibe `sec_edgar_documentos_candidatos.json`, prueba **un solo CIK candidato**, registra `METRICAS_SEC_CANDIDATAS_NO_VERIFICADAS.json` y, si SEC rechaza la consulta, conserva `sec_unavailable_or_unreadable` y tipo/código HTTP sin inventar cifras.
- `tools/editorial_package.py` combina `reporte_investigacion.json`, `AUDITORIA_EDITORIAL.json`, SEC/XBRL opcionales. Produce `EXPEDIENTE_EDITORIAL_PENDIENTE.json` y `EXPEDIENTE_PARA_REVISOR.md`: ID de afirmación, enlaces/páginas candidatos, carencias, diferencias numéricas y decisiones pendientes. **Cero hechos verificados; no autoriza narración, render ni YouTube.**
- `tools/official_document_links.py` proporciona alternativa de fuente al bloqueo SEC: desde HTML corporativo **ya obtenido** encuentra enlaces presentes a PDF, annual reports, informes financieros y páginas de inversores. No inventa URLs, no sigue enlaces y no confiere autoría o licencia. Si están en otro host, los etiqueta como externos; los archivos quedan sin descargar. `tools/primary_source_discovery.py` añade `linked_document_candidates` por entidad y total.
- `.github/workflows/research-ai-cpu.yml` añade pruebas de XBRL/expediente y, en temas libres, un paso de lectura XBRL no obligatorio; consolida el expediente **antes** del borrador Qwen. Nada activa render ni publicación automática.
- `tools/production_preflight.sh` centraliza el chequeo JS/Python del build de Cloudflare en código versionado. Pruebas `tests/test_financial_facts.py`, `tests/test_editorial_package.py`, `tests/test_official_document_links.py` y `tests/test_primary_source_discovery.py` incluyen periodos diferentes, SEC bloqueada, fuente SEC falsa, licencia pendiente y enlaces no existentes. CI [39625136678](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39625136678) `success`.
- **Prueba externa real 1:** [39621724636](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39621724636) halló un CIK candidato para Apple mediante Wikidata, pero el endpoint `data.sec.gov/submissions` devolvió `HTTPError`. No devolvió ningún filing legible ni contenido.
- **Prueba externa real 2:** [39624310668](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39624310668) usó el CIK conocido para probar Companyfacts. Resultado `sec_unavailable_or_unreadable` (`HTTPError`), **0 observaciones recuperadas y 0 verificadas**. La acción `success` significa que el diagnóstico funcionó, NO que SEC entregó cifras. Ambos workflows de smoke siguen solo manuales.
- Los resultados económicos de los tests proceden de **datos artificiales para validar el contrato**: nunca citarlos como cifras reales de Apple o BlackBerry. Fuente XBRL real / informe financiero contrastado aún **pendientes**.

**Próximo bloque:** buscar enlaces originales de informes que estén realmente disponibles, obtener un conjunto auténtico de métricas o tablas con sus unidades/periodos y contrastarlas; revisar identidad jurídica, fechas y cifras antes de redactar escenas. Después generar guion documental original de 8–14 minutos y audio/video únicamente con licencias validadas.
