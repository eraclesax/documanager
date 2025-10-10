from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect, get_object_or_404
from mail.models import Mail
from mail.utils import _send

def send_selected(modeladmin, request, queryset):
    for mail in queryset:
        _send(mail)

send_selected.short_description = "Send selected mail"

class MailAdmin(admin.ModelAdmin):
    actions = [send_selected]
    list_display = ('pk', 'to', 'subject', 'creation_date', 'sent', 'uuid', 'apri_link', "duplica_link")
    list_filter = ('sent', )
    ordering = ['-pk']

    def apri_link(self, obj):
        return format_html('<a class="button" href="/mail/render/%s/" target="_blank">Apri</a>' % (obj.uuid))
        
    apri_link.short_description = 'Dettagli'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:object_id>/duplica/",
                self.admin_site.admin_view(self.duplica_view),
                name="mail_duplica",
            ),
        ]
        return custom_urls + urls

    def duplica_link(self, obj):
        return format_html(
            '<a class="button" href="{}">Duplica</a>',
            f"{obj.id}/duplica/",
        )
    duplica_link.short_description = "Duplica"

    def duplica_view(self, request, object_id):
        import uuid
        obj = get_object_or_404(Mail, pk=object_id)
        obj.pk = None  # questo crea una copia
        obj.sent = False
        obj.end_date = None
        obj.html_text = None
        obj.txt_text = None
        obj.uuid = uuid.uuid4()
        obj.save()
        self.message_user(request, f"'{obj}' duplicato con successo.")
        return redirect("admin:mail_mail_change", obj.pk)

admin.site.register(Mail, MailAdmin)
