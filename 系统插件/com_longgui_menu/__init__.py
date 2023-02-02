import json

from arkid.core import extension
from typing import Optional, List
from arkid.core.api import operation
from arkid.core.translation import gettext_default as _
from arkid.core import pages, actions, routers
from arkid.core.pagenation import CustomPagination
from arkid.core import event as core_event
from arkid.core.schema import ResponseSchema
from ninja.pagination import paginate
from arkid.core.constants import *
from ninja import Field, Schema
from arkid.core import routers
from .models import Menu


class MenuItemOut(Schema):

    id: str
    name: str = Field(title=_("Name", "名称"))
    path: str = Field(title=_("Path", "路径"), notranslation=True)
    status: bool = Field(title=_("switch", "开关"), item_action={"path":"/api/v1/com_longgui_menu/menu/{id}/toggle_activate/", "method":actions.FrontActionMethod.GET.value})


class MenuListOut(ResponseSchema):
    data: List[MenuItemOut]


class MenuExtension(extension.Extension):

    def load(self):
        super().load()
        self.register_extension_api()
        self.register_pages()
        self.listen_event(core_event.EXCLUDE_PATHS, self.exclude_paths)

    def register_extension_api(self):

        self.menu_path = self.register_api(
            '/menus/', 
            'GET', 
            self.list_menus, 
            response=List[MenuItemOut], 
            tenant_path=False
        )
        
        self.toogle_menu_activate_path = self.register_api(
            '/menu/{id}/toggle_activate/', 
            'GET', 
            self.toggle_menu_active,
            tenant_path=False
        )

    def exclude_paths(self, event, **kwargs):
        menus = Menu.valid_objects.all()
        menu_path = []
        for menu in menus:
            menu_path.append(menu.path)
        return menu_path

    def register_pages(self):
        from . import page as menu_page
        from api.v1.pages.platform_admin import router

        self.register_front_pages([
            menu_page.page,
        ])

        self.register_front_routers(menu_page.router, router)


    @operation(MenuListOut, roles=[PLATFORM_ADMIN])
    @paginate(CustomPagination)
    def list_menus(self, request):
        """ 获取菜单
        """
        # 目前只考虑2级菜单情况
        global_routers = routers._get_global_routers()
        menus = Menu.valid_objects.all()
        menu_path = []
        for menu in menus:
            menu_path.append(menu.path)
        items = []
        for global_router in global_routers:
            items.append({
                'id': global_router.get('path', '') if global_router.get('path', '') else 'empty',
                'name': global_router.get('name', ''),
                'path': global_router.get('path', ''),
                'status': False if global_router.get('path', '') in menu_path else True
            })
            item_children = global_router.get('children', [])
            for item_child in item_children:
                items.append({
                    'id': item_child.get('path', '') if item_child.get('path', '') else 'empty',
                    'name': item_child.get('name', ''),
                    'path': '{}/{}'.format(global_router.get('path', ''), item_child.get('path', '')),
                    'status': False if item_child.get('path', '') in menu_path else True
                })
        return items
    
    @operation(roles=[PLATFORM_ADMIN])
    def toggle_menu_active(self, request, id: str):
        if id == 'empty':
            id = ''
        menu = Menu.valid_objects.filter(path=id).first()
        if menu:
            menu.delete()
        else:
            menu = Menu()
            menu.path = id
            menu.save()
        return self.success()

extension = MenuExtension()