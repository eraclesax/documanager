# from reportlab.pdfgen import canvas
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
from django.conf import settings

from crispy_forms.utils import render_crispy_form
from rest_framework.views import APIView
from weasyprint import HTML

from django.http import HttpResponse

# def ping(request):
#     return HttpResponse("pong from Django via Gunicorn")

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
        defunto_fields = {}
        for category,field_names in defunto.FIELD_CATEGORIES.items():
            defunto_fields[category] = []
            for field_name in field_names:
                field = AnagraficaDefunto._meta.get_field(field_name)
                defunto_fields[category].append({
                    "name":field_name,
                    "verbose_name":field.verbose_name,
                    "value": getattr(defunto, field_name),
                    })
        return render(request, self.template_name, {
            "defunto":defunto,
            "defunto_fields":defunto_fields,
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
    template_name = 'defunto_docs.html'

    @method_decorator(login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        return self.GET_render(request, *args, **kwargs)

    def GET_render(self, request, *args, **kwargs):
        def_id = kwargs.get("def_id", None)
        doc_id = kwargs.get("doc_id", None)
        action = kwargs.get("action", "open")

        doc = get_object_or_404(Documento, id=doc_id)
        defunto = get_object_or_404(AnagraficaDefunto, id=def_id)

        # leggo il contenuto del file template
        with doc.file.open("r") as f:
            template_string = f.read()

        # renderizzo il template con i dati
        template = Template(template_string)
        context = Context({
            "defunto": defunto,
        })
        contenuto_html = template.render(context)

        if settings.BUILDING_DOCUMENTS_LAYOUT:
            filename = f"{doc.nome} - {defunto.cognome} {defunto.nome}.html"
            response = HttpResponse(contenuto_html)
            return response
        else:
            # converto in PDF con WeasyPrint
            pdf_file = HTML(string=contenuto_html, base_url=request.build_absolute_uri('/')).write_pdf()

            # preparo la risposta
            filename = f"{doc.nome} - {defunto.cognome} {defunto.nome}.pdf"
            response = HttpResponse(pdf_file, content_type="application/pdf")

            if action == "save":
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
            else:
                response['Content-Disposition'] = f'inline; filename="{filename}"'

        return response

    # def GET_render(self,request,*args, **kwargs):
    #     from .utils import generate_filled_pdf

    #     def_id = kwargs.get("def_id", None)
    #     doc_id = kwargs.get("doc_id", None)
    #     action = kwargs.get("action", "open")

    #     # prendo il template (Documento)
    #     doc = get_object_or_404(Documento, id=doc_id)
    #     # prendo i dati del defunto
    #     defunto = get_object_or_404(AnagraficaDefunto, id=def_id)


    #     empty_fields = doc.fields
    #     filled_fields = defunto.fill_fields(empty_fields)
    #     pdf_bytes = generate_filled_pdf(doc.file, filled_fields)
    #     filename = f"{defunto.cognome}_{defunto.nome} - {doc}"

    #     if action == "save":
    #         # Ritorno il PDF come risposta
    #         response = FileResponse(pdf_bytes, as_attachment=True, filename=filename)
    #     else:
    #         # Ritorno il PDF aperto nel browser
    #         response = FileResponse(pdf_bytes, filename=filename)
    #         response['Content-Disposition'] = f'inline; filename="{filename}"'

    #     return response

# class EditDocConfig(View):
#     """[summary]

#     Args:
#         APIView ([type]): [description]
#     """
#     template_name = 'defunto_docs.html'

#     @method_decorator(login_required(login_url="/login/"))
#     def get(self, request, *args, **kwargs):
#         return self.GET_render(request,*args, **kwargs)

#     def GET_render(self,request,*args, **kwargs):
#         def_id = kwargs.get("def_id", None)
#         doc_id = kwargs.get("doc_id", None)
#         documento = get_object_or_404(Documento, pk=doc_id)
#         defunto = get_object_or_404(AnagraficaDefunto, pk=def_id)

#         json_data = documento.fields or {}
#         form = DynamicJsonConfigForm(json_data=json_data)

#         return render(request, "edit_doc_config.html", {"form": form, "documento": documento})

#     @method_decorator(login_required(login_url="/login/"))
#     def post(self, request, *args, **kwargs):
#         def_id = kwargs.get("def_id", None)
#         doc_id = kwargs.get("doc_id", None)
#         documento = get_object_or_404(Documento, pk=doc_id)
#         defunto = get_object_or_404(AnagraficaDefunto, pk=def_id)
#         json_data = documento.fields or {}

#         form = DynamicJsonConfigForm(request.POST, json_data=json_data)
#         if form.is_valid():
#             documento.fields = form.to_json()
#             documento.save()

#             documenti = Documento.objects.all()
#             return render(request, "defunto_docs.html", {
#                 "defunto":defunto,
#                 "documenti":documenti,
#             })
#         else:
#             # Provvisorio
#             return render(request, "edit_doc_config.html", {"form": form, "documento": documento})


