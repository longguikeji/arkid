from collections import OrderedDict


global_routers = []


class FrontRouter(OrderedDict):
    def __init__(self, path, name=None, icon=None, children=None, redirect=None, page=None, url=None, *args, **kwargs):
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
        if url:
            self['url'] = url
        super().__init__(*args, **kwargs)

    def add_child(self, child):
        if not self["children"]:
            self["children"] = []
        self["children"].append(child)

    def remove_child(self, child):
        if not self["children"]:
            return
        self["children"].remove(child)

    def change_page_tag(self, header):
        if self['page']:
            self['page'] = header + '_' + self['page']
        if self['children']:
            for child in self['children']:
                child.change_page_tag(header)


def register_front_routers(routers, primary: str = ''):
    if not isinstance(routers, tuple) or not isinstance(routers, list):
        routers = list(routers)

    for primary_router in routers:
        if primary == primary_router["path"]:
            for router in routers:
                primary_router.add_child(router)
            return

    global_routers.extend(routers)


def unregister_front_routers(routers, primary: str = ''):
    if not isinstance(routers, tuple) or not isinstance(routers, list):
        routers = list(routers)

    for primary_router in routers:
        if primary == primary_router.path:
            for router in routers:
                primary_router.remove_child(router)
            return

    for router in routers:
        global_routers.remove(router)