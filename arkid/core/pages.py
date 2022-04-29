from enum import Enum
from typing import List
from arkid.common import DeepSN
from arkid.common.utils import gen_tag
from arkid.core.actions import FrontAction
from arkid.core.translation import gettext_default as _
global_pages = {}


class FrontPageType(Enum):
    """前端页面类型枚举类
    Type页面类型 [可扩展]:
    ```
        - 表格型页面 (table)
        - 表单型页面 (form)
        - 描述型页面 (description)
        - 树状型页面 (tree)
        - 切换型页面 (tabs)- 暂不支持
        - 列表型页面 (list)- 暂不支持
        - 卡片型页面 (cards)- 暂不支持
        - 网格型页面 (grid)- 暂不支持
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

    def __init__(self, name: str, tag: str = None, tag_pre: str = None, type:FrontPageType=FrontPageType.TABLE_PAGE,*args, **kwargs):
        """初始化函数

        Args:
            name (str): 页面名称
            page_type (FrontPageType): 页面类型
            init_action (FrontAction|OrderedDict): 初始化动作
            global_actions (list): 全局动作
            local_actions (list): 本地动作
            tag (str, optional): 标识. 
            tag_pre (str, optional): 标识前缀. 
        """
        self.tag = gen_tag(tag, tag_pre)
        self.name = name
        self.type = type.value
        super().__init__(*args, **kwargs)
        
    def create_actions(self, init_action:FrontAction = None, global_actions: list = [], local_actions: list = [], node_actions:list=[]):
        self.init_action = init_action
        self.add_global_actions(global_actions)
        self.add_local_actions(local_actions)
        self.add_node_actions(node_actions)
        
    def add_global_actions(self, actions):
        """ 添加全局动作

        Args:
            actions (FrontAction|OrderedDict)): 动作列表
        """
        if not actions:
            return

        if not isinstance(actions, tuple) or not isinstance(actions, list):
            actions = list(actions)
        if not hasattr(self, "global_action"):
            self.global_action = []
        self.global_action.extend(actions)

    def add_local_actions(self, actions):
        """ 添加表单动作

        Args:
            actions (FrontAction|OrderedDict)): 动作列表
        """
        if not actions:
            return

        if not isinstance(actions, tuple) or not isinstance(actions, list):
            actions = list(actions)
        if not hasattr(self, "local_action"):
            self.local_action = []
        self.local_action.extend(actions)
    
    def add_node_actions(self, actions):
        """ 添加表单动作

        Args:
            actions (FrontAction|OrderedDict)): 动作列表
        """
        if not actions:
            return
            
        if not isinstance(actions, tuple) or not isinstance(actions, list):
            actions = list(actions)
        if not hasattr(self, "node_action"):
            self.node_action = []
        self.node_action.extend(actions)

    def add_tag_pre(self, tag_pre: str):
        """添加标识前缀
        用于插件中生成页面时给页面的标识添加前缀
        Args:
            tag_pre (str): 前缀
        """
        self.tag = gen_tag(self.tag, tag_pre)

    def dict(self):
        return super().dict()


class SelectPage(FrontPage):
    """选择型页面
    """

    def __init__(self, select: bool = False, *args, **kwargs):
        if select:
            self.select = select
        super().__init__(*args, **kwargs)

    def create_actions(self, select:bool=False,*args, **kwargs):
        if select:
            self.select = select
        return super().create_actions(*args, **kwargs)


class FormPage(FrontPage):
    """表单页面
    """

    def __init__(self, *args, **kwargs):
        super().__init__(type=FrontPageType.FORM_PAGE, *args, **kwargs)


class TablePage(SelectPage):
    """表格页面
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(type=FrontPageType.TABLE_PAGE, *args, **kwargs)


class TreePage(SelectPage):
    """树形页面
    """
    def __init__(self, *args, **kwargs):
        super().__init__(type=FrontPageType.TREE_PAGE, *args, **kwargs)


class DescriptionPage(FrontPage):
    """描述页面
    """

    def __init__(self, *args, **kwargs):
        super().__init__(type=FrontPageType.DESCRIPTION_PAGE, *args, **kwargs)


class ListPage(SelectPage):
    """列表页面
    """

    def __init__(self, *args, **kwargs):
        super().__init__(type=FrontPageType.LIST_PAGE, *args, **kwargs)


class CardsPage(SelectPage):
    """卡片列表
    """

    def __init__(self, *args, **kwargs):
        super().__init__(type=FrontPageType.CARDS_PAGE, *args, **kwargs)


class GridPage(FrontPage):
    """网格页面
    """

    def __init__(self, *args, **kwargs):
        super().__init__(type=FrontPageType.GRID_PAGE, *args, **kwargs)

class TabsPage(FrontPage):
    """网格页面
    """

    def __init__(self, pages:list=[],*args, **kwargs):
        self.add_pages(pages)
        super().__init__(type=FrontPageType.TABS_PAGE, *args, **kwargs)

    def add_pages(self,pages:list=[]):
        if not pages:
            return
            
        if not isinstance(pages, tuple) or not isinstance(pages, list):
            pages = list(pages)
        if not hasattr(self, "pages"):
            self.pages = []
        
        for item in pages:
            self.pages.append(item.tag if isinstance(item,FrontPage) else item)

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
    return [item.dict() for item in list(global_pages.values())]
