"""Pruebas del aprovisionamiento independiente online."""
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from aula.models import Perfil, saldo_de


class InicializacionOnlineTests(TestCase):
    def test_exige_passwords_privados(self):
        with patch.dict("os.environ", {
            "MERITUM_SENA_DOCENTE_PASSWORD": "DemoSENA2026!",
            "MERITUM_SENA_ESTUDIANTE_PASSWORD": "muy-corta",
        }):
            with self.assertRaises(CommandError):
                call_command("preparar_demo_online")

    def test_idempotencia_y_roles(self):
        secrets = {
            "MERITUM_SENA_DOCENTE_PASSWORD": "Docente-privado-de-prueba-12345",
            "MERITUM_SENA_ESTUDIANTE_PASSWORD": "Alumno-privado-de-prueba-12345",
        }
        with patch.dict("os.environ", secrets):
            call_command("preparar_demo_online")
            call_command("preparar_demo_online")
        User = get_user_model()
        docente = User.objects.get(username="docente_sena")
        estudiante = User.objects.get(username="estudiante_sena")
        self.assertEqual(docente.perfil.rol, Perfil.Rol.DOCENTE)
        self.assertEqual(estudiante.perfil.rol, Perfil.Rol.ESTUDIANTE)
        self.assertEqual(saldo_de(estudiante), 40)
        self.assertTrue(docente.check_password(secrets["MERITUM_SENA_DOCENTE_PASSWORD"]))
        self.assertEqual(User.objects.filter(username__in=["docente_sena", "estudiante_sena"]).count(), 2)


class EstadoServicioTests(TestCase):
    def test_salud_publica_esta_disponible(self):
        from django.urls import reverse
        response = self.client.get(reverse("salud"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")
        self.assertEqual(response["Cache-Control"], "no-store")

    def test_salud_rechaza_post(self):
        from django.urls import reverse
        self.assertEqual(self.client.post(reverse("salud")).status_code, 405)

    def test_salud_informa_indisponibilidad_sin_detalles(self):
        from django.db import OperationalError
        from django.urls import reverse
        with patch("aula.health.connection.cursor", side_effect=OperationalError("DB secreta")):
            response = self.client.get(reverse("salud"))
        self.assertEqual(response.status_code, 503)
        self.assertNotIn(b"DB secreta", response.content)


class ContraseñasDemoTests(TestCase):
    def test_rechaza_claves_iguales(self):
        with patch.dict("os.environ", {
            "MERITUM_SENA_DOCENTE_PASSWORD": "ClavesIgualesSoloParaPrueba2026!",
            "MERITUM_SENA_ESTUDIANTE_PASSWORD": "ClavesIgualesSoloParaPrueba2026!",
        }):
            with self.assertRaises(CommandError):
                call_command("preparar_demo_online")

    def test_no_restaurar_password_existente(self):
        User = get_user_model()
        user = User.objects.create_user(username="docente_sena", password="ClavePropiaAnterior-2026!")
        Perfil.objects.create(usuario=user, rol=Perfil.Rol.DOCENTE)
        with patch.dict("os.environ", {
            "MERITUM_SENA_DOCENTE_PASSWORD": "ClaveNuevaNoUsadaDocente-2026!",
            "MERITUM_SENA_ESTUDIANTE_PASSWORD": "ClaveNuevaNoUsadaAlumno-2026!",
        }):
            call_command("preparar_demo_online")
        user.refresh_from_db()
        self.assertTrue(user.check_password("ClavePropiaAnterior-2026!"))
