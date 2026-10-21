# Arquitectura: Meritum-SENA

## 1. Diseño general

**Django monolítico educativo + SQLite**: un proceso web local gestiona pantallas, reglas de negocio y persistencia. No existen microservicios, alojamiento cloud ni frontend separado.

```text
Navegador (http://127.0.0.1:8000)
           |
           v
   Django (config/urls.py)
           |
           v
     aula/views.py
      |         |
   Formularios   Validación de rol + sesiones
      |         |
      +---------+
           |
           v
    aula/models.py
           |
           v
      db.sqlite3
```

## 2. Entidades y relaciones

- **Usuario** (Django Auth): credenciales, nombre y sesión.
- **Perfil**: relación 1:1 con Usuario; rol DOC/EST y grado.
- **Movimiento**: estudiante 1:N movimientos; cantidad positiva/negativa; responsable y motivo.
- **Recompensa**: nombre, descripción, costo, existencias, activa.
- **Canje**: estudiante 1:N canjes y recompensa 1:N canjes; costo histórico aplicado.
- **Publicación**: título, contenido, docente responsable y fecha.

El **saldo** se calcula por suma de movimientos y no se guarda como campo editable. Un canje crea un movimiento negativo y un registro de canje dentro de la misma transacción.

## 3. Flujo de un canje

1. El estudiante autenticado envía un formulario POST con CSRF.
2. Django verifica rol EST y recompensa activa.
3. Dentro de una transacción, calcula el saldo disponible.
4. Si el saldo alcanza, realiza una actualización condicional de existencias (`existencias > 0`).
5. Registra el canje y el movimiento negativo; confirma la transacción.
6. Si alguna operación falla, el bloque atómico evita un canje parcial.

## 4. Organización de código

```text
Meritum-SENA/
├─ manage.py
├─ requirements.txt
├─ INICIAR_WINDOWS.bat
├─ config/              # Configuración y rutas
├─ aula/
│  ├─ models.py         # Entidades y saldo
│  ├─ forms.py          # Validaciones de entrada
│  ├─ views.py          # Autorización y reglas de negocio
│  ├─ admin.py          # Administración de laboratorio
│  ├─ tests.py          # Pruebas automatizadas
│  ├─ migrations/       # Esquema de SQLite
│  ├─ management/commands/cargar_demo.py
│  ├─ templates/        # HTML
│  └─ static/           # CSS
└─ docs/
   ├─ REQUERIMIENTOS.md
   └─ ARQUITECTURA.md
```

## 5. Decisiones y restricciones

- **Separación de roles:** no basta con ocultar botones; las vistas verifican los permisos en el servidor.
- **Protección básica:** Django Auth almacena hashes de contraseña, utiliza sesiones y CSRF.
- **Datos:** no se guardan credenciales en el código, excepto contraseñas conocidas para cuentas de demostración creadas bajo comando explícito.
- **Interfaz:** HTML y CSS servidos localmente, sin CDN ni JavaScript remoto.
- **Transparencia:** movimiento de Boscoins como asiento; no se permite editar desde el panel de administración.
- **Limitación:** los usuarios con acceso físico y de escritura a la base SQLite pueden modificar su contenido; no es un libro mayor antifraude.
