# Checklist final — exposición Meritum-SENA

## Antes de fusionar
- [ ] PR #2 aprobado: arranque estable en Render.
- [ ] PR #3 aprobado: interfaz adaptada a celular.
- [ ] PR #4 aprobado: prueba integral y archivo render.yaml.
- [ ] Fusionar en orden #2, #3 y #4; volver a ejecutar las pruebas en main.

## Antes de publicar
- [ ] Crear **un servicio nuevo**, llamado meritum-sena-demo, desde matepraxis/Meritum-SENA.
- [ ] Seleccionar el plan gratuito en Render.
- [ ] Usar únicamente datos y cuentas ficticios.
- [ ] No conectar DATABASE_URL de Meritum institucional.
- [ ] En modo temporal usar MERITUM_SENA_DEMO_EFIMERA=true y DEBUG=false.
- [ ] Configurar una clave de Django privada, larga (50+ caracteres), y dos contraseñas distintas (14+ caracteres). Nunca subirlas a GitHub.
- [ ] Verificar que el sitio responde por HTTPS, que /salud/ funciona y que se muestran los estilos.

## Ensayo con el equipo
- [ ] Docente entra y otorga 10 Boscoins.
- [ ] Estudiante entra y ve los 10 Boscoins.
- [ ] Estudiante canjea una recompensa y se actualiza el saldo.
- [ ] Se impide que un estudiante haga acciones de docente.
- [ ] Se puede crear y consultar una publicación.
- [ ] Se ve bien desde celular y computador.
- [ ] Tener capturas de respaldo sin credenciales visibles.

## Al terminar
- [ ] Guardar las evidencias de la exposición.
- [ ] Retirar solo el servicio web temporal meritum-sena-demo.
- [ ] Si existe meritum-sena-demo-db y ya no sirve, retirarla por separado.
- [ ] Conservar el GitHub del proyecto SENA.
- [ ] Confirmar que meritum-pilot y meritum-pilot-db no fueron modificados.

**Nota:** SQLite temporal puede reiniciarse y perder los cambios. No guardar información real ni oficial.
