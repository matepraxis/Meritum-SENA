from django import forms
from django.contrib.auth import get_user_model
from .models import Perfil, Publicacion, Recompensa


class ReconocimientoForm(forms.Form):
    estudiante = forms.ModelChoiceField(queryset=get_user_model().objects.none(), label="Estudiante")
    cantidad = forms.IntegerField(min_value=1, max_value=100, label="Boscoins (1-100)")
    motivo = forms.CharField(max_length=200, label="Motivo pedagógico")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["estudiante"].queryset = get_user_model().objects.filter(perfil__rol=Perfil.Rol.ESTUDIANTE).order_by("username")


class RecompensaForm(forms.ModelForm):
    class Meta:
        model = Recompensa
        fields = ["nombre", "descripcion", "costo", "existencias", "activa"]


class PublicacionForm(forms.ModelForm):
    class Meta:
        model = Publicacion
        fields = ["titulo", "contenido"]
        widgets = {"contenido": forms.Textarea(attrs={"rows": 5})}
