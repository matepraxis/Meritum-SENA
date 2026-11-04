# Adaptación del módulo de evidencias de MERITUM original

**Referencia de código:** repositorio `matepraxis/meritum-platform`, módulo `evidence/` (y `coins/services.py`).

Meritum-SENA no reconstruye el flujo desde cero: **adapta el proceso existente** a la escala del proyecto académico, manteniendo la independencia del sistema institucional.

| Meritum original | Adaptación SENA |
|---|---|
| `evidence.models.Evidence` y estados `pending/received/approved/rejected` | `aula.models.Evidencia` con los mismos estados |
| `EvidenceSubmissionForm` | `EvidenciaForm`: título, descripción, PDF o imagen y token de envío |
| `submit_evidence` | `subir_evidencia`: envío idempotente |
| `receive_evidence_view` | `recibir_evidencia`: recepción docente |
| `EvidenceReviewForm`, `EvidenceReview` | `EvaluacionEvidenciaForm`, `EvaluacionEvidencia`: decisión, comentario y puntos |
| `evidence.services.review_evidence` | `evaluar_evidencia`: transacción atómica entre decisión, comentario y Boscoins |
| `resubmit_evidence` | `reenviar_evidencia`: nueva versión solo si se solicitaron ajustes |
| `evidence_attachment` | `descargar_evidencia`: archivo descargable solo por dueño o docente |
| `evidence.images` | `evidencias_archivos`: verificación con Pillow, fotos optimizadas y tamaño restringido |
| `CoinTransaction` con `idempotency_key` | `Movimiento` enlazado por OneToOne a la revisión: una sola asignación |

## Simplificaciones conscientes

- No se incluyen asignaturas, periodos, grupos, valores salesianos, insignias ni inventario de múltiples fotografías, porque estos módulos no forman parte del prototipo SENA.
- Solo se permite un archivo por envío: PDF, JPG o PNG, máximo 2 MB en esta demo. Las fotos se optimizan a JPEG, como ocurre en el proyecto original.
- En vez de MEDIA institucional, los archivos se almacenan **como binarios privados en la SQLite temporal exclusiva de SENA**. Esto evita configurar almacenamiento público o una base de datos de pago.
- Los datos y archivos pueden desaparecer tras reinicios de Render. No se deben subir evidencias reales ni información de menores.
- Los reconocimientos se limitan a **1–100 Boscoins por evidencia validada**, compatibles con el modelo simplificado.

## Guion de exposición

1. El estudiante sube una evidencia ficticia.
2. El docente ve la bandeja de pendientes, marca **Recibida**, descarga el soporte y revisa.
3. El docente escribe una observación y selecciona **Validar** para otorgar Boscoins, o **Solicitar ajustes** sin otorgar.
4. El estudiante consulta su comentario y, si corresponde, envía una nueva versión.
5. La plataforma impide evaluar dos veces la misma versión y evita duplicados por reintento de envío.

El flujo se comprueba mediante `python manage.py test aula.tests_evidencias`.
