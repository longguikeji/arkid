from . import app_list,app_protocol,app_group
from arkid.core import routers


router = routers.FrontRouter(
    path='app',
    name='应用管理',
    icon='app',
    children=[
        app_list.router,
        app_group.router,
        app_protocol.router,
    ],
)