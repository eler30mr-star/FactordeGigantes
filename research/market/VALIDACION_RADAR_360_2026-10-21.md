# Factor de Gigantes · Segundo estudio exploratorio real: 360 artículos

**21 de octubre de 2026 · Solo detección y métricas Wikimedia, NO demanda YouTube validada**

## Evidencia ejecutada

- [GitHub Actions 39652155079](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39652155079): **success**; el descubridor inspeccionó 360 artículos populares en Wikipedia es/en y 12 lotes Wikidata; detectó 2 empresas y recuperó 2 series de 14 días.
- [GitHub Actions 39652982369](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39652982369): **success**; repitió el descubrimiento y escribió un **snapshot SQLite válido con esquema D1 compatible**, registrado como artefacto `fdg-empresas-descubiertas-wikimedia` (ID `12369113919`). Se descargó y verificó con SQLite: `market_runs=1`, `market_entities=2`, `market_pageview_observations=2`, `market_interest_windows=2`, `market_selection_decisions=0`. **No se migró ni escribió D1 remoto**.

## Datos observados (NO simulados)

| Empresa candidata | Wikidata | Artículo fuente | Vistas al artículo 14–20 oct | Vistas 7–13 oct |
|---|---|---|---:|---:|
| Theranos | Q16956307 | https://en.wikipedia.org/wiki/Theranos | 291.435 | 55.952 |
| DuPont Corporation | Q221062 | https://es.wikipedia.org/wiki/DuPont_Corporation | 3.512 | 338 |

La tabla se refiere a **visualizaciones de artículos de Wikipedia**, no a visitas de YouTube, búsquedas en Google ni rendimiento del canal. La fecha del ranking diario descubierto fue **18 de octubre de 2026**, con tres días de retraso deliberado para evitar datos incompletos. Estas cifras no convierten las entidades en empresas recomendadas para un documental; deben pasar por estudio competitivo, fuentes originales y análisis del público.

## Persistencia y futuro

- Migración `migrations/0004_market_intelligence.sql`: tablas aditivas `market_runs`, `market_entities`, `market_pageview_observations`, `market_interest_windows` y `market_selection_decisions`. No borra ni altera jobs, eventos, expedientes o peticiones existentes.
- `tools/market_persistence.py` valida fechas, IDs, URLs, host y series de 14 días; usa claves compuestas, inserciones idempotentes y transacciones. `tests/test_market_persistence.py` verifica duplicados, preservación del historial entre días, rechazo de datos falsos y compatibilidad con migraciones 0001–0003.
- El workflow diario `.github/workflows/topic-discovery-smoke.yml` ahora descubre empresas, mide interés y genera un archivo SQLite local como artefacto. **Cada ejecución diaria crea un archivo de cero: no es todavía un historial persistente multi-día en Cloudflare D1**. La carga remota controlada a D1 es el siguiente hito.
- Prohibido interpretar `market_unverified` como decisión de producir. Nadie ha aprobado o publicado material.

**ESTADO:** dos candidatas reales + mediciones verificadas + D1 schema y snapshot probados ✅. Competencia YouTube, ranking profesional, migración remota y documental autónomo aún pendientes.
