"""Evidencias privadas: envío, descarga autorizada y evaluación una sola vez."""
from io import BytesIO
from pathlib import Path

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET

from .forms import EvidenciaForm, EvaluacionEvidenciaForm, TIPOS_EVIDENCIA
from .models import Evidencia, Movimiento
from .views import es_docente, es_estudiante, exigir_docente


@login_required
def subir_evidencia(request):
    if not es_estudiante(request.user):
        raise PermissionDenied("Solo un estudiante puede enviar evidencias.")

    # El control preliminar evita analizar solicitudes excesivas.
    longitud = request.META.get("CONTENT_LENGTH", "")
    if request.method == "POST" and longitud.isdecimal() and int(longitud) > 2_400_000:
        messages.error(request, "La solicitud supera el límite de 2 MB para evidencias.")
        return redirect("subir_evidencia")

    form = EvidenciaForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        archivo = form.cleaned_data["archivo"]
        extension = Path(archivo.name).suffix.lower()
        Evidencia.objects.create(
            estudiante=request.user,
            titulo=form.cleaned_data["titulo"],
            descripcion=form.cleaned_data["descripcion"],
            nombre_archivo=Path(archivo.name).name[:120],
            tipo_archivo=TIPOS_EVIDENCIA[extension][0],
            contenido=archivo.read(),
        )
        messages.success(request, "Evidencia enviada. Está pendiente de revisión docente.")
        return redirect("inicio")

    return render(request, "aula/subir_evidencia.html", {"form": form})


@login_required
@require_GET
def descargar_evidencia(request, evidencia_id):
    evidencia = get_object_or_404(Evidencia, pk=evidencia_id)
    if not es_docente(request.user) and evidencia.estudiante_id != request.user.pk:
        raise Http404("Evidencia no disponible.")

    extension = Path(evidencia.nombre_archivo).suffix.lower()
    if extension not in TIPOS_EVIDENCIA:
        raise Http404("Archivo no disponible.")

    respuesta = FileResponse(
        BytesIO(bytes(evidencia.contenido)),
        as_attachment=True,
        filename=f"evidencia-{evidencia.pk}{extension}",
        content_type=evidencia.tipo_archivo,
    )
    respuesta["Cache-Control"] = "private, no-store"
    respuesta["Content-Security-Policy"] = "sandbox"
    respuesta["X-Content-Type-Options"] = "nosniff"
    return respuesta


@login_required
def evaluar_evidencia(request, evidencia_id):
    exigir_docente(request.user)
    evidencia = get_object_or_404(
        Evidencia.objects.select_related("estudiante").defer("contenido"),
        pk=evidencia_id,
    )
    if evidencia.evaluada_en is not None:
        messages.info(request, "Esta evidencia ya fue evaluada. No se pueden duplicar los Boscoins.")
        return redirect("inicio")

    form = EvaluacionEvidenciaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            evidencia = get_object_or_404(
                Evidencia.objects.select_for_update().select_related("estudiante").defer("contenido"),
                pk=evidencia_id,
            )
            if evidencia.evaluada_en is not None:
                messages.info(request, "La evidencia ya había sido evaluada.")
                return redirect("inicio")
            # Misma transacción: comentario, nota y Boscoins se guardan juntos.
            get_user_model().objects.select_for_update().get(pk=evidencia.estudiante_id)
            movimiento = Movimiento.objects.create(
                estudiante=evidencia.estudiante,
                cantidad=form.cleaned_data["boscoins"],
                motivo=f"Evidencia: {evidencia.titulo}"[:200],
                responsable=request.user,
            )
            evidencia.comentario = form.cleaned_data["comentario"]
            evidencia.boscoins = form.cleaned_data["boscoins"]
            evidencia.docente_evaluador = request.user
            evidencia.evaluada_en = timezone.now()
            evidencia.movimiento = movimiento
            evidencia.save(update_fields=[
                "comentario", "boscoins", "docente_evaluador", "evaluada_en", "movimiento"
            ])

        messages.success(request, "Evaluación registrada y Boscoins asignados al estudiante.")
        return redirect("inicio")

    return render(request, "aula/evaluar_evidencia.html", {
        "form": form,
        "evidencia": evidencia,
    })
