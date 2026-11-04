from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from aula import views, evidencias
from aula.health import salud

urlpatterns = [
    path("salud/", salud, name="salud"),
    path("admin/", admin.site.urls),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.inicio, name="inicio"),
    path("evidencias/subir/", evidencias.subir_evidencia, name="subir_evidencia"),
    path("evidencias/<int:evidencia_id>/archivo/", evidencias.descargar_evidencia, name="descargar_evidencia"),
    path("evidencias/<int:evidencia_id>/evaluar/", evidencias.evaluar_evidencia, name="evaluar_evidencia"),
    path("boscoins/otorgar/", views.otorgar, name="otorgar"),
    path("mercado/recompensas/nueva/", views.nueva_recompensa, name="nueva_recompensa"),
    path("mercado/canjear/<int:recompensa_id>/", views.canjear, name="canjear"),
    path("publicaciones/nueva/", views.nueva_publicacion, name="nueva_publicacion"),
]
