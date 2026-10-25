# Revisión y subida privada

El canal OAuth conectado se utiliza únicamente cuando el propietario autoriza una exportación concreta. Registrar el canal y terminar el montaje no suben el episodio.

## Flujo implementado

1. `youtube-stage.yml` verifica el run canónico terminado de main, descarga el artefacto narrado, comprueba el ZIP, el SHA del MP4, las fuentes y el informe QA. Registra título, capítulos y descripción como borrador. No llama a Google ni a investigadores; tampoco concede aprobación humana.
2. En «Revisión final y subida privada», el propietario descarga y revisa el video, declara audiencia, comprueba voz/fuentes/derechos/gráficos/subtítulos/metadatos e identifica al responsable. Todas las casillas empiezan sin marcar. La aprobación queda vinculada al SHA exacto del video.
3. Una acción separada «Subir como privado» reserva una solicitud única y despacha `youtube-upload.yml`. No hay programación ni cambio a público.
4. El runner vuelve a verificar el mismo paquete y archivo aprobado. El Worker abre una única sesión reanudable de YouTube con privacidad `private` y notificaciones desactivadas. El runner transfiere fragmentos por el Worker: nunca recibe access tokens, refresh tokens ni la URL secreta de sesión.
5. Un corte de red provoca consulta del rango recibido y continuación de esa sesión. «Reanudar la misma subida» reutiliza la solicitud; un inicio de resultado incierto se bloquea para revisión, sin crear automáticamente otra sesión/video.
6. El Worker consulta a Google el resultado y comprueba ID, canal autorizado y privacidad antes de marcarlo como subido. Se muestra un enlace al video privado; no existe acción de publicación pública.

## Límites y roles

- ADMIN revisa y solicita la subida; RENDERER sólo registra o ejecuta solicitudes ya aprobadas.
- Credenciales OAuth y sesión se mantienen cifradas en D1. El cliente de entrega sólo conoce el broker oficial y su token de servicio.
- Reconectar un canal distinto, cambiar el archivo, omitir aprobaciones o declarar público bloquea el flujo.
- La descarga depende de la disponibilidad del artefacto de Actions. El paquete actual tiene siete días de retención; guárdalo. Un artefacto caducado no genera una nueva subida.
- Las pruebas de protocolo usan respuestas Google simuladas. La primera subida real necesita revisión y autorización del propietario. No se ha subido un video durante la implementación.

Migración aditiva: `0016_youtube_exports.sql`. El historial de registro, revisión y solicitud se conserva en `youtube_export_events`. Las tablas anteriores y el audio canónico no se sustituyen.

Documentación oficial: [subidas reanudables](https://developers.google.com/youtube/v3/guides/using_resumable_upload_protocol) y [videos.insert](https://developers.google.com/youtube/v3/docs/videos/insert).
