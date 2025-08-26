from django.contrib import admin
from .models import *

class AnagraficaDefuntoAdmin(admin.ModelAdmin):
    pass

class DocumentoAdmin(admin.ModelAdmin):
    pass

admin.site.register(AnagraficaDefunto, AnagraficaDefuntoAdmin)
admin.site.register(Documento, DocumentoAdmin)
