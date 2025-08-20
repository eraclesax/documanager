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
        