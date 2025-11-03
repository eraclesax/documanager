import re, traceback, sys,os
from django.db import models
from django.utils.translation import gettext_lazy as _
from logger.utils import add_log
from app.models import Organization, User

class Anagrafica(models.Model):    
    # Metadata
    created_by = models.ForeignKey(User, verbose_name=_("Creato da"), on_delete=models.PROTECT, blank=False, null=False)
    organization = models.ForeignKey(Organization, verbose_name=_("Organizzazione"), on_delete=models.PROTECT, blank=False, null=False)
    
    # Autofields (non compilare)
    relative_id = models.PositiveIntegerField(blank=False, null=False) 
    created = models.DateTimeField(verbose_name="Data di creazione", auto_now_add=True) # Campo automatico, non compilare
    modified = models.DateTimeField(verbose_name="Ultima modifica", blank=True, null=True, auto_now=True) # Campo automatico, non compilare

    # User fields
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
        
    @classmethod
    def read_from_NFC(cls,save=False):
        from cie_nis_python_sdk.lib.CIEInterface import CIEInterface

        interface = CIEInterface()
        interface.mrtdAuth('930818', '290818', 'CA77748ET')
        data = interface.extractData()
        return data

        # if save:
        #     obj.save()

        # return obj