from django.urls import path
from .views import AnagraficaListView, AnagraficaView, AnagraficaEditView, \
    AnagraficaDeleteView, AnagraficaNewNFCView

urlpatterns = [
    path('', AnagraficaListView.as_view(), name='anagrafiche'),    
    path('<int:id>', AnagraficaView.as_view(), name='anagrafica'),
    path('<int:id>/edit', AnagraficaEditView.as_view(), name='anagrafica_edit'),
    path('new', AnagraficaEditView.as_view(), name='anagrafica_new'),
    path('new-NFC', AnagraficaNewNFCView.as_view(), name='anagrafica_new_nfc'),
    path("<int:pk>/delete/", AnagraficaDeleteView.as_view(), name="anagrafica_delete"),
]