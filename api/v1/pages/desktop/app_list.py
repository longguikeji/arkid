from arkid.core import routers, pages, actions

tag = 'mine_app_list'
name = '应用市集'

page = pages.CardsPage(tag = tag, name = name)

pages.register_front_pages(page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='app',
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/mine/tenant/{tenant_id}/apps/',
        method=actions.FrontActionMethod.GET,
    )
)