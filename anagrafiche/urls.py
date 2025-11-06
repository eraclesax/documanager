from django.urls import path
from .views import AnagraficaListView, AnagraficaView, AnagraficaEditView, \
    AnagraficaDeleteView, AnagraficaOcrPicView

urlpatterns = [
    path('', AnagraficaListView.as_view(), name='anagrafiche'),    
    path('<int:id>', AnagraficaView.as_view(), name='anagrafica'),
    path('<int:id>/edit', AnagraficaEditView.as_view(), name='anagrafica_edit'),
    path('new', AnagraficaEditView.as_view(), name='anagrafica_new'),
    path("<int:pk>/delete/", AnagraficaDeleteView.as_view(), name="anagrafica_delete"),
    ## AJAX ##
    path('ajax/ocr_pic', AnagraficaOcrPicView.as_view(), name='ajax_ocr_pic'),
]