import traceback

from django.shortcuts import render
from django.conf import settings
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from logger.utils import add_log
# from .models import Picture

class PictureView(View):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    template_name = 'picture_cut.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return self.GET_render(request,*args, **kwargs)

    def GET_render(self,request,*args, **kwargs):
        try:
            # from .forms import PictureForm
            add_log(level=2,user=request.user, custom_message="Entering view PictureView.GET_render",request=request)
            #### Objects from post ####
            # form = kwargs.get("form",None)
            # has_error = kwargs.get("has_error",False)
            ###########################

            # id = kwargs.get("id", None)
            # if id is not None:
            #     obj = get_object_or_404(AnagraficaDefunto,pk=id)
            # else:
            #     obj = None
            # if not form:
            #     form = PictureView(
            #         instance = obj,
            #     )
            return render(request, self.template_name, {})
        except Exception as e:
            msg = "Exception in PictureView.GET_render"
            add_log(level=4,user=request.user, custom_message=msg,request=request,exception=traceback.format_exc())
            raise(e)

    # @method_decorator(login_required)
    # def post(self, request, *args, **kwargs):
    #     try:
    #         from .forms import DefuntoEditForm
    #         from django.contrib import messages
    #         add_log(level=2,user=request.user, custom_message="Entering view DefuntoEditView.post",request=request)
    #         id = kwargs.get("id", None)
    #         user = request.user
    #         if id is not None:
    #             obj = get_object_or_404(AnagraficaDefunto,pk=id)
    #         else:
    #             obj = None
    #         form = DefuntoEditForm(
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
