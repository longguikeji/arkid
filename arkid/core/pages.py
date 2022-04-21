
from collections import OrderedDict
from uuid import uuid4
from enum import Enum
global_pages = []


class FrontPageType(Enum):
    """前端页面类型枚举类
    Type页面类型 [可扩展]:
    >>> 表格型页面 （table）
    >>> 表单型页面 （form）
    >>> 描述型页面 （description）
    >>> 树状型页面 （tree）
    >>> 切换型页面 （tabs）- 暂不支持
    >>> 列表型页面 （list）- 暂不支持
    >>> 卡片型页面 （cards）- 暂不支持
    >>> 网格型页面 （grid）- 暂不支持
    """
    FORM_PAGE = 'form'
    TABLE_PAGE = 'table'
    TREE_PAGE = 'tree'
    DESCRIPTION_PAGE = 'description'
    TABS_PAGE = 'tabs'
    LIST_PAGE = 'list'
    CARDS_PAGE = 'cards'
    GRID_PAGE = 'grid'

global_tags = []

def gen_tag(tag:str=None,tag_pre:str=None) -> str:
    """ 为页面或者行为生成tag

    Args:
        tag (str, optional): tag字符串，可指定亦可动态生成. Defaults to None.
        tag_pre (str, optional): tag前缀，一般可为插件名称或者其他. Defaults to None.

    Returns:
        str: tag字符串
    """
    tag = tag if tag else uuid4().hex
    tag = f"{tag_pre}_{tag}" if tag_pre else tag
    assert tag not in global_tags
    global_tags.append(tag)
    return tag

class FrontPage(OrderedDict):
    """ 前端页面配置类
    """
    def __init__(self, name:str, page_type:FrontPageType, init_action, tag:str=None, tag_pre:str=None, *args, **kwargs):
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
        self["type"] = page_type.value
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

class FrontActionType(Enum):
    """前端动作类型枚举类
    
    ActionType操作类型 [可扩展]:
    
    >>> direct 直接操作类型
    >>> open 打开新页面类型
    >>> cancel 取消操作类型
    >>> reset 重置表单类型
    >>> import 导入数据类型
    >>> node 节点点击类型(页面中将隐藏该操作)
    >>> url 内外链接类型
    >>> password 编辑密码类型
    """
    
    DIRECT_ACTION = 'direct'
    OPEN_ACTION = 'open'
    CANCEL_ACTION = 'cancel'
    RESET_ACTION = 'reset'
    IMPORT_ACTION = 'import'
    NODE_ACTION = 'node'
    URL_ACTION = 'url'
    PASSWORD_ACTION = 'password'


class FrontAction(OrderedDict):
    def __init__(self, tag=None, action_type:FrontActionType=None,name=None, page=None, path=None, method=None, icon=None,tag_pre:str=None, *args, **kwargs):
        
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
            
        if action_type:
            self["type"] = action_type.value
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