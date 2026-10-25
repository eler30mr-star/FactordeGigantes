# Publicar o programar el video revisado

El cierre del canal separa cuatro acciones: conectar Google, revisar el video exacto, subirlo como privado y autorizar su publicación o programación. Cambiar automático o elegir tema por chat no concede autorización para publicar.

## Permiso de Google

La conexión existente conserva lectura y subida privada. Para modificar la privacidad o programar un video se requiere además `youtube.force-ssl`, de acuerdo con [videos.update](https://developers.google.com/youtube/v3/docs/videos/update).

El panel ofrece **Ampliar permisos para publicar/programar** cuando el canal está conectado sin ese permiso. El propietario concede el acceso en Google. La petición es opcional: conectar normalmente conserva los permisos anteriores. El callback comprueba el permiso adicional cuando se solicitó y guarda únicamente los scopes realmente devueltos por Google. No reemplaza una conexión válida por un consentimiento incompleto ni entrega tokens al navegador.

## Autorización por video

Tras subir como privado un video con revisión completa:

1. Abrir su sección de publicación en el panel.
2. Elegir **Publicar ahora** o **Programar fecha UTC**. La fecha programada debe estar entre diez minutos y un año en el futuro.
3. Identificar al responsable y marcar la autorización explícita del archivo revisado.
4. Enviar la solicitud y comprobar el estado confirmado por YouTube.

El servidor exige el SHA exacto del MP4, la revisión de hechos/voz/derechos/metadatos, la subida privada terminada y el mismo canal OAuth. Verifica que el video siga siendo privado y sin programación ajena antes de reservar la operación. Actualiza solo `status`, conservando los valores editables existentes; no elimina título, descripción o etiquetas.

Google programa con `privacyStatus=private` y `publishAt` UTC. La publicación inmediata usa `privacyStatus=public`. No se introducen tareas cron para publicar videos sin autorización individual.

## Reintentos y límites

Cada solicitud tiene identificador persistente y registro de responsable, acción y fecha. La reserva evita envíos concurrentes. Repetir el identificador devuelve el resultado registrado; no vuelve a cambiar el video.

Si el resultado de red es incierto, **Comprobar publicación en YouTube** consulta el video sin repetir el PUT. Una operación rechazada explícitamente admite un nuevo intento autorizado; una operación incierta o confirmada no se duplica. El cambio de canal o desconexión impide continuar.

Los contratos usan Google simulado. Su aprobación técnica no demuestra consentimiento real ampliado, primera subida, publicación ni programación real. La entrega no publica el documental de desarrollo ni fabrica sus revisiones o derechos.
