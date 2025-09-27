from django.core.management.base import BaseCommand
from docdefunto.utils import setup_superuser, crea_defunto_di_test

class Command(BaseCommand):
    help = "Inizializza i dati di test per admin e AnagraficaDefunto."

    # def add_arguments(self, parser):
    #     # Se vuoi parametri da riga di comando
    #     parser.add_argument(
    #         "--dry-run",
    #         action="store_true",
    #         help="Mostra cosa farebbe senza scrivere in DB",
    #     )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Avvio inizializzazione..."))

        # if options["dry_run"]:
        #     self.stdout.write("Eseguo in modalità dry-run (nessuna modifica).")
        # else:
        setup_superuser()
        crea_defunto_di_test() 

        self.stdout.write(self.style.SUCCESS("Inizializzazione completata."))