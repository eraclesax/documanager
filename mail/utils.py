from __future__ import print_function
from mail.models import Mail


def send_msgs():
    # prendo tutte le mail fallite e provo a reinviarle
    mails = Mail.objects.filter(sent=False)
    for mail in mails:
        mail.send()
    
