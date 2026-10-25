# Estudio de oportunidades YouTube — versión 2

El ciclo busca oportunidades del nicho en YouTube. Solo maneja metadatos de videos y una comparación editorial; no descarga ni reutiliza contenido audiovisual de terceros ni investiga hechos de todas las empresas.

## Orden y presupuesto

1. Reservar el estudio del día en D1, solo con automático encendido, investigadores habilitados y ningún episodio activo.
2. Buscar con tres consultas del nicho, sin lista fija de empresas. Guardar IDs, títulos, canales, fechas, vistas y duración de los resultados observados.
3. La IA gratuita propone dos o tres empresas y enfoques a partir de los títulos. No puede introducir nombres no observados. Se registra proveedor/modelo; requiere reserva de cuota D1 y modalidad gratuita confirmada.
4. Buscar metadatos comparables de cada propuesta. Consultar publicaciones recientes de hasta cuatro canales por propuesta, máximo doce canales, para obtener una referencia habitual independiente de los videos candidatos.
5. El Worker recalcula la comparación y conserva consultas, métricas, candidatos, razones, descartes y límites. El cliente no puede imponer un ganador enviando un score.
6. Antes de guardar una elección, verificar nuevamente modo y revisión. Un apagado o cambio concurrente cancela la elección; un episodio creado por el propietario nunca se reemplaza.

Máximo 32 llamadas YouTube y siete búsquedas por ejecución; el recorrido actual utiliza hasta seis búsquedas. No son unidades de cuota garantizadas: la cuota real depende de YouTube. Máximo cien videos observados y diez referencias de publicaciones por canal. Antes de cada consulta y del análisis IA se vuelve a consultar el permiso efectivo del propietario. La clave no se imprime ni se guarda en informes.

## Criterios iniciales y límites

Para comparar una empresa se exigen al menos cuatro videos de 5–30 minutos, publicados hace 2–90 días; al menos dos ejemplos de los últimos treinta días; observación desde dos consultas distintas; y cuatro comparaciones de rendimiento con al menos tres canales que tengan tres referencias comparables cada uno. Las búsquedas nuevas filtran formato medio; los Shorts no se mezclan con el documental.

La referencia por canal usa la mediana de visitas divididas por antigüedad, entre publicaciones con entre la mitad y el doble de duración y antigüedad entre un tercio y tres veces la del video evaluado. Se excluyen de su propia referencia los videos candidatos. La mediana de las razones de rendimiento debe superar 1,3. Un solo video excepcional no basta. Las empresas tratadas en los últimos treinta días se descartan.

Puntuación inicial versionada: 65 % rendimiento relativo normalizado y acotado, 20 % diversidad de canales y 15 % ejemplos recientes. Deben existir al menos dos empresas con comparación suficiente antes de elegir. Los datos repetidos, caducados, sin procedencia o incoherentes se rechazan. Si no hay evidencia suficiente se conserva un resultado sin selección.

Son parámetros iniciales sujetos a calibración, no una demostración de viralidad. El promedio de visitas por edad no mide crecimiento. La muestra no revela demanda total, CTR, retención ajena ni saturación de todo YouTube. Se conserva el razonamiento editorial y la afinidad con el nicho como hipótesis explícita, separada de las métricas.

## Puertas operativas

- `FINAL_AI_INTEGRATION_ENABLED=0`: conserva la pausa previa del propietario; no inicia el estudio ni llamadas IA.
- Automático apagado: no reserva ni consulta oportunidades. Las instrucciones del propietario continúan siendo una entrada separada.
- `YOUTUBE_SELECTOR_VALIDATED` ausente o distinto de `1`: el estudio queda como **calibración**, sin crear episodio automáticamente. Habilitar solo después de revisar muestras reales, sus descartes y el ajuste al nicho; no cambiar umbrales para forzar un ganador.
- La selección crea un episodio `selected`, no una aprobación factual, un render autorizado ni permiso para publicar.

La fase `opportunity` del workflow `topic-discovery-smoke.yml` ejecuta este recorrido, y el horario diario llama a la misma fase lógica. El radar Wikimedia anterior continúa retirado. El panel permite consultar el estudio y sus motivos. La conexión del episodio seleccionado a investigación/guion/producción sigue siendo un bloque independiente y no se acredita solo por disponer de una puntuación.
