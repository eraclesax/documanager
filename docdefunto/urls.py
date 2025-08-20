# test/urls.py
from django.urls import path
from .views import *
from .views import AnagraficaDefuntoDeleteView

urlpatterns = [
    path('defunti', DefuntiListView.as_view(), name='defunti'),
    path('defunti/<int:id>', DefuntoView.as_view(), name='defunto'),
    path('defunti/<int:id>/edit', DefuntoEditView.as_view(), name='defunto_edit'),
    path('defunti/new', DefuntoEditView.as_view(), name='defunto_new'),
    path("defunti/<int:pk>/delete/", AnagraficaDefuntoDeleteView.as_view(), name="defunto_delete"),

    # path('generate-pdf/', views.generate_pdf, name='generate_pdf'),
]