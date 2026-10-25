# Aceptación real del episodio dirigido — 2026-10-25

Elección de prueba: **BlackBerry, por qué perdió su liderazgo en teléfonos y cómo cambió su negocio**. Se usan las funciones del runner del chat: identidad observada, búsqueda, análisis, revisión y guion. Codex no suministró fuentes ni prosa para acreditar autonomía.

| Ejecución | Trabajo real | Resultado |
| --- | --- | --- |
| [40207786180](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40207786180) | Tavily, Gemini y Groq | Tres pasajes de un documento/dominio, seis afirmaciones candidatas; guion bloqueado |
| [40208403147](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40208403147) | Continuación de fuentes y revisión, sin repetir Gemini/Qwen | Seis pasajes de dos documentos/dominios; revisión pendiente por comparaciones omitidas |
| [40214951196](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40214951196) | Solo revisión Groq de pasajes guardados; cero búsquedas/descargas | Matriz válida por pasaje; una afirmación incorpora apoyo de dos documentos independientes |

## Correcciones implementadas

- Expediente incompleto: completar contraste conservando las afirmaciones; no repetir el analista.
- Analista fallido: reutilizar los documentos descargados.
- Revisión pendiente: recuperar los pasajes guardados sin nuevas descargas.
- Guion fallido con investigación suficiente: continuar directamente el guionista.
- Identidad: usar artículo corporativo y sitios P856 observados; seguir enlaces reales a informes y dirigir la búsqueda primaria al dominio correspondiente.
- Panel: distinguir análisis, contraste, revisión y guion en el mensaje y el botón de recuperación.
- Diagnóstico: conservar respuestas por SHA del prompt y retirar el motivo de revisión pendiente después de una revisión correcta. La versión padre conserva su historial.

## Límites de la prueba

La última muestra aún carece de fuente primaria corporativa accesible dentro de la recuperación acotada. Cinco afirmaciones siguen sin segundo documento de apoyo. **No se generó un guion válido, un video ni una publicación.**

Las fuentes, Tavily, Gemini y Groq son reales; las reservas usan D1 real. Las funciones de persistencia editorial se ejecutaron contra **SQLite aislado en el artefacto**, no contra episodios de producción del propietario. Sigue pendiente el recorrido autenticado completo del Worker y su aceptación humana en el panel.

Qwen local no se ejecutó porque la prueba ligera no instala sus dependencias. Exa no se invocó por falta de confirmación de modalidad gratuita. Pausa general, automático, OAuth y autorización de publicación se conservan.

## Evidencia y continuación

[Artefacto final 12607275865](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40214951196/artifacts/12607275865), SHA-256 ZIP `c27a4f3ec3bde1c698167dda431094ccb1245029f04ca9d297cb4a10977e3099`. Retención: siete días. Incluye identidad, fuentes, investigación, respuesta Groq, resultado y base aislada para reanudar.

CI [40214918373](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40214918373) aprobado. Despliegue `1735f9b5-31ae-493f-aa51-e04b4273166d`, versión `2db3dd88-0e88-4516-97a6-8fe29d4ade5e`, al 100 %. Lectura del Worker confirma fases diferenciadas del checkpoint.

Siguiente trabajo: recuperar originales corporativos por rutas documentales observadas y contrastar las afirmaciones restantes, reanudando esta base. Solo entonces generar guion para revisión y continuar al video. No bajar umbrales ni interpretar un run exitoso como aceptación del episodio completo.
