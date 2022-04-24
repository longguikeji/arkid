
from collections import OrderedDict
from uuid import uuid4
from enum import Enum
from arkid.common import DeepSN
global_pages = {}

class FrontPageType(Enum):
    """前端页面类型枚举类
    Type页面类型 [可扩展]:
    ```
        - 表格型页面 （table）
        - 表单型页面 （form）
        - 描述型页面 （description）
        - 树状型页面 （tree）
        - 切换型页面 （tabs）- 暂不支持
        - 列表型页面 （list）- 暂不支持
        - 卡片型页面 （cards）- 暂不支持
        - 网格型页面 （grid）- 暂不支持
    ```
    """
    FORM_PAGE = 'form'
    TABLE_PAGE = 'table'
    TREE_PAGE = 'tree'
    DESCRIPTION_PAGE = 'description'
    TABS_PAGE = 'tabs'
    LIST_PAGE = 'list'
    CARDS_PAGE = 'cards'
    GRID_PAGE = 'grid'

global_tags = [] # 全局tag列表

def gen_tag(tag:str=None,tag_pre:str=None) -> str:
    """ 为页面或者行为生成tag

    Args:
        tag (str, optional): tag字符串，可指定亦可动态生成. 
        tag_pre (str, optional): tag前缀，一般可为插件名称或者其他. 

    Returns:
        str: tag字符串
    """
    tag = tag if tag else uuid4().hex
    tag = f"{tag_pre}_{tag}" if tag_pre else tag
    assert tag not in global_tags
    global_tags.append(tag)
    return tag

class FrontPage(DeepSN):
    """ 前端页面配置类

    Examples:
        >>> from arkid.core import pages
        >>> from arkid.core.translation import gettext_default as _
        >>>
        >>> # 申明一个页面
        >>> page = pages.FrontPage(
        >>>     tag="user_list",
        >>>     name="user_list",
        >>>     page_type=pages.FrontPageType.TABLE_PAGE,
        >>>     init_action=pages.FrontAction(
        >>>         path='/api/v1/tenant/{tenant_id}/users/',
        >>>         method=pages.FrontActionMethod.GET
        >>>     )
        >>> )
        >>> # 添加局部动作
        >>> page.add_local_action(
        >>>     [
        >>>         pages.FrontAction(
        >>>             name=_("编辑"),
        >>>             page=user_edit_page,
        >>>             icon="icon-edit",
        >>>             action_type=pages.FrontActionType.OPEN_ACTION
        >>>         ),
        >>>         ...
        >>>     ]
        >>> )
        >>> # 添加全局动作
        >>> page.add_global_action(
        >>>     [
        >>>         pages.FrontAction(
        >>>             name="创建",
        >>>             page=user_create_page,
        >>>             icon="icon-create",
        >>>             action_type=pages.FrontActionType.OPEN_ACTION
        >>>         )
        >>>     ]
        >>> )
    """
    def __init__(self, name:str, tag:str=None, tag_pre:str=None, *args, **kwargs):
        """初始化函数

        Args:
            name (str): 页面名称
            page_type (FrontPageType): 页面类型
            init_action (FrontAction|OrderedDict): 初始化动作
            tag (str, optional): 标识. 
            tag_pre (str, optional): 标识前缀. 
        """
        self.tag = gen_tag(tag,tag_pre)
        self.name = name
        super().__init__(*args, **kwargs)

    def add_global_action(self, actions):
        """ 添加全局动作

        Args:
            actions (FrontAction|OrderedDict)): 动作列表
        """
        if not isinstance(actions, tuple) or not isinstance(actions, list):
            actions = list(actions)
        if not hasattr(self,"global_action"):
            self.global_action = []
        self.global_action.extend(actions)
    
    def add_local_action(self, actions):
        """ 添加表单动作

        Args:
            actions (FrontAction|OrderedDict)): 动作列表
        """
        if not isinstance(actions, tuple) or not isinstance(actions, list):
            actions = list(actions)
        if not hasattr(self,"local_action"):
            self.local_action = []
        self.local_action.extend(actions)  

    def add_node_action(self, actions):
        """ 添加树节点动作

        Args:
            actions (FrontAction|OrderedDict)): 动作列表
        """
        if not isinstance(actions, tuple) or not isinstance(actions, list):
            actions = list(actions)
        if not hasattr(self,'node'):
            self.node = []
        self.node.extend(actions)

    def add_tag_pre(self,tag_pre:str):
        """添加标识前缀

        用于插件中生成页面时给页面的标识添加前缀

        Args:
            tag_pre (str): 前缀
        """
        self.tag = gen_tag(self.tag,tag_pre)

    def dict(self):
        return super().dict()

class FormPage(FrontPage):
    """表单页面
    """
    def __init__(self, *args, **kwargs):
        self.type = FrontPageType.FORM_PAGE.value
        super().__init__(*args, **kwargs)

class TablePage(FrontPage):
    """表格页面
    """
    def __init__(self, *args, **kwargs):
        self.type = FrontPageType.TABLE_PAGE.value
        super().__init__(*args, **kwargs)

class TreePage(FrontPage):
    """树形页面
    """
    def __init__(self, *args, **kwargs):
        self.type = FrontPageType.TREE_PAGE.value
        super().__init__(*args, **kwargs)

    def set_next(self,next):
        self.next = next.tag if isinstance(next,FrontPage) else next

class DescriptionPage(FrontPage):
    """描述页面
    """
    def __init__(self, *args, **kwargs):
        self.type = FrontPageType.DESCRIPTION_PAGE.value
        super().__init__(*args, **kwargs)

class ListPage(FrontPage):
    """列表页面
    """
    def __init__(self, *args, **kwargs):
        self.type = FrontPageType.LIST_PAGE.value
        super().__init__(*args, **kwargs)

class CardsPage(FrontPage):
    """卡片列表
    """
    def __init__(self, *args, **kwargs):
        self.type = FrontPageType.CARDS_PAGE.value
        super().__init__(*args, **kwargs)

class GridPage(FrontPage):
    """网格页面
    """
    def __init__(self, *args, **kwargs):
        self.type = FrontPageType.GRID_PAGE.value
        super().__init__(*args, **kwargs)


class FrontActionType(Enum):
    """前端动作类型枚举类
    
    ActionType操作类型 [可扩展]:
    ```
    - direct 直接操作类型
    - open 打开新页面类型
    - cancel 取消操作类型
    - reset 重置表单类型
    - import 导入数据类型
    - node 节点点击类型(页面中将隐藏该操作)
    - url 内外链接类型
    - password 编辑密码类型
    ```
    """
    
    DIRECT_ACTION = 'direct'
    OPEN_ACTION = 'open'
    CANCEL_ACTION = 'cancel'
    RESET_ACTION = 'reset'
    IMPORT_ACTION = 'import'
    NODE_ACTION = 'node'
    URL_ACTION = 'url'
    PASSWORD_ACTION = 'password'

class FrontActionMethod(Enum):
    """ 前端动作类型枚举类
    
    ActionMethod 动作方法 [可扩展]:
    
    ```
    - get
    - post
    - put
    - delete
    ```
    """
    
    GET = 'get'
    POST = 'post'
    PUT = 'put'
    DELETE = 'delete'


class FrontAction(DeepSN):
    """ 前端页面动作类

    Examples:
        >>> from arkid.core import pages
        >>> from arkid.core.translation import gettext_default as _
        >>>
        >>> edit_action = pages.FrontAction(
        >>>     name=_("编辑"),
        >>>     page=user_edit_page,
        >>>     icon="icon-edit",
        >>>     action_type=pages.FrontActionType.OPEN_ACTION
        >>> )
        >>> delete_action = pages.FrontAction(
        >>>     name=_("删除"),
        >>>     method=pages.FrontActionMethod.DELETE,
        >>>     path="/api/v1/tenant/{tenant_id}/users/{id}/",
        >>>     icon="icon-delete",
        >>>     action_type=pages.FrontActionType.DIRECT_ACTION
        >>> )
    """
    
    def __init__(self, tag:str=None, action_type:FrontActionType=None,name:str=None, page=None, path:str=None, method:FrontActionMethod=None, icon:str=None,tag_pre:str=None, *args, **kwargs):
        """初始化函数

        Args:
            tag (str, optional): 标识. 
            action_type (FrontActionType, optional): 动作类型. 
            name (str, optional): 名称. 
            page (FrontPage|str, optional): 指向页面,此处存储页面的标识. 
            path (str, optional): 请求路径. 
            method (FrontActionMethod, optional): 请求方法. 
            icon (str, optional): 图标名称. 
            tag_pre (str, optional): 标识前缀. 
        """
        self.tag = gen_tag(tag,tag_pre)
        
        if name:
            self.name = name
        # 指向page的tag
        if page:
            self.page = page.tag if isinstance(page,FrontPage) else page
        if path:
            self.path = path
        if method:
            self.method = method.value
        if icon:
            self.icon = icon
            
        if action_type:
            self.type = action_type.value
        super().__init__(*args, **kwargs)

    def add_tag_pre(self,tag_pre:str):
        """ 添加标识前缀

        Args:
            tag_pre (str): 标识前缀
        """
        self.tag = gen_tag(self.tag,tag_pre)

def register_front_pages(pages):
    """注册前端页面

    Args:
        pages (List|FrontPage): 前端页面
    """
    if not isinstance(pages, tuple) or not isinstance(pages, list):
        pages = [pages]
    
    for page in pages:
        global_pages[page.tag] = page


def unregister_front_pages(pages):
    """卸载页面

    Args:
        pages (List|FrontPage): 前端页面
    """
    if not isinstance(pages, tuple) or not isinstance(pages, list):
        pages = [pages]

    for page in pages:
        global_pages.pop(page.tag)

def get_global_pages():
    """获取页面列表
    """
    return [ item.dict() for item in list(global_pages.values()) ]