# Conectar el canal de Factor de Gigantes

La conexión oficial usa OAuth de Google. La clave YouTube del estudio de mercado no autoriza el acceso al canal ni una subida. El código de conexión está preparado; el consentimiento y las credenciales del cliente de Google siguen siendo del propietario. La revisión y subida privada están implementadas como acciones separadas; consulta [Subida privada](SUBIDA_PRIVADA.md). No hay publicación pública automática.

## Configuración concreta

En el proyecto Google Cloud que ya tiene YouTube Data API v3 habilitada, crea un **ID de cliente OAuth de tipo Aplicación web**. Configura la pantalla de consentimiento para la cuenta que administra el canal. Si la aplicación está en pruebas, añade esa cuenta como usuario de prueba.

Registra exactamente esta URI de redirección autorizada, sin barra final:

```
https://factor-de-gigantes.martin30-eler.workers.dev/oauth/youtube/callback
```

En Cloudflare → Workers & Pages → `factor-de-gigantes` → Settings → Variables and Secrets, guarda estos valores como **secretos** (así se conservan entre despliegues):

| Nombre | Valor |
|---|---|
| `YOUTUBE_CLIENT_ID` | ID del cliente web terminado en `.apps.googleusercontent.com`. |
| `YOUTUBE_CLIENT_SECRET` | Secreto de ese cliente web. No pegarlo en el chat ni en el repositorio. |
| `YOUTUBE_CHANNEL_ID` | ID `UC…` del canal correcto, copiado de YouTube Studio → Configuración → Canal → Configuración avanzada. No es el handle `@…`. |

`YOUTUBE_TOKEN_ENCRYPTION_KEY` se genera y configura de forma segura durante el despliegue. No reemplazarla si hay credenciales guardadas: una rotación requiere reconectar el canal. No se guarda en GitHub ni se entrega al navegador. No es necesario activar facturación para configurar este flujo.

## Consentimiento y resultado

Abre el panel, entra con `ADMIN_TOKEN` y usa «Canal YouTube → Conectar canal con Google». Google pide autorización de lectura del canal y subida de videos. El servidor comprueba que el canal devuelto coincide exactamente con `YOUTUBE_CHANNEL_ID`; una cuenta o canal distinto no queda conectado.

Al regresar al panel, vuelve a entrar con el token administrativo: permanece sólo en memoria y no se transmite a Google. «Actualizar conexión» muestra la conexión registrada y el canal, no las credenciales. Conectar no sube ningún video ni acredita derechos comerciales o revisión del documental.

La aplicación solicita acceso sin conexión y conserva el refresh token cifrado. En el estado **Testing** de Google, las autorizaciones con estos permisos pueden caducar a los siete días; no presentar ese modo como autorización permanente. La configuración de producción y la verificación que corresponda se realizan en Google. Google y el propietario pueden revocar el acceso.

«Desconectar canal» elimina credenciales y solicitudes pendientes del sistema e intenta revocar el acceso en Google. Si Google no confirma la revocación, el panel lo indica; también puede retirarse el acceso en la cuenta Google. Ningún fallo restaura credenciales eliminadas.

## Seguridad y aceptación

- Consentimiento iniciado exclusivamente por ADMIN mediante POST. La API del renderizador no tiene este permiso.
- Callback con state aleatorio, cookie Secure/HttpOnly/SameSite, PKCE y consumo de una sola vez con caducidad de diez minutos. No usa `ADMIN_TOKEN` en una URL.
- Verificador y credenciales cifrados con AES-GCM; secretos de cliente en Cloudflare. Ni API ni errores entregan access/refresh tokens al navegador.
- Renovación interna de acceso, sin ruta pública que devuelva credenciales; desconectar durante una renovación no resucita la conexión.
- Migración aditiva `0015_youtube_oauth.sql`, sin modificar expedientes, trabajos o aprobaciones.

Las pruebas locales usan respuestas Google simuladas para verificar el protocolo, errores y aislamiento. No equivalen a una cuenta Google conectada. La aceptación real requiere guardar el cliente, entrar a Google y conceder acceso al canal esperado. La cola de revisión, metadatos y subida privada por episodio están descritos en [Subida privada](SUBIDA_PRIVADA.md); conectar OAuth no concede esa aprobación ni habilita publicación.

## Fuentes oficiales consultadas

- [OAuth para aplicaciones servidor](https://developers.google.com/identity/protocols/oauth2/web-server).
- [Autorización servidor de YouTube](https://developers.google.com/youtube/v3/guides/auth/server-side-web-apps).
- [Consulta de canales](https://developers.google.com/youtube/v3/docs/channels/list).
