"""Comprobaciones de la interfaz de exposición sin dependencias externas."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Movimiento, Perfil, Recompensa


class InterfazExposicionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.docente = User.objects.create_user(username="docente_ui", password="Demo2026-clave-ficticia")
        cls.estudiante = User.objects.create_user(username="estudiante_ui", password="Demo2026-clave-ficticia")
        Perfil.objects.create(usuario=cls.docente, rol=Perfil.Rol.DOCENTE)
        Perfil.objects.create(usuario=cls.estudiante, rol=Perfil.Rol.ESTUDIANTE, grado="10")
        cls.recompensa = Recompensa.objects.create(nombre="Premio de muestra", costo=20, existencias=3)

    def test_acceso_tiene_formulario_y_sin_contrasena_publica(self):
        respuesta = self.client.get(reverse("login"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'id="titulo-acceso"')
        self.assertContains(respuesta, 'name="username"')
        self.assertNotContains(respuesta, "DemoSENA2026!")

    def test_panel_docente_muestra_tres_acciones(self):
        self.client.force_login(self.docente)
        respuesta = self.client.get(reverse("inicio"))
        for nombre in ("Otorgar Boscoins", "Crear recompensa", "Publicar anuncio"):
            self.assertContains(respuesta, nombre)
        self.assertContains(respuesta, 'id="acciones"')
        self.assertNotContains(respuesta, "Mis canjes")

    def test_panel_estudiante_no_muestra_acciones_docentes(self):
        self.client.force_login(self.estudiante)
        respuesta = self.client.get(reverse("inicio"))
        self.assertContains(respuesta, 'id="boscomarket"')
        self.assertContains(respuesta, "Mis canjes")
        self.assertContains(respuesta, "Saldo insuficiente")
        self.assertNotContains(respuesta, 'href="' + reverse("otorgar") + '"')

    def test_estudiante_con_saldo_puede_ver_canje_habilitado(self):
        Movimiento.objects.create(
            estudiante=self.estudiante, cantidad=40,
            motivo="Reconocimiento ficticio", responsable=self.docente,
        )
        self.client.force_login(self.estudiante)
        respuesta = self.client.get(reverse("inicio"))
        self.assertContains(respuesta, ">Canjear</button>")
        self.assertContains(respuesta, "40")

    def test_recompensa_agotada_informa_estado_y_no_permita_canjear(self):
        self.recompensa.existencias = 0
        self.recompensa.save(update_fields=["existencias"])
        self.client.force_login(self.estudiante)
        respuesta = self.client.get(reverse("inicio"))
        self.assertContains(respuesta, "Agotado")
        self.assertContains(respuesta, 'aria-disabled="true"')

    def test_formulario_docente_conserva_csrf_y_navegacion(self):
        self.client.force_login(self.docente)
        respuesta = self.client.get(reverse("nueva_recompensa"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Guardar cambios")
        self.assertContains(respuesta, "Volver al panel")
        self.assertContains(respuesta, 'name="csrfmiddlewaretoken"')
