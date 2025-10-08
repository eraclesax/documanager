from django.urls import path
from .views import *

# region KpiType Admin Pages
urlpatterns=[
    # Mail urls
    path('render/<str:uuid>/', RenderMailView.as_view(), name='render_mail'),
    # Pages urls (attualmente bloccati ma funzionanti)
    # path('sent_mail_list/', SentMailListView.as_view(), name='sent_mail_list'),
    # path('sent_mail/<int:id>', SentMailView.as_view(), name='sent_mail'),
]