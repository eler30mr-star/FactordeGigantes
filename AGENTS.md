# Reglas de desarrollo — Factor de Gigantes

Estas reglas se aplican a todo cambio posterior.

## Dirección técnica y editorial
1. Trabajar **exclusivamente en la rama principal `main`**: no crear ramas de trabajo salvo instrucción expresa del propietario.
2. No sustituir el producto por plantillas genéricas: código, interfaz y documentos deben responder a Factor de Gigantes.
3. Antes de cambiar código leer `docs/PLAN_PROYECTO.md`, `docs/AVANCE.md` y los archivos que se van a editar.
4. Mantener en `docs/AVANCE.md` un historial claro de: cambios realmente realizados, pruebas ejecutadas, bloqueos y próximo paso.
5. No marcar tareas completadas si solamente se han escrito archivos; distinguir commit, test, despliegue e integración real.
6. Prohibido exponer tokens, contraseñas, datos OAuth, cookies o credenciales de servicios externos.
7. No dar inicio automático a publicaciones en YouTube ni a campañas de contenido sin aprobación humana y políticas verificadas.
8. Seguridad por defecto: rutas protegidas, validación de entradas, separación de tokens de render y administración, permisos mínimos, registro de errores.
9. No utilizar contenido audiovisual sin licencia comprobada ni automatizar afirmaciones no verificadas.
10. Priorizar primero un pipeline probado de principio a fin; después calidad profesional, OAuth/YouTube, analítica y escalamiento.

## Punto de reinicio

Revisar sección «Próximas tareas prioritarias» en `docs/AVANCE.md` y confirmar en GitHub el estado actual antes de continuar.
