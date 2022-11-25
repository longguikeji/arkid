from . import app_list,app_protocol,app_group, appstore,app_buy,app_api_config,app_edit,app_protocol_config
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
        app_buy.router,
        app_api_config.router,
        app_edit.router,
        app_protocol_config.router
    ],
)