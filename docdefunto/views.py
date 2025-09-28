import io

from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.template.context_processors import csrf
from django.views.generic import View, DeleteView
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.template import Template, Context
from django.conf import settings
from django.http import HttpResponse
from .models import *
from .forms import *
# from reportlab.pdfgen import canvas


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
        defunti = AnagraficaDefunto.objects.filter(organization=request.user.profile.organization).order_by('-relative_id')
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
        # Determina le categorie per ciascun campo
        defunto_fields = {}
        for category,field_names in defunto.FIELD_CATEGORIES.items():
            defunto_fields[category] = []
            for field_name in field_names:
                field = AnagraficaDefunto._meta.get_field(field_name)
                verbose_name = field.verbose_name
                value = getattr(defunto, field_name)
                if type(value) == bool:
                    value = "Sì" if value else "No"
                defunto_fields[category].append({
                    "verbose_name":verbose_name,
                    "value": value,
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
        id = kwargs.get("id", None)
        user = request.user
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
            obj = form.save(commit=False)
            obj.created_by = user
            obj.organization = user.profile.organization
            obj.save()
            messages.add_message(
                request, 
                messages.SUCCESS, 
                _('Anagrafica "%s" salvata con successo!'%(obj)))
            return HttpResponseRedirect(reverse('defunti'))
        else:
            kwargs["form"] = form
            kwargs["has_error"] = True
            for field, errors in form.errors.items():
                # Recupera la label leggibile (o il nome campo se non c'è)
                label = form.fields[field].label if field in form.fields else field
                messages.add_message(
                    request,
                    messages.ERROR,
                    _('%s: %s' % (label, errors[0]))
                )

            for error in form.non_field_errors():
                messages.add_message(
                    request,
                    messages.ERROR,
                    '%s' % (error)
                )
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
        documenti = Documento.objects.all().order_by('order_number')

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
        from weasyprint import HTML
        from PyPDF2 import PdfReader, PdfWriter
        def_id = kwargs.get("def_id", None)
        doc_id = kwargs.get("doc_id", None)
        action = kwargs.get("action", "open")
        user = request.user
        doc = get_object_or_404(Documento, id=doc_id)
        defunto = get_object_or_404(AnagraficaDefunto, id=def_id)

        # leggo il contenuto del file template
        with doc.file.open("r") as f:
            template_string = f.read()

        # renderizzo il template con i dati
        template = Template(template_string)
        context = Context({
            "user": user,
            "defunto": defunto,
            "doc_name": doc.nome,
        })
        contenuto_html = template.render(context)
        #TODO: Check se è inumazione altro comune che ci sia il comune
        if settings.BUILDING_DOCUMENTS_LAYOUT:
            filename = f"{doc.nome} - {defunto.cognome} {defunto.nome}.html"
            response = HttpResponse(contenuto_html)
            return response
        else:

            # 1. Genera PDF del contenuto in memoria
            # converto in PDF con WeasyPrint
            contenuto_pdf_bytes = HTML(
                string=contenuto_html, 
                base_url=request.build_absolute_uri('/')
                ).write_pdf()

            if doc.background and contenuto_pdf_bytes:
                contenuto_pdf = PdfReader(io.BytesIO(contenuto_pdf_bytes))
                # 2. Carica il foglio intestato (da FileField di Django)
                bg_file = doc.background.open("rb")  # assicura apertura
                bg_pdf = PdfReader(bg_file)
                pdf_writer = PdfWriter()
                # 3. Sovrapponi contenuto alle pagine del foglio intestato
                output_buffer = io.BytesIO()
                for page in contenuto_pdf.pages:
                    bg_page = bg_pdf.pages[0]  # usa la prima pagina come sfondo
                    page.merge_page(bg_page)           # unisce il contenuto sopra lo sfondo
                    pdf_writer.add_page(page)
                # 4. Salva in memoria il PDF finale
                pdf_writer.add_metadata({
                    '/Author': str(user.profile.organization),
                    '/Title': str(doc.nome)
                })
                pdf_writer.write(output_buffer)
                output_buffer.seek(0)

                # for page in contenuto_pdf.pages:
                #     background_page = foglio_pdf.pages[0]  # usa la prima pagina come sfondo
                #     page.merge_page(background_page)           # unisce il contenuto sopra lo sfondo
                #     writer.add_page(page)
                #     # 4. Salva in memoria il PDF finale
                #     output_buffer = io.BytesIO()
                #     writer.write(output_buffer)
                #     output_buffer.seek(0)
                response = HttpResponse(output_buffer, content_type="application/pdf")
            else:
                response = HttpResponse(contenuto_pdf_bytes, content_type="application/pdf")

            # preparo la risposta
            filename = f"{doc.nome} - {defunto.cognome} {defunto.nome}.pdf"
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


