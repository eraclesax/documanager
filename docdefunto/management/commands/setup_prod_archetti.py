from django.core.management.base import BaseCommand
# from docdefunto.utils import setup_prod_archetti

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
        self.stdout.write(self.style.NOTICE("Questo comando non è ancora stato abilitato!"))
        # self.stdout.write(self.style.NOTICE("Avvio inizializzazione server archetti..."))

        # if options["dry_run"]:
        #     self.stdout.write("Eseguo in modalità dry-run (nessuna modifica).")
        # else:
        # setup_prod_archetti()

        # self.stdout.write(self.style.SUCCESS("Inizializzazione server archetti completata."))