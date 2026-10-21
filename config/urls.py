from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from aula import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.inicio, name="inicio"),
    path("boscoins/otorgar/", views.otorgar, name="otorgar"),
    path("mercado/recompensas/nueva/", views.nueva_recompensa, name="nueva_recompensa"),
    path("mercado/canjear/<int:recompensa_id>/", views.canjear, name="canjear"),
    path("publicaciones/nueva/", views.nueva_publicacion, name="nueva_publicacion"),
]
