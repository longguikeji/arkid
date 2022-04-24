from . import app_market
from arkid.core import routers,pages


mine_router = routers.FrontRouter(
    path='mine',
    name='桌面',
    icon='home',
    children=[
    ]
)

mine_router.hidden = True