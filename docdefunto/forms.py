import datetime
from django.db.models import query
from django.forms import widgets
from django.forms.widgets import HiddenInput
from django.utils import timezone
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django.utils.translation import gettext_lazy as _
from .models import *

class DefuntoEditForm(forms.ModelForm):
    
    ## Crispy forms helper for formatting staff
    helper = FormHelper()
        
    # codice_fiscale = forms.CharField(
    #     max_length=16,
    #     required=False,
    #     widget=forms.TextInput(
    #         attrs={
    #             "style": "text-transform: uppercase;",
    #             # "placeholder": "Codice fiscale del defunto",
    #             "oninput": "this.value = this.value.toUpperCase()"
    #         }
    #     )
    # )

    class Meta:
        from .models import AnagraficaDefunto
        model = AnagraficaDefunto
        exclude = ("id",)
        # labels = {
        #     "name":"Nome",
        #     "full_address":"Indirizzo",
        #     "city":"Città",
        #     "province":"Provincia",
        #     "country":"Stato",
        # }
        
    def __init__(self, *args,**kwargs):
        super().__init__(*args, **kwargs)
        # Inserimento in uppercase
        self.fields['codice_fiscale'].widget.attrs['style'] = 'text-transform: uppercase;'
        self.fields['provincia_nascita'].widget.attrs['style'] = 'text-transform: uppercase;'
        self.fields['provincia_residenza'].widget.attrs['style'] = 'text-transform: uppercase;'
        self.fields['provincia_decesso'].widget.attrs['style'] = 'text-transform: uppercase;'
        self.fields['provincia_salma'].widget.attrs['style'] = 'text-transform: uppercase;'
        self.fields['provincia_chiesa'].widget.attrs['style'] = 'text-transform: uppercase;'
        self.fields['provincia_inumazione'].widget.attrs['style'] = 'text-transform: uppercase;'
        # Placeholders
        self.fields['data_nascita'].widget.attrs['placeholder'] = 'Es. 31/05/1936'
        self.fields['data_doc_def'].widget.attrs['placeholder'] = 'Es. 31/05/1936'
        self.fields['data_morte'].widget.attrs['placeholder'] = 'Es. 31/05/1936'
        self.fields['ora_morte'].widget.attrs['placeholder'] = 'Es. 21:45'
        self.fields['via_salma'].widget.attrs['placeholder'] = 'Omettere la parola "Via"'
        self.fields['data_nascita_parente'].widget.attrs['placeholder'] = 'Es. 31/05/1936'
        self.fields['data_doc_par'].widget.attrs['placeholder'] = 'Es. 31/05/1936'
        self.fields['data_ora_funerale'].widget.attrs['placeholder'] = 'Es. 31/05/1936 15:30'
        # self.fields['data_inumazione'].widget.attrs['placeholder'] = 'Es. 31/05/1936'
        # self.fields['ora_inumazione'].widget.attrs['placeholder'] = 'Es. 21:45'
        self.fields['data_incarico'].widget.attrs['placeholder'] = 'Es. 31/05/1936'
        self.fields['affissione_manifesti'].widget.attrs['placeholder'] = 'Rionero in Vulture\nBarile\necc.'

        # aggiungo un onchange al select di stato_civile
        self.fields['stato_civile'].widget.attrs.update({
            'onchange': 'toggleConiugeFields(this.value);'
        })
        # # inizialmente nascondo i campi coniuge
        # self.fields['cognome_coniuge'].widget.attrs.update({
        #     'style': 'display:none;'
        # })
        # self.fields['nome_coniuge'].widget.attrs.update({
        #     'style': 'display:none;'
        # })

    def clean_codice_fiscale(self):
        value = self.cleaned_data["codice_fiscale"]
        # Validazione sul numero di caratteri
        if value is None:
            return None
        value = value.strip()
        if len(value) != 16:
            raise forms.ValidationError("Il codice fiscale deve avere esattamente 16 caratteri.")
        # Salva in uppercase
        value = value.upper()
        return value
    
    def clean_provincia_nascita(self):
        value = self.cleaned_data['provincia_nascita']
        if value:
            value = value.upper()
        return value
    
    def clean_provincia_residenza(self):
        value = self.cleaned_data['provincia_residenza']
        if value:
            value = value.upper()
        return value
    
    def clean_provincia_decesso(self):
        value = self.cleaned_data['provincia_decesso']
        if value:
            value = value.upper()
        return value
    def clean_provincia_salma(self):
        value = self.cleaned_data['provincia_salma']
        if value:
            value = value.upper()
        return value
    
    def clean_provincia_chiesa(self):
        value = self.cleaned_data['provincia_chiesa']
        if value:
            value = value.upper()
        return value
    
    def clean_provincia_inumazione(self):
        value = self.cleaned_data['provincia_inumazione']
        if value:
            value = value.upper()
        return value

class DynamicJsonConfigForm(forms.Form):
    """
    Form che genera dinamicamente i campi a partire dal JSON.
    """

    def __init__(self, *args, json_data=None, **kwargs):
        super().__init__(*args, **kwargs)

        if json_data is None:
            json_data = {}

        for field_name, field_data in json_data.items():
            info = field_data.get("info", {})

            # Aggiungo i campi dinamici con un prefisso legato al "nome logico" (es. cognome, nome…)
            self.fields[f"{field_name}_x"] = forms.IntegerField(
                label=f"{field_name.capitalize()} X",
                initial=field_data.get("x", 0)
            )
            self.fields[f"{field_name}_y"] = forms.IntegerField(
                label=f"{field_name.capitalize()} Y",
                initial=field_data.get("y", 0)
            )
            self.fields[f"{field_name}_font"] = forms.CharField(
                label=f"{field_name.capitalize()} Font",
                initial=info.get("font", "Helvetica"),
                max_length=50
            )
            self.fields[f"{field_name}_size"] = forms.IntegerField(
                label=f"{field_name.capitalize()} Font Size",
                initial=info.get("size", 12)
            )
            self.fields[f"{field_name}_active"] = forms.BooleanField(
                label=f"{field_name.capitalize()} Active",
                initial=info.get("active", False),
                required=False
            )
            self.fields[f"{field_name}_invert_y"] = forms.BooleanField(
                label=f"{field_name.capitalize()} Invert Y",
                initial=info.get("invert_y", False),
                required=False
            )

        # Salvo i nomi dei "gruppi logici" per ricostruire il JSON
        self._json_keys = list(json_data.keys())

    def to_json(self):
        """
        Ricostruisce il JSON a partire dai dati del form.
        """
        data = {}
        for key in self._json_keys:
            data[key] = {
                "x": self.cleaned_data[f"{key}_x"],
                "y": self.cleaned_data[f"{key}_y"],
                "info": {
                    "font": self.cleaned_data[f"{key}_font"],
                    "size": self.cleaned_data[f"{key}_size"],
                    "active": self.cleaned_data[f"{key}_active"],
                    "invert_y": self.cleaned_data[f"{key}_invert_y"],
                }
            }
        return data
        