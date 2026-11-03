# Guía para exponer Meritum-SENA (5–7 minutos)

**Público:** docentes y jurados del SENA. **Objetivo:** explicar y demostrar un sistema web sencillo. Usar exclusivamente cuentas y datos ficticios.

## Reparto entre tres integrantes

### Integrante 1 — Problema y solución (1–2 minutos)
**Qué decir, con sus palabras:** «Queríamos que un docente pudiera reconocer el trabajo de un estudiante sin llevar cuentas en un cuaderno. Por eso desarrollamos Meritum-SENA: una aplicación web donde un estudiante acumula Boscoins por actividades y puede cambiarlos por recompensas simbólicas».

**Mostrar:** pantalla de ingreso y panel inicial. Aclarar que los Boscoins no son dinero real.

### Integrante 2 — Construcción y tecnología (1–2 minutos)
**Qué decir:** «La desarrollamos con Python y Django, que nos ayuda a manejar los usuarios, formularios y reglas de seguridad. Las páginas se muestran con HTML y CSS. Los datos se guardan en una base de datos. Para la demostración online usamos PostgreSQL. Separamos los permisos del docente y del estudiante».

**Mostrar:** el diagrama de [ARQUITECTURA.md](ARQUITECTURA.md) y las funcionalidades del panel docente. No es necesario memorizar código.

### Integrante 3 — Demostración, pruebas y cierre (2–3 minutos)
**Qué decir:** «Vamos a comprobar que el sistema funciona: un docente entrega Boscoins; un estudiante consulta su saldo y canjea una recompensa. El programa revisa que tenga puntos suficientes y que todavía queden existencias. También probamos que un estudiante no pueda entrar a funciones de docente».

**Mostrar:** el recorrido de [DEMOSTRACION.md](DEMOSTRACION.md).

**Cerrar:** «Este proyecto muestra cómo una necesidad educativa se transforma en una aplicación con usuarios, base de datos, reglas y pruebas. Es una versión académica, independiente de Meritum institucional».

## Cinco preguntas probables del jurado

**¿Qué problema resuelve?** Facilita el registro de reconocimientos y el seguimiento de puntos.

**¿Qué es Django?** Una herramienta de Python para crear aplicaciones web, gestionar usuarios, vistas y base de datos.

**¿Qué es una base de datos?** El lugar donde el sistema organiza y conserva usuarios, reconocimientos, premios y canjes.

**¿Por qué hay dos roles?** Porque el docente puede asignar Boscoins y publicar anuncios, pero el estudiante solo puede consultar y canjear.

**¿Qué pasa si el estudiante no tiene saldo?** El canje se rechaza; tampoco se permite comprar una recompensa agotada.

## Para la exposición

- Hablar de lo que entienden; no atribuirse funciones que el prototipo no tiene.
- Tener la URL probada, conexión a Internet y credenciales ficticias entregadas de forma privada.
- Llevar capturas de pantalla de respaldo si falla Internet.
- **No** compartir contraseñas ni datos reales en las diapositivas o el repositorio.
