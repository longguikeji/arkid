from . import app_list,app_protocol,app_group, appstore
from arkid.core import routers


router = routers.FrontRouter(
    path='app',
    name='应用管理',
    icon='app',
    children=[
        app_list.router,
        appstore.router,
        app_group.router,
        app_protocol.router,
    ],
)