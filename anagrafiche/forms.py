from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset
from crispy_forms.helper import FormHelper
from django.utils.translation import gettext_lazy as _
from .models import Anagrafica

class AnagraficaEditForm(forms.ModelForm):

    class Meta:
        from .models import Anagrafica
        model = Anagrafica
        fields = ["cognome", "nome", "sesso",]