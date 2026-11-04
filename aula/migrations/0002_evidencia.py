# Evidencias ficticias y evaluación docente — Meritum-SENA.
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
                ("titulo", models.CharField(max_length=120)),
                ("descripcion", models.CharField(blank=True, max_length=500)),
                ("nombre_archivo", models.CharField(max_length=120)),
                ("tipo_archivo", models.CharField(max_length=40)),
                ("contenido", models.BinaryField()),
                ("fecha", models.DateTimeField(auto_now_add=True)),
                ("comentario", models.TextField(blank=True, default="", max_length=1200)),
                ("boscoins", models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)])),
                ("evaluada_en", models.DateTimeField(blank=True, null=True)),
                ("estudiante", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="evidencias", to=settings.AUTH_USER_MODEL)),
                ("docente_evaluador", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="evidencias_evaluadas", to=settings.AUTH_USER_MODEL)),
                ("movimiento", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="evidencia_origen", to="aula.movimiento")),
            ],
            options={"ordering": ["-fecha", "-id"]},
        ),
    ]
