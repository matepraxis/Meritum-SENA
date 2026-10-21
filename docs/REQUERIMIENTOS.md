# Requerimientos del proyecto: MERITUM-SENA (MVP local)

**Versión:** 1.0 · **Fecha:** 21 de octubre de 2026  
**Tipo:** Proyecto académico demostrativo para formación SENA  
**Entorno:** Un computador personal; servidor local `127.0.0.1`; sin despliegue público.

## 1. Planteamiento del problema

En el aula se necesita un mecanismo digital sencillo para reconocer avances observables, consultar el historial de reconocimientos y hacer visibles metas formativas. El prototipo muestra cómo una aplicación web puede registrar transacciones en una base de datos y diferenciar permisos entre usuarios.

## 2. Objetivo general

Diseñar e implementar un prototipo web local de gestión de reconocimientos pedagógicos mediante Boscoins, con acceso diferenciado para docentes y estudiantes, un catálogo de recompensas y un módulo de comunicaciones.

## 3. Objetivos específicos

1. Desarrollar autenticación y autorización según roles.
2. Registrar estudiantes y reconocimientos de forma persistente.
3. Calcular saldos a partir de movimientos sin almacenar un saldo editable.
4. Permitir canjes únicamente con inventario y saldo suficientes.
5. Mostrar publicaciones docentes a los estudiantes.
6. Documentar instalación, estructura, seguridad y pruebas.

## 4. Requerimientos funcionales (RF)

| ID | Requerimiento | Actor | Criterio de aceptación |
| --- | --- | --- | --- |
| RF-01 | Iniciar y cerrar sesión | Ambos | Usuario autenticado accede; usuario anónimo se redirige a ingreso |
| RF-02 | Gestionar roles | Administrador | Un perfil define docente o estudiante; estudiante no entra a acciones docentes |
| RF-03 | Consultar panel docente | Docente | Muestra accesos a reconocimientos, recompensas y anuncios |
| RF-04 | Registrar reconocimiento | Docente | Selecciona estudiante, cantidad de 1 a 100 y motivo; queda movimiento positivo |
| RF-05 | Consultar saldo e historial propios | Estudiante | Saldo corresponde a suma de movimientos; no muestra historial de otros |
| RF-06 | Crear recompensas | Docente | Registra nombre, costo mayor que cero, unidades y estado activo |
| RF-07 | Consultar BoscoMarket | Ambos | Se ven recompensas activas con costo y existencias |
| RF-08 | Canjear recompensa | Estudiante | Con saldo e inventario disponibles, registra canje, débito y descuento de stock |
| RF-09 | Impedir canjes inválidos | Sistema | Saldo insuficiente o stock agotado no produce compra ni débito |
| RF-10 | Publicar mensajes | Docente | Crea título y contenido; aparece en aula |
| RF-11 | Ver anuncios | Ambos | Se listan anuncios recientes, sin permitir edición de estudiantes |
| RF-12 | Cargar datos ficticios | Equipo técnico | Comando crea docente, estudiante, recompensas y anuncio de prueba |
| RF-13 | Gestionar usuarios en administración | Superusuario | Permite crear usuarios y perfiles mediante Django Admin local |

## 5. Requerimientos no funcionales (RNF)

| ID | Requerimiento | Condición verificable |
| --- | --- | --- |
| RNF-01 | Ejecución local | Disponible desde `http://127.0.0.1:8000` sin servicios cloud |
| RNF-02 | Base de datos | SQLite en archivo `db.sqlite3`, excluido del repositorio |
| RNF-03 | Autenticación | Contraseñas procesadas mediante hashing de Django; sesiones protegidas |
| RNF-04 | Autorización | Acciones docentes denegadas a estudiantes (HTTP 403) |
| RNF-05 | Integridad | Canje con `transaction.atomic`, inventario actualizado condicionalmente y registro de movimiento |
| RNF-06 | Usabilidad | Interfaz responsiva para escritorio y celular; mensajes de error y confirmación |
| RNF-07 | Mantenibilidad | Python, Django, app modular `aula`, documentación y pruebas |
| RNF-08 | Privacidad | Solo datos ficticios; sin recopilación real de menores ni APIs externas |
| RNF-09 | Instalación | Un archivo `requirements.txt`, migraciones y comando de carga de demo |
| RNF-10 | Alcance de red | Servidor ligado a `127.0.0.1` por defecto; no accesible desde Internet |

## 6. Requerimientos técnicos del computador

| Componente | Mínimo | Recomendado |
| --- | --- | --- |
| Sistema operativo | Windows 10 de 64 bits, Linux o macOS | Windows 11 |
| Procesador | Doble núcleo | Cuatro núcleos |
| RAM | 4 GB | 8 GB |
| Almacenamiento libre | 1 GB | 2 GB |
| Python | 3.12 o 3.13 | 3.13 |
| Navegador | Chrome, Edge o Firefox actualizado | Versión vigente |
| Internet | Para descargar Python y dependencias | No necesario tras instalar |
| Base de datos | SQLite (integrada con Python) | SQLite |
| Editor de código | Cualquier editor | Visual Studio Code |

> Requisito de licencias: se emplean Python, Django y SQLite, sin servicios comerciales obligatorios para la demo.

## 7. Reglas del negocio (RN)

- **RN-01:** Solo el docente o superadministrador puede crear un reconocimiento.
- **RN-02:** Cada reconocimiento suma de 1 a 100 Boscoins.
- **RN-03:** El saldo es la suma de los movimientos de cada estudiante; no se edita manualmente.
- **RN-04:** Un canje descuenta exactamente el costo vigente al momento del canje.
- **RN-05:** No se permite saldo negativo derivado de canjes normales.
- **RN-06:** El inventario nunca se reduce por debajo de cero.
- **RN-07:** Solo los estudiantes pueden hacer canjes.
- **RN-08:** Los Boscoins son una unidad pedagógica, no dinero ni criptoactivos.
- **RN-09:** Esta versión no comparte datos con la plataforma MERITUM institucional.

## 8. Historias de usuario

**HU-01:** Como docente, quiero otorgar Boscoins a un estudiante por una actividad para reconocer una evidencia pedagógica.  
**HU-02:** Como estudiante, quiero ver mi saldo e historial para comprender mi progreso.  
**HU-03:** Como estudiante, quiero canjear recompensas disponibles para usar los Boscoins acumulados.  
**HU-04:** Como docente, quiero publicar anuncios para comunicar actividades.  
**HU-05:** Como administrador, quiero gestionar usuarios para demostrar permisos diferenciados.

## 9. Casos de prueba para sustentación

| Prueba | Pasos principales | Resultado esperado |
| --- | --- | --- |
| CP-01 | Ingresar como docente y otorgar 30 Boscoins | Nuevo movimiento +30 y saldo actualizado |
| CP-02 | Entrar como estudiante y abrir ruta docente | HTTP 403, no se registra cambio |
| CP-03 | Intentar canje con 0 Boscoins | Mensaje de saldo insuficiente, sin movimiento |
| CP-04 | Canjear con 40 Boscoins un premio de 20 | Saldo 20, stock -1, canje registrado |
| CP-05 | Intentar canjear premio sin existencias | Operación rechazada |
| CP-06 | Ejecutar `python manage.py test` | Todas las pruebas unitarias deben terminar correctamente |
| CP-07 | Desconectar el equipo de Internet tras instalar | Se puede iniciar sesión y usar funcionalidades locales |

## 10. Alcance excluido y limitaciones

**No incluido:** integración con producción, IA, gamificación avanzada, simulaciones, calificaciones oficiales, pagos, nube, acceso por múltiples instituciones, sincronización, auditoría certificada, recuperación automática de contraseñas y aplicaciones móviles nativas.

**Límite de concurrencia:** SQLite es apropiada para una demostración local de baja concurrencia. El sistema no ha sido endurecido ni probado para producción, ni para transacciones en paralelo a gran escala. Antes de un despliegue real sería necesario proteger claves y sesiones, cambiar `DEBUG`, usar HTTPS, validar la gestión de datos personales, ampliar auditorías y ejecutar pruebas de concurrencia reales.

## 11. Entregables del equipo SENA

1. Código fuente funcional y organizado en GitHub.
2. Documento de requerimientos y descripción de arquitectura.
3. Manual de instalación y ejecución local.
4. Base de datos local construida mediante migraciones y datos de demostración.
5. Evidencia de ejecución de pruebas y capturas de uso.
6. Sustentación de roles, arquitectura, reglas del negocio y flujo de canje.

## 12. Fases sugeridas de trabajo

- **Fase 1 — Análisis:** problema, objetivos, requerimientos y casos de uso.
- **Fase 2 — Diseño:** modelos de datos, navegación, permisos y bocetos.
- **Fase 3 — Construcción:** autenticación, Boscoins, BoscoMarket, publicaciones.
- **Fase 4 — Pruebas:** casos funcionales, controles de acceso y corrección de errores.
- **Fase 5 — Sustentación:** demostración local, documentación y aprendizajes.
