from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'app_protocol'
name = '应用协议'


page = pages.TablePage(tag=tag, name=name)

pages.register_front_pages(page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='protocal',
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/app_protocols/',
        method=actions.FrontActionMethod.GET,
    ),
)