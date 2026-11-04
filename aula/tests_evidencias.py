"""Ensayos de la adaptación del módulo evidence de MERITUM original."""
from io import BytesIO
import uuid

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from PIL import Image

from .models import Evidencia, EvaluacionEvidencia, Movimiento, Perfil, saldo_de


def pdf_ficticio():
    return SimpleUploadedFile(
        "evidencia.pdf",
        b"%PDF-1.4\n%Archivo de laboratorio SENA\n1 0 obj\nendobj\n%%EOF",
        content_type="application/pdf",
    )


class EvidenciasComoMeritumTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.docente = User.objects.create_user(username="docente_evidencia", password="ClaveFicticiaDocente2026!")
        cls.estudiante = User.objects.create_user(username="alumno_evidencia", password="ClaveFicticiaAlumno2026!")
        cls.ajeno = User.objects.create_user(username="alumno_ajeno", password="ClaveFicticiaAjeno2026!")
        Perfil.objects.create(usuario=cls.docente, rol=Perfil.Rol.DOCENTE)
        Perfil.objects.create(usuario=cls.estudiante, rol=Perfil.Rol.ESTUDIANTE)
        Perfil.objects.create(usuario=cls.ajeno, rol=Perfil.Rol.ESTUDIANTE)

    def enviar(self, usuario=None, token=None, titulo="Trabajo de exposición", url=None):
        self.client.force_login(usuario or self.estudiante)
        return self.client.post(url or reverse("subir_evidencia"), {
            "token_envio": str(token or uuid.uuid4()),
            "titulo": titulo,
            "descripcion": "Realicé el taller y expliqué lo aprendido.",
            "archivo": pdf_ficticio(),
        })

    def test_estudiante_envia_y_docente_descarga_archivo_privado(self):
        r = self.enviar()
        self.assertRedirects(r, reverse("inicio"))
        evidencia = Evidencia.objects.get()
        self.assertEqual(evidencia.estado, Evidencia.Estado.ENVIADA)
        self.assertEqual(evidencia.numero_version, 1)
        self.client.force_login(self.docente)
        descarga = self.client.get(reverse("descargar_evidencia", args=[evidencia.public_id]))
        self.assertEqual(descarga.status_code, 200)
        self.assertEqual(descarga["Cache-Control"], "private, no-store")
        self.assertTrue(b"%PDF-" in b"".join(descarga.streaming_content))

    def test_docente_recibe_aprueba_comenta_y_otorga_saldo(self):
        self.enviar()
        evidencia = Evidencia.objects.get()
        self.client.force_login(self.docente)
        self.assertRedirects(
            self.client.post(reverse("recibir_evidencia", args=[evidencia.public_id])),
            reverse("inicio"),
        )
        evidencia.refresh_from_db()
        self.assertEqual(evidencia.estado, Evidencia.Estado.RECIBIDA)
        self.assertRedirects(self.client.post(
            reverse("evaluar_evidencia", args=[evidencia.public_id]), {
                "decision": "approved",
                "comentario": "Explicaste correctamente el procedimiento matemático.",
                "boscoins": 30,
            }), reverse("inicio"))
        evidencia.refresh_from_db()
        self.assertEqual(evidencia.estado, Evidencia.Estado.APROBADA)
        self.assertEqual(evidencia.evaluacion.boscoins, 30)
        self.assertEqual(evidencia.evaluacion.movimiento.cantidad, 30)
        self.assertEqual(saldo_de(self.estudiante), 30)
        self.client.force_login(self.estudiante)
        panel = self.client.get(reverse("inicio"))
        self.assertContains(panel, "Explicaste correctamente")
        self.assertContains(panel, "+30 Boscoins")

    def test_rechazar_y_reenviar_crea_nueva_version_sin_boscoins(self):
        self.enviar()
        evidencia = Evidencia.objects.get()
        self.client.force_login(self.docente)
        self.assertRedirects(self.client.post(
            reverse("evaluar_evidencia", args=[evidencia.public_id]), {
                "decision": "rejected",
                "comentario": "Debes mejorar las conclusiones.",
                "boscoins": 99,
            }), reverse("inicio"))
        evidencia.refresh_from_db()
        self.assertEqual(evidencia.estado, Evidencia.Estado.AJUSTES)
        self.assertIsNone(evidencia.evaluacion.boscoins)
        self.assertEqual(saldo_de(self.estudiante), 0)
        self.assertEqual(Movimiento.objects.count(), 0)
        url = reverse("reenviar_evidencia", args=[evidencia.public_id])
        self.assertRedirects(self.enviar(url=url, titulo="Corrección del trabajo"), reverse("inicio"))
        nueva = Evidencia.objects.exclude(pk=evidencia.pk).get()
        self.assertEqual(nueva.revision_anterior, evidencia)
        self.assertEqual(nueva.numero_version, 2)
        self.assertEqual(nueva.estado, Evidencia.Estado.ENVIADA)
        self.assertEqual(saldo_de(self.estudiante), 0)

    def test_no_otorga_dos_veces_al_repetir_evaluacion(self):
        self.enviar()
        evidencia = Evidencia.objects.get()
        url = reverse("evaluar_evidencia", args=[evidencia.public_id])
        self.client.force_login(self.docente)
        payload = {"decision": "approved", "comentario": "Proceso verificado.", "boscoins": 20}
        self.assertRedirects(self.client.post(url, payload), reverse("inicio"))
        self.assertRedirects(self.client.post(url, payload), reverse("inicio"))
        self.assertEqual(Movimiento.objects.count(), 1)
        self.assertEqual(EvaluacionEvidencia.objects.count(), 1)

    def test_token_repetido_no_duplica_envio(self):
        token = uuid.uuid4()
        self.enviar(token=token)
        self.enviar(token=token)
        self.assertEqual(Evidencia.objects.count(), 1)

    def test_archivo_ajeno_es_privado(self):
        self.enviar()
        evidencia = Evidencia.objects.get()
        self.client.force_login(self.ajeno)
        self.assertEqual(self.client.get(reverse("descargar_evidencia", args=[evidencia.public_id])).status_code, 404)
        self.assertNotContains(self.client.get(reverse("inicio")), "Trabajo de exposición")

    def test_estudiante_no_puede_evaluar_y_docente_no_puede_subir(self):
        self.enviar()
        evidencia = Evidencia.objects.get()
        self.client.force_login(self.estudiante)
        self.assertEqual(self.client.post(reverse("evaluar_evidencia", args=[evidencia.public_id]), {
            "decision": "approved", "comentario": "No permitido", "boscoins": 100,
        }).status_code, 403)
        self.client.force_login(self.docente)
        self.assertEqual(self.client.get(reverse("subir_evidencia")).status_code, 403)
        self.assertEqual(Movimiento.objects.count(), 0)

    def test_pdf_falso_se_rechaza(self):
        self.client.force_login(self.estudiante)
        response = self.client.post(reverse("subir_evidencia"), {
            "titulo": "Prueba de formato",
            "descripcion": "Adjunto un documento de laboratorio.",
            "archivo": SimpleUploadedFile("falso.pdf", b"<html>No es PDF</html>"),
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Evidencia.objects.count(), 0)
        self.assertContains(response, "PDF válido")

    def test_archivo_excesivo_se_rechaza(self):
        self.client.force_login(self.estudiante)
        response = self.client.post(reverse("subir_evidencia"), {
            "titulo": "Archivo enorme",
            "descripcion": "Archivo ficticio para comprobar límites.",
            "archivo": SimpleUploadedFile("gigante.pdf", b"%PDF-" + b"X" * (2 * 1024 * 1024)),
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "2 MB")
        self.assertEqual(Evidencia.objects.count(), 0)

    def test_imagen_png_valida_se_optimiza_como_en_meritum(self):
        buffer = BytesIO()
        Image.new("RGB", (40, 30), color="white").save(buffer, format="PNG")
        self.client.force_login(self.estudiante)
        response = self.client.post(reverse("subir_evidencia"), {
            "titulo": "Fotografía de la exposición",
            "descripcion": "Captura de una evidencia académica ficticia.",
            "archivo": SimpleUploadedFile("foto.png", buffer.getvalue(), content_type="image/png"),
        })
        self.assertRedirects(response, reverse("inicio"))
        evidencia = Evidencia.objects.get()
        self.assertEqual(evidencia.tipo_archivo, "image/jpeg")
        self.assertTrue(bytes(evidencia.contenido).startswith(bytes.fromhex("ffd8ff")))

    def test_csrf_real_protege_evaluacion(self):
        self.enviar()
        evidencia = Evidencia.objects.get()
        cliente = Client(enforce_csrf_checks=True)
        cliente.force_login(self.docente)
        response = cliente.post(reverse("evaluar_evidencia", args=[evidencia.public_id]), {
            "decision": "approved", "comentario": "Sin token CSRF", "boscoins": 100,
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Movimiento.objects.count(), 0)

    def test_nueva_version_no_se_envia_dos_veces(self):
        self.enviar()
        primera = Evidencia.objects.get()
        self.client.force_login(self.docente)
        self.client.post(reverse("evaluar_evidencia", args=[primera.public_id]), {
            "decision": "rejected", "comentario": "Corrige el procedimiento.",
        })
        url = reverse("reenviar_evidencia", args=[primera.public_id])
        self.enviar(url=url)
        self.assertRedirects(self.enviar(url=url), reverse("inicio"))
        self.assertEqual(Evidencia.objects.count(), 2)
