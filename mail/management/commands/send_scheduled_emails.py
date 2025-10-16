import time, random, json, os
from datetime import datetime, timedelta
from django.conf import settings
from django.core.management.base import BaseCommand
from mail.models import Mail 
from app.models import Badge, Organization
from logger.utils import add_log

class Command(BaseCommand):
    help = "Invia email in modo scaglionato secondo una policy temporale"

    def add_arguments(self, parser):
        parser.add_argument(
            "file",
            type=str,
            help="Percorso relativo del file JSON o TXT contenente indirizzi e dati email",
            required=True,
        )
        parser.add_argument(
            "-f",
            "--fake_delay",
            action="store_true",
            help="Imposta il reale ritardo di invio a 0s simulando la generazione del ritardo normalmente",
        )

    def handle(self, *args, **options):
        filepath = os.path.join(os.path.dirname(__file__), options["file"])
        fake_delay = options["fake_delay"]
        msg =  f"[{datetime.now()}] Lettura file: {filepath}"
        self.stdout.write(msg)
        add_log(level=2, custom_message=f"Command send_scheduled_emails: {msg}")

        # --- 1. Leggi file (può essere JSON o semplice lista di email)
        data = self._read_input_file(filepath)
        # --- 2. Crea organizzazione e codice promozionale
        msg =  f"Inizio il processo per inviare {len(data)} email.\n"
        self.stdout.write(msg)
        add_log(level=2, custom_message=f"Command send_scheduled_emails: {msg}")
        for entry in data:
            # --- 3. Applica la policy di ritardo “umano”
            self._wait_policy(fake_delay=fake_delay)
            # --- 4. Genera le email e altri oggetti
            organization, _ = self._get_or_create_trial_organization(entry)
            promo_code, _ = self._get_or_create_freetrial30(organization)
            mail = self._create_freetrial30_mail(organization,promo_code)
            # --- 5. Invia effettivamente l’email
            try:
                mail.send()
                msg =  f"Inviata a {mail.to}"
                self.stdout.write(self.style.SUCCESS(msg))
                add_log(level=2, custom_message=f"Command send_scheduled_emails: {msg}")
            except Exception as e:
                msg =  self.style.ERROR(f"Errore con {mail.to}: {e}")
                self.stdout.write(self.style.SUCCESS(msg))
                add_log(level=2, custom_message=f"Command send_scheduled_emails: {msg}")

        msg = "Tutte le email sono state processate."
        self.stdout.write(self.style.SUCCESS(msg))
        add_log(level=2, custom_message=f"Command send_scheduled_emails: {msg}")

    def _read_input_file(self, filepath:str):
        """
        Reads the input file and create mails, organizations and promo_codes. The file must have
        this structure:

        <email organization 1>, <name organization 1>, <tag organization 1>
        <email organization 2>, <name organization 2>, <tag organization 2>
        ...

        """
        if filepath.endswith(".json"):
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            with open(filepath, "r", encoding="utf-8") as f:
                data = []
                for line in f:
                    if line.strip():
                        args = line.split(",")
                        data.append({
                            "email" : args[0].strip(),
                            "organization_name" : args[1].strip(),
                            "organization_tag" : args[2].lower().strip(),
                        })
        return data
    
    def _get_or_create_trial_organization(self, data:dict):
        """
        Get or create a trial organization account using the information contained in the dictionary data
        """
        organization, c = Organization.objects.get_or_create(
            tag = data["organization_tag"],
            defaults={
                "name" : data["organization_name"],
                "email" : data["email"],
                "domain" : settings.TRIAL_DOMAIN,
            }
        )
        if c:
            msg = f" - Creata Organizzazione(id={organization.pk})"
            self.stdout.write(msg)
            add_log(level=2, custom_message=f"Command send_scheduled_emails: {msg}")
        else:
            msg = f" - Trovata Organizzazione(id={organization.pk})"
            self.stdout.write(msg)
            add_log(level=2, custom_message=f"Command send_scheduled_emails: {msg}")
        
        return organization, c
    
    def _get_or_create_freetrial30(self, organization:Organization):
        """
        Get or create a promo code using the information contained in the dictionary data
        """
        promo_code, c = Badge.objects.get_or_create(
            tag = "prova30" + organization.tag,
            organization = organization,
            defaults={
                "name" : "Free-trial promo code 30 days",
                "duration" : timedelta(days=30),
            }
        )
        if c:
            msg = f" - Creato PromoCode(id={promo_code.pk})"
            self.stdout.write(msg)
            add_log(level=2, custom_message=f"Command send_scheduled_emails: {msg}")
        else:
            promo_code.refresh()
            msg = f" - Trovato PromoCode(id={promo_code.pk})"
            self.stdout.write(msg)
            add_log(level=2, custom_message=f"Command send_scheduled_emails: {msg}")
            
        return promo_code, c

    def _create_freetrial30_mail(self,organization:Organization,promo_code:Badge):
        mail = Mail(
            from_email = settings.DEFAULT_FROM_EMAIL,
            reply_to = settings.DEFAULT_REPLY_TO_EMAIL,
            to = [organization.email,],
            subject = "Proposta di applicativo per la vostra Agenzia",
            template_name = "freetrial30",
            template_context = {
                "organization_name" : organization.name,
                "promo_code" : promo_code.tag,
                "trial_url_name" : "trial_login",
                "prices_url_name" : "site_prices",
                "full_url" : settings.FULL_URL,
            },
        )
        mail.save()
        msg = f"Salvata Mail(id={mail.id}) → {mail.to}"
        self.stdout.write(msg)
        add_log(level=2, custom_message=f"Command send_scheduled_emails: {msg}")
        
        return mail

    # ============================================================
    # Policy temporale
    # ============================================================
    def _get_delay(self,lmbda,min=0,max=10**17,gen_limit=100000):
        i = 0
        delay = -1
        while delay < min or delay > max or i < 1000:
            i += 1
            delay = random.expovariate(lmbda)
        if i == gen_limit:
            delay = lmbda
            msg =  f"send_scheduled_emails.Command._wait_policy WARNING: random generation loop limit reached"
            self.stdout.write(msg)
            add_log(level=3, custom_message=msg)
        return delay

    def _wait_policy(self,fake_delay=False):
        """Definisce i tempi di attesa tra un invio e l'altro."""
        # Invio ogni min_delay-max_delay minuti, con jitter casuale 
        # esponenziale decrescente (simula azioni random) e media average
        average = 10 * 60 # 10 min
        min_delay = 5 * 60   # 5 minuti = 5 * 60
        max_delay = 24 * 60 * 60   # 24 ore
        # Invio solo in una certa fascia oraria, dalle min_hour alle max_hour
        min_hour = 9
        max_hour = 14

        now = datetime.now()
        if min_hour < max_hour:
            condition = now.hour >= min_hour and now.hour < max_hour
            if not condition:
                delay = ((24 - (now.hour - min_hour))%24)*60*60
            else:
                delay = self._get_delay(average,min_delay,max_delay)
        elif min_hour > max_hour:
            condition = (now.hour >= min_hour and now.hour <= 23) or (now.hour >= 0 and now.hour < max_hour)
            if not condition:
                delay = (min_hour - now.hour )*60*60
            else:
                delay = self._get_delay(average,min_delay,max_delay)

        next_time = (datetime.now() + timedelta(seconds=delay)).strftime("%d/%m/%Y %H:%M:%S")
        msg = f"Aspetto {delay//60} min (fake_delay={fake_delay}) prima del prossimo invio ({next_time})\n"
        self.stdout.write(msg)
        add_log(level=2, custom_message=f"Command send_scheduled_emails: {msg}")
        if fake_delay:
            time.sleep(0)
        else:
            time.sleep(delay)
