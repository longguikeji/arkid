from platform import platform
from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _
from .extension_admin import profile_page
from .extension_manage import setting_page,config_page

tag = 'extension_psc'
name = '插件配置'

page = pages.TabsPage(tag=tag, name=name)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='extension_psc',
    hidden=True
)
pages.register_front_pages(page)

page.add_pages(
    [profile_page,
    setting_page,
    config_page]
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/extensions/{id}/',
        method=actions.FrontActionMethod.GET,
    ),
)