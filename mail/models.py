import uuid
from builtins import str, object
from django.db import models
from django.conf import settings
from logger.utils import add_log

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
                if settings.DEFAULT_BCC_EMAIL not in self.bcc:
                    self.bcc.append(settings.DEFAULT_BCC_EMAIL)

            self.template_context['uuid'] = str(self.uuid)
            extra_info = ""
            if self.to:
                extra_info += 'to=' + ';'.join(self.to)
            if self.cc:
                extra_info += '   cc=' + ';'.join(self.cc)
            if self.bcc:
                extra_info += '   bcc=' + ';'.join(self.bcc)
            self.template_context['extra_info'] = extra_info

            ## If template_name is not None, it overwrites the custom text and html
            if self.template_name:
                template_html = 'mail/' + self.template_name + '.html'
                template_text = 'mail/' + self.template_name + '.txt'
                self.txt_text = render_to_string(template_text, self.template_context )
                self.html_text = render_to_string(template_html, self.template_context )
            self.render = False

        super(Mail, self).save(*args, **kwargs) # Call the "real" save() method.
    
    def send(self):
        from django.utils import timezone
        from django.core.mail import EmailMultiAlternatives, get_connection

        if settings.DEBUG_EMAIL:
            to = [settings.DEFAULT_REPLY_TO_EMAIL]
            bcc = None
            cc = None
        else:
            to = self.to
            bcc = self.bcc
            cc = self.cc

        subject = self.subject or ""
        body = self.txt_text or ""
        from_email = self.from_email
        reply_to = [self.reply_to,] if self.reply_to else []
        attachments = self.attachments or []

        msg = EmailMultiAlternatives(
            subject = subject, 
            body = body, 
            from_email = from_email, 
            to = to, 
            bcc = bcc, 
            cc = cc, 
            reply_to = reply_to,
            )
        msg.attach_alternative(self.html_text or "" , "text/html")

        if attachments:
            for file_path in attachments:
                msg.attach_file( str(file_path) )

        try:
            print('Starting email send')
            connection = get_connection()
            connection.username = settings.EMAIL_HOST_USER
            connection.password = settings.EMAIL_HOST_PASSWORD
            connection.host = settings.EMAIL_HOST
            connection.port = settings.EMAIL_PORT
            connection.use_ssl = settings.EMAIL_USE_SSL
            connection.send_messages([msg,])
            connection.close()
            print('Email sended.')

            self.end_date = timezone.now()
            self.sent = True
            self.save()

            msg =  f"Inviata email {self.pk} con oggetto: {self.subject} -> {self.to}"
            add_log(level=2, custom_message=f"mail.send: {msg}")
        except Exception as exc:
            # print('Error get_dashbaord_url: %s' % e)
            # TODO: forse basta il print(sopra senza usare sys.exc_info()[0])
            import sys
            exc = sys.exc_info()
            retry = self.retry or 0
            self.retry = retry + 1
            print(exc)
            add_log(level=4, exception=exc )
            self.save()
