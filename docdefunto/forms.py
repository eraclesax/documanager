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
        
    ## Crispy forms helper for formatting staff
    helper = FormHelper()
    def __init__(self, *args,**kwargs):
        super().__init__(*args, **kwargs)

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
        