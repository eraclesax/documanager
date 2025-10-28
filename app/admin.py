from django.contrib import admin
from django.urls import reverse_lazy
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin 
from django.contrib.auth.models import User,Permission
from .models import *
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string

class ProfilerInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profilo"

class CustomUserAdmin(UserAdmin):
    list_display = [ld for ld in UserAdmin.list_display] + ["date_joined","invita"]

    def invita(self, obj):
        if not obj.last_login:
            button = render_to_string(
                'admin/send_mail_button.html',
                {"email":obj.email}
                )
            return format_html(button)
            
    invita.short_description = 'Invia email nuovo utente'

    inlines = (ProfilerInline,)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'tag', 'email', 'is_active', 'domain')
    ordering = ['-pk']

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    pass

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'tag', 'name', 'active', 'organization', 'validity', 'duration')
    ordering = ['-pk']