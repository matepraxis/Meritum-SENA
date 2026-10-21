# Migración inicial creada para la versión didáctica Meritum-SENA.
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Recompensa", fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=100)),
                ("descripcion", models.CharField(blank=True, max_length=240)),
                ("costo", models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ("existencias", models.PositiveIntegerField(default=1)),
                ("activa", models.BooleanField(default=True)),
            ], options={"ordering": ["costo", "nombre"]}
        ),
        migrations.CreateModel(
            name="Perfil", fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("rol", models.CharField(choices=[("DOC", "Docente"), ("EST", "Estudiante")], max_length=3)),
                ("grado", models.CharField(blank=True, max_length=30)),
                ("usuario", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="perfil", to=settings.AUTH_USER_MODEL)),
            ]
        ),
        migrations.CreateModel(
            name="Movimiento", fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("cantidad", models.IntegerField(help_text="Positivo: reconocimiento. Negativo: canje.")),
                ("motivo", models.CharField(max_length=200)),
                ("fecha", models.DateTimeField(auto_now_add=True)),
                ("estudiante", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="movimientos", to=settings.AUTH_USER_MODEL)),
                ("responsable", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="movimientos_creados", to=settings.AUTH_USER_MODEL)),
            ], options={"ordering": ["-fecha", "-id"]}
        ),
        migrations.CreateModel(
            name="Canje", fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("costo_aplicado", models.PositiveIntegerField()),
                ("fecha", models.DateTimeField(auto_now_add=True)),
                ("estudiante", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="canjes", to=settings.AUTH_USER_MODEL)),
                ("recompensa", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="aula.recompensa")),
            ], options={"ordering": ["-fecha", "-id"]}
        ),
        migrations.CreateModel(
            name="Publicacion", fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("titulo", models.CharField(max_length=120)),
                ("contenido", models.TextField(max_length=2000)),
                ("fecha", models.DateTimeField(auto_now_add=True)),
                ("docente", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ], options={"ordering": ["-fecha", "-id"]}
        ),
    ]
