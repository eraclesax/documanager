    
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings

def index(request):
    
    context = {}
    context['segment'] = 'index'
    INDEX_PAGE = settings.INDEX_PAGE
    return HttpResponseRedirect(reverse(INDEX_PAGE))