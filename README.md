# MERITUM-SENA

**Prototipo educativo local** inspirado en la experiencia pedagógica de MERITUM, reducido para el proyecto de formación del SENA. No depende de Render, PostgreSQL, APIs de IA ni acceso permanente a Internet.

MERITUM-SENA permite registrar reconocimientos mediante **Boscoins**, consultar el saldo, canjear recompensas simbólicas en **BoscoMarket** y publicar mensajes de aula. La aplicación funciona en el navegador de un solo computador, guardando sus datos en **SQLite**.

> **Importante:** Esta edición es académica, no equivale a la plataforma MERITUM institucional y no debe utilizarse con información real de menores ni publicarse en Internet sin endurecimiento de seguridad y revisión legal.

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
