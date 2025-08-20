from django.contrib import admin
from .models import *

class AnagraficaDefuntoAdmin(admin.ModelAdmin):
    pass

admin.site.register(AnagraficaDefunto, AnagraficaDefuntoAdmin)
