# test/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('lista', views.lista, name='lista'),
    path('generate-pdf/', views.generate_pdf, name='generate_pdf'),
]