"""Cuentas ficticias para una demostración local. Nunca usar con datos reales."""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from aula.models import Movimiento, Perfil, Publicacion, Recompensa


class Command(BaseCommand):
    help = "Carga datos completamente ficticios para el proyecto SENA (idempotente)."

    def handle(self, *args, **options):
        usuario_modelo = get_user_model()
        for username, rol, first_name in [
            ("docente", Perfil.Rol.DOCENTE, "Docente Demo"),
            ("estudiante", Perfil.Rol.ESTUDIANTE, "Estudiante Demo"),
        ]:
            user, creado = usuario_modelo.objects.get_or_create(username=username, defaults={"first_name": first_name})
            if creado:
                user.set_password("DemoSENA2026!")
                user.save()
            Perfil.objects.update_or_create(usuario=user, defaults={"rol": rol, "grado": "10°" if rol == Perfil.Rol.ESTUDIANTE else ""})
        docente = usuario_modelo.objects.get(username="docente")
        alumno = usuario_modelo.objects.get(username="estudiante")
        if not alumno.movimientos.exists():
            Movimiento.objects.create(estudiante=alumno, cantidad=40, motivo="Participación académica de demostración", responsable=docente)
        Recompensa.objects.get_or_create(nombre="Elegir actividad de repaso", defaults={"descripcion": "Recompensa simbólica en clase", "costo": 15, "existencias": 10})
        Recompensa.objects.get_or_create(nombre="Insignia de perseverancia", defaults={"descripcion": "Reconocimiento formativo", "costo": 25, "existencias": 5})
        Publicacion.objects.get_or_create(titulo="Bienvenidos a Meritum-SENA", defaults={"contenido": "Este proyecto funciona localmente con datos ficticios.", "docente": docente})
        self.stdout.write(self.style.SUCCESS("Demo cargada. Usuarios: docente / estudiante; contraseña: DemoSENA2026!"))
