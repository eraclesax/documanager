from django.utils.deprecation import MiddlewareMixin
from .models import Organization
from django.conf import settings
from logger.utils import add_log

class OrganizationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            import re
            if settings.DEBUG_DOMAIN:
                host = settings.DEBUG_DOMAIN
            else:
                host = request.get_host().lower().split(":")[0]  # togli eventuale porta
                host = re.sub(r"^www\d*\.", "", host)  # togli eventuale www, www2, ecc.
            try:
                org = Organization.objects.get(domain=host)
                request.organization = org
            except Organization.DoesNotExist as e:
                    request.organization = None
                    msg = f"Exception in OrganizationMiddleware.process_request: organization with domain {host} does not exists."
                    add_log(level=3,exception=e, custom_message=msg)

        except Exception as e:
            add_log(level=4,exception=e,custom_message="Exception in OrganizationMiddleware.process_request")
            raise(e)
