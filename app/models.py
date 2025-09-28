# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import traceback,os
from django.db import models
from django.contrib.auth.models import User,Group
from django.contrib.admin import ModelAdmin
from django.contrib.contenttypes.fields import GenericRelation,GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.conf import settings

def org_logo_path(instance, filename):
    return f"{instance.tag}/logo/{filename}"
class Organization(models.Model):
    tag = models.CharField(verbose_name="Tag Organizzazione", blank=False, null=False, unique=True, max_length=255) #Usato per nome cartelle ecc.
    name = models.CharField(verbose_name="Nome Organizzazione", blank=False, null=False, max_length=255)
    email = models.EmailField(verbose_name="Email", blank=True, null=True)
    tel = models.CharField(verbose_name="Telefono", blank=True, null=True, max_length=63)
    is_active = models.BooleanField(verbose_name="Attiva", default=True)
    # Contabilità
    free_trial = models.BooleanField(verbose_name="Periodo di prova", default=False)
    free_trial_finish = models.DateField(verbose_name="Fine periodo di prova", blank=True, null=True)
    account_expires = models.DateField(verbose_name="Scadenza account", blank=True, null=True)
    # Brandizzazione
    domain = models.CharField(max_length=200, unique=True)  # es: "azienda1.ade.it"
    logo = models.ImageField(verbose_name=_("Logo"), upload_to=org_logo_path, blank=True, null=True)

    class Meta(): # type: ignore
        verbose_name = _("Organizzazione")
        verbose_name_plural = _("Organizzazioni")
    
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
        (light_theme,_("Chiaro")),
        (darl_theme,_("Scuro"))
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    theme = models.CharField(verbose_name=_("Tema"),max_length=512, choices=THEMES,default="light")
    img = models.ImageField(verbose_name=_("Immagine del profilo"),null=True,blank=True,upload_to=user_imgs_path)
    organization = models.ForeignKey(Organization, verbose_name=_("Organizzazione"), on_delete=models.PROTECT, blank=True, null=True)
    signature = models.ImageField(verbose_name=_("Firma"), blank=True, null=True, upload_to=user_signature_path)
    
    class Meta():
        verbose_name = _("Profilo utente")
        verbose_name_plural = _("Profili utente")

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
    

