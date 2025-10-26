from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView
from django.views.generic.base import TemplateView
# from django.contrib.auth.models import User
# from django.forms.utils import ErrorList
# from django.http import HttpResponse
from .forms import CustomAuthenticationForm, SignUpForm

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

