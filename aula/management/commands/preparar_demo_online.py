"""Crea cuentas ficticias desde secretos del servicio, jamás desde contraseñas públicas."""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from aula.models import Movimiento, Perfil, Publicacion, Recompensa


class Command(BaseCommand):
    help = "Inicializa únicamente cuentas ficticias de la edición web, sin cambiar contraseñas existentes."

    @transaction.atomic
    def handle(self, *args, **options):
        configuraciones = [
            ("MERITUM_SENA_DOCENTE_PASSWORD", "docente_sena", Perfil.Rol.DOCENTE),
            ("MERITUM_SENA_ESTUDIANTE_PASSWORD", "estudiante_sena", Perfil.Rol.ESTUDIANTE),
        ]
        for var, _, _ in configuraciones:
            password = os.getenv(var, "")
            if len(password) < 14 or password == "DemoSENA2026!":
                raise CommandError(
                    f"Configura {var} con una contraseña privada de 14 o más caracteres."
                )

        User = get_user_model()
        usuarios = {}
        for var, username, rol in configuraciones:
            user, creado = User.objects.get_or_create(
                username=username, defaults={"is_active": True}
            )
            if creado:
                user.set_password(os.environ[var])
                user.save(update_fields=["password"])
                Perfil.objects.create(
                    usuario=user,
                    rol=rol,
                    grado="Laboratorio SENA" if rol == Perfil.Rol.ESTUDIANTE else "",
                )
            elif not Perfil.objects.filter(usuario=user, rol=rol).exists():
                raise CommandError(f"Conflicto de rol en {username}. Revisar manualmente.")
            usuarios[rol] = user

        estudiante = usuarios[Perfil.Rol.ESTUDIANTE]
        docente = usuarios[Perfil.Rol.DOCENTE]
        if not estudiante.movimientos.exists():
            Movimiento.objects.create(
                estudiante=estudiante, cantidad=40,
                motivo="Participación académica ficticia", responsable=docente,
            )
        Recompensa.objects.get_or_create(
            nombre="Elegir actividad de repaso",
            defaults={"descripcion": "Premio simbólico de laboratorio", "costo": 15, "existencias": 10},
        )
        Publicacion.objects.get_or_create(
            titulo="Bienvenidos a Meritum-SENA",
            defaults={"contenido": "Esta versión web usa exclusivamente información ficticia.", "docente": docente},
        )
        self.stdout.write(self.style.SUCCESS("Cuentas y datos ficticios verificados. No se muestran claves."))
