# test/urls.py
from django.urls import path
from .views import *
from .views import AnagraficaDefuntoDeleteView
from django.urls import path
from .views import ping

urlpatterns = [
    path("ping/", ping),
]

# urlpatterns = [
#     path('defunti', DefuntiListView.as_view(), name='defunti'),
#     path('defunti/<int:id>', DefuntoView.as_view(), name='defunto'),
#     path('defunti/<int:id>/edit', DefuntoEditView.as_view(), name='defunto_edit'),
#     path('defunti/new', DefuntoEditView.as_view(), name='defunto_new'),
#     path("defunti/<int:pk>/delete/", AnagraficaDefuntoDeleteView.as_view(), name="defunto_delete"),
#     path("defunti/<int:id>/docs/", DefuntoDocsView.as_view(), name="defunto_docs"),
#     path("defunti/<int:def_id>/docs/<int:doc_id>/<str:action>", GetDocView.as_view(), name="get_doc"),
#     # path("defunti/<int:def_id>/docs/<int:doc_id>/", EditDocConfig.as_view(), name="edit_doc_config"),
# ]