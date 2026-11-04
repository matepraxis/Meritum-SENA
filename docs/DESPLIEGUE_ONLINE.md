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

Render gratuito puede suspender los servicios inactivos y no garantiza que los archivos locales sobrevivan a un reinicio o nuevo despliegue. **Para la exposición temporal se permite SQLite efímera**, activando `MERITUM_SENA_DEMO_EFIMERA=true`. Los datos de demostración pueden desaparecer si Render reinicia o vuelve a desplegar; el comando de inicio recrea cuentas y datos ficticios. Si se requiere conservar avances o datos entre reinicios, usar una base PostgreSQL independiente. La PostgreSQL gratuita expira a los 30 días.

**Antes de crear servicios o bases de pago, confirmar precios, presupuesto y espacio de trabajo.**

## Crear servicio

1. Para una exhibición temporal, utilizar **SQLite efímera** y añadir `MERITUM_SENA_DEMO_EFIMERA=true` en las variables del servicio. **No configurar DATABASE_URL institucional**. Opcionalmente, utilizar una base PostgreSQL exclusiva de SENA si se necesita guardar progresos entre reinicios.
2. Crear un **Web Service** nuevo en Render desde `https://github.com/matepraxis/Meritum-SENA`, rama `main` después de fusionar el PR.
3. Runtime: Python. Región sugerida: Virginia.
4. Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`.
5. Start Command: `bash deploy/start.sh`.
6. Variables del **servicio nuevo**:
   - `MERITUM_SENA_DEMO_EFIMERA`: `true` en la muestra temporal. Si más adelante se usa PostgreSQL, desactivar esta bandera y configurar `DATABASE_URL` de la base **SENA**.
   - `MERITUM_SENA_SECRET_KEY`: secreto aleatorio largo, independiente.
   - `MERITUM_SENA_DEBUG`: `false`.
   - `MERITUM_SENA_DOCENTE_PASSWORD`: contraseña privada fuerte (14+ caracteres).
   - `MERITUM_SENA_ESTUDIANTE_PASSWORD`: contraseña privada distinta (14+ caracteres).
   - `PYTHON_VERSION`: `3.13.9` si la versión está disponible en Render o la versión estable 3.13 disponible.
7. Configurar `RENDER_EXTERNAL_HOSTNAME` automáticamente mediante Render; no se necesita abrir hosts con `*`.
8. Ejecutar el despliegue; `deploy/start.sh` verifica Django, aplica migraciones y crea **solo las cuentas ficticias**, sin cambiar las contraseñas de cuentas que ya existían. Gunicorn usa un solo trabajador para evitar bloqueos de SQLite en la demo.
9. Verificar la ruta pública `/salud/` (debe responder `OK`), y luego el inicio de sesión con `docente_sena` y `estudiante_sena`; publicar una prueba, otorgar 10 Boscoins y hacer un canje de demostración. Comprobar una nueva sesión y el CSS.
10. En modo **temporal**, avisar a los expositores que un reinicio puede restaurar la demo. No usar el saldo acumulado como evidencia permanente. En modo PostgreSQL debe persistir el saldo.

## Seguridad

- No publicar credenciales en GitHub, chats o capturas de la presentación.
- Solo se utilizan cuentas ficticias compartidas. No deben introducir datos de estudiantes reales.
- Compartir URL y claves por un canal privado y rotarlas cuando termine el ejercicio.
- Evitar acceso real de menores y fines productivos: es un prototipo educativo de laboratorio.
- No habilitar registro público ni configurar `is_staff` o `is_superuser` para las cuentas de demostración.
- La demo temporal puede perder sus cambios al reiniciar Render. La creación repetida de la demo no restablece contraseñas. Para rotarlas, usar operaciones seguras de administración de Django y documentar el cambio.
- Si se requiere uso en producción con personas reales: incorporar limitación de intentos de acceso, políticas de privacidad, permisos por grupo, auditoría, respaldos y revisión de seguridad.

## Diagnóstico

```bash
python manage.py check --deploy
python manage.py test
python manage.py makemigrations --check --dry-run
```

La edición local sigue funcionando mediante `INICIAR_WINDOWS.bat` con SQLite y DEBUG local. La web **no** modifica la base de datos de la otra aplicación.

## Comprobaciones añadidas en PR #2

- `GET /salud/` devuelve `OK` si la base de datos responde, o HTTP 503 si falla. No revela datos privados.
- En Render temporal, SQLite se ubica en el directorio temporal del sistema, no en el repositorio.
- Una sola instancia de Gunicorn atiende solicitudes para evitar escrituras simultáneas de la demo.
- Para reiniciar una demostración efímera, un nuevo despliegue puede restaurar los datos ficticios. Nunca guardar evidencias importantes únicamente en la demo.
- La integración continua simula arranque web (`DEBUG=False`) y comprueba migraciones, datos de prueba y carga de archivos estáticos.
