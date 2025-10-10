from __future__ import print_function
from builtins import str
from django.core.mail import EmailMultiAlternatives, get_connection
from mail.models import Mail
from django.utils import timezone
from logger.utils import add_log
import json
from django.conf import settings


def send_msgs():
    # prendo tutte le mail fallite e provo a reinviarle
    mails = Mail.objects.filter(sent=False)
    for mail in mails:
        _send(mail)


def _send(mail):

    if settings.DEBUG_EMAIL:
        to = [settings.DEFAULT_REPLY_TO_EMAIL]
        bcc = None
        cc = None
    else:
        to = mail.to
        bcc = mail.bcc
        cc = mail.cc

    msg = EmailMultiAlternatives(
        subject = mail.subject, 
        body = mail.txt_text, 
        from_email = mail.from_email, 
        to = to, 
        bcc = bcc, 
        cc = cc, 
        reply_to = [mail.reply_to,],
        )
    msg.attach_alternative(mail.html_text, "text/html")

    if mail.attachments:
        for f in mail.attachments:
            msg.attach_file( str(f) )

    try:
        print('here')
        connection = get_connection()
        connection.username = settings.EMAIL_HOST_USER
        connection.password = settings.EMAIL_HOST_PASSWORD
        connection.host = settings.EMAIL_HOST
        connection.port = settings.EMAIL_PORT
        connection.use_ssl = settings.EMAIL_USE_SSL
        connection.send_messages([msg,])
        connection.close()

        print('sended?')

        mail.end_date = timezone.now()
        mail.sent = True
        mail.save()

    except Exception as e:
        # print('Error get_dashbaord_url: %s' % e)
        # TODO: forse basta il print(sopra senza usare sys.exc_info()[0])
        import sys
        e = sys.exc_info()
        print(e)
        mail.retry = mail.retry + 1
        add_log(level=5, message=1, custom_message=e )
        mail.save()
    
