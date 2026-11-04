"""Flujo de evidencias adaptado de evidence/views.py + evidence/services.py de MERITUM.

Únicamente usa las tablas y cuentas ficticias de Meritum-SENA.
"""
from io import BytesIO
import uuid

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .evidencias_archivos import preparar_evidencia
from .forms import EvidenciaForm, EvaluacionEvidenciaForm
from .models import Evidencia, EvaluacionEvidencia, Movimiento
from .views import es_docente, es_estudiante, exigir_docente


def _envio_por_token(token, estudiante, anterior=None):
    """Como _student_submission_by_token en MERITUM: un reintento no crea duplicados."""
    if not token:
        return None
    try:
        token = uuid.UUID(str(token))
    except (TypeError, ValueError, AttributeError):
        return None
    return Evidencia.objects.filter(
        token_envio=token, estudiante=estudiante, revision_anterior=anterior
    ).first()


def _guardar_envio(request, anterior=None):
    if not es_estudiante(request.user):
        raise PermissionDenied("Solo un estudiante puede presentar evidencias.")

    if anterior is not None:
        anterior = get_object_or_404(
            Evidencia, public_id=anterior, estudiante=request.user,
        )
        if anterior.estado != Evidencia.Estado.AJUSTES:
            raise PermissionDenied("Solo puedes reenviar evidencias que requieren ajustes.")
        if anterior.tiene_revision:
            messages.info(request, "Esta evidencia ya tiene una nueva versión.")
            return redirect("inicio")

    if request.method == "POST":
        repetida = _envio_por_token(
            request.POST.get("token_envio"), request.user, anterior,
        )
        if repetida:
            messages.info(request, "Este envío ya estaba guardado; no se creó una copia.")
            return redirect("inicio")

        longitud = request.META.get("CONTENT_LENGTH", "")
        if longitud.isdecimal() and int(longitud) > 2_400_000:
            messages.error(request, "El archivo de evidencia supera el límite de 2 MB.")
            return redirect("inicio")

    form = EvidenciaForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        archivo = form.cleaned_data["archivo"]
        try:
            nombre, tipo, contenido = preparar_evidencia(archivo)
        except ValidationError as exc:
            form.add_error("archivo", exc)
        else:
            token = form.cleaned_data.get("token_envio") or uuid.uuid4()
            try:
                with transaction.atomic():
                    Evidencia.objects.create(
                        estudiante=request.user,
                        token_envio=token,
                        titulo=form.cleaned_data["titulo"],
                        descripcion=form.cleaned_data["descripcion"],
                        nombre_archivo=nombre,
                        tipo_archivo=tipo,
                        contenido=contenido,
                        revision_anterior=anterior,
                        numero_version=(anterior.numero_version + 1) if anterior else 1,
                    )
            except IntegrityError:
                repetida = _envio_por_token(token, request.user, anterior)
                if repetida:
                    messages.info(request, "Este envío ya estaba guardado.")
                    return redirect("inicio")
                if anterior and anterior.tiene_revision:
                    messages.info(request, "La corrección ya estaba enviada.")
                    return redirect("inicio")
                raise
            messages.success(request, "Tu evidencia fue enviada para validación docente.")
            return redirect("inicio")

    return render(request, "aula/subir_evidencia.html", {
        "form": form, "anterior": anterior,
    })


@login_required
def subir_evidencia(request):
    return _guardar_envio(request)


@login_required
def reenviar_evidencia(request, public_id):
    return _guardar_envio(request, anterior=public_id)


@login_required
@require_GET
def descargar_evidencia(request, public_id):
    evidencia = get_object_or_404(Evidencia, public_id=public_id)
    if not es_docente(request.user) and evidencia.estudiante_id != request.user.pk:
        raise Http404("Evidencia no disponible.")
    extension = ".pdf" if evidencia.tipo_archivo == "application/pdf" else ".jpg"
    if evidencia.tipo_archivo not in ("application/pdf", "image/jpeg"):
        raise Http404("Archivo no disponible.")
    respuesta = FileResponse(
        BytesIO(bytes(evidencia.contenido)),
        as_attachment=True,
        filename=f"evidencia-{str(evidencia.public_id)[:8]}{extension}",
        content_type=evidencia.tipo_archivo,
    )
    respuesta["Cache-Control"] = "private, no-store"
    respuesta["X-Content-Type-Options"] = "nosniff"
    respuesta["Content-Security-Policy"] = "sandbox"
    return respuesta


@login_required
@require_POST
def recibir_evidencia(request, public_id):
    exigir_docente(request.user)
    with transaction.atomic():
        evidencia = get_object_or_404(
            Evidencia.objects.select_for_update(), public_id=public_id,
        )
        if evidencia.estado != Evidencia.Estado.ENVIADA:
            messages.info(request, "Esta evidencia ya fue recibida o revisada.")
            return redirect("inicio")
        evidencia.estado = Evidencia.Estado.RECIBIDA
        evidencia.save(update_fields=["estado"])
    messages.success(request, "Evidencia recibida. Puedes realizar la revisión docente.")
    return redirect("inicio")


@login_required
def evaluar_evidencia(request, public_id):
    exigir_docente(request.user)
    evidencia = get_object_or_404(
        Evidencia.objects.select_related("estudiante").defer("contenido"),
        public_id=public_id,
    )
    if evidencia.estado not in (Evidencia.Estado.ENVIADA, Evidencia.Estado.RECIBIDA):
        messages.info(request, "Esta evidencia ya tiene una decisión registrada.")
        return redirect("inicio")

    form = EvaluacionEvidenciaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            evidencia = get_object_or_404(
                Evidencia.objects.select_for_update().select_related("estudiante").defer("contenido"),
                public_id=public_id,
            )
            if evidencia.estado not in (Evidencia.Estado.ENVIADA, Evidencia.Estado.RECIBIDA):
                messages.info(request, "La evidencia ya fue evaluada.")
                return redirect("inicio")

            decision = form.cleaned_data["decision"]
            comentario = form.cleaned_data["comentario"].strip()
            cantidad = form.cleaned_data.get("boscoins")
            movimiento = None
            if decision == Evidencia.Estado.APROBADA:
                get_user_model().objects.select_for_update().get(pk=evidencia.estudiante_id)
                movimiento = Movimiento.objects.create(
                    estudiante=evidencia.estudiante,
                    cantidad=cantidad,
                    motivo=f"Evidencia: {evidencia.titulo}"[:200],
                    responsable=request.user,
                )

            EvaluacionEvidencia.objects.create(
                evidencia=evidencia,
                revisor=request.user,
                decision=decision,
                comentario=comentario,
                boscoins=cantidad,
                movimiento=movimiento,
            )
            evidencia.estado = decision
            evidencia.save(update_fields=["estado"])

        if decision == Evidencia.Estado.APROBADA:
            messages.success(request, f"Evidencia validada. Se asignaron {cantidad} Boscoins.")
        else:
            messages.success(request, "Observación registrada. El estudiante puede corregir y reenviar.")
        return redirect("inicio")

    return render(request, "aula/evaluar_evidencia.html", {
        "form": form, "evidencia": evidencia,
    })
