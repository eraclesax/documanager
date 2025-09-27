from django.utils.deprecation import MiddlewareMixin
from .models import Organization

class OrganizationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        host = request.get_host().lower().split(":")[0]  # togli eventuale porta
        try:
            org = Organization.objects.get(domain=host)
            request.organization = org
        except Organization.DoesNotExist:
            request.organization = None
