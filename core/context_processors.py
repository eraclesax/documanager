from django.conf import settings

def cms_context(request):
    from django.urls import resolve
    current_url_name = resolve(request.path_info).url_name

    context = dict()

    context = {
        **context, 
        **side_menu_context(current_url_name),
        "BASE_TEMPLATE":settings.BASE_TEMPLATE,
    }

    return context

def side_menu_context(current_url_name):
    side_menu = []
    
    url_name = "index"
    INDEX_PAGE = settings.INDEX_PAGE
    item = {
        "type":"url",
        "text":"Home",
        "url":url_name,
        "active":current_url_name==url_name or current_url_name==INDEX_PAGE,
        "icon_classes":"ni ni-bullet-list-67 text-primary",
        "childs":None,
        }
    side_menu.append(item)  

    if settings.FOTO_ACTIVE:
        url_name = "foto"
        item = {
            "type":"url",
            "text":"Rimuovi sfondo",
            "url":url_name,
            "active":current_url_name==url_name,
            "icon_classes":"ni ni-camera-compact text-primary",
            "childs":None,
            }
        side_menu.append(item)

    if settings.ANAGRAFICHE_ACTIVE:
        url_name = "anagrafiche"
        item = {
            "type":"url",
            "text":"Anagrafiche",
            "url":url_name,
            "active":current_url_name==url_name,
            "icon_classes":"ni ni-badge text-primary",
            "childs":None,
            }
        side_menu.append(item)

    # url_name = "storico_dash"
    # item = {
    #     "type":"url",
    #     "text":"Storico Accessi",
    #     "url":url_name,
    #     "active":current_url_name==url_name,
    #     "icon_classes":"ni ni-chart-pie-35 text-yellow",
    #     "childs":None,
    #     }
    # side_menu.append(item)
    
    # item = {
    #     "type":"bar",
    #     }
    # side_menu.append(item)
    
    # url_name = "hospitals"
    # item = {
    #     "type":"url",
    #     "text":"Ospedale",
    #     "url":url_name,
    #     "active":current_url_name==url_name,
    #     "icon_classes":"ni ni-building text-red",
    #     "childs":None,
    #     }
    # side_menu.append(item)
    
    # url_name = "patients"
    # item = {
    #     "type":"url",
    #     "text":"Pazienti",
    #     "url":url_name,
    #     "active":current_url_name==url_name,
    #     "icon_classes":"fa fa-id-card text-warning",
    #     "childs":None,
    #     }
    # side_menu.append(item)
    
    # url_name = "user_profile"
    # item = {
    #     "type":"url",
    #     "text":"Profilo",
    #     "url":url_name,
    #     "active":current_url_name==url_name,
    #     "icon_classes":"ni ni-single-02 text-yellow",
    #     "childs":None,
    #     }
    # side_menu.append(item)
    
    # url_name = "user_profile"
    # item = {
    #     "type":"url",
    #     "text":"Supporto",
    #     "url":url_name,
    #     "active":current_url_name==url_name,
    #     "icon_classes":"ni ni-support-16 text-green",
    #     "childs":None,
    #     }
    # side_menu.append(item)

    # url_name = "logout"
    # item = {
    #     "type":"url",
    #     "text":"Esci",
    #     "url":url_name,
    #     "active":current_url_name==url_name,
    #     "icon_classes":"ni ni-user-run text-red",
    #     "childs":None,
    #     }
    # side_menu.append(item)

    return {
        "side_menu":side_menu,
    }