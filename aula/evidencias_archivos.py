"""Adaptación de evidence/images.py y validate_evidence_file de MERITUM original.

Los adjuntos de la demo se guardan privados en SQLite efímera (no en MEDIA público).
"""
from io import BytesIO
from pathlib import Path

from django.core.exceptions import ValidationError
from PIL import Image, ImageOps, UnidentifiedImageError


MAX_EVIDENCIA_BYTES = 2 * 1024 * 1024
MAX_SOURCE_PIXELS = 24_000_000
MAX_IMAGE_EDGE = 2048
TIPOS_EVIDENCIA = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}


def validar_evidencia(archivo):
    extension = Path(archivo.name).suffix.lower()
    if extension not in TIPOS_EVIDENCIA:
        raise ValidationError("Adjunta un PDF, PNG o JPG.")
    if archivo.size < 1 or archivo.size > MAX_EVIDENCIA_BYTES:
        raise ValidationError("El archivo debe pesar entre 1 byte y 2 MB.")
    try:
        archivo.seek(0)
        if extension == ".pdf":
            if archivo.read(5) != b"%PDF-":
                raise ValidationError("El archivo no contiene un PDF válido.")
            return
        with Image.open(archivo) as image:
            ancho, alto = image.size
            if ancho < 1 or alto < 1 or ancho * alto > MAX_SOURCE_PIXELS:
                raise ValidationError("La imagen supera el límite de 24 megapíxeles.")
            if image.format not in ("JPEG", "PNG"):
                raise ValidationError("El archivo no coincide con una imagen JPG o PNG.")
            if extension == ".png" and image.format != "PNG":
                raise ValidationError("El archivo no coincide con su extensión PNG.")
            if extension in (".jpg", ".jpeg") and image.format != "JPEG":
                raise ValidationError("El archivo no coincide con su extensión JPG.")
            image.verify()
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:
        raise ValidationError("No fue posible verificar el archivo de imagen.") from exc
    finally:
        archivo.seek(0)


def preparar_evidencia(archivo):
    """Optimiza fotografías como en Meritum; no convierte ni ejecuta el PDF."""
    validar_evidencia(archivo)
    extension = Path(archivo.name).suffix.lower()
    if extension == ".pdf":
        return Path(archivo.name).name[:120], "application/pdf", archivo.read()

    try:
        with Image.open(archivo) as original:
            original.draft("RGB", (MAX_IMAGE_EDGE, MAX_IMAGE_EDGE))
            original.thumbnail((MAX_IMAGE_EDGE, MAX_IMAGE_EDGE), Image.Resampling.LANCZOS, reducing_gap=2.0)
            girada = ImageOps.exif_transpose(original)
            try:
                imagen = girada.convert("RGB")
                try:
                    salida = BytesIO()
                    imagen.save(salida, "JPEG", quality=78, optimize=True)
                    return "imagen-optimizada.jpg", "image/jpeg", salida.getvalue()
                finally:
                    imagen.close()
            finally:
                girada.close()
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:
        raise ValidationError("No fue posible procesar la imagen.") from exc
    finally:
        archivo.seek(0)
