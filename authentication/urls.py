from django.urls import path
from .views import password_reset_sent
from django.contrib.auth import views as auth_views

urlpatterns = [
    # path('login/', login_view, name="login"),
    path("accounts/login/", 
        auth_views.LoginView.as_view(
            template_name="registration/login.html"
        ),
        name='login'),
    # path('register/', register_user, name="register"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),    
    # invio link (simile a password reset)
    path('accounts/imposta-password/', 
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset.html',
             email_template_name='mail/password_reset_email_tmpl.html',
             subject_template_name='mail/password_reset_subject.txt',
             success_url='accounts/password_reset_sent/'
         ), 
         name='password_reset'),

    # link che l’utente clicca per settare la password
    path('accounts/imposta-password/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url='accounts/login/'
         ), 
         name='password_reset_confirm'),
    path('accounts/password_reset_sent/', password_reset_sent, name="password_reset_sent"),
    # path('register/', register_user, name="register"),
]


