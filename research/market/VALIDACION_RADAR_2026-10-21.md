# Factor de Gigantes — primer descubrimiento real del radar

**Fecha de comprobación:** 21 de octubre de 2026 (UTC).  
**Resultado:** prueba del **descubridor**, no estudio completo de mercado ni elección de episodio.

## Ejecuciones auditables

- [Prueba externa inicial 39650638377](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39650638377): falló por límite local de lectura del ranking Wikimedia (1 MB). **No se trató como señal confirmada**.
- [Primera ejecución real válida 39650844704](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39650844704): éxito. 240 artículos populares de Wikipedia (es/en), 8 lotes Wikidata y 1 entidad candidata de tipo empresarial.
- [Segunda ejecución con interés de 14 días 39651368713](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39651368713): éxito, igual cantidad de artículos y entidades, **1 serie de interés diario completa**. Artefacto de GitHub `fdg-empresas-descubiertas-wikimedia` (retención limitada; archivo descargado y comprobado).

## Candidata descubierta sin lista manual

- **Entidad:** Theranos. Wikidata `Q16956307`.
- **Origen:** ranking público diario de artículos de Wikipedia en inglés del **18 de octubre de 2026**, consultado el 21 de octubre, con desambiguación y tipo empresarial Wikidata P31. El radar examinó artículos tanto en español como en inglés, pero la candidata procede de una señal de la Wikipedia inglesa.
- **Trazabilidad:** https://en.wikipedia.org/wiki/Theranos y https://www.wikidata.org/wiki/Q16956307 .
- **Métrica real de Wikimedia Pageviews:** `views_last_7d=291435` (14–20 octubre 2026) y `views_previous_7d=55952` (7–13 octubre 2026), obtenidas mediante API Wikimedia en la ejecución 39651368713.
- **Interpretación limitada:** aumentó el interés por el artículo, pero NO implica la misma variación en búsquedas Google, demanda de documentales, probabilidad de clics o retención de audiencia en YouTube. No supone que Theranos deba ocupar la primera posición.
- **Faltan:** muestra de videos comparables de YouTube (y su evolución temporal), análisis de competencia, originalidad del enfoque, relevancia para audiencia hispanohablante, validación de documentos primarios y disponibilidad de material audiovisual legal. Ningún documental ha sido encolado automáticamente a partir de esta señal.

## Automatización instalada

El workflow `.github/workflows/topic-discovery-smoke.yml` quedó con `schedule` de **una ejecución diaria** (10:17 UTC programados por GitHub; la ejecución exacta puede retrasarse) y opción manual. **No hay ejecución por push, servicios de pago, publicación YouTube ni generación de Qwen desde este workflow**. Wikimedia publica el ranking diario con retraso, por eso el descubridor consulta la jornada de tres días antes y complementa con 14 días de visitas reales.

## Próximo bloque que sí falta construir

1. Ampliar la detección con señales de noticias empresariales actuales y estudios de YouTube para tener varias entidades/temas, no depender de Wikipedia en solitario.
2. Conectar YouTube Data API mediante secreto con cuota autorizada, obtener muestras y contexto de competencia del nicho, y verificar disponibilidad de documentos originales. En caso de falta de cuota o API, no fabricar puntuaciones.
3. Crear un expediente de decisión de mercado trazable para varios temas y guardar historial/estados duraderos en D1; el artefacto diario temporal por sí solo no da trazabilidad permanente.
4. Conectar selección calificada a Gemini/Qwen para investigación, guion y producción, con aprobación editorial y de derechos antes de publicar.

**Estado:** descubrimiento real ✅ · medición Wikimedia 14 días ✅ · radar diario configurado ✅ · selección de mejor tema en YouTube ❌ · video autónomo ❌ · YouTube ❌.
