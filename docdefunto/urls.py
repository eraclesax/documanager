# test/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('defunti', DefuntiListView.as_view(), name='lista'),
    path('defunti/<int:id>', DefuntoView.as_view(), name='defunto'),
    # path('generate-pdf/', views.generate_pdf, name='generate_pdf'),
]