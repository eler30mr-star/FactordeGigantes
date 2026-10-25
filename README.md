# Factor de Gigantes — automatización documental

Repositorio oficial **eler30mr-star/FactordeGigantes**, rama de trabajo **main**. Panel: [Factor de Gigantes](https://factor-de-gigantes.martin30-eler.workers.dev).

El sistema descubre temas, conserva investigación y borradores citados en D1, exige revisión humana y prepara documentales originales en español. La conexión OAuth de YouTube está preparada; falta configurar el cliente y conceder acceso al canal. La subida y publicación requieren su integración y autorización por episodio.

## Entrega actual

- **Panel y API desplegados:** oportunidades de mercado, fuentes, equipo investigador, guion, expediente editorial, aprobación y seguimiento del montaje.
- **Motor genérico de episodios:** voz canónica Qwen3-TTS Base 1.7B CPU, tomas recuperables, gráficos originales por escena, MP4, capítulos, SRT/VTT, créditos, QA sobre archivo real y página de revisión. La generación final y la aprobación auditiva son verificaciones distintas.
- **Desarrollo sin gastar búsquedas de proveedores:** Codex preparó directamente el [guion citado de Theranos](research/theranos-development/GUION_PRUEBA_CITADO.md), con 1.600 palabras, ocho escenas y nueve fuentes. No se presenta como investigación autónoma de las otras IA.
- **Montaje técnico completo comprobado en GitHub:** [descargar video y material de revisión](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40163254722/artifacts/12587492309), 11:36, QA aprobada. **Contiene señal de audio técnica, no narración.** Artefacto temporal, retención de siete días.
- **Investigadores pausados** por indicación del propietario, incluidos cron y lanzamiento desde el panel. Su prueba integrada se habilita expresamente; la prueba final individual del narrador no los reactiva.

La prueba final de narración canónica se sigue en [Actions](https://github.com/eler30mr-star/FactordeGigantes/actions/runs/40163555937). Su inicio no equivale a generación completa, identidad vocal aprobada ni aceptación profesional. El estado verificado y los pendientes se registran en [AVANCE](docs/AVANCE.md).

## Operación y arquitectura

- [Conectar el canal YouTube](docs/CONEXION_YOUTUBE.md): cliente web, consentimiento, almacenamiento cifrado y límites de esta entrega.

- [Plan del proyecto](docs/PLAN_PROYECTO.md): objetivo, criterios editoriales y fases.
- [Producción de episodios](docs/PRODUCCION_EPISODIOS.md): montaje técnico, prueba final, recuperación de tomas y conexión al panel.
- [Configuración del equipo IA](docs/CONFIGURACION_EQUIPO_IA.md): proveedores, funciones y límites.
- [Despliegue](docs/DESPLIEGUE.md) y [QA audiovisual](docs/QA_AUDIOVISUAL.md).

Cloudflare Workers sirve el panel y la API; D1 conserva proyectos, evidencias y eventos. GitHub Actions ejecuta investigación y producción con permisos separados. FFmpeg y Pillow construyen los gráficos, subtítulos y exportaciones; Qwen usa la referencia aprobada sin sustituirla. El renderizador anterior (`tools/render.py`, Piper/eSpeak) permanece como previsualización histórica y no recibe los guiones autónomos canónicos.

No se necesita una laptop encendida ni n8n. La API no devuelve secretos y los tokens del panel y del renderizador tienen funciones distintas. Un resultado técnico no concede aprobación factual, licencias, identidad vocal ni permiso de publicación.

## Desarrollo

```bash
python -m pip install 'pypdf==5.9.0' 'Pillow==11.3.0'
python -m unittest discover -s tests -v
npm run check
```

CI también ejecuta los contratos Node, pruebas audiovisuales con FFmpeg y una comprobación de producción de sólo lectura. El motor requiere fuentes DejaVu. Los comandos de exportación y requisitos de la prueba final se detallan en [Producción de episodios](docs/PRODUCCION_EPISODIOS.md).

Los servicios gratuitos tienen límites: no se prometen cuotas ilimitadas. El narrador CPU no requiere una API de pago; las licencias de modelos, voz y recursos, la revisión del documental y el coste operativo siguen siendo comprobaciones separadas. No hay publicación automática en YouTube ni se almacenan contraseñas de Google.
