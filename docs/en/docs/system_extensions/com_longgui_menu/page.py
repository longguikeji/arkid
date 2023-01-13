from arkid.core.translation import gettext_default as _
from arkid.core import routers, pages, actions

tag = 'menu_manage'
name = '菜单管理'

page = pages.TablePage(tag=tag, name=name)

pages.register_front_pages(page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='list',
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/com_longgui_menu/menus/',
        method=actions.FrontActionMethod.GET,
    ),
)
