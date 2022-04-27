from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'app_grant'
name = '所有应用'


page = pages.ListPage(tag=tag,name=name)
app_permission_page = pages.TablePage(name=_("该应用权限"))

pages.register_front_pages(page)
pages.register_front_pages(app_permission_page)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/apps/',
        method=actions.FrontActionMethod.GET,
    ),
    node_actions=[
        actions.CascadeAction(
            page=app_permission_page
        )
    ]
)

app_permission_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/apps/{app_id}/permissions/',
        method=actions.FrontActionMethod.GET
    )
)