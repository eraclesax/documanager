from django.contrib.auth.models import User

def create_user(username,email):
    # crea l'utente senza password
    utente = User.objects.create_user(
        username=username,
        email=email,
        password=None,
        is_active=True
    )
    return utente