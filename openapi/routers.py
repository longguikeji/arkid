from arkid.spectacular_settings import SPECTACULAR_SETTINGS
import json
root_list = []

class Router(dict):
    def __init__(self, path=None, name=None, icon=None, children=None, redirect=None, page=None, *args, **kwargs):
        if path:
            self['path'] = path
        if name:
            self['name'] = name
        if icon:
            self['icon'] = icon
        if children:
            self['children'] = children
        if redirect:
            self['redirect'] = redirect
        if page:
            self['page'] = page
        super().__init__(*args, **kwargs)

    def add_child(self, child):
        if not self.children:
            self.children = []
        self.children.append(child)

class PageRouter(Router):
    def __init__(self, page, *args, **kwargs):
        super().__init__(path=page.path, name=page.name, page=page.tag, *args, **kwargs)


class UrlRouter(Router):
    def __init__(self, path, name, url, *args, **kwargs):
        super().__init__(path=path, name=name, url=url, *args, **kwargs)


def fresh():
    SPECTACULAR_SETTINGS['EXTENSIONS_INFO']['routers'] = root_list

def root_add_routers(routers:list):
    root_list.extend(routers)
    fresh()

def get_router_by_path(paths:list, routers:list = root_list):
    path = paths.pop(0)
    for router in routers:
        router:Router
        if router.path == path:
            if len(paths) == 0:
                return router
            else:
                return get_router_by_path(paths, router.children)
    return None

def add_router_by_path(path:str, router:Router):
    if path == '/':
        root_list.append(router)
    else:
        paths = path.split('/')
        get_router_by_path(paths).add_child(router)

    fresh()


    
