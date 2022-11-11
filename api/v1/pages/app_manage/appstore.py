from . import saas_app_list, private_app_list
from arkid.core import routers


router = routers.FrontRouter(
    path='appstore',
    name='应用商店',
    icon='app',
    children=[
        saas_app_list.router,
        private_app_list.router,
    ],
)