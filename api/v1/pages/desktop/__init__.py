from . import app_market
from arkid.core import routers,pages


desktop_page = pages.GridPage(
    name="桌面",
    tag="descktop"
)

desktop_page.children = [app_market.page]

router = routers.FrontRouter(
    path='desktop',
    name='桌面',
    icon='home',
    page=[desktop_page]
)