def organization_context(request):
    try:
        return {"organization": getattr(request, "organization", None)}
    except Exception as e:
        import traceback
        from logger.utils import add_log
        msg = "Exception in documanager.context_processors.organization_context"
        add_log(level=4,exception=traceback.format_exc(),custom_message=msg)
        raise(e)