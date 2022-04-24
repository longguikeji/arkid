from . import app_list
from arkid.core import routers


router = routers.FrontRouter(
    path='app',
    name='应用管理',
    icon='app',
    children=[
        app_list.router,
    ],
)