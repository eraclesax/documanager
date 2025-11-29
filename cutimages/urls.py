from .views import PictureView
from django.urls import path

urlpatterns = [
    path('', PictureView.as_view(), name='foto'),
]