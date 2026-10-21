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
