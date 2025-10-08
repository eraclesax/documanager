from __future__ import print_function
from builtins import str
from django.core.mail import EmailMultiAlternatives, get_connection
from mail.models import Mail
from django.template.loader import render_to_string
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

    to = [i for i in mail.to_who.split(';') if i != '']
    bcc = ''
    cc = ''
    if mail.bcc_who:
        bcc = [i for i in mail.bcc_who.split(';') if i != '']
    if mail.cc_who:
        cc =  [i for i in mail.cc_who.split(';') if i != '']
    reply_to = [i for i in mail.reply_to.split(';') if i != '']
    try:
        from_email = [i for i in mail.from_who.split(';') if i != ''][0]
    except:
        from_email = settings.DEFAULT_FROM_EMAIL
        
    subject = mail.subject
    try:
        template_context = mail.template_context.replace("'",'"')
        print(template_context)
        template_context = json.loads(template_context)
    except:
        import traceback
        traceback.print_exc()
        print('error on utils.py')
        template_context = mail.template_context

    template_context['uuid'] = str(mail.uuid)

    if settings.DEBUG_EMAIL:
        template_context['extra_info'] = 'to=' + ';'.join(to) + '   cc=' + ';'.join(cc)+ '   bcc=' + ';'.join(bcc)
        to = [settings.DEFAULT_FROM_EMAIL]
        bcc = None
        cc = None
    else:
        template_context['extra_info'] = ''
    
    template_html = 'mail/' + mail.template_name + '.html'
    template_text = 'mail/' + mail.template_name + '.txt'

    text_content = render_to_string(template_text, template_context )
    html_content = render_to_string(template_html, template_context )
    mail.html_text=html_content
    mail.txt_text=text_content
    mail.save()

    msg = EmailMultiAlternatives(subject, text_content, from_email, to, bcc=bcc , cc=cc, reply_to=reply_to)
    msg.attach_alternative(html_content, "text/html")

    if mail.attachments:
        attachments = [i for i in mail.attachments.split(';') if i != '']
        for f in attachments:
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
    
