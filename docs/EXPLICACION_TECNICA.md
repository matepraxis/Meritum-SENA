# Meritum-SENA explicado de forma sencilla

## Qué construimos

Meritum-SENA es una **aplicación web académica**. Un docente otorga puntos llamados Boscoins por reconocimientos. Cada estudiante ve su saldo y puede canjear recompensas simbólicas. También existe un espacio para publicaciones.

## Tecnologías utilizadas

| Tecnología | Para qué sirve |
|---|---|
| Python | Lenguaje con el que se programa la lógica |
| Django | Framework que gestiona pantallas, usuarios, formularios y reglas |
| HTML | Estructura de lo que aparece en las páginas |
| CSS | Apariencia de la interfaz |
| SQLite | Base de datos de la edición instalada en computador |
| PostgreSQL | Base de datos exclusiva cuando se usa la versión online |
| GitHub | Guarda el código y la documentación con control de versiones |
| Render | Servicio que puede alojar la demo online |

## Cómo funciona una petición

1. El usuario abre una página o envía un formulario.
2. Django comprueba si está autenticado y tiene permisos.
3. El programa valida los datos y aplica las reglas.
4. Se consulta o actualiza la base de datos.
5. El usuario ve un resultado o un mensaje.

## Tablas principales

- **Usuario:** cuenta para iniciar sesión.
- **Perfil:** indica si es docente o estudiante.
- **Movimiento:** registra cuántos Boscoins se suman o restan, cuándo y por qué.
- **Recompensa:** registra costo y cantidad disponible.
- **Canje:** registra qué recompensa tomó cada estudiante.
- **Publicación:** mensaje creado por un docente.

## Reglas importantes

- Los puntos no son dinero real.
- Solo el docente puede asignar Boscoins.
- El saldo se calcula sumando los movimientos: no se modifica a mano.
- Los canjes requieren saldo y existencias suficientes.
- El sistema separa acciones permitidas por tipo de usuario.

## Qué NO es este proyecto

No es la plataforma institucional Meritum, no usa sus cuentas ni su base de datos. No administra notas oficiales, dinero ni información real de menores. Es una prueba de concepto para exponer los temas aprendidos en el SENA.

## Material de apoyo

- [Requerimientos funcionales y no funcionales](REQUERIMIENTOS.md)
- [Arquitectura y entidades](ARQUITECTURA.md)
- [Guía para la exposición](GUIA_EXPOSICION.md)
- [Demostración en vivo](DEMOSTRACION.md)
- [Publicación y retiro de la versión online](DESPLIEGUE_ONLINE.md)
