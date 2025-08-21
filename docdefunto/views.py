from reportlab.pdfgen import canvas
from app.models import AppUser
from .models import *
from .forms import *

import datetime

from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, FileResponse
from django.template.context_processors import csrf
from django.views.generic import View, DeleteView
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.template import Template, Context

from crispy_forms.utils import render_crispy_form
from rest_framework.views import APIView



# class RedirectView(View):
#     def get(self, request, *args, **kwargs):
#         url_name = kwargs["url_name"]
#         url_kwargs = kwargs.get("url_kwargs",{})
#         return redirect(reverse(url_name,kwargs=url_kwargs))
    
class DefuntiListView(View):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    template_name = 'defunti.html'
    
    @method_decorator(login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        return self.GET_render(request,*args, **kwargs)
    
    def GET_render(self,request,*args, **kwargs):
        
        defunti = AnagraficaDefunto.objects.all().order_by('-id')
        return render(request, self.template_name, {
            "defunti":defunti,
        })

class DefuntoView(View):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    template_name = 'defunto.html'
    
    @method_decorator(login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        return self.GET_render(request,*args, **kwargs)
    
    def GET_render(self,request,*args, **kwargs):
        
        id = kwargs.get("id", None)
        defunto = get_object_or_404(AnagraficaDefunto,pk=id)
        return render(request, self.template_name, {
            "defunto":defunto,
        })
    
class DefuntoEditView(View):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    template_name = 'defunto_edit.html'
    
    @method_decorator(login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        return self.GET_render(request,*args, **kwargs)
    
    def GET_render(self,request,*args, **kwargs):
        from .forms import DefuntoEditForm
        from .models import AnagraficaDefunto
        #### Objects from post ####
        form = kwargs.get("form",None)
        has_error = kwargs.get("has_error",False)
        ###########################
    
        id = kwargs.get("id", None)
        if id is not None:
            obj = get_object_or_404(AnagraficaDefunto,pk=id)
        else:
            obj = None
        if not form:
            form = DefuntoEditForm(
                instance = obj,
            )
        return render(request, self.template_name, {
            "form":form,
            "has_error":has_error,
        })
    
    @method_decorator(login_required(login_url="/login/"))
    def post(self, request, *args, **kwargs):
        from .forms import DefuntoEditForm
        from django.contrib import messages
        from app.models import AppUser
        id = kwargs.get("id", None)
        if id is not None:
            obj = get_object_or_404(AnagraficaDefunto,pk=id)
        else:
            obj = None
        form = DefuntoEditForm(
            request.POST or None,
            request.FILES or None,
            instance = obj,
        )
        if form.is_valid():
            obj = form.save()
            messages.add_message(request, messages.SUCCESS, _('Anagrafica "%s" salvata con successo!'%(obj)))
            return HttpResponseRedirect(reverse('defunti'))
        else:
            kwargs["form"] = form
            kwargs["has_error"] = True
            return self.GET_render(request, *args, **kwargs)

class AnagraficaDefuntoDeleteView(DeleteView):
    model = AnagraficaDefunto
    template_name = "defunti/defunto_confirm_delete.html"  # non verrà usato con il modal
    success_url = reverse_lazy("defunti")

class DefuntoDocsView(View):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    template_name = 'defunto_docs.html'
    
    @method_decorator(login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        return self.GET_render(request,*args, **kwargs)
    
    def GET_render(self,request,*args, **kwargs):
        
        id = kwargs.get("id", None)
        defunto = get_object_or_404(AnagraficaDefunto,pk=id)
        documenti = Documento.objects.all()

        return render(request, self.template_name, {
            "defunto":defunto,
            "documenti":documenti,
        })

class GetDocView(View):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    template_name = 'defunto_docs.html'
    
    @method_decorator(login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        return self.GET_render(request,*args, **kwargs)
    
    def GET_render(self,request,*args, **kwargs):
        from .utils import generate_filled_pdf

        def_id = kwargs.get("def_id", None)
        doc_id = kwargs.get("doc_id", None)
        action = kwargs.get("action", "open")
        
        # prendo il template (Documento)
        doc = get_object_or_404(Documento, id=doc_id)
        # prendo i dati del defunto
        defunto = get_object_or_404(AnagraficaDefunto, id=def_id)


        fields = {
                "nome": {"text": "Mario Rossi", "x": 100, "y": 700},
                "data": {"text": "21/08/2025", "x": 400, "y": 700},
                "luogo": {"text": "Trieste", "x": 100, "y": 650},
            }

        pdf_bytes = generate_filled_pdf(doc.file, fields)

        if action == "save":
            # Ritorno il PDF come risposta
            response = FileResponse(pdf_bytes, as_attachment=True, filename="documento.pdf")
        else:
            # Ritorno il PDF aperto nel browser
            response = FileResponse(pdf_bytes, filename="documento.pdf")
            response['Content-Disposition'] = 'inline; filename="documento.pdf"'
            print("Sto salvando")

        return response
    
    # def GET_render(self,request,*args, **kwargs):
        
    #     def_id = kwargs.get("def_id", None)
    #     doc_id = kwargs.get("doc_id", None)

    #     # prendo il template (Documento)
    #     doc = get_object_or_404(Documento, id=doc_id)
    #     # prendo i dati del defunto
    #     defunto = get_object_or_404(AnagraficaDefunto, id=def_id)

    #     # leggo il contenuto del file template
    #     with doc.file.open("r") as f:
    #         template_string = f.read()

    #     # renderizzo il template con i dati del defunto
    #     template = Template(template_string)
    #     context = Context({
    #         "defunto": defunto,  # puoi accedere con {{ defunto.nome }} ecc.
    #     })
    #     contenuto = template.render(context)

    #     # preparo la risposta per il download
    #     filename = f"{defunto.cognome}_{defunto.nome} - {doc}.txt"
    #     response = HttpResponse(contenuto, content_type="text/plain")
    #     response["Content-Disposition"] = f'attachment; filename="{filename}"'
    #     return response
    



# def generate_pdf_file():
#     from io import BytesIO

#     buffer = BytesIO()
#     p = canvas.Canvas(buffer)

#     # Create a PDF document
#     books = AnagraficaDefunto.objects.all()
#     p.drawString(100, 750, "Book Catalog")

#     y = 700
#     for book in books:
#         p.drawString(100, y, f"Title: {book.title}")
#         p.drawString(100, y - 20, f"Author: {book.author}")
#         p.drawString(100, y - 40, f"Year: {book.publication_year}")
#         y -= 60

#     p.showPage()
#     p.save()

#     buffer.seek(0)
#     return buffer