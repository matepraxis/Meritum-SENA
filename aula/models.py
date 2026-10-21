"""Modelo educativo simplificado. Solo almacenar datos ficticios."""
from django.conf import settings
from django.core.validators import MinValueValidator
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
