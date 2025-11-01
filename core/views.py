    
from django.http import HttpResponseRedirect
from django.urls import reverse

def index(request):
    
    context = {}
    context['segment'] = 'index'

    return HttpResponseRedirect(reverse('defunti'))