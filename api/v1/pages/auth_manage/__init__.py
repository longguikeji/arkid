from . import auth_factor,auth_rules
from arkid.core import routers

router = routers.FrontRouter(
    path='auth',
    name='认证管理',
    children=[
        auth_factor.router,
        auth_rules.router
    ],
)