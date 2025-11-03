import re, traceback
from django.db import models
from logger.utils import add_log

class Anagrafica(models.Model):
    cognome = models.CharField(verbose_name="Cognome Defunto", blank=True, null=True, max_length=255)
    nome = models.CharField(verbose_name="Nome Defunto", blank=True, null=True, max_length=255)
    sesso = models.CharField(verbose_name="Sesso", max_length=1, blank=True, null=True, 
                             choices=[
                                 ("F", "Femmina"),
                                 ("M", "Maschio")]
                                 )
    def __str__(self):
        try:
            return f"{self.cognome} {self.nome}"
        except Exception as e:
            add_log(level=4,exception=traceback.format_exc(),custom_message="Exception in Anagrafica.__str__")
            raise(e)