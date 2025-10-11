# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User

def org_logo_path(instance, filename):
    return f"{instance.tag}/logo/{filename}"
class Organization(models.Model):
    tag = models.CharField(verbose_name="Tag Organizzazione", unique=True, max_length=255) #Usato per nome cartelle ecc.
    name = models.CharField(verbose_name="Nome Organizzazione", blank=False, null=False, max_length=255)
    email = models.EmailField(verbose_name="Email", blank=True, null=True)
    tel = models.CharField(verbose_name="Telefono", blank=True, null=True, max_length=63)
    is_active = models.BooleanField(verbose_name="Attiva", default=True)
    # Brandizzazione
    domain = models.CharField(max_length=200, blank=True, null=True)  # es: "azienda1.ade.it"
    logo = models.ImageField(verbose_name="Logo", upload_to=org_logo_path, blank=True, null=True)
    # Auto Fields
    created = models.DateTimeField(verbose_name="Data di creazione", auto_now_add=True) # Campo automatico, non compilare
    modified = models.DateTimeField(verbose_name="Ultima modifica", blank=True, null=True, auto_now=True) # Campo automatico, non compilare

    class Meta(): # type: ignore
        verbose_name = "Organizzazione"
        verbose_name_plural = "Organizzazioni"
    
    def __str__(self):
        return f"{self.name}"
        
def user_signature_path(instance, filename):
    return f"{instance.organization.tag}/users/{instance.user.username}/signature/{filename}"
def user_imgs_path(instance, filename):
    return f"{instance.organization.tag}/users/{instance.user.username}/imgs/{filename}"
class Profile(models.Model):
    """
    This is the base user of this app. It inherit from User, so all the functionality
    of the User class can be found here.
    """
    light_theme = "light"
    darl_theme = "dark"
    THEMES = (
        (light_theme,"Chiaro"),
        (darl_theme,"Scuro")
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    theme = models.CharField(verbose_name="Tema",max_length=512, choices=THEMES,default="light")
    img = models.ImageField(verbose_name="Immagine del profilo",null=True,blank=True,upload_to=user_imgs_path)
    organization = models.ForeignKey(Organization, verbose_name="Organizzazione", on_delete=models.PROTECT, blank=True, null=True)
    signature = models.ImageField(verbose_name="Firma", blank=True, null=True, upload_to=user_signature_path)
    
    class Meta():
        verbose_name = "Profilo utente"
        verbose_name_plural = "Profili utente"

    @property
    def get_active(self):
        if self.organization:
            return self.is_active and self.organization.is_active
        else:
            return self.is_active
    @get_active.setter
    def get_active(self,value):
        self.is_active = value
    
    def __str__(self):
        return f"{self.user.username}"
    
class Badge(models.Model):
    tag = models.CharField(verbose_name="tag", blank=True, null=True, max_length=255)
    name = models.CharField(verbose_name="Nome", blank=True, null=True, max_length=255)
    description = models.TextField(verbose_name="Descrizione", blank=True, null=True)
    validity = models.DateField(verbose_name="Valido fino al", blank=True, null=True)
    duration = models.DurationField(verbose_name="Durata", blank=True, null=True)
    active = models.BooleanField(verbose_name="Attivo", default=True)
    organization = models.ForeignKey(Organization, verbose_name="Organizzazione", on_delete=models.CASCADE, blank=True, null=True)  
    # Auto Fields
    created = models.DateTimeField(verbose_name="Data di creazione", auto_now_add=True) # Campo automatico, non compilare
    modified = models.DateTimeField(verbose_name="Ultima modifica", blank=True, null=True, auto_now=True) # Campo automatico, non compilare

    def refresh(self, activate=False):
        """
        Refresh the validity of the code
        """
        from datetime import datetime, timedelta
        if not activate:
            self.active = False
            self.validity = None # Badge disattivato
        else:
            self.active = True
            if self.duration is None:
                self.validity = None # Durata illimitata
            else:
                self.validity = datetime.today() + self.duration
        self.save()
        return self.validity
    
    def activate(self):
        from datetime import datetime, timedelta
        self.active = True
        if self.duration is None:
            self.validity = None # Durata illimitata
        else:
            self.validity = datetime.today() + self.duration

        self.save()
        return self.validity

        