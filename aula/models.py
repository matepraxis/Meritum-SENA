"""Modelo educativo simplificado. Solo almacenar datos ficticios."""
import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Sum


class Perfil(models.Model):
    class Rol(models.TextChoices):
        DOCENTE = "DOC", "Docente"
        ESTUDIANTE = "EST", "Estudiante"

    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="perfil")
    rol = models.CharField(max_length=3, choices=Rol.choices)
    grado = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.get_rol_display()}"


class Movimiento(models.Model):
    estudiante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="movimientos")
    cantidad = models.IntegerField(help_text="Positivo: reconocimiento. Negativo: canje.")
    motivo = models.CharField(max_length=200)
    responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="movimientos_creados")
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-id"]

    def __str__(self):
        return f"{self.estudiante}: {self.cantidad:+} ({self.motivo})"


def saldo_de(usuario):
    return usuario.movimientos.aggregate(total=Sum("cantidad"))["total"] or 0


class Recompensa(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=240, blank=True)
    costo = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    existencias = models.PositiveIntegerField(default=1)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ["costo", "nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.costo} Boscoins)"


class Canje(models.Model):
    estudiante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="canjes")
    recompensa = models.ForeignKey(Recompensa, on_delete=models.PROTECT)
    costo_aplicado = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-id"]


class Publicacion(models.Model):
    titulo = models.CharField(max_length=120)
    contenido = models.TextField(max_length=2000)
    docente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-id"]

    def __str__(self):
        return self.titulo



class Evidencia(models.Model):
    """Modelo simplificado de evidence.Evidence de Meritum, independiente."""

    class Estado(models.TextChoices):
        ENVIADA = "pending", "Enviada"
        RECIBIDA = "received", "Recibida por el docente"
        APROBADA = "approved", "Validada por el docente"
        AJUSTES = "rejected", "Requiere ajustes"

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    token_envio = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    estudiante = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="evidencias",
    )
    titulo = models.CharField(max_length=120)
    descripcion = models.CharField(max_length=500, blank=True)
    nombre_archivo = models.CharField(max_length=120)
    tipo_archivo = models.CharField(max_length=40)
    contenido = models.BinaryField()
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.ENVIADA)
    revision_anterior = models.OneToOneField(
        "self", blank=True, null=True, on_delete=models.PROTECT, related_name="revision",
    )
    numero_version = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["-fecha", "-id"]

    def __str__(self):
        return f"{self.titulo} — {self.estudiante.username}"

    @property
    def tiene_revision(self):
        return hasattr(self, "revision")


class EvaluacionEvidencia(models.Model):
    """La decisión docente y su reconocimiento quedan relacionados por una clave única."""

    evidencia = models.OneToOneField(
        Evidencia, on_delete=models.PROTECT, related_name="evaluacion",
    )
    revisor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="evaluaciones_evidencia",
    )
    decision = models.CharField(max_length=10, choices=(
        (Evidencia.Estado.APROBADA, "Validada"),
        (Evidencia.Estado.AJUSTES, "Requiere ajustes"),
    ))
    comentario = models.TextField(max_length=1000)
    boscoins = models.PositiveSmallIntegerField(
        blank=True, null=True,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
    )
    movimiento = models.OneToOneField(
        Movimiento, on_delete=models.PROTECT,
        blank=True, null=True, related_name="evaluacion_origen",
    )
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.evidencia.titulo}: {self.get_decision_display()}"
