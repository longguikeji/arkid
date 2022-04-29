from . import user_list,user_group,devices,account_life
from arkid.core import routers


router = routers.FrontRouter(
    path='user',
    name='用户管理',
    icon='user',
    children=[
        user_list.router,
        user_group.router,
        devices.router,
        account_life.router
    ],
)