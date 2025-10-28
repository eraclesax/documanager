from __future__ import print_function
import json
from mail.models import Mail


def send_msgs():
    # prendo tutte le mail fallite e provo a reinviarle
    mails = Mail.objects.filter(sent=False)
    for mail in mails:
        mail.send()
    
def safe_json_dumps(data, **kwargs):
    """
    Serializza `data` in JSON, sostituendo gli oggetti non serializzabili
    con la stringa "__non-serializable-obj__".
    """
    def default_serializer(obj):
        try:
            # Proviamo prima a fare una conversione leggibile
            return str(obj)
        except Exception:
            return f"__non-serializable-obj__({obj.__class__.__name__})"

    # try:
    return json.dumps(data, default=default_serializer, **kwargs)
    # except Exception:
    #     # Se anche json.dumps dovesse fallire, ritorna una stringa di fallback
    #     return json.dumps(f"__non-serializable-obj__({data.__class__.__name__})")