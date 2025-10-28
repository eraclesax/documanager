import time, random, json, os
from datetime import datetime, timedelta
from django.conf import settings
from django.core.management.base import BaseCommand
from mail.models import Mail 
from app.models import Badge, Organization
from logger.utils import add_log

from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Invia email in modo scaglionato secondo una policy temporale"

    def add_arguments(self, parser):
        parser.add_argument(
            "username",
            type=str,
            help="Username",
        )
        parser.add_argument(
            "email",
            type=str,
            help="Indirizzo email",
        )

    def handle(self, *args, **options):
        username = options["username"]
        email = options["email"]
        try:
            # --- Crea nuovo utente
            User = get_user_model()

            user = User.objects.create_user(
                username=username,
                email=email,
                password=None
            )
            user.is_active = True
            user.save()

            msg = f"Creato utente {username} con email {email}"
            add_log(level=2, custom_message=f"Command send_scheduled_emails: {msg}")
            self.stdout.write(self.style.SUCCESS(msg))
        except Exception as exc:
            import traceback
            msg = "Errore durante la creazione dell'utente %s"%username
            add_log(level=4, custom_message=msg,exception=traceback.format_exc())
            self.stdout.write(self.style.ERROR(msg))
            traceback.print_exc()