import os
import signal
import sys
import time
import gc
import tracemalloc
from django.core.management.base import BaseCommand
from customtest.models import MemoryLog

PID_FILE = "/tmp/memwatch.pid"

class Command(BaseCommand):
    help = "Monitoraggio memoria"

    def add_arguments(self, parser):
        parser.add_argument("--interval", type=int, default=600)
        parser.add_argument("--top", type=int, default=5)
        parser.add_argument("--stop", action="store_true")

    def handle(self, *args, **options):
        if options["stop"]:
            # interrompi processo
            if os.path.exists(PID_FILE):
                with open(PID_FILE) as f:
                    pid = int(f.read().strip())
                try:
                    os.kill(pid, signal.SIGTERM)
                    self.stdout.write(self.style.SUCCESS(f"Terminato processo {pid}"))
                except ProcessLookupError:
                    self.stdout.write(self.style.WARNING("Processo non trovato"))
                os.remove(PID_FILE)
            else:
                self.stdout.write(self.style.WARNING("Nessun PID file trovato"))
            return

        # avvio monitoraggio
        if os.path.exists(PID_FILE):
            self.stdout.write(self.style.ERROR("Memwatch già in esecuzione"))
            sys.exit(1)

        with open(PID_FILE, "w") as f:
            f.write(str(os.getpid()))

        interval = options["interval"]
        top = options["top"]

        tracemalloc.start()
        self.stdout.write(f"Avviato memwatch con pid {os.getpid()}")

        try:
            while True:
                time.sleep(interval)
                gc.collect()
                snapshot = tracemalloc.take_snapshot()
                top_stats = snapshot.statistics("lineno")

                for stat in top_stats[:top]:
                    MemoryLog.objects.create(
                        location=str(stat.traceback[0]),
                        size_kb=int(stat.size / 1024),
                        count=stat.count,
                    )

        except KeyboardInterrupt:
            pass
        finally:
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)
            self.stdout.write("Memwatch interrotto")