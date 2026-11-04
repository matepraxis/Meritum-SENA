"""Ensayo integral de la exposición académica, sin datos reales ni servicios externos."""
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.staticfiles import finders

from .models import Canje, Movimiento, Perfil, Publicacion, Recompensa, saldo_de


class EnsayoExposicionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.docente = User.objects.create_user(
            username="docente_prueba_expo", password="ClaveFicticia-Pruebas-Docente2026"
        )
        cls.estudiante = User.objects.create_user(
            username="estudiante_prueba_expo", password="ClaveFicticia-Pruebas-Alumno2026"
        )
        cls.otro = User.objects.create_user(
            username="otro_prueba_expo", password="ClaveFicticia-Pruebas-Otro2026"
        )
        Perfil.objects.create(usuario=cls.docente, rol=Perfil.Rol.DOCENTE)
        Perfil.objects.create(usuario=cls.estudiante, rol=Perfil.Rol.ESTUDIANTE, grado="10")
        Perfil.objects.create(usuario=cls.otro, rol=Perfil.Rol.ESTUDIANTE, grado="10")
        cls.premio = Recompensa.objects.create(
            nombre="Recompensa Expo SENA", costo=20, existencias=2, activa=True
        )

    def test_recorrido_completo_docente_estudiante_y_canje(self):
        docente = Client()
        estudiante = Client()

        self.assertTrue(docente.login(
            username="docente_prueba_expo", password="ClaveFicticia-Pruebas-Docente2026"
        ))
        self.assertTrue(estudiante.login(
            username="estudiante_prueba_expo", password="ClaveFicticia-Pruebas-Alumno2026"
        ))

        respuesta = docente.post(reverse("otorgar"), {
            "estudiante": self.estudiante.pk,
            "cantidad": 35,
            "motivo": "Presentación ficticia",
        })
        self.assertRedirects(respuesta, reverse("inicio"))
        self.assertEqual(saldo_de(self.estudiante), 35)
        self.assertContains(estudiante.get(reverse("inicio")), "Presentación ficticia")

        respuesta = estudiante.post(reverse("canjear", args=[self.premio.pk]))
        self.assertRedirects(respuesta, reverse("inicio"))
        self.premio.refresh_from_db()
        self.assertEqual(saldo_de(self.estudiante), 15)
        self.assertEqual(self.premio.existencias, 1)
        self.assertEqual(Canje.objects.filter(estudiante=self.estudiante).count(), 1)
        self.assertEqual(Movimiento.objects.filter(
            estudiante=self.estudiante,
            cantidad__lt=0
        ).count(), 1)

    def test_exposicion_con_anuncio_y_recompensa_creados_por_docente(self):
        self.client.force_login(self.docente)
        respuesta = self.client.post(reverse("nueva_publicacion"), {
            "titulo": "Anuncio ficticio para jurados",
            "contenido": "Trabajo de equipo",
        })
        self.assertRedirects(respuesta, reverse("inicio"))
        respuesta = self.client.post(reverse("nueva_recompensa"), {
            "nombre": "Mención académica",
            "descripcion": "Demostración ficticia",
            "costo": 10,
            "existencias": 4,
            "activa": "on",
        })
        self.assertRedirects(respuesta, reverse("inicio"))
        self.client.force_login(self.estudiante)
        respuesta = self.client.get(reverse("inicio"))
        self.assertContains(respuesta, "Anuncio ficticio para jurados")
        self.assertContains(respuesta, "Mención académica")
        self.assertEqual(Publicacion.objects.count(), 1)

    def test_estudiante_no_puede_modificar_contenidos_docentes(self):
        self.client.force_login(self.estudiante)
        for nombre in ("otorgar", "nueva_recompensa", "nueva_publicacion"):
            with self.subTest(nombre=nombre):
                self.assertEqual(self.client.get(reverse(nombre)).status_code, 403)
        self.assertEqual(Movimiento.objects.count(), 0)
        self.assertEqual(Publicacion.objects.count(), 0)

    def test_cliente_real_debe_enviar_csrf_para_otorgar(self):
        cliente = Client(enforce_csrf_checks=True)
        cliente.force_login(self.docente)
        respuesta = cliente.post(reverse("otorgar"), {
            "estudiante": self.estudiante.pk,
            "cantidad": 40,
            "motivo": "Sin token",
        })
        self.assertEqual(respuesta.status_code, 403)
        self.assertEqual(Movimiento.objects.count(), 0)

    def test_saldo_es_privado_para_cada_usuario(self):
        Movimiento.objects.create(
            estudiante=self.otro,
            cantidad=50,
            motivo="Información privada del otro usuario",
            responsable=self.docente,
        )
        self.client.force_login(self.estudiante)
        respuesta = self.client.get(reverse("inicio"))
        self.assertNotContains(respuesta, "Información privada del otro usuario")

    def test_recursos_estaticos_existen_sin_cdn(self):
        self.assertTrue(finders.find("aula/estilos.css"))

    def test_login_anonimo_y_salida_post(self):
        self.assertEqual(self.client.get(reverse("inicio")).status_code, 302)
        self.client.force_login(self.estudiante)
        self.assertEqual(self.client.post(reverse("logout")).status_code, 302)
        self.assertEqual(self.client.get(reverse("inicio")).status_code, 302)
