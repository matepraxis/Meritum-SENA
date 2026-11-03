"""Comprobación mínima de disponibilidad sin información sensible."""
from django.db import DatabaseError, connection
from django.http import HttpResponse
from django.views.decorators.http import require_GET


@require_GET
def salud(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except DatabaseError:
        respuesta = HttpResponse("Sin servicio", content_type="text/plain", status=503)
    else:
        respuesta = HttpResponse("OK", content_type="text/plain")
    respuesta["Cache-Control"] = "no-store"
    return respuesta
