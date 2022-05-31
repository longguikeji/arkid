# 所有租户列表/租户开关
from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'platform_config'
name = '平台配置'

page = pages.FormPage(name=name,tag=tag)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='settings',
)

pages.register_front_pages(page)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/platform_config/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
       'confirm': actions.ConfirmAction(
            path="/api/v1/platform_config/"
        ),
    }
)