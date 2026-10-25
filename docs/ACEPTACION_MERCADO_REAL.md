# Aceptación real del estudio YouTube — 2026-10-25

Esta prueba acredita búsqueda real y análisis Gemini; **no acredita selección automática calibrada ni el flujo completo hasta publicación**.

| Ejecución | Verificación | Resultado |
| --- | --- | --- |
| [40202682856](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40202682856) | Tres búsquedas generales y Gemini `gemini-3.5-flash-lite` (1.454 tokens entrada, 313 salida) | Tres candidatas; consultas por empresa y enfoque demasiado restrictivas |
| [40202996674](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40202996674) | Reutiliza descubrimiento e inferencia; tres consultas específicas de doce resultados y referencias de doce canales | Sin selección: evidencia comparativa insuficiente |
| [40203259358](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40203259358) | Reasocia evidencia general y específica, sin nuevas consultas ni inferencias | Sin selección: insuficiencia confirmada después de corregir asociación |

## Resultado final de la muestra

| Empresa | Videos largos comparables | Canales con suficientes referencias comparables | Motivo restante |
| --- | ---: | ---: | --- |
| Nikola | 3 | 0 | Faltan videos, referencias y rendimiento relativo consistente |
| Palm | 9 | 1 | Faltan referencias comparables de tres canales |
| TomTom | 11 | 0 | Faltan referencias y rendimiento relativo consistente |

Las empresas son propuestas editoriales; las hipótesis del analista no son hechos verificados para un guion. Las referencias deben ser del mismo canal, de edades y duraciones semejantes, excluyendo los videos del candidato. Haber consultado doce canales no significa disponer de doce referencias válidas.

## Correcciones comprobadas

- Consultar la empresa sin concatenar toda la hipótesis narrativa.
- Conservar los videos pertinentes hallados en consultas generales y específicas.
- Asociar nombres por palabras completas: Palm no coincide con Palmolive.
- Priorizar canales con más ejemplos observados para nuevas muestras.
- Reutilizar artefactos para no gastar otra inferencia o repetir búsquedas al corregir el comparador.

El último cambio de priorización de canales está probado por código, pero esta reevaluación conserva las referencias ya obtenidas; no se atribuye una nueva medición a ese cambio.

## Evidencia y continuidad

Artefacto final [12602503257](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40203259358/artifacts/12602503257), SHA-256 del ZIP `ce5b0d52c9f00105fb4972e929ef204012ca47ab8eb335baa655f5696d7ce838`. Incluye estudio, evaluación y diagnóstico; retención de siete días.

CI de la corrección [40203227146](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40203227146) aprobado. Cinco regresiones Python del estudio y 157 contratos Node aprobados en el bloque.

**Pendiente:** validar suficiencia de cobertura y referencias en otras muestras reales acotadas, sin bajar umbrales para obtener un ganador; después comprobar un episodio dirigido y uno automático hasta video y publicación autorizada. Un run de aceptación correcto significa que ejecutó y evaluó la muestra, no que aprobó al selector.

Automático apagado y pausa general conservados. No se crearon episodios, no se investigó profundamente a las candidatas, no se renderizó, subió ni publicó. Se retira del CI el disparador temporal por mensaje de commit; permanece la prueba manual explícita y reanudable.
