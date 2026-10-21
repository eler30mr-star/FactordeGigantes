# Revisión del primer borrador IA — BlackBerry

**Fecha:** 2026-10-20 · **Ejecución real:** [39528648495](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39528648495) · **Artefacto:** [12314626338](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/39528648495/artifacts/12314626338)

## Lo que sí ocurrió

La herramienta automatizada consultó las seis fuentes originales del dossier, leyó tres páginas, obtuvo cinco pasajes lexicalmente relacionados con ocho afirmaciones candidatas, y generó un borrador de 722 caracteres usando Qwen/Qwen3-0.6B local (CPU). El texto no contiene una investigación económica completa; conserva el estado pendiente de revisión.

## Error detectado en la salida de IA

El modelo afirmó: «La empresa lanzó su IPO en el Toronto Stock Exchange el **10 de octubre de 1997**» [S01].

El pasaje efectivamente descargado de S01 (BlackBerry Investor Relations) en el mismo artefacto dice que la IPO fue el **28 de octubre de 1997**. Por tanto, esa fecha del borrador es una contradicción concreta, **NO un hecho aprobado**.

**Acción correctiva:** tools/local_research_ai.py añadió audit_numeric_support: compara tokens numéricos de cada línea con las cifras del fragmento citado y genera una lista de alertas en metadatos_ia.json. Las pruebas unitarias incluyen exactamente la discrepancia del día 10 frente al 28. Esa comprobación es una señal de posible error, no una verificación material. La primera ejecución se hizo antes del guardia y **no debe representarse como superada por la nueva auditoría**.

## Otros límites descubiertos

- S04, S05 y S06 resultaron bloqueadas/no analizables (categoría ValueError en el registro); no afirmar haber leído esas páginas ni extraído afirmaciones de ellas.
- No se accedió a informes financieros originales para reconstruir causalidad competitiva o cifras históricas de ventas.
- La IA concentró su narrativa en S01 aunque S02 y S03 resultaron legibles; falta ampliar diversidad y comprobar que el texto refleje evidencias múltiples.
- La voz y los elementos audiovisuales tienen licencias comerciales pendientes. Una narración anterior de 43,296 segundos aceptada por el propietario no implica aprobación del primer guion BlackBerry.

**Dictamen editorial:** borrador experimental con hechos incorrectos; útil únicamente para mejorar el motor. Bloqueo explícito de guion final, render comercial y publicación. Consultar docs/MOTOR_INVESTIGACION.md y docs/LICENCIAS_NARRACION.md.
