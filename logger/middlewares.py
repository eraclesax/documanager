from threading import local
from django.utils.deprecation import MiddlewareMixin

_user = local()
def get_current_user():
    try:
        return _user.value.id
    except:
        pass
# Fixes the bug of empty REMOTE_ADDR
class XForwardedForMiddleware():
    def process_request(self, request):
        if "HTTP_X_FORWARDED_FOR" in request.META:
            request.META["HTTP_X_PROXY_REMOTE_ADDR"] = request.META["REMOTE_ADDR"]
            parts = request.META["HTTP_X_FORWARDED_FOR"].split(",", 1)
            request.META["REMOTE_ADDR"] = parts[0]

class CurrentUserMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.process_request(request)
        if response is None:
            response = self.get_response(request)

        return response
        
    def process_request(self, request):
        _user.value = request.user 
        from logger.utils import add_log
        from ipware.ip import get_client_ip
        try:
            ip = get_client_ip(request)
        except:
            ip = 'none'
        # add_log(level=1, request=request, custom_message=ip )

class ErrorMiddleware(MiddlewareMixin):

    def process_exception(self, request, exception):
        from logger.utils import add_log
        from ipware.ip import get_client_ip
        import traceback
        try:
            ip = get_client_ip(request)
        except:
            ip = 'none'
        add_log(level=5, message=1, request=request,exception=traceback.format_exc(), custom_message=ip  )
        return None