# MERITUM-SENA

**Prototipo educativo local y web independiente** inspirado en la experiencia pedagógica de MERITUM, reducido para el proyecto de formación del SENA. Su modo local no requiere nube; la edición web se aloja en un servicio independiente, con PostgreSQL propia, sin APIs de IA.

MERITUM-SENA permite registrar reconocimientos mediante **Boscoins**, consultar el saldo, canjear recompensas simbólicas en **BoscoMarket** y publicar mensajes de aula. En modo local funciona con **SQLite**. En modo web funciona desde cualquier navegador autorizado, con una base **PostgreSQL exclusiva de Meritum-SENA**.

> **Importante:** Esta edición es académica, no equivale a la plataforma MERITUM institucional y no debe utilizarse con información real de menores. El despliegue web es exclusivamente una demo ficticia y requiere aplicar la guía de seguridad.

## 1. Requerimientos

- Windows 10/11, Linux o macOS; **Python 3.12 o 3.13** recomendado.
- 4 GB de RAM como mínimo (8 GB recomendado), 1 GB de espacio libre y navegador actualizado.
- Internet **solamente durante la instalación inicial** de Django; después puede funcionar sin conexión.
- El código usa **Django 5.2** y **SQLite**, que se crea automáticamente al ejecutar migraciones.

Consulta el alcance funcional y no funcional en [docs/REQUERIMIENTOS.md](docs/REQUERIMIENTOS.md).

## 2. Instalación en Windows (manual)

Abre PowerShell en la carpeta descargada o clonada y ejecuta:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py cargar_demo
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Abre <http://127.0.0.1:8000>.

**Alternativa en Windows:** haz doble clic en `INICIAR_WINDOWS.bat`. El archivo prepara el entorno, aplica las migraciones e inicia el servidor local.

### Cuentas ficticias de demostración

| Rol | Usuario | Contraseña (solo demo) |
| --- | --- | --- |
| Docente | `docente` | `DemoSENA2026!` |
| Estudiante | `estudiante` | `DemoSENA2026!` |

El comando `cargar_demo` prepara las cuentas y datos de prueba solo si faltan. No sobrescribe contraseñas existentes. Estas credenciales son **públicas y de laboratorio**: no las uses con información real.

## 3. Linux / macOS

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py cargar_demo
.venv/bin/python manage.py runserver 127.0.0.1:8000
```

## 4. Funcionalidades del MVP

- Inicio de sesión y cierre de sesión con Django Auth.
- Roles de **docente** y **estudiante**; no existe registro público.
- Docentes: otorgar entre 1 y 100 Boscoins por reconocimiento, crear recompensas y publicar anuncios.
- Estudiantes: consultar saldo e historial, leer anuncios y canjear recompensas con saldo suficiente.
- Registro de cada movimiento de la economía pedagógica (positivo al otorgar; negativo al canjear).
- Control básico de inventario y prevención de canjes sin saldo.
- Panel de administración de Django para un superusuario de desarrollo.

## 5. Administración de prueba

Para crear un administrador en tu propio computador:

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

Acceso local: <http://127.0.0.1:8000/admin/>. Para crear manualmente estudiantes, crea un usuario y luego un `Perfil` con rol `EST` desde el panel de administración. El superusuario puede entrar al panel docente sin perfil adicional.

## 6. Validaciones

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py test
```

La batería incluye permisos por rol, reconocimiento, consulta de saldo, canje, inventario y publicación.

## 7. Datos y copias

Toda la información local se guarda en `db.sqlite3`, excluido de Git. Para respaldarla, **detén el servidor** y copia `db.sqlite3` a un lugar seguro. Para reiniciar una demo de laboratorio puedes eliminar la base, ejecutar `migrate` y volver a cargar `cargar_demo` (esto borra cualquier dato anterior).

## 8. Qué no incorpora

Esta versión no contiene Ruta Kaizen, Ruta Saber, aXiomatic, AlgeBlocks, nivelaciones, módulos avanzados de evaluaciones, expedientes reales, fotografías, pagos ni conexión con MERITUM productivo.

**Documentación:** [Requerimientos del proyecto](docs/REQUERIMIENTOS.md) · [Arquitectura y flujo](docs/ARQUITECTURA.md)


## 9. Edición web independiente (opcional)

La rama estable puede publicarse en un **servicio Render distinto** conectado únicamente a este repositorio, con una **base PostgreSQL nueva**. Los estudiantes solo necesitarán el enlace y una cuenta de prueba; no instalarán Python.

- **No usar las credenciales públicas locales en Internet.** El servicio web genera las cuentas ficticias `docente_sena` y `estudiante_sena` con claves privadas configuradas en su propio entorno.
- El uso web requiere `MERITUM_SENA_DEBUG=false`, `MERITUM_SENA_SECRET_KEY` y `DATABASE_URL` de SENA; sin esos valores el servidor no puede arrancar.
- Para una exposición temporal, `MERITUM_SENA_DEMO_EFIMERA=true` permite ejecutar con SQLite efímera y datos ficticios, sin coste de base. Los cambios pueden perderse en reinicios; para persistencia usar PostgreSQL independiente.
- Guía paso a paso: [Despliegue online independiente](docs/DESPLIEGUE_ONLINE.md).


## Material para la exposición SENA

- [Guion de exposición para tres integrantes (5–7 min)](docs/GUIA_EXPOSICION.md)
- [Demostración guiada y plan de respaldo](docs/DEMOSTRACION.md)
- [Explicación sencilla de módulos y tecnologías](docs/EXPLICACION_TECNICA.md)
- [Requerimientos funcionales, técnicos y pruebas](docs/REQUERIMIENTOS.md)

### Cierre del sitio temporal

Una vez finalice la exposición, desactivar o eliminar **únicamente** el servicio y la base `meritum-sena-*` en Render. Conservar el repositorio GitHub y sus documentos como evidencia. Nunca eliminar `meritum-pilot` ni `meritum-pilot-db`, que pertenecen al sistema institucional.

### Verificación técnica de la demo web

La ruta `/salud/` comprueba que la aplicación y su base de datos responden. En el alojamiento gratuito el servicio emplea un trabajador Gunicorn y SQLite temporal, por lo que **los movimientos pueden reiniciarse** al reconstruir el servicio. Esta versión solo admite datos ficticios.

## Evidencias y validación docente (adaptación de MERITUM original)

La versión de exposición incluye el flujo **enviar → recibir → validar o solicitar ajustes → comentar → otorgar Boscoins**. Las correcciones se presentan como nuevas versiones; un mismo envío o evaluación no puede duplicar puntos. Los archivos son privados y los datos de la demo temporal pueden reiniciarse.

- [Referencia al módulo original y decisiones de adaptación](docs/ADAPTACION_EVIDENCIAS.md)
