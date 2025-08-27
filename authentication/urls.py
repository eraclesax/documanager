# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from .views import login_view, register_user, password_reset_sent
from django.contrib.auth.views import LogoutView, PasswordResetView, PasswordResetConfirmView

urlpatterns = [
    path('login/', login_view, name="login"),
    # path('register/', register_user, name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),    
    # invio link (simile a password reset)
    path('imposta-password/', 
         PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='mail/password_reset_email_tmpl.html',
             subject_template_name='mail/password_reset_subject.txt',
             success_url='/password_reset_sent/'
         ), 
         name='password_reset'),

    # link che l’utente clicca per settare la password
    path('imposta-password/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(
             template_name='password_reset_confirm.html',
             success_url='/login/'
         ), 
         name='password_reset_confirm'),
    path('password_reset_sent/', password_reset_sent, name="password_reset_sent"),
    # path('register/', register_user, name="register"),
]


