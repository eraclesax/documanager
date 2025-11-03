import traceback
from django.conf import settings
from django.shortcuts import render,get_object_or_404
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import View, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from logger.utils import add_log
from .models import Anagrafica

class AnagraficaListView(View):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    template_name = 'anagrafiche.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return self.GET_render(request,*args, **kwargs)

    def GET_render(self,request,*args, **kwargs):
        try:
            add_log(level=2,user=request.user, custom_message="Entering view AnagraficaListView.GET_render",request=request)
            items = Anagrafica.objects.filter(organization=request.user.profile.organization).order_by('-relative_id')
            return render(request, self.template_name, {
                "items":items,
            })
        except Exception as e:
            msg = "Exception in AnagraficaListView.GET_render"
            add_log(level=4,user=request.user, custom_message=msg,request=request,exception=traceback.format_exc())
            raise(e)

class AnagraficaView(View):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    template_name = 'anagrafica.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return self.GET_render(request,*args, **kwargs)

    def GET_render(self,request,*args, **kwargs):
        try:
            add_log(level=2,user=request.user, custom_message="Entering view DefuntoView.GET_render",request=request)
            id = kwargs.get("id", None)
            defunto = get_object_or_404(Anagrafica,pk=id)
            # Determina le categorie per ciascun campo
            defunto_fields = {}
            for category,field_names in defunto.FIELD_CATEGORIES.items():
                defunto_fields[category] = []
                for field_name in field_names:
                    field = Anagrafica._meta.get_field(field_name)
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
        except Exception as e:
            msg = "Exception in AnagraficaView.GET_render"
            add_log(level=4,user=request.user, custom_message=msg,request=request,exception=traceback.format_exc())
            raise(e)

class AnagraficaEditView(View):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    template_name = 'anagrafica_edit.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return self.GET_render(request,*args, **kwargs)

    def GET_render(self,request,*args, **kwargs):
        try:
            from .forms import AnagraficaEditForm
            from .models import Anagrafica
            add_log(level=2,user=request.user, custom_message="Entering view AnagraficaEditView.GET_render",request=request)
            #### Objects from post ####
            form = kwargs.get("form",None)
            has_error = kwargs.get("has_error",False)
            ###########################

            id = kwargs.get("id", None)
            if id is not None:
                obj = get_object_or_404(Anagrafica,pk=id)
            else:
                obj = None
            if not form:
                form = AnagraficaEditForm(
                    instance = obj,
                )
            return render(request, self.template_name, {
                "form":form,
                "has_error":has_error,
            })
        except Exception as e:
            msg = "Exception in AnagraficaEditView.GET_render"
            add_log(level=4,user=request.user, custom_message=msg,request=request,exception=traceback.format_exc())
            raise(e)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        try:
            from .forms import AnagraficaEditForm
            from django.contrib import messages
            add_log(level=2,user=request.user, custom_message="Entering view DefuntoEditView.post",request=request)
            id = kwargs.get("id", None)
            user = request.user
            if id is not None:
                obj = get_object_or_404(Anagrafica,pk=id)
            else:
                obj = None
            form = AnagraficaEditForm(
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
                    'Anagrafica "%s" salvata con successo!'%(obj))
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
                        '%s: %s' % (label, errors[0])
                    )

                for error in form.non_field_errors():
                    messages.add_message(
                        request,
                        messages.ERROR,
                        '%s' % (error)
                    )
                return self.GET_render(request, *args, **kwargs)
        except Exception as e:
            msg = "Exception in DefuntoEditView.post"
            add_log(level=4,user=request.user, custom_message=msg,request=request,exception=traceback.format_exc())
            raise(e)

class AnagraficaNewNFCView(View):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    template_name = 'anagrafica_edit_test.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return self.GET_render(request,*args, **kwargs)

    def GET_render(self,request,*args, **kwargs):
        try:
            # from .forms import AnagraficaEditForm
            from .models import Anagrafica
            add_log(level=2,user=request.user, custom_message="Entering view AnagraficaEditView.GET_render",request=request)


            ## Qui inizializzo l'oggetto con le cose lette da NFC
            
            data = Anagrafica.read_from_NFC(save=True)

            ## Creo il form -> in futuro è meglio se rimando alla View del normale edit
            # form = AnagraficaEditForm(
            #     instance = obj,
            # )

            return render(request, self.template_name, {
                # "form":form,
                "data":data,
            })
        except Exception as e:
            msg = "Exception in AnagraficaNewNFCView.GET_render"
            add_log(level=4,user=request.user, custom_message=msg,request=request,exception=traceback.format_exc())
            raise(e)

    # @method_decorator(login_required)
    # def post(self, request, *args, **kwargs):
    #     try:
    #         from .forms import AnagraficaEditForm
    #         from django.contrib import messages
    #         add_log(level=2,user=request.user, custom_message="Entering view DefuntoEditView.post",request=request)
    #         id = kwargs.get("id", None)
    #         user = request.user
    #         if id is not None:
    #             obj = get_object_or_404(Anagrafica,pk=id)
    #         else:
    #             obj = None
    #         form = AnagraficaEditForm(
    #             request.POST or None,
    #             request.FILES or None,
    #             instance = obj,
    #         )
    #         if form.is_valid():
    #             obj = form.save(commit=False)
    #             obj.created_by = user
    #             obj.organization = user.profile.organization
    #             obj.save()
    #             messages.add_message(
    #                 request, 
    #                 messages.SUCCESS, 
    #                 'Anagrafica "%s" salvata con successo!'%(obj))
    #             return HttpResponseRedirect(reverse('defunti'))
    #         else:
    #             kwargs["form"] = form
    #             kwargs["has_error"] = True
    #             for field, errors in form.errors.items():
    #                 # Recupera la label leggibile (o il nome campo se non c'è)
    #                 label = form.fields[field].label if field in form.fields else field
    #                 messages.add_message(
    #                     request,
    #                     messages.ERROR,
    #                     '%s: %s' % (label, errors[0])
    #                 )

    #             for error in form.non_field_errors():
    #                 messages.add_message(
    #                     request,
    #                     messages.ERROR,
    #                     '%s' % (error)
    #                 )
    #             return self.GET_render(request, *args, **kwargs)
    #     except Exception as e:
    #         msg = "Exception in DefuntoEditView.post"
    #         add_log(level=4,user=request.user, custom_message=msg,request=request,exception=traceback.format_exc())
    #         raise(e)
        
class AnagraficaDeleteView(DeleteView):
    model = Anagrafica
    template_name = "anagrafica/anagrafica_confirm_delete.html"  # non verrà usato con il modal
    success_url = reverse_lazy("anagrafiche")