# Licencias y procedencia de la narración — Factor de Gigantes

**Fecha de revisión inicial:** 2026-10-20. **Estado:** uso comercial de la identidad vocal **SIN autorizar**. Aplicar junto con `AGENTS.md` y `docs/PLAN_PROYECTO.md`.

## Hechos comprobados y fuentes primarias

1. **Modelo ejecutado localmente:** [Qwen/Qwen3-TTS-12Hz-1.7B-Base](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base). La ficha del repositorio oficial de modelos muestra `License: apache-2.0`. Consultar [archivos y revisión del modelo](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base/tree/main). La distribución Apache 2.0 del modelo **no sustituye** el examen de los derechos del material empleado para crear/condicionar voces sintéticas.
2. **Implementación y procedimiento de clonación:** repositorio original [QwenLM/Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS), con ejemplo oficial `generate_voice_clone(..., ref_audio, ref_text)` y opción de preparar un prompt reutilizable. En nuestro ensayo se carga localmente el modelo abierto y se condiciona con un MP3 validado por SHA, sin servicio TTS pagado.
3. **Voz canónica del canal:** `assets/voice/approved/narrador_documental_aprobado.mp3`, SHA-256 `78d872509f5401c097ee04fcad009337fa65a2a7752aabdcd46a9ed9ed465d4d`. Su procedencia interna está documentada en `assets/voice/approved/reference.json` y `docs/MOTOR_AUDIOVISUAL.md`: es una toma sintética generada mediante un flujo experimental de Qwen y posteriormente aprobada auditivamente por el propietario. **Aprobación de timbre no equivale a cadena documental de derechos comerciales.**
4. **Atención:** sitios de terceros con nombres parecidos a Qwen3-TTS pueden aplicar condiciones distintas a sus servicios. **No atribuir** condiciones de un servicio no oficial al repositorio del modelo Qwen ni a la demo pública que generó la referencia.

## Puertas obligatorias antes de publicar y monetizar

- [x] Modelo exacto identificado y licencia declarada Apache-2.0 en su ficha pública oficial.
- [x] Ejecución del modelo local sin API de síntesis facturable demostrada con logs de GitHub Actions.
- [x] Integridad de la toma canónica registrada mediante SHA-256 y fuente interna trazable.
- [ ] Guardar evidencia verificable de términos y autorizaciones **específicas del servicio/demo usado para generar la toma vocal inicial**, vigentes en el momento de creación, y del derecho a usar dicha salida como voz de marca comercial y referencia de síntesis posterior. Sin inferir automáticamente desde la licencia Apache del modelo.
- [ ] Confirmar procedencia y derechos del texto usado en el audio canónico y ausencia de voces de personas reconocibles sin autorización; documentar la comprobación por responsable editorial.
- [ ] Registrar las obligaciones efectivas de aviso, atribución y redistribución para los componentes (paquetes, pesos/modelo y otros materiales incluidos en entregables), cuando proceda.
- [ ] Comprobar derechos de música, imágenes, efectos, archivos de video y fuentes de cada documental.
- [ ] Confirmar evaluación audible de constancia de identidad vocal, naturalidad, pronunciación y derechos del resultado final antes de cambiar `render.yml`.

## Decisión operativa

Los artefactos de voz nuevos son **material de escucha privada/editorial**, no entregables aprobados para publicación ni un permiso comercial. No se activa un proveedor de pago, no se modifica la referencia canónica, no se conecta el clon experimental al render principal y no se publica en YouTube sin completar las puertas anteriores y recibir aprobación humana. La prioridad tras la prueba de tres párrafos es reducir deriva de timbre con el modelo local y cuantificar costos/tiempos bajo los límites gratuitos.
