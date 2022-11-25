from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'app_protocol_config'
name = '应用协议配置'

page = pages.FormPage(tag=tag, name=name)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='app_protocol_config',
    hidden=True
)

pages.register_front_pages(page)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/apps/{id}/config/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
       'confirm': actions.ConfirmAction(
            path="/api/v1/tenant/{tenant_id}/apps/{id}/config/"
        ),
    }
)
