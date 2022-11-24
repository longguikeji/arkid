from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'app_edit'
name = '编辑应用'

page = pages.FormPage(tag=tag, name=name)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='app_edit',
    hidden=True
)

pages.register_front_pages(page)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/apps/{id}/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
       'confirm': actions.ConfirmAction(
            path="/api/v1/tenant/{tenant_id}/apps/{id}/"
        ),
    }
)