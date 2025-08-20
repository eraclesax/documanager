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

# class AnagraficaForm(forms.ModelForm):
#     class Meta:
#         model = AnagraficaDefunto
#         fields = ['title', 'author', 'publication_year']
        