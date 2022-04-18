from arkid.core import routers, pages

app_market_tag = 'app_market'
app_market_name = '应用市集'


router = routers.FrontRouter(
    path=app_market_tag,
    name=app_market_name,
    icon='app',
    page=app_market_tag,
)


page = pages.FrontPage(
    tag = app_market_tag, 
    name = app_market_name,
    type = pages.TABLE_PAGE_TYPE,
    init_action=pages.FrontAction(
        path = '/api/v1/tenant/{tenant_id}/app/',
        method = 'get'
    )
)

pages.register_front_pages(page)
