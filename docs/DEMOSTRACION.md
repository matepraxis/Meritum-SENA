# Demostración en vivo — Meritum-SENA

Duración sugerida: **3 minutos**. Aplicación exclusivamente de laboratorio.

## Preparación (antes de la exposición)

1. Probar que la URL HTTPS abre desde el computador donde van a presentar.
2. Confirmar que las cuentas ficticias `docente_sena` y `estudiante_sena` pueden ingresar. Sus claves se entregan **fuera de GitHub**.
3. Tener abiertas dos sesiones independientes (dos perfiles del navegador o normal + incógnito).
4. Verificar que existan al menos 20 Boscoins de prueba y una recompensa con existencias.
5. Preparar capturas de ambas pantallas por si se cae Internet. No mostrar credenciales.

## Recorrido paso a paso

| Paso | Persona | Acción | Qué explicar |
|---|---|---|---|
| 1 | Docente | Ingresar | Cada persona tiene permisos distintos |
| 2 | Docente | Otorgar 10 Boscoins a `estudiante_sena` | El reconocimiento deja un registro con motivo |
| 3 | Estudiante | Ingresar o actualizar el inicio | El saldo aumenta y se ve el historial |
| 4 | Estudiante | Abrir BoscoMarket | Cada recompensa tiene costo e inventario |
| 5 | Estudiante | Canjear una recompensa disponible | El sistema resta saldo y disminuye existencias |
| 6 | Docente | Mostrar publicaciones | Se pueden compartir anuncios en el aula |

**Si la recompensa cuesta más que el saldo:** elegir otra, o entregar primero los Boscoins faltantes desde la cuenta docente.

## Comportamientos que conviene mencionar

- La contraseña no se guarda como texto visible, Django usa hashing.
- El estudiante no puede crear premios ni entregar Boscoins.
- No se pueden canjear premios sin saldo suficiente ni con inventario agotado.
- Un canje registra movimiento negativo y compra en una única operación.
- Los puntos son pedagógicos: no tienen valor monetario.

## Plan de contingencia

Si el alojamiento gratuito está inactivo puede tardar en responder. Abrir la página antes de empezar. Si no funciona, enseñar las capturas y explicar el flujo. No cambiar la configuración técnica durante la sustentación.
