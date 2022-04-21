from . import app_market
from arkid.core import routers


router = routers.FrontRouter(
    path='desktop',
    name='桌面',
    icon='home',
    children=[
        app_market.router
    ],
)