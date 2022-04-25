from enum import Enum
from typing import Union, Tuple
from arkid.common import DeepSN
from arkid.common.utils import gen_tag
from arkid.core.translation import gettext_default as _

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

    def __init__(self, action_type: FrontActionType, tag: str = None, path: str = None, method: FrontActionMethod = None,
                name: str = None, page=None, page_tag=None, icon: str = None, tag_pre: str = None, next_action = None,
                result_page = None, result_page_tag = None, *args, **kwargs):
        """初始化函数

        Args:
            tag (str, optional): 标识.
            action_type (FrontActionType): 动作类型.
            name (str, optional): 名称.
            page (FrontPage|str, optional): 指向页面,此处存储页面的标识.
            path (str, optional): 请求路径.
            method (FrontActionMethod, optional): 请求方法.
            icon (str, optional): 图标名称.
            tag_pre (str, optional): 标识前缀.
        """
        self.type = action_type.value
        
        self.tag = gen_tag(tag, tag_pre)

        if name:
            self.name = name
        if page:
            self.page = page.tag
        # 指向page的tag
        if page_tag:
            self.page = page_tag
        if path:
            self.path = path
        if method:
            self.method = method
        if icon:
            self.icon = icon
            
        if next_action:
            self.next_action = next_action
        if result_page:
            self.result_page = result_page.tag
        if result_page_tag:
            self.result_page = result_page_tag
        
        super().__init__(*args, **kwargs)

    def add_tag_pre(self, tag_pre: str):
        """ 添加标识前缀

        Args:
            tag_pre (str): 标识前缀
        """
        self.tag = gen_tag(self.tag, tag_pre)


class DirectAction(FrontAction):
    def __init__(self, *args, **kwargs):
        super().__init__(action_type=FrontActionType.DIRECT_ACTION, *args, **kwargs)


class OpenAction(FrontAction):
    def __init__(self, *args, **kwargs):
        super().__init__(action_type=FrontActionType.OPEN_ACTION, *args, **kwargs)


class CancelAction(FrontAction):
    """取消"""

    def __init__(self, *args, **kwargs):
        self.name = _("取消")
        super().__init__(action_type=FrontActionType.CANCEL_ACTION, *args, **kwargs)


class ResetAction(FrontAction):
    def __init__(self, *args, **kwargs):
        self.name = _("重置")
        super().__init__(action_type=FrontActionType.RESET_ACTION, *args, **kwargs)


class ImportAction(FrontAction):
    def __init__(self, *args, **kwargs):
        super().__init__(action_type=FrontActionType.IMPORT_ACTION, *args, **kwargs)


class URLAction(FrontAction):
    def __init__(self, *args, **kwargs):
        super().__init__(action_type=FrontActionType.URL_ACTION, *args, **kwargs)


class PasswordAction(FrontAction):
    def __init__(self, *args, **kwargs):
        super().__init__(action_type=FrontActionType.PASSWORD_ACTION, *args, **kwargs)


class ConfirmAction(DirectAction):
    def __init__(self, path: str, *args, **kwargs):
        self.name = _("确认")
        self.path = path
        self.icon="icon-confirm"
        self.method=FrontActionMethod.POST.value
        super().__init__(*args, **kwargs)


class DeleteAction(DirectAction):
    def __init__(self, path: str, *args, **kwargs):
        self.name = _("删除"),
        self.method = FrontActionMethod.DELETE.value,
        self.icon="icon-delete",
        self.path = path
        super().__init__(*args, **kwargs)

class  CreateAction(OpenAction):
    def __init__(self, page, *args, **kwargs):
        self.name=_("创建"),
        self.icon="icon-create",
        super().__init__(page=page, *args, **kwargs)

class  EditAction(OpenAction):
    def __init__(self, page, *args, **kwargs):
        self.name=_("编辑"),
        self.icon="icon-edit",
        super().__init__(page=page, *args, **kwargs)