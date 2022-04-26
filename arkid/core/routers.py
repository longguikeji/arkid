from arkid.common import DeepSN
from arkid.core.pages import FrontPage

global_routers = []

class FrontRouter(DeepSN):
    """_前端路由类

    Examples:
        >>> from arkid.core import routers
        >>> 
        >>> router = routers.FrontRouter(
        >>>     path='user',
        >>>     name='用户管理',
        >>>     icon='user',
        >>>     children=[
        >>>         routers.FrontRouter(
        >>>             path=user_list_tag,
        >>>             name='用户管理',
        >>>             icon='user',
        >>>             page=user_list_tag,
        >>>         )
        >>>     ],
        >>> )
    """
    def __init__(self, path:str, name:str=None, icon:str=None, children=None, redirect=None, page=None, url=None, *args, **kwargs):
        """初始化

        Args:
            path (str): 路由路径
            name (str, optional): 路由名称. Defaults to None.
            icon (str, optional): 图标. Defaults to None.
            children (List, optional): 子路由列表. Defaults to None.
            redirect (str, optional): 跳转链接. Defaults to None.
            page (FrontPage, optional): 页面. Defaults to None.
            url (str, optional): 链接地址. Defaults to None.
        """
        self.path = path
        if name:
            self.name = name
        if icon:
            self.icon = icon
        if children:
            self.children = children
        if redirect:
            self.redirect = redirect
        if page:
            if isinstance(page,list):
                self.page = []
                for p in page:
                    self.page.append(
                        p.tag if isinstance(p,FrontPage) else p
                    )
            else:
                self.page = page.tag if isinstance(page,FrontPage) else page
        if url:
            self.url = url
        super().__init__(*args, **kwargs)

    def add_children(self, child):
        """添加子路由

        Args:
            child (OrderedDict): 子路由描述
        """
        if not hasattr(self,"children"):
            self.children = []
        self.children.append(child)

    def remove_child(self, child):
        """移除子路由

        Args:
            child (OrderedDict): 子路由描述
        """
        if not self.children:
            return
        self.children.remove(child)

    def change_page_tag(self, header):
        """更改页面标识，主要用于插件中添加标识前缀以注明该页面来源

        注意： 此处会将子页面标识一并更改

        Args:
            header (str): 页面标识前缀
        """
        if hasattr(self,"page"):
            self.page:FrontPage
            self.page.add_tag_pre(header)
        if hasattr(self,"children"):
            for child in self.children:
                child.change_page_tag(header)

def register_front_routers(routers, primary: FrontRouter = None):
    """注册前端路由

    Args:
        routers (list): 路由列表或者路由
        primary (str, optional): 主路由. Defaults to ''.
    """
    if not isinstance(routers, tuple) or not isinstance(routers, list):
        routers = list(routers)

    if primary:
        primary.add_children(routers)
        return
    global_routers.extend(routers)


def unregister_front_routers(routers, primary: FrontRouter = None):
    """卸载前端路由

    Args:
        routers (list): 路由列表或路由
        primary (str, optional): 主路由. Defaults to ''.
    """
    if not isinstance(routers, tuple) or not isinstance(routers, list):
        routers = list(routers)

    if primary:
        for router in routers:
            primary.remove_child(router)
        return
        
    for router in routers:
        global_routers.remove(router)

def get_global_routers():
    return [ item.dict() for item in global_routers ]