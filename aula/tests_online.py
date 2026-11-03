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
