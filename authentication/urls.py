from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView, \
    PasswordResetView, PasswordResetConfirmView
from .views import password_reset_sent, CustomLoginView
from .forms import LoginForm, SignUpForm

# i tempalte_name sono quelli di default, quindi anche levandoli funziona comunque tutto
_logout_view = LogoutView.as_view(
    template_name='registration/logged_out.html',
    )
_password_reset_view = PasswordResetView.as_view(
    template_name='registration/password_reset.html',
    email_template_name='mail/password_reset_email_tmpl.html',
    subject_template_name='mail/password_reset_subject.txt',
    success_url='accounts/password_reset_sent/'
    )
_password_reset_confirm_view = PasswordResetConfirmView.as_view(
    template_name='registration/password_reset_confirm.html',
    success_url='accounts/login/'
    )

urlpatterns = [
    # path('login/', login_view, name="login"),
    # path('register/', register_user, name="register"),

    path("accounts/login/", CustomLoginView.as_view(), name='login'),
    path("accounts/logout/", _logout_view, name="logout"),    
    # invio link (simile a password reset)
    path('accounts/imposta-password/', _password_reset_view, name='password_reset'),
    # link che l’utente clicca per settare la password
    path('accounts/imposta-password/<uidb64>/<token>/', _password_reset_confirm_view, name='password_reset_confirm'),
    path('accounts/password_reset_sent/', password_reset_sent, name="password_reset_sent"),
]


