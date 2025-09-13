# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin 
from django.contrib.auth.models import User,Permission
from .models import *
from django.utils.translation import gettext_lazy as _

class ProfilerInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profilo"

class CustomUserAdmin(UserAdmin):
    inlines = (ProfilerInline,)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    pass
