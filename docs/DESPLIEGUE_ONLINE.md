# Meritum-SENA — guía para desplegar en Render

## Objetivo

Publicar **Meritum-SENA** con URL propia, sin instalaciones en los equipos del SENA y **sin conexión a MERITUM institucional**. Usar exclusivamente datos ficticios, no almacenar nombres completos, fotos ni información de menores.

## Independencia obligatoria

- Repositorio: `matepraxis/Meritum-SENA`, no `meritum-platform`.
- Servicio web NUEVO: por ejemplo `meritum-sena-demo`. No cambiar el servicio Meritum existente.
- PostgreSQL NUEVO y privado de Meritum-SENA. **No copiar ni reutilizar el DATABASE_URL institucional**.
- Variables y contraseñas exclusivas de este servicio, jamás las de Meritum institucional.
- `MERITUM_SENA_DEBUG=false`. Sin API de OpenAI, sin Render Blueprint institucional.
- No ejecutar `cargar_demo` en Internet; se reservó a instalaciones locales.

## Costos y persistencia

Render gratuito suspende los servicios web inactivos y borra los archivos locales en cada reinicio/despliegue. **SQLite no es apto para este caso.** La base PostgreSQL gratuita expira a los 30 días y solo se permite una gratuita por espacio de trabajo. Para conservar los datos durante el semestre, usar PostgreSQL con un plan estable o proveedor externo de persistencia compatible.

**Antes de crear servicios o bases de pago, confirmar precios, presupuesto y espacio de trabajo.**

## Crear servicio

1. Crear una base **PostgreSQL nueva**, no conectada a MERITUM institucional, y conservar su URL interna privada.
2. Crear un **Web Service** nuevo en Render desde `https://github.com/matepraxis/Meritum-SENA`, rama `main` después de fusionar el PR.
3. Runtime: Python. Región sugerida: Virginia.
4. Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`.
5. Start Command: `bash deploy/start.sh`.
6. Variables del **servicio nuevo**:
   - `DATABASE_URL`: URL interna de la **nueva** base SENA.
   - `MERITUM_SENA_SECRET_KEY`: secreto aleatorio largo, independiente.
   - `MERITUM_SENA_DEBUG`: `false`.
   - `MERITUM_SENA_DOCENTE_PASSWORD`: contraseña privada fuerte (14+ caracteres).
   - `MERITUM_SENA_ESTUDIANTE_PASSWORD`: contraseña privada distinta (14+ caracteres).
   - `PYTHON_VERSION`: `3.13.9` si la versión está disponible en Render o la versión estable 3.13 disponible.
7. Configurar `RENDER_EXTERNAL_HOSTNAME` automáticamente mediante Render; no se necesita abrir hosts con `*`.
8. Ejecutar el despliegue; `deploy/start.sh` aplica migraciones y crea **solo las cuentas ficticias**, sin cambiar las contraseñas de cuentas que ya existían.
9. Verificar inicio de sesión con `docente_sena` y `estudiante_sena`; publicar una prueba, otorgar 10 Boscoins y hacer un canje de demostración. Comprobar una nueva sesión y el CSS.
10. Verificar que una actualización/reinicio no elimine el saldo: en la web debe persistir PostgreSQL, no SQLite.

## Seguridad

- No publicar credenciales en GitHub, chats o capturas de la presentación.
- Solo se utilizan cuentas ficticias compartidas. No deben introducir datos de estudiantes reales.
- Compartir URL y claves por un canal privado y rotarlas cuando termine el ejercicio.
- Evitar acceso real de menores y fines productivos: es un prototipo educativo de laboratorio.
- No habilitar registro público ni configurar `is_staff` o `is_superuser` para las cuentas de demostración.
- La creación repetida de la demo no restablece contraseñas. Para rotarlas, usar operaciones seguras de administración de Django y documentar el cambio.
- Si se requiere uso en producción con personas reales: incorporar limitación de intentos de acceso, políticas de privacidad, permisos por grupo, auditoría, respaldos y revisión de seguridad.

## Diagnóstico

```bash
python manage.py check --deploy
python manage.py test
python manage.py makemigrations --check --dry-run
```

La edición local sigue funcionando mediante `INICIAR_WINDOWS.bat` con SQLite y DEBUG local. La web **no** modifica la base de datos de la otra aplicación.
