from arkid.core import routers, pages

app_list_tag = 'mine_app_list'
app_list_name = '应用市集'

page = pages.CardsPage(
    tag = app_list_tag, 
    name = app_list_name,
    init_action=pages.FrontAction(
        path = '/api/v1/tenant/{tenant_id}/mine/apps/',
        method = pages.FrontActionMethod.GET
    )
)

router = routers.FrontRouter(
    path=app_list_tag,
    name=app_list_name,
    page=page
)

pages.register_front_pages(page)
