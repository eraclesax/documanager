from __future__ import print_function
from __future__ import absolute_import
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View
from .models import Mail

class RenderMailView(View):

    template_name = ''
 
    def get(self, request, *args, **kwargs):
        import json
        mail = Mail.objects.get(uuid=kwargs.get('uuid'))
        self.template_name = 'mail/' + mail.template_name + '.html'
        
        # return render(request, self.template_name, mail.template_context)
        return HttpResponse(mail.html_text)
    
class SentMailListView(View):

    template_name = 'pages/sent_mail_list.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser is True:
            from .models import Mail

            mails=Mail.objects.all()

            return render(request, self.template_name, {'mails': mails })

        else:
            # Unauthorized
            return render(request, 'errors/401.html', {'page_content': ''}, status=401)

class SentMailView(View):

    template_name = 'pages/sent_mail.html'

    def get(self, request, *args, **kwargs):
        mail_id = kwargs.get("id", None)

        # If user in role Filters Viewer
        # 31: Dashboard email notification

        if request.user.is_superuser is True:
            from .models import Mail

            if mail_id:
                mail=Mail.objects.get(pk=mail_id)
            else:
                mail=None

            return render(request, self.template_name, {'mail': mail })

        else:
            # Unauthorized
            return render(request, 'errors/401.html', {'page_content': ''}, status=401)