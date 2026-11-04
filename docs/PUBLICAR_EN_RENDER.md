# Publicación temporal de Meritum-SENA en Render

## Requisito previo

Fusionar primero los PR #2, #3 y #4. El archivo render.yaml se prepara para la **demo temporal**, no se ejecuta por sí mismo ni modifica servicios existentes.

## Publicar

1. Abrir Render y crear un **Blueprint nuevo** desde el repositorio matepraxis/Meritum-SENA.
2. Revisar que el servicio que propone sea **meritum-sena-demo**, plan **free**, región Virginia.
3. En la configuración del Blueprint, establecer las tres variables que solicitan valores privados:
   - MERITUM_SENA_SECRET_KEY: clave aleatoria distinta de la institucional y de 50 caracteres o más.
   - MERITUM_SENA_DOCENTE_PASSWORD: contraseña fuerte, 14 caracteres o más.
   - MERITUM_SENA_ESTUDIANTE_PASSWORD: contraseña fuerte **diferente**, 14 caracteres o más.
4. La demo usa SQLite efímera, por lo que **no** hay que agregar DATABASE_URL ni crear una PostgreSQL para este servicio.
5. Confirmar que no se modificará ningún servicio o base de datos institucional.
6. Aplicar el Blueprint y ejecutar el primer despliegue si es necesario. Se han desactivado los despliegues automáticos.
7. Abrir la URL generada por Render y verificar /salud/ y el ingreso de las cuentas ficticias docente_sena y estudiante_sena.

## Ensayo mínimo

Otorgar Boscoins, consultar saldo, hacer un canje, publicar un anuncio y verificar desde el celular. Consultar el [checklist](CHECKLIST_EXPOSICION.md).

## Limitaciones

El plan gratuito puede suspenderse por inactividad. La base SQLite en el sistema de archivos efímero **no garantiza conservar datos** tras reinicios o nuevos despliegues. El comando de inicio reconstruye los datos ficticios si se pierden.

## Cierre

Después de la exposición, seguir [RETIRO_DE_LA_WEB.md](RETIRO_DE_LA_WEB.md). El repositorio queda como evidencia; no se toca Meritum institucional.
