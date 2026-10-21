"""Operaciones pedagógicas, restringidas por rol y confirmadas con POST+CSRF."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import PublicacionForm, ReconocimientoForm, RecompensaForm
from .models import Canje, Movimiento, Perfil, Publicacion, Recompensa, saldo_de


def es_docente(usuario):
    return usuario.is_superuser or (
        hasattr(usuario, "perfil") and usuario.perfil.rol == Perfil.Rol.DOCENTE
    )


def es_estudiante(usuario):
    return hasattr(usuario, "perfil") and usuario.perfil.rol == Perfil.Rol.ESTUDIANTE


def exigir_docente(usuario):
    if not es_docente(usuario):
        raise PermissionDenied("Solo puede realizar esta operación un docente.")


@login_required
def inicio(request):
    docente = es_docente(request.user)
    estudiante = es_estudiante(request.user)
    if not (docente or estudiante):
        raise PermissionDenied("Tu cuenta no tiene rol asignado.")
    contexto = {
        "docente": docente,
        "saldo": saldo_de(request.user) if estudiante else None,
        "movimientos": request.user.movimientos.all()[:10] if estudiante else [],
        "canjes": request.user.canjes.select_related("recompensa").all()[:10] if estudiante else [],
        "recompensas": Recompensa.objects.filter(activa=True),
        "publicaciones": Publicacion.objects.select_related("docente").all()[:10],
    }
    if docente:
        contexto["reconocimientos_recientes"] = Movimiento.objects.select_related("estudiante").all()[:8]
    return render(request, "aula/inicio.html", contexto)


@login_required
def otorgar(request):
    exigir_docente(request.user)
    form = ReconocimientoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        Movimiento.objects.create(
            estudiante=form.cleaned_data["estudiante"],
            cantidad=form.cleaned_data["cantidad"],
            motivo=form.cleaned_data["motivo"],
            responsable=request.user,
        )
        messages.success(request, "Reconocimiento registrado correctamente.")
        return redirect("inicio")
    return render(request, "aula/formulario.html", {"form": form, "titulo": "Otorgar Boscoins"})


@login_required
def nueva_recompensa(request):
    exigir_docente(request.user)
    form = RecompensaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Recompensa creada.")
        return redirect("inicio")
    return render(request, "aula/formulario.html", {"form": form, "titulo": "Crear recompensa"})


@login_required
def nueva_publicacion(request):
    exigir_docente(request.user)
    form = PublicacionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        publicacion = form.save(commit=False)
        publicacion.docente = request.user
        publicacion.save()
        messages.success(request, "Publicación creada.")
        return redirect("inicio")
    return render(request, "aula/formulario.html", {"form": form, "titulo": "Nueva publicación"})


@login_required
@require_POST
def canjear(request, recompensa_id):
    if not es_estudiante(request.user):
        raise PermissionDenied("Solo un estudiante puede canjear recompensas.")
    with transaction.atomic():
        recompensa = get_object_or_404(Recompensa, pk=recompensa_id, activa=True)
        if saldo_de(request.user) < recompensa.costo:
            messages.error(request, "No tienes suficientes Boscoins.")
            return redirect("inicio")
        # La actualización condicional impide descontar una existencia ya agotada.
        actualizado = Recompensa.objects.filter(pk=recompensa.pk, existencias__gt=0, activa=True).update(existencias=F("existencias") - 1)
        if not actualizado:
            messages.error(request, "Esta recompensa está agotada.")
            return redirect("inicio")
        Canje.objects.create(estudiante=request.user, recompensa=recompensa, costo_aplicado=recompensa.costo)
        Movimiento.objects.create(estudiante=request.user, cantidad=-recompensa.costo, motivo=f"Canje: {recompensa.nombre}", responsable=request.user)
    messages.success(request, "Canje registrado. Coordina la entrega con tu docente.")
    return redirect("inicio")
