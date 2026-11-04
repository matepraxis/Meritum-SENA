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


# Adaptación del EvidenceSubmissionForm y EvidenceReviewForm de MERITUM original.
import uuid
from .models import Evidencia
from .evidencias_archivos import validar_evidencia, MAX_EVIDENCIA_BYTES


class EvidenciaForm(forms.Form):
    token_envio = forms.UUIDField(
        required=False, initial=uuid.uuid4, widget=forms.HiddenInput,
    )
    titulo = forms.CharField(label="Título de la evidencia", max_length=120)
    descripcion = forms.CharField(
        label="¿Qué hiciste y qué aprendiste?", max_length=500, min_length=10,
        widget=forms.Textarea(attrs={"rows": 4}),
    )
    archivo = forms.FileField(
        label="Archivo de evidencia",
        help_text="PDF, JPG o PNG. Máximo 2 MB en esta demo temporal.",
        widget=forms.ClearableFileInput(attrs={"accept": ".pdf,.jpg,.jpeg,.png"}),
    )

    def clean_archivo(self):
        archivo = self.cleaned_data["archivo"]
        validar_evidencia(archivo)
        return archivo


class EvaluacionEvidenciaForm(forms.Form):
    decision = forms.ChoiceField(
        label="Decisión",
        choices=(
            (Evidencia.Estado.APROBADA, "Validar y otorgar Boscoins"),
            (Evidencia.Estado.AJUSTES, "Solicitar ajustes sin otorgar Boscoins"),
        ),
        widget=forms.RadioSelect,
    )
    comentario = forms.CharField(
        label="Observación para el estudiante",
        min_length=5, max_length=1000,
        widget=forms.Textarea(attrs={
            "rows": 5,
            "placeholder": "Reconoce lo logrado o explica con claridad qué debe ajustar.",
        }),
    )
    boscoins = forms.IntegerField(
        label="Boscoins (solo si se valida)",
        min_value=1, max_value=100, required=False,
    )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("decision") == Evidencia.Estado.APROBADA:
            if cleaned.get("boscoins") is None:
                self.add_error("boscoins", "Indica cuántos Boscoins deseas otorgar.")
        else:
            cleaned["boscoins"] = None
        return cleaned
