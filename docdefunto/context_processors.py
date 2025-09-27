def organization_context(request):
    return {"organization": getattr(request, "organization", None)}