from . import auth_factor
from arkid.core import routers

auth_router = routers.FrontRouter(
    path='auth',
    name='认证管理',
    children=[
        auth_factor.router
    ],
)