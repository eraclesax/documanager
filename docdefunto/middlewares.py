from django.utils.deprecation import MiddlewareMixin
from .models import Organization
from django.conf import settings

class OrganizationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if settings.DEBUG_DOMAIN:
            host = settings.DEBUG_DOMAIN
        else:
            host = request.get_host().lower().split(":")[0]  # togli eventuale porta
        try:
            org = Organization.objects.get(domain=host)
            request.organization = org
        except Organization.DoesNotExist:
                request.organization = None
