from . import user_list
from arkid.core import routers


auth_router = routers.FrontRouter(
    path='auth',
    name='认证管理',
    children=[
    ],
)