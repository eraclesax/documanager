from django.conf import settings
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth.views import LoginView, PasswordResetView
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
# from django.contrib.auth.models import User
# from django.forms.utils import ErrorList
# from django.http import HttpResponse
from logger.utils import add_log
from .forms import CustomAuthenticationForm, CustomPasswordResetForm

class CustomLoginView(LoginView):
    form_class=CustomAuthenticationForm
    template_name="registration/login.html"
    extra_context = {"DEFAULT_REPLY_TO_EMAIL":settings.DEFAULT_REPLY_TO_EMAIL}

    def form_valid(self, form):
        ## Questo metodo è pensato a posta per aggiungere codice dopo la validazione del form

        # Qui chiama il comportamento di login standard
        response = super().form_valid(form)

        # Qui il form è valido e l'utente è autenticato
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # Sessione scade quando il browser viene chiuso
            self.request.session.set_expiry(0)
            self.request.session.modified = True
        else:
            # Sessione "persistente"
            self.request.session.set_expiry(settings.SESSION_COOKIE_AGE)
            self.request.session.modified = True

        return response

class CustomPasswordResetView(PasswordResetView):

    form_class = CustomPasswordResetForm

    template_name='registration/password_reset_form.html'

    email_template_name='mail/password_reset_email.txt'
    subject_template_name='mail/password_reset_subject.txt'
    html_email_template_name= 'mail/password_reset_email.html'
    # extra_email_context ={}
    success_url=reverse_lazy("password_reset_done")

    # Sovrascrivo la funzione per poter chiamare l'errore di invio email e riportarlo
    # all'utente
    def form_valid(self, form):
        """Valida il form (non c'è nulla da validare) e invia l'email tramite form.save()
        che chiama send_mail della classe ereditaria CustomPasswordResetForm
        """
        msg = "Richiesto reset password"
        add_log(level=2, custom_message=msg)
        print(msg)

        # opzioni usate da PasswordResetView
        opts = {
            "use_https": self.request.is_secure(),
            "token_generator": self.token_generator,
            "from_email": self.from_email,
            "email_template_name": self.email_template_name,
            "subject_template_name": self.subject_template_name,
            "request": self.request,
            "html_email_template_name": self.html_email_template_name,
            "extra_email_context": self.extra_email_context,
        }

        # chiamiamo form.save e controlliamo il risultato / eventuali errori aggiunti
        form.save(**opts)

        # se il form ha errori (es. self.add_error chiamato nella form), mostriamo il form con gli errori
        if form.errors:
            return self.form_invalid(form)

        # NON chiamo super().form_valid(form) di PasswordResetView perché la sua implementazione
        # chiamerebbe di nuovo form.save(); uso FormView.form_valid per ricevere il redirect.
        return FormView.form_valid(self, form)

class CustomPasswordSetView(PasswordResetView):

    form_class = CustomPasswordResetForm

    template_name='registration/password_reset_form.html'

    email_template_name='mail/password_reset_email.txt'
    subject_template_name='mail/password_reset_subject.txt'
    html_email_template_name= 'mail/password_reset_email.html'
    # extra_email_context ={}
    success_url=reverse_lazy("password_reset_done")

    # Sovrascrivo la funzione per poter chiamare l'errore di invio email e riportarlo
    # all'utente
    def form_valid(self, form):
        """Valida il form (non c'è nulla da validare) e invia l'email tramite form.save()
        che chiama send_mail della classe ereditaria CustomPasswordResetForm
        """
        msg = f"Richiesta impostazione della password"
        add_log(level=2, custom_message=msg)
        print(msg)

        # opzioni usate da PasswordResetView
        opts = {
            "use_https": self.request.is_secure(),
            "token_generator": self.token_generator,
            "from_email": self.from_email,
            "email_template_name": self.email_template_name,
            "subject_template_name": self.subject_template_name,
            "request": self.request,
            "html_email_template_name": self.html_email_template_name,
            "extra_email_context": self.extra_email_context,
        }

        # chiamiamo form.save e controlliamo il risultato / eventuali errori aggiunti
        form.save(**opts)

        # se il form ha errori (es. self.add_error chiamato nella form), mostriamo il form con gli errori
        if form.errors:
            return self.form_invalid(form)

        # NON chiamo super().form_valid(form) di PasswordResetView perché la sua implementazione
        # chiamerebbe di nuovo form.save(); uso FormView.form_valid per ricevere il redirect.
        return FormView.form_valid(self, form)

# def login_view(request):
#     form = CustomAuthenticationForm(request.POST or None)

#     msg = None

#     if request.method == "POST":

#         if form.is_valid():
#             username = form.cleaned_data.get("username")
#             password = form.cleaned_data.get("password")
#             user = authenticate(username=username, password=password)
#             next = request.GET.get("next", None)
#             if user is not None:
#                 login(request, user)
#                 if next:
#                     return redirect(next)
#                 else:
#                     return redirect("/")
#             else:    
#                 msg = 'Invalid credentials'    
#         else:
#             msg = 'Error validating the form'    

#     return render(request, "accounts/login.html", {"form": form, "msg" : msg})

# def password_reset_sent(request):

#     return render(request, "accounts/password_reset_sent.html")

def register_user(request):

    msg     = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg     = 'User created - please <a href="/login">login</a>.'
            success = True
            
            #return redirect("/login/")

        else:
            msg = 'Form is not valid'    
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg" : msg, "success" : success })

