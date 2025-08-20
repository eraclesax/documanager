# test/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('lista', DefuntiListView.as_view(), name='lista'),
    path('defunto/<int:id>', DefuntoView.as_view(), name='defunto'),
    # path('generate-pdf/', views.generate_pdf, name='generate_pdf'),
]