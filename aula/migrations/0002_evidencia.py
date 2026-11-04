# Adaptación académica del flujo evidence de Meritum original, sin datos institucionales.
import uuid
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("aula", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Evidencia",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("public_id", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("token_envio", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("titulo", models.CharField(max_length=120)),
                ("descripcion", models.CharField(blank=True, max_length=500)),
                ("nombre_archivo", models.CharField(max_length=120)),
                ("tipo_archivo", models.CharField(max_length=40)),
                ("contenido", models.BinaryField()),
                ("fecha", models.DateTimeField(auto_now_add=True)),
                ("estado", models.CharField(choices=[("pending", "Enviada"), ("received", "Recibida por el docente"), ("approved", "Validada por el docente"), ("rejected", "Requiere ajustes")], default="pending", max_length=10)),
                ("numero_version", models.PositiveSmallIntegerField(default=1)),
                ("estudiante", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="evidencias", to=settings.AUTH_USER_MODEL)),
                ("revision_anterior", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="revision", to="aula.evidencia")),
            ], options={"ordering": ["-fecha", "-id"]}
        ),
        migrations.CreateModel(
            name="EvaluacionEvidencia",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("decision", models.CharField(choices=[("approved", "Validada"), ("rejected", "Requiere ajustes")], max_length=10)),
                ("comentario", models.TextField(max_length=1000)),
                ("boscoins", models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)])),
                ("fecha", models.DateTimeField(auto_now_add=True)),
                ("evidencia", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="evaluacion", to="aula.evidencia")),
                ("movimiento", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="evaluacion_origen", to="aula.movimiento")),
                ("revisor", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="evaluaciones_evidencia", to=settings.AUTH_USER_MODEL)),
            ]
        )
    ]
