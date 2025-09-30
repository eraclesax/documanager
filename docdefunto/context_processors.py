def organization_context(request):
    try:
        return {"organization": getattr(request, "organization", None)}
    except Exception as e:
        from logger.utils import add_log
        msg = "Exception in documanager.context_processors.organization_context"
        add_log(level=4,exception=e,custom_message=msg)
        raise(e)