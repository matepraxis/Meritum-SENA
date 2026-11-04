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


MAX_EVIDENCIA_BYTES = 2 * 1024 * 1024
TIPOS_EVIDENCIA = {
    ".pdf": ("application/pdf", b"%PDF-"),
    ".png": ("image/png", b"\\x89PNG\\r\\n\\x1a\\n"),
    ".jpg": ("image/jpeg", b"\\xff\\xd8\\xff"),
    ".jpeg": ("image/jpeg", b"\\xff\\xd8\\xff"),
}


class EvidenciaForm(forms.Form):
    titulo = forms.CharField(label="Título de la evidencia", max_length=120)
    descripcion = forms.CharField(
        label="Descripción breve", max_length=500, required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    archivo = forms.FileField(
        label="Archivo de evidencia",
        help_text="PDF, JPG o PNG. Tamaño máximo: 2 MB. Solo archivos ficticios.",
        widget=forms.ClearableFileInput(attrs={"accept": ".pdf,.jpg,.jpeg,.png"}),
    )

    def clean_archivo(self):
        from pathlib import Path

        archivo = self.cleaned_data["archivo"]
        if archivo.size == 0 or archivo.size > MAX_EVIDENCIA_BYTES:
            raise forms.ValidationError("El archivo debe pesar entre 1 byte y 2 MB.")
        extension = Path(archivo.name).suffix.lower()
        if extension not in TIPOS_EVIDENCIA:
            raise forms.ValidationError("Solo se permiten PDF, JPG y PNG.")
        _, firma = TIPOS_EVIDENCIA[extension]
        principio = archivo.read(8)
        archivo.seek(0)
        if not principio.startswith(firma):
            raise forms.ValidationError("El contenido del archivo no coincide con su formato.")
        return archivo


class EvaluacionEvidenciaForm(forms.Form):
    comentario = forms.CharField(
        label="Comentarios y retroalimentación", max_length=1200, min_length=3,
        widget=forms.Textarea(attrs={
            "rows": 5, "placeholder": "Explica qué hizo bien y qué puede mejorar..."
        }),
    )
    boscoins = forms.IntegerField(
        label="Boscoins por esta evidencia (1 a 100)", min_value=1, max_value=100,
    )
