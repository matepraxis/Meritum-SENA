from django.contrib import admin
from .models import Canje, Movimiento, Perfil, Publicacion, Recompensa


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("usuario", "rol", "grado")
    list_filter = ("rol", "grado")
    search_fields = ("usuario__username",)


@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ("estudiante", "cantidad", "motivo", "responsable", "fecha")
    list_filter = ("fecha",)
    readonly_fields = ("estudiante", "cantidad", "motivo", "responsable", "fecha")
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Canje)
class CanjeAdmin(admin.ModelAdmin):
    list_display = ("estudiante", "recompensa", "costo_aplicado", "fecha")
    readonly_fields = ("estudiante", "recompensa", "costo_aplicado", "fecha")
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Recompensa)
admin.site.register(Publicacion)
admin.site.site_header = "Administración Meritum-SENA"
