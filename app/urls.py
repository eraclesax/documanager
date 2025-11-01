from django.urls import path, reverse_lazy
from django.contrib.auth.views import LogoutView, PasswordResetConfirmView
from django.views.generic.base import TemplateView
from .views import CustomLoginView, CustomPasswordResetView, PasswordChangedView

# i tempalte_name sono quelli di default, quindi anche levandoli funziona comunque tutto
_logout_view = LogoutView.as_view(
    template_name='registration/logged_out.html',
)
_password_sent_view = TemplateView.as_view(
    template_name='registration/password_sent.html',
)
_password_reset_view = PasswordResetConfirmView.as_view(
    template_name='registration/password_reset.html',
    success_url=reverse_lazy("password_changed")
)

urlpatterns = [
    # path('login/', login_view, name="login"),
    # path('register/', register_user, name="register"),

    path("login/", CustomLoginView.as_view(), name='login'),
    path("logout/", _logout_view, name="logout"),    
    # invio link (simile a password reset)
    path('password/richiedi/', CustomPasswordResetView.as_view(), name='password_request'),
    path('password/inviata/', _password_sent_view, name="password_sent"),
    path('password/reset/<uidb64>/<token>/', _password_reset_view, name='password_reset'),
    path("password/cambiata/", PasswordChangedView.as_view(), name="password_changed"),    
]


# if settings.DEBUG:
#     urlpatterns.extend([
#         # Matches any html file
#         # re_path(r'^.*\.*', views.pages, name='pages'),
#         # re_path('', views.pages, name='pages'),
#     ])