from builtins import str
from builtins import object
from django.db import models
import uuid

class Mail(models.Model):

    ## Auto Fields
    id = models.AutoField(primary_key=True, verbose_name='Mail ID')
    sent = models.BooleanField(default=False, verbose_name='Inviata')
    creation_date = models.DateTimeField(auto_now_add=True, blank=True, verbose_name='Data di creazione')
    end_date = models.DateTimeField(null=True, blank=True, verbose_name='Data di invio')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    render = models.BooleanField(default=True, verbose_name='Renderizza')
    ## Setting fields
    retry = models.IntegerField(null=True, blank=True, default=0, verbose_name='Numero di tentativi')
    ## Email fields
    from_email = models.CharField(verbose_name='From email',max_length=255, null=True, blank=True,)
    reply_to = models.CharField(verbose_name='Reply to',max_length=255, null=True, blank=True,)
    to = models.JSONField(verbose_name="TOs (as a Python list)", default=list, null=True, blank=True)
    cc = models.JSONField(verbose_name='CCs (as a Python list)', default=list, null=True, blank=True,)
    bcc = models.JSONField(verbose_name='BCCs (as a Python list)', default=list, null=True, blank=True,)
    subject = models.TextField(verbose_name='Subject', null=True, blank=True,)
    template_name = models.CharField(verbose_name='Template name',max_length=255, null=True, blank=True,)
    template_context = models.JSONField(verbose_name='Template Context (JSON)', default=dict, null=True, blank=True,)
    html_text = models.TextField(verbose_name='Rendered Html Text', null=True, blank=True,)
    txt_text = models.TextField(verbose_name='Rendered Txt Text', null=True, blank=True,)
    attachments = models.JSONField(verbose_name='Attachments (as a Python list)', default=list, null=True, blank=True,)

    class Meta(object):
        verbose_name = 'Mail'
        verbose_name_plural = 'Mails'

    def __str__(self):
        return str(self.sent) + ' - ' + str(self.from_email) + ' - ' + str(self.subject)

    def save(self, *args, **kwargs):
        if self.render:
            from django.conf import settings
            from django.template.loader import render_to_string
            if not self.from_email:
                self.from_email = settings.DEFAULT_FROM_EMAIL
            if not self.reply_to:
                self.reply_to = settings.DEFAULT_REPLY_TO_EMAIL

            if not self.template_context:
                self.template_context = {}
            if not self.to:
                self.to = []
            if not self.cc:
                self.cc = []
            if not self.bcc:
                self.bcc = []
            if not self.bcc:
                self.bcc = []

            if settings.DEFAULT_BCC_EMAIL:
                self.bcc.append(settings.DEFAULT_BCC_EMAIL)

            self.template_context['uuid'] = str(self.uuid)
            self.template_context['extra_info'] = 'to=' + ';'.join(self.to) + \
                '   cc=' + ';'.join(self.cc) + \
                '   bcc=' + ';'.join(self.bcc)

            ## If template_name is not None, it overwrites the custom text and html
            if self.template_name:
                template_html = 'mail/' + self.template_name + '.html'
                template_text = 'mail/' + self.template_name + '.txt'
                self.txt_text = render_to_string(template_text, self.template_context )
                self.html_text = render_to_string(template_html, self.template_context )
            self.render = False

        super(Mail, self).save(*args, **kwargs) # Call the "real" save() method.
