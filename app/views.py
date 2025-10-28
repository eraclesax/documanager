from django.http import HttpResponseRedirect
from django.urls import reverse

def index(request):
    
    context = {}
    context['segment'] = 'index'

    return HttpResponseRedirect(reverse('defunti'))



# @login_required
# def debug_pages(request):
#     """Get the original templates of the UI only for DEBUG purpose
#     """
#     context = {}
#     # All resource paths end in .html.
#     # Pick out the html file name from the url. And load that template.
#     try:
        
#         load_template      = "original_templates/templates/"+request.path.split('/')[-1]
#         context['segment'] = load_template
#         html_template = loader.get_template( load_template )
#         return HttpResponse(html_template.render(context, request))
        
#     except template.TemplateDoesNotExist:
#         if settings.DEBUG:
#             import traceback
#             traceback.print_exc()
#         html_template = loader.get_template( 'original_templates/templates/page-404.html' )
#         return HttpResponse(html_template.render(context, request))

#     except:
#         if settings.DEBUG:
#             import traceback
#             traceback.print_exc()
#         html_template = loader.get_template( 'original_templates/templates/page-500.html' )
#         return HttpResponse(html_template.render(context, request))


