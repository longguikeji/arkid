from arkid.core import routers, pages

app_market_tag = 'app_market'
app_market_name = '应用市集'

page = pages.CardsPage(
    tag = app_market_tag, 
    name = app_market_name,
    init_action=pages.FrontAction(
        path = '/api/v1/tenant/{tenant_id}/app/',
        method = pages.FrontActionMethod.GET
    )
)

pages.register_front_pages(page)
