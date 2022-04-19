
from collections import OrderedDict
from uuid import uuid4
global_pages = []

FORM_PAGE_TYPE = 'form_page'
TABLE_PAGE_TYPE = 'table_page'
TREE_PAGE_TYPE = 'tree_page'

global_tags = []

def gen_tag(tag:str=None,tag_pre:str=None) -> str:
    """ 为页面或者行为生成tag

    Args:
        tag (str, optional): tag字符串，可指定亦可动态生成. Defaults to None.
        tag_pre (str, optional): tag前缀，一般可为插件名称或者其他. Defaults to None.

    Returns:
        str: tag字符串
    """
    tag = tag if tag else str(uuid4())
    tag = f"{tag_pre}_{tag}" if tag_pre else tag
    assert tag not in global_tags
    global_tags.append(tag)
    return tag

class FrontPage(OrderedDict):
    """ 前端页面配置类
    """
    def __init__(self, name:str, type, init_action, tag:str=None, tag_pre:str=None, *args, **kwargs):
        """初始化

        Args:
            name (_type_): _description_
            type (_type_): _description_
            init_action (_type_): _description_
            tag (str, optional): _description_. Defaults to None.
            tag_pre (str, optional): _description_. Defaults to None.
        """
        self["tag"] = gen_tag(tag,tag_pre)
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
    def __init__(self, tag=None, name=None, page=None, path=None, method=None, icon=None,tag_pre:str=None, *args, **kwargs):
        if tag:
            self["tag"] = gen_tag(tag,tag_pre)
        if name:
            self["name"] = name
        # 指向page的tag
        if page:
            self["page"] = page["tag"] if isinstance(page,FrontPage) else page
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
        pages = [pages]

    for page in pages:
        global_pages.remove(page)