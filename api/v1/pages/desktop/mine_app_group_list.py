from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'mine_app_group_list'
name = ''

page = pages.TreePage(tag = tag, name = name,show_vnode=True,show_page_if_no_node=False)
mine_group_apps_page = pages.CardsPage(name=name)

pages.register_front_pages(page)
pages.register_front_pages(mine_group_apps_page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='app',
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/mine/tenant/{tenant_id}/mine_app_groups/',
        method=actions.FrontActionMethod.GET,
    ),
    node_actions=[
        actions.DirectAction(
            path='/api/v1/mine/tenant/{tenant_id}/mine_app_groups/?parent_id={id}',
            method=actions.FrontActionMethod.GET,
        ),
        actions.CascadeAction(
            page=mine_group_apps_page
        )
    ]
)

mine_group_apps_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/mine/tenant/{tenant_id}/mine_group_apps/?app_group_id={app_group_id}',
        method=actions.FrontActionMethod.GET
    ),
)