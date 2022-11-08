from platform import platform
from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _
from .extension_admin import profile_page
from .extension_manage import setting_page

tag = 'extension_psc'
name = '插件配置'

page = pages.TabsPage(tag=tag, name=name)
config_page = pages.TablePage(name='插件运行时配置')

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='extension_psc',
    hidden=True
)
pages.register_front_pages(page)
pages.register_front_pages(config_page)


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

config_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/extension/{extension_id}/config/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
        'new': actions.CreateAction(
            path="/api/v1/tenant/{tenant_id}/extension/{extension_id}/config/",
            init_data={
                'package': 'package',
                # 'type': 'type'
            }
        ),
    },
)