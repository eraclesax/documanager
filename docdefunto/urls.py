from django.urls import path
from .views import *
# from .views import ping

urlpatterns = [
    path('', DefuntiListView.as_view(), name='defunti'),
    path('<int:id>', DefuntoView.as_view(), name='defunto'),
    path('<int:id>/edit', DefuntoEditView.as_view(), name='defunto_edit'),
    path('new', DefuntoEditView.as_view(), name='defunto_new'),
    path("<int:pk>/delete/", AnagraficaDefuntoDeleteView.as_view(), name="defunto_delete"),
    path("<int:id>/docs/", DefuntoDocsView.as_view(), name="defunto_docs"),
    path("<int:def_id>/docs/<int:doc_id>/<str:action>", GetDocView.as_view(), name="get_doc"),
    # path("ping/", ping),
    # path("defunti/<int:def_id>/docs/<int:doc_id>/", EditDocConfig.as_view(), name="edit_doc_config"),
]