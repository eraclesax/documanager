#!/bin/bash

# File di log
LOGFILE="gunicorn_mem.log"

echo "Monitor di Gunicorn avviato. Scriverò i dati in $LOGFILE."
echo "Premi CTRL+C per fermare (se in foreground), oppure usa 'monitor_gunicorn.sh stop'."

case "$1" in
  start)
    # Avvia in background con nohup
    nohup bash -c 'while true; do
      echo "---- $(date) ----"
      ps -o pid,rss,cmd -p $(pgrep /home/ubuntu/documanager/venv/bin/python3 /home/ubuntu/documanager/venv/bin/gunicorn")
      echo
      sleep 5
    done' >> "$LOGFILE" 2>&1 &
    echo $! > monitor_gunicorn.pid
    echo "Monitor avviato (PID $(cat monitor_gunicorn.pid))"
    ;;
  stop)
    if [ -f monitor_gunicorn.pid ]; then
      kill $(cat monitor_gunicorn.pid) 2>/dev/null
      rm monitor_gunicorn.pid
      echo "Monitor fermato."
    else
      echo "Nessun monitor in esecuzione."
    fi
    ;;
  status)
    if [ -f monitor_gunicorn.pid ]; then
      echo "Monitor attivo (PID $(cat monitor_gunicorn.pid))"
    else
      echo "Monitor non in esecuzione."
    fi
    ;;
  *)
    echo "Uso: $0 {start|stop|status}"
    ;;
esac