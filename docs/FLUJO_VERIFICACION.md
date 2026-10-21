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

## Integración implementada en `main` — pendiente de migrar y desplegar en Cloudflare

El Worker `src/worker.js` importa `src/editorial.mjs` y expone rutas **protegidas por `ADMIN_TOKEN`**:

- `GET /api/jobs/:id/dossier`: leer expediente y estado de verificación.
- `PUT /api/jobs/:id/dossier`: guardar/editar durante `draft` o `review`; cada guardado **revoca** la acreditación anterior y comprueba que las fuentes del guion estén representadas.
- `POST /api/jobs/:id/dossier/attest`: solo durante `review`, con `confirmed:true`, revisor identificado, fuentes enlazadas a todas las afirmaciones, cada afirmación marcada `verificada` y revisada por una persona, y licencia de todos los activos declarada `verificado` (incluido uno de tipo `voz`).
- `POST /api/jobs/:id/approve` y `POST /api/jobs/:id/dispatch`: rechazan con HTTP 409 si no existe expediente acreditado y estructuralmente completo. En caso de solicitud de cambios, la acreditación se invalida.

El panel incluye una sección «Fuentes y licencias» para editar el JSON del expediente, guardarlo y registrar la acreditación del editor, sin dejar tokens persistidos en el navegador. **La interfaz permite administrar evidencias, no investiga ni abre automáticamente los enlaces.** El estado `verificada` es una declaración editorial y debe reflejar una comprobación real.

La base de datos incorpora `migrations/0002_editorial_dossiers.sql`, por lo que **el despliegue en Cloudflare depende de aplicar esa migración a la D1 remota**. Ver `docs/DESPLIEGUE.md`; hasta que esto se ejecute y se compruebe el sitio, solo hay integración validada por CI, no integración verificada en producción.

Las pruebas `tests/test_editorial_gate.mjs` comprueban autenticación, guardado, revisión, revocación, bloqueo de render y ausencia de la tabla; `tests/test_editorial_migration.py` comprueba restricciones e integridad SQL en SQLite local. Superar las pruebas **no concede derechos de publicación**.

## Integración pendiente con la plataforma

1. [HECHO EN CÓDIGO] Tabla D1 `editorial_dossiers` con JSON del expediente, revisor y fecha de acreditación mediante migración `0002`, sin modificar `0001_initial.sql`. El esquema granular de `research_sources`, `claims`, `claim_evidence`, `asset_licenses` sigue siendo una futura mejora para búsqueda y analítica.
2. [HECHO EN CÓDIGO / NO DESPLEGADO] Edición de expedientes, revisión y derechos en el panel privado y API, con eventos auditables.
3. [PENDIENTE] Aplicar migración a D1 real, desplegar Worker+assets y ejecutar el flujo de integración autenticado completo.
3. Asociar las afirmaciones verificadas al guion aprobado antes del render, sin reemplazar la validación humana por una etiqueta técnica.
4. Al iniciar un documental real de 8 a 14 minutos, registrar cada dato, atribución, visual y derecho comercial antes de abrir la puerta a OAuth/YouTube.

## Restricciones

Repositorio `main`, cero servicios pagos, cero subida automática, ningún video ajeno sin licencia. No presentar el ejemplo de guion hipotético de la audición Qwen como investigación factual de una empresa real.
