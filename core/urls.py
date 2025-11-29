"""
URL configuration for documanager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include  # add this
from django.conf import settings
from django.conf.urls.static import static
from .views import index

admin.autodiscover()
admin.site.enable_nav_sidebar = False

urlpatterns = [
    path('admin/', admin.site.urls),          # Django admin route
    path('', index, name='index'),
    path('accounts/', include("app.urls")),             # Auth routes - login / register
    path('defunti/', include('docdefunto.urls')),
    path('mail/', include("mail.urls")),
]
if settings.FOTO_ACTIVE:
    urlpatterns.append(
        path('foto/', include('cutimages.urls'))
        )

if settings.ANAGRAFICHE_ACTIVE:
    urlpatterns.append(
        path('anagrafiche/', include('anagrafiche.urls'))
        )

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# # Serving the media files in development mode
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# else:
#     urlpatterns += staticfiles_urlpatterns()

