from django.urls import path, reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView, \
    PasswordResetView, PasswordResetConfirmView
from django.views.generic.base import TemplateView
from .views import CustomLoginView, CustomPasswordResetView
from .forms import SignUpForm, CustomPasswordResetForm

# i tempalte_name sono quelli di default, quindi anche levandoli funziona comunque tutto
_logout_view = LogoutView.as_view(
    template_name='registration/logged_out.html',
)
_password_reset_sent_view = TemplateView.as_view(
    template_name='registration/password_reset_sent.html',
)
_password_reset_confirm_view = PasswordResetConfirmView.as_view(
    template_name='registration/password_reset_confirm.html',
    success_url=reverse_lazy("login")
)

urlpatterns = [
    # path('login/', login_view, name="login"),
    # path('register/', register_user, name="register"),

    path("accounts/login/", CustomLoginView.as_view(), name='login'),
    path("accounts/logout/", _logout_view, name="logout"),    
    # invio link (simile a password reset)
    path('accounts/imposta-password/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('accounts/password-reset-inviata/', _password_reset_sent_view, name="password_reset_done"),
    # link che l’utente clicca per settare la password
    path('accounts/imposta-password/<uidb64>/<token>/', _password_reset_confirm_view, name='password_reset_confirm'),
    
]


