# Investigación con trazabilidad por afirmación — Factor de Gigantes

**Fase 2 del plan maestro.** Este procedimiento evita convertir en documental datos empresariales sin pruebas. El código está en `tools/editorial_evidence.py`; las pruebas en `tests/test_editorial_evidence.py`.

## Contrato editorial vigente

Cada episodio real debe responder una pregunta concreta y conservar el enlace entre **cada afirmación material** y la evidencia identificable que respalda su versión final.

- `title`: título de investigación; `thesis`: enfoque y pregunta.
- `sources`: al menos dos fuentes con identificador único `S01`, URL HTTPS, entidad publicadora, fecha de consulta y tipo primaria/secundaria.
- `claims`: afirmaciones con ID `C01`, texto concreto, evidencia asociada a `source_id`, ubicación precisa `locator` dentro del documento, estado `pendiente`, `verificada` o `rechazada` y revisor humano cuando corresponda.
- `assets`: recursos audiovisuales con `kind` (imagen, video, música, voz, gráfico), descripción y `rights_status` (`pendiente`, `verificado`, `rechazado`).
- `publication_authorized: false` obligatorio en expedientes de investigación. Un documento validado **jamás** habilita por sí mismo subir contenido.

Un ejemplo de una `evidence` estructural (los identificadores deben existir en `sources`):

```json
{
  "id": "C01",
  "text": "Una afirmación empresarial concreta que necesita respaldo documental.",
  "evidence": [
    {
      "source_id": "S01",
      "locator": "Informe anual, sección y página pendientes de completar",
      "status": "pendiente"
    }
  ]
}
```

**No confundir formato con verificación:** el validador comprueba estructura, referencias cruzadas y estados, pero no abre las páginas ni comprueba que una cita demuestre lo afirmado. `verificada` solo puede asignarla un editor después de consultar el material original; no se asignará automáticamente por IA ni por validación sintáctica.

## Cómo verificar un expediente

```bash
python -m tools.editorial_evidence ruta/al/expediente.json
python -m unittest discover -s tests -p test_editorial_evidence.py -v
```

El reporte separa afirmaciones revisadas, pendientes y activos sin derechos; `can_release_documentary` siempre es falso, incluso si una estructura se presenta como completa, hasta contar con un proceso de publicación autorizado independiente. **La ausencia de errores de estructura no demuestra veracidad, originalidad ni licencia.**

## Integración pendiente con la plataforma

1. Diseñar tablas D1 para `research_sources`, `claims`, `claim_evidence` y `asset_licenses` mediante una nueva migración versionada, sin tocar `0001_initial.sql`.
2. Conectar edición de citas, identificadores, estado de revisión y derechos al panel privado de Cloudflare. Mantener permisos administrativos y auditoría de cambios.
3. Asociar las afirmaciones verificadas al guion aprobado antes del render, sin reemplazar la validación humana por una etiqueta técnica.
4. Al iniciar un documental real de 8 a 14 minutos, registrar cada dato, atribución, visual y derecho comercial antes de abrir la puerta a OAuth/YouTube.

## Restricciones

Repositorio `main`, cero servicios pagos, cero subida automática, ningún video ajeno sin licencia. No presentar el ejemplo de guion hipotético de la audición Qwen como investigación factual de una empresa real.
