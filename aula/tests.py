from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import Canje, Movimiento, Perfil, Publicacion, Recompensa, saldo_de


class PrototipoTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.docente = User.objects.create_user(username="profe", password="PasswordDemo123!")
        self.estudiante = User.objects.create_user(username="alumno", password="PasswordDemo123!")
        self.segundo = User.objects.create_user(username="otro", password="PasswordDemo123!")
        Perfil.objects.create(usuario=self.docente, rol=Perfil.Rol.DOCENTE)
        Perfil.objects.create(usuario=self.estudiante, rol=Perfil.Rol.ESTUDIANTE, grado="10°")
        Perfil.objects.create(usuario=self.segundo, rol=Perfil.Rol.ESTUDIANTE, grado="10°")
        self.premio = Recompensa.objects.create(nombre="Premio demo", costo=20, existencias=1)

    def test_inicio_exige_login(self):
        self.assertRedirects(self.client.get(reverse("inicio")), "/login/?next=/")

    def test_docente_otorga_boscoins(self):
        self.client.force_login(self.docente)
        r = self.client.post(reverse("otorgar"), {"estudiante": self.estudiante.id, "cantidad": 30, "motivo": "Buen trabajo"})
        self.assertRedirects(r, reverse("inicio"))
        self.assertEqual(saldo_de(self.estudiante), 30)

    def test_estudiante_no_puede_otorgar(self):
        self.client.force_login(self.estudiante)
        r = self.client.post(reverse("otorgar"), {"estudiante": self.estudiante.id, "cantidad": 30, "motivo": "Abuso"})
        self.assertEqual(r.status_code, 403)
        self.assertEqual(saldo_de(self.estudiante), 0)

    def test_no_se_puede_otorgar_a_docente(self):
        self.client.force_login(self.docente)
        self.client.post(reverse("otorgar"), {"estudiante": self.docente.id, "cantidad": 10, "motivo": "No"})
        self.assertEqual(Movimiento.objects.count(), 0)

    def test_reconocimiento_limitado_a_100(self):
        self.client.force_login(self.docente)
        self.client.post(reverse("otorgar"), {"estudiante": self.estudiante.id, "cantidad": 101, "motivo": "Exceso"})
        self.assertEqual(Movimiento.objects.count(), 0)

    def test_canje_descuenta_saldo_y_existencias(self):
        Movimiento.objects.create(estudiante=self.estudiante, cantidad=40, motivo="Demo", responsable=self.docente)
        self.client.force_login(self.estudiante)
        r = self.client.post(reverse("canjear", args=[self.premio.id]))
        self.assertRedirects(r, reverse("inicio"))
        self.premio.refresh_from_db()
        self.assertEqual(self.premio.existencias, 0)
        self.assertEqual(saldo_de(self.estudiante), 20)
        self.assertEqual(Canje.objects.count(), 1)

    def test_sin_saldo_no_hay_canje(self):
        self.client.force_login(self.estudiante)
        self.client.post(reverse("canjear", args=[self.premio.id]))
        self.assertEqual(Canje.objects.count(), 0)
        self.premio.refresh_from_db()
        self.assertEqual(self.premio.existencias, 1)

    def test_no_se_canjea_sin_existencias(self):
        Movimiento.objects.create(estudiante=self.estudiante, cantidad=40, motivo="Demo", responsable=self.docente)
        self.premio.existencias = 0
        self.premio.save()
        self.client.force_login(self.estudiante)
        self.client.post(reverse("canjear", args=[self.premio.id]))
        self.assertEqual(saldo_de(self.estudiante), 40)
        self.assertEqual(Canje.objects.count(), 0)

    def test_canje_rechaza_get(self):
        self.client.force_login(self.estudiante)
        self.assertEqual(self.client.get(reverse("canjear", args=[self.premio.id])).status_code, 405)

    def test_docente_no_canjea(self):
        self.client.force_login(self.docente)
        self.assertEqual(self.client.post(reverse("canjear", args=[self.premio.id])).status_code, 403)

    def test_estudiante_no_crea_recompensas_ni_publicaciones(self):
        self.client.force_login(self.estudiante)
        self.assertEqual(self.client.post(reverse("nueva_recompensa"), {}).status_code, 403)
        self.assertEqual(self.client.post(reverse("nueva_publicacion"), {}).status_code, 403)

    def test_docente_publica(self):
        self.client.force_login(self.docente)
        self.client.post(reverse("nueva_publicacion"), {"titulo": "Actividad", "contenido": "Resolver taller"})
        self.assertEqual(Publicacion.objects.count(), 1)

    def test_estudiante_no_ve_movimientos_ajenos(self):
        Movimiento.objects.create(estudiante=self.segundo, cantidad=25, motivo="Privado", responsable=self.docente)
        self.client.force_login(self.estudiante)
        r = self.client.get(reverse("inicio"))
        self.assertNotContains(r, "Privado")
