from django.contrib import admin, messages
from django.urls import reverse_lazy, path
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin 
from django.contrib.auth.models import User,Permission
from .models import *
from .forms import CustomPasswordResetForm
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import get_user_model
from logger.utils import add_log
User = get_user_model()

class ProfilerInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profilo"

class CustomUserAdmin(UserAdmin):
    list_display = [ld for ld in UserAdmin.list_display] + ["date_joined","invita"]

    def get_urls(self):
        """Aggiunge una URL custom per l’invio dell’invito."""
        urls = super().get_urls()
        # url = f"{obj.pk}/send-invite/{obj.pk}/"
        # invite_url = f"/admin/auth/user/send-invite/{obj.pk}/"
        custom_urls = [
            path(
                "send-invite/<int:user_id>/", 
                self.admin_site.admin_view(
                    self.send_invite_view
                ), 
                name="send_invite"
            ),
        ]
        return custom_urls + urls

    def send_invite_view(self, request, user_id):
        """Vista chiamata dal pulsante Invita."""
        from django.contrib.auth.views import PasswordResetView

        email_template_name='mail/password_set_email.txt'
        subject_template_name='mail/password_set_subject.txt'
        html_email_template_name= 'mail/password_set_email.html'

        if request.method == "GET":
            user = get_object_or_404(User, pk=user_id)
            try:
                form = CustomPasswordResetForm(data={"email": user.email})
                if form.is_valid():
                    opts = {
                        "use_https": request.is_secure(),
                        "token_generator": PasswordResetView.token_generator,
                        "from_email": PasswordResetView.from_email,
                        "email_template_name": email_template_name,
                        "subject_template_name": subject_template_name,
                        "request": request,
                        "html_email_template_name": html_email_template_name,
                        # "extra_email_context": {},
                    }
                    form.save(**opts)
                    if form.errors:
                        msg = f"Email di set password NON inviata a {user.email}: {form.errors}"
                        messages.error(request, msg)
                        # add_log(level=2, custom_message=msg) # Già loggato nel form
                        print(msg)
                    else:
                        msg = f"Email di set password inviata a {user.email}"
                        messages.success(request, msg)
                        # add_log(level=2, custom_message=msg) # Già loggato nel form
                        print(msg)
            except Exception as e:
                import traceback
                msg = f"Errore durante l'invio a {user.email}: {e}"
                messages.error(request, msg)
                add_log(level=4, custom_message=msg, exception=traceback.format_exc())
                traceback.print_exc()

            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/admin/"))


    def invita(self, obj):
        """Crea il pulsante HTML nella colonna."""
        if not obj.last_login:
            # Usa il reverse name della view admin custom
            context = {"user_id": obj.pk}
            return format_html(
                render_to_string("admin/send_mail_button.html", context)
            )
        return "—"

    invita.short_description = "Invia email nuovo utente"

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