
from collections import OrderedDict

global_pages = []

FORM_PAGE_TYPE = 'form_page'
TABLE_PAGE_TYPE = 'table_page'
TREE_PAGE_TYPE = 'tree_page'


class FrontPage(OrderedDict):
    def __init__(self, tag, name, type, init_action,  *args, **kwargs):
        self["tag"] = tag
        self["name"] = name
        self["type"] = type
        self["init"] = init_action
        super().__init__(*args, **kwargs)

    def add_global_action(self, actions):
        if not isinstance(actions, tuple) or not isinstance(actions, list):
            actions = list(actions)
        if not self.get('global'):
            self['global'] = []
        self['global'].extend(actions)
    
    def add_local_action(self, actions):
        if not isinstance(actions, tuple) or not isinstance(actions, list):
            actions = list(actions)
        if not self.get('local'):
            self['local'] = []
        self['local'].extend(actions)  

    def add_node_action(self, actions):
        if not isinstance(actions, tuple) or not isinstance(actions, list):
            actions = list(actions)
        if not self.get('node'):
            self['node'] = []
        self['node'].extend(actions)  


class FrontAction(OrderedDict):
    def __init__(self, tag=None, name=None, page=None, path=None, method=None, icon=None, *args, **kwargs):
        if tag:
            self["tag"] = tag
        if name:
            self["name"] = name
        if page:
            self["page"] = page
        if path:
            self["path"] = path
        if method:
            self["method"] = method
        if icon:
            self["icon"] = icon
        super().__init__(*args, **kwargs)


def register_front_pages(pages):
    if not isinstance(pages, tuple) or not isinstance(pages, list):
        pages = [pages]

    global_pages.extend(pages)


def unregister_front_pages(pages):
    if not isinstance(pages, tuple) or not isinstance(pages, list):
        pages = list(pages)

    for page in pages:
        global_pages.remove(page)